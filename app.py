import os
import secrets
import threading
import time

from flask import Flask, flash, jsonify, redirect, render_template, request, send_from_directory, session, url_for
from flask_login import LoginManager, current_user, login_required

from admin_routes import admin_bp
from auth_routes import auth_bp
from code_runner import run_python
from code_runner.interactive_session import InteractiveSession
from config import Config
from course_data.constants import DEFAULT_CODE_EDITOR_PLACEHOLDER
from course_data.dish_calculator import DISH_CALCULATOR_PRODUCTS, DISH_CALCULATOR_RECIPES
from course_data.project import PROJECT_LINE
from course_data.project_state import build_project_meta, completed_project_stages, project_line_for_module, project_meta_for_task
from course_data import (
    ACHIEVEMENTS,
    LESSONS,
    TASK_BY_ID,
    TOTAL_TASKS_COUNT,
    task_client_payload,
    topic_by_task_id,
    validate_interactive_answer,
    validate_project_tests,
    stdout_matches,
)
from course_data.task_text_format import format_task_text
from course_data.project_stage_runner import (
    PROJECT_STAGE_TIMEOUT_SEC,
    task_auto_stdin_mode,
    validate_m1_project_stage,
    validate_project_stage_runs,
)
from db import db
from models import User
from profile_service import build_profile_context
from progress_service import (
    UserProgress,
    course_started,
    get_user_progress,
    mark_course_started,
    module_access_lock_message,
    strict_course_enforcement_enabled,
    task_access_lock_message,
)

app = Flask(__name__, static_folder='CSS', template_folder='HTML')
app.config.from_object(Config)
if not app.config.get('SECRET_KEY'):
    app.config['SECRET_KEY'] = secrets.token_hex(32)
Config.init_app(app)
app.jinja_env.filters['format_task_text'] = format_task_text
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['TEMPLATES_AUTO_RELOAD'] = True

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Войдите или зарегистрируйтесь, чтобы продолжить обучение.'

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)


@app.errorhandler(403)
def forbidden(_error):
    return render_template('errors/403.html'), 403


@app.context_processor
def inject_auth_context():
    return {
        'auth_user': current_user if current_user.is_authenticated else None,
    }


@login_manager.user_loader
def load_user(user_id: str):
    return db.session.get(User, int(user_id))


@login_manager.unauthorized_handler
def unauthorized():
    if request.path.startswith('/api/') or request.is_json:
        return jsonify({
            'error': 'Требуется вход',
            'login_url': url_for('auth.login', next=request.path),
        }), 401
    return redirect(url_for('auth.login', next=request.path))


# One-line toggle: True = нельзя сдавать project_stage без предыдущей версии.
ENFORCE_PROJECT_STAGE_PREREQUISITE = Config.ENFORCE_PROJECT_STAGE_PREREQUISITE
ENFORCE_M1_BEFORE_M2 = Config.ENFORCE_M1_BEFORE_M2
COURSE_GRADE_PROJECT_WEIGHTS = {1: 52, 2: 28}
COURSE_GRADE_TASK_WEIGHT = 20
PROJECT_TASK_KINDS = frozenset({'project_stage', 'project_step'})
COURSE_GRADE_DEMO_PANEL_ENABLED = Config.COURSE_GRADE_DEMO_PANEL_ENABLED


def _enforce_m1_gate() -> bool:
    return ENFORCE_M1_BEFORE_M2 and strict_course_enforcement_enabled()


def _enforce_project_prerequisite() -> bool:
    return ENFORCE_PROJECT_STAGE_PREREQUISITE and strict_course_enforcement_enabled()


def _course_grade_demo_panel_enabled() -> bool:
    return COURSE_GRADE_DEMO_PANEL_ENABLED and current_user.is_authenticated and current_user.is_admin


@app.route('/health')
def health():
    """Проверка для Railway и других PaaS (без сессии и без запуска кода)."""
    return 'ok', 200

INTERACTIVE_SESSIONS: dict[str, InteractiveSession] = {}
INTERACTIVE_LOCK = threading.Lock()


def _navigate_to_task_by_id(progress: UserProgress, task_id: int) -> bool:
    """Переключает модуль и индекс задания по id задачи. False если id не найден или модуль закрыт."""
    if task_id not in TASK_BY_ID:
        return False
    for mid in sorted(LESSONS.keys()):
        mod = LESSONS[mid]
        if mod.get('stub'):
            continue
        tasks = mod.get('tasks') or []
        for i, t in enumerate(tasks):
            if t['id'] == task_id:
                lock = module_access_lock_message(progress, mid, enforce=_enforce_m1_gate())
                if lock:
                    return False
                progress.current_module = mid
                progress.current_task_index = i
                progress.save()
                return True
    return False


def build_modules_stats(progress):
    return [
        {
            'id': i,
            'title': LESSONS[i]['title'],
            'icon': LESSONS[i]['icon'],
            'icon_file': LESSONS[i].get('icon_file'),
            'progress': progress.get_module_progress(i),
            'is_locked': bool(LESSONS[i].get('stub')) or bool(
                module_access_lock_message(progress, i, enforce=_enforce_m1_gate())
            ),
            'is_stub': bool(LESSONS[i].get('stub')),
        }
        for i in sorted(LESSONS.keys())
        if i in LESSONS
    ]


def build_sidebar_modules(progress, current_module_num, current_topic=None):
    current_topic_id = current_topic['id'] if current_topic else None
    out = []
    for mid in sorted(LESSONS.keys()):
        mod = LESSONS[mid]
        tasks = mod.get('tasks') or []
        topics_out = []
        for topic in mod.get('topics') or []:
            if topic.get('draft'):
                continue
            topic_tasks = topic.get('tasks') or []
            if not topic_tasks:
                continue
            topics_out.append({
                'id': topic['id'],
                'title': topic['title'],
                'first_task_id': topic_tasks[0]['id'],
                'is_active': mid == current_module_num and topic['id'] == current_topic_id,
            })
        out.append({
            'id': mid,
            'progress': progress.get_module_progress(mid),
            'completed_tasks': sum(1 for t in tasks if t['id'] in progress.completed_tasks),
            'total_tasks': len(tasks),
            'is_current': mid == current_module_num,
            'expanded': mid == current_module_num,
            'is_locked': bool(module_access_lock_message(progress, mid, enforce=_enforce_m1_gate())),
            'topics': topics_out,
        })
    return out


def build_course_grade_demo() -> dict:
    steps = []
    project_stage_totals = {}
    non_project_total = 0

    for mid in sorted(LESSONS.keys()):
        mod = LESSONS[mid]
        if mod.get('stub'):
            continue
        project_stage_totals[str(mid)] = len(project_line_for_module(mid))
        for task in mod.get('tasks') or []:
            is_project = task.get('kind') in PROJECT_TASK_KINDS
            topic = topic_by_task_id(mid, task['id'])
            if not is_project:
                non_project_total += 1
            steps.append({
                'module': mid,
                'taskId': task['id'],
                'topic': topic.get('num') if topic else None,
                'isProject': is_project,
                'projectStage': topic.get('num') if topic and is_project else None,
            })

    return {
        'steps': steps,
        'projectWeights': COURSE_GRADE_PROJECT_WEIGHTS,
        'projectStageTotals': project_stage_totals,
        'taskWeight': COURSE_GRADE_TASK_WEIGHT,
        'taskTotal': non_project_total,
    }


def _task_preview_parts(task: dict, topic: dict | None, task_index_in_module: int) -> tuple[str, str]:
    """Короткие части для карточки «Следующее задание»: тема и номер задания."""
    topic_title = (topic or {}).get('title') or ''
    task_label = ''
    if topic and topic.get('tasks'):
        for i, row in enumerate(topic['tasks']):
            if row.get('id') == task.get('id'):
                task_label = f'Задание {i + 1}'
                break
    if not task_label:
        kind = task.get('kind') or task.get('type') or ''
        kind_labels = {
            'project_stage': 'Версия проекта',
            'ordering': 'Расставить шаги',
            'quiz': 'Тест',
            'fill_gaps': 'Заполнить пропуски',
            'matching': 'Сопоставление',
            'code': 'Практика',
        }
        task_label = kind_labels.get(kind, f'Задание {task_index_in_module + 1}')
    if not topic_title:
        topic_title = task_label
        task_label = ''
    return topic_title, task_label


def _compact_task_preview(task: dict, topic: dict | None, task_index_in_module: int) -> str:
    """Короткая строка для карточек на главной и в профиле — без полного текста задания."""
    topic_title, task_label = _task_preview_parts(task, topic, task_index_in_module)
    if topic_title and task_label:
        return f'{topic_title} · {task_label.lower()}'
    return topic_title or task_label or f'Задание {task_index_in_module + 1}'


def next_task_preview(progress):
    mid = progress.current_module
    idx = progress.current_task_index
    if mid not in LESSONS:
        return None
    mod = LESSONS[mid]
    tasks = mod['tasks']
    if mod.get('stub') or not tasks:
        return {
            'module_title': mod['title'],
            'module_icon': mod['icon'],
            'module_icon_file': mod.get('icon_file'),
            'text': 'Откройте модуль в разделе заданий.',
            'task_id': None,
        }
    if idx >= len(tasks):
        return None
    t = tasks[idx]
    topic = topic_by_task_id(mid, t['id'])
    topic_title, task_label = _task_preview_parts(t, topic, idx)
    return {
        'module_title': mod['title'],
        'module_icon': mod['icon'],
        'module_icon_file': mod.get('icon_file'),
        'text': _compact_task_preview(t, topic, idx),
        'topic_title': topic_title,
        'task_label': task_label,
        'task_id': t['id'],
    }


def _is_topic_completed(progress, module_id: int, topic_num: int) -> bool:
    mod = LESSONS.get(module_id) or {}
    completed = set(progress.completed_tasks)
    for topic in mod.get('topics') or []:
        if topic.get('num') != topic_num:
            continue
        tasks = topic.get('tasks') or []
        return bool(tasks) and all(task['id'] in completed for task in tasks)
    return False


def _is_project_completed(progress, module_id: int) -> bool:
    total = len(project_line_for_module(module_id))
    return total > 0 and len(completed_project_stages(progress, module_id)) >= total


def achievement_list(progress, total_n):
    completed_n = len(progress.completed_tasks)
    frac = completed_n / total_n if total_n else 0.0
    out = []
    for a in ACHIEVEMENTS:
        unlocked = False
        if 'min_completed' in a:
            unlocked = completed_n >= a['min_completed']
        elif 'min_fraction' in a:
            unlocked = frac >= a['min_fraction'] - 1e-9
        elif 'topic_completed' in a:
            req = a['topic_completed']
            unlocked = _is_topic_completed(progress, req['module'], req['topic'])
        elif 'project_completed' in a:
            req = a['project_completed']
            unlocked = _is_project_completed(progress, req['module'])
        out.append({
            'id': a['id'],
            'icon': a['icon'],
            'title': a['title'],
            'description': a['description'],
            'unlocked': unlocked,
            **({'min_completed': a['min_completed']} if 'min_completed' in a else {}),
            **({'min_fraction': a['min_fraction']} if 'min_fraction' in a else {}),
            **({'topic_completed': a['topic_completed']} if 'topic_completed' in a else {}),
            **({'project_completed': a['project_completed']} if 'project_completed' in a else {}),
        })
    return out


def _course_grade_label(pct: int) -> tuple[str, str]:
    if pct >= 85:
        label = 'Отлично'
        state = 'excellent'
    elif pct >= 70:
        label = 'Хорошо'
        state = 'good'
    elif pct >= 50:
        label = 'Удовлетворительно'
        state = 'satisfactory'
    else:
        label = 'Здесь появится твоя оценка'
        state = 'pending'
    return label, state


def _module_task_counts(progress: UserProgress, module_id: int) -> tuple[int, int]:
    mod = LESSONS.get(module_id) or {}
    tasks = mod.get('tasks') or []
    if not tasks:
        return 0, 0
    completed = set(progress.completed_tasks)
    done = sum(1 for task in tasks if task['id'] in completed)
    return done, len(tasks)


def _non_project_task_counts(progress) -> tuple[int, int]:
    completed = set(progress.completed_tasks)
    done = 0
    total = 0
    for mod in LESSONS.values():
        if mod.get('stub'):
            continue
        for task in mod.get('tasks') or []:
            if task.get('kind') in PROJECT_TASK_KINDS:
                continue
            total += 1
            if task['id'] in completed:
                done += 1
    return done, total


def course_grade_meta(progress) -> dict:
    pct = 0
    project_done = 0
    project_total = 0

    for module_id, weight in COURSE_GRADE_PROJECT_WEIGHTS.items():
        stages_total = len(project_line_for_module(module_id))
        stages_done = len(completed_project_stages(progress, module_id))
        project_done += stages_done
        project_total += stages_total
        if stages_total:
            pct += int(stages_done * weight / stages_total)

    task_done, task_total = _non_project_task_counts(progress)
    if task_total:
        pct += int(task_done * COURSE_GRADE_TASK_WEIGHT / task_total)

    pct = max(0, min(100, pct))
    label, state = _course_grade_label(pct)
    return {
        'percent': pct,
        'label': label,
        'state': state,
        'completed': task_done + project_done,
        'total': task_total + project_total,
        'task_completed': task_done,
        'task_total': task_total,
        'project_completed': project_done,
        'project_total': project_total,
    }


@app.route('/')
def home():
    progress = get_user_progress() if current_user.is_authenticated else None
    completed_tasks = len(progress.completed_tasks) if progress else 0
    has_progress = course_started(progress) if progress else False
    overall_pct = int(completed_tasks * 100 / TOTAL_TASKS_COUNT) if TOTAL_TASKS_COUNT and progress else 0
    return render_template(
        'index.html',
        user=progress,
        auth_user=current_user if current_user.is_authenticated else None,
        modules_stats=build_modules_stats(progress) if progress else build_modules_stats(UserProgress()),
        total_tasks=TOTAL_TASKS_COUNT,
        completed_tasks=completed_tasks,
        has_progress=has_progress,
        course_grade=course_grade_meta(progress) if progress else course_grade_meta(UserProgress()),
        course_grade_demo=build_course_grade_demo(),
        next_task=next_task_preview(progress) if progress else None,
        achievements=achievement_list(progress, TOTAL_TASKS_COUNT) if progress else achievement_list(UserProgress(), TOTAL_TASKS_COUNT),
        overall_progress_pct=overall_pct,
    )


@app.route('/theory_schemes/<path:filename>')
def theory_schemes_file(filename: str):
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'theory_schemes')
    return send_from_directory(base, filename)


@app.route('/calorie-calculator')
def calorie_calculator():
    return render_template(
        'calorie_calculator.html',
        products=DISH_CALCULATOR_PRODUCTS,
        recipes=DISH_CALCULATOR_RECIPES,
    )


@app.route('/profile')
@login_required
def profile():
    if current_user.is_admin:
        return redirect(url_for('admin.index'))
    progress = get_user_progress()
    ctx = build_profile_context(current_user, progress, enforce_m1_gate=_enforce_m1_gate())
    return render_template('profile.html', **ctx)


@app.route('/learn')
@login_required
def learn():
    progress = get_user_progress()
    mark_course_started()

    m_lock = module_access_lock_message(progress, progress.current_module, enforce=_enforce_m1_gate())
    if m_lock:
        progress.current_module = 1
        progress.current_task_index = 0
        progress.save()
        flash(m_lock, 'error')

    task_id_arg = request.args.get('task_id', type=int)
    if task_id_arg is not None:
        if not _navigate_to_task_by_id(progress, task_id_arg):
            lock = module_access_lock_message(progress, 2, enforce=_enforce_m1_gate())
            if lock:
                flash(lock, 'error')
            return redirect(url_for('learn'))
        return redirect(url_for('learn'))

    current_module = progress.current_module
    current_task_index = progress.current_task_index

    if current_module in LESSONS:
        tasks = LESSONS[current_module]['tasks']
        mod_obj = LESSONS[current_module]
        if mod_obj.get('stub') or not tasks:
            return render_template(
                'learn_stub.html',
                user=progress,
                current_module=mod_obj,
                current_module_num=current_module,
                modules_stats=build_modules_stats(progress),
                total_tasks=TOTAL_TASKS_COUNT,
                completed_tasks=len(progress.completed_tasks),
                course_grade=course_grade_meta(progress),
                project_meta=build_project_meta(progress, current_module),
            )
        if current_task_index >= len(tasks):
            current_task_index = max(0, len(tasks) - 1)
            progress.current_task_index = current_task_index
            progress.save()

    if current_module not in LESSONS:
        current_module = 1
        progress.current_module = 1
        current_task_index = 0

    module = LESSONS[current_module]
    tasks = module['tasks']
    if module.get('stub') or not tasks:
        return render_template(
            'learn_stub.html',
            user=progress,
            current_module=module,
            current_module_num=current_module,
            modules_stats=build_modules_stats(progress),
            total_tasks=TOTAL_TASKS_COUNT,
            completed_tasks=len(progress.completed_tasks),
            course_grade=course_grade_meta(progress),
            project_meta=build_project_meta(progress, current_module),
        )

    if current_task_index >= len(tasks):
        current_task_index = 0

    current_task = tasks[current_task_index]
    topics = module.get('topics') or []
    current_topic = topic_by_task_id(current_module, current_task['id'])
    topic_index = next((i for i, t in enumerate(topics) if t['id'] == current_topic['id']), 0) if current_topic else 0
    tasks_in_topic = len(current_topic['tasks']) if current_topic else 1
    task_ord_in_topic = next(
        (j for j, t in enumerate(current_topic['tasks']) if t['id'] == current_task['id']),
        0,
    ) if current_topic else 0

    is_project_stage = current_task.get('kind') == 'project_stage'
    is_project_release_task = current_task.get('kind') in ('project_stage', 'project_step')
    project_stage_lock_message = _project_stage_lock_message(progress, current_task['id'])
    project_stage_is_locked = bool(project_stage_lock_message)
    task_done = current_task['id'] in progress.completed_tasks
    topic_num = current_topic.get('num') if current_topic else None
    focused_project_topic = topic_num if is_project_release_task and not project_stage_is_locked else None
    project_meta = build_project_meta(progress, current_module, topic_num=focused_project_topic)
    saved_project = progress.project_code.get(current_module, '')
    project_spec = current_task.get('project_spec') if is_project_stage else None
    topic_tasks_nav = [
        {'id': t['id'], 'index': i, 'done': t['id'] in progress.completed_tasks}
        for i, t in enumerate((current_topic or {}).get('tasks') or [])
    ]

    return render_template(
        'learn.html',
        user=progress,
        current_module=module,
        current_module_num=current_module,
        current_topic=current_topic,
        current_topic_num=topic_num,
        topic_index=topic_index,
        topics_count=len(topics),
        task_in_topic_index=task_ord_in_topic,
        tasks_in_topic_count=tasks_in_topic,
        current_task=current_task,
        current_task_index=current_task_index,
        tasks_total_in_module=len(tasks),
        modules_stats=build_modules_stats(progress),
        total_tasks=TOTAL_TASKS_COUNT,
        completed_tasks=len(progress.completed_tasks),
        course_grade=course_grade_meta(progress),
        task_already_done=task_done,
        safe_task=task_client_payload(current_task),
        topics=topics,
        sidebar_modules=build_sidebar_modules(progress, current_module, current_topic),
        default_code_placeholder=DEFAULT_CODE_EDITOR_PLACEHOLDER,
        project_meta=project_meta,
        project_code=saved_project,
        is_project_stage=is_project_stage,
        project_spec=project_spec,
        project_stage_lock_message=project_stage_lock_message,
        project_stage_is_locked=project_stage_is_locked,
        topic_tasks_nav=topic_tasks_nav,
        course_grade_demo=build_course_grade_demo(),
        course_grade_demo_panel_enabled=_course_grade_demo_panel_enabled(),
    )


def _run_with_timing(code: str, stdin: str, *, echo_stdin: bool = False, timeout_sec: float | None = None):
    t0 = time.perf_counter()
    kwargs: dict = {}
    if timeout_sec is not None:
        kwargs['timeout_sec'] = timeout_sec
    result = run_python(code, stdin=stdin, echo_stdin=echo_stdin, **kwargs)
    duration_ms = round((time.perf_counter() - t0) * 1000.0, 2)
    return result, duration_ms


def _topic_project_stage_task_id(topic: dict) -> int | None:
    for t in topic.get('tasks') or []:
        if t.get('kind') == 'project_stage':
            return t.get('id')
    return None


def _project_version_label(module_id: int, topic_num: int) -> str:
    """Подпись версии проекта для модуля (M1: 0.x, M2: 1.x–2.0)."""
    line = project_line_for_module(module_id)
    row = line.get(topic_num) or {}
    label = row.get('version_label', row.get('version', ''))
    if label:
        return str(label)
    return f'{topic_num / 10:.1f}'


def _project_stage_prerequisite(task_id: int) -> dict | None:
    """Возвращает обязательный предыдущий этап для текущего project_stage."""
    task = TASK_BY_ID.get(task_id) or {}
    if task.get('kind') != 'project_stage':
        return None

    module_id = None
    for mid, mod in LESSONS.items():
        if any((t.get('id') == task_id) for t in (mod.get('tasks') or [])):
            module_id = mid
            break
    if module_id is None:
        return None

    topic = topic_by_task_id(module_id, task_id)
    if not topic:
        return None
    current_num = topic.get('num')
    if not isinstance(current_num, int) or current_num <= 1:
        return None

    prev_num = current_num - 1
    prev_topic = next(
        (t for t in (LESSONS[module_id].get('topics') or []) if t.get('num') == prev_num),
        None,
    )
    if not prev_topic:
        return None
    prev_stage_id = _topic_project_stage_task_id(prev_topic)
    if prev_stage_id is None:
        return None

    prev_ver = _project_version_label(module_id, prev_num)
    cur_ver = _project_version_label(module_id, current_num)
    return {
        'required_task_id': prev_stage_id,
        'required_version': prev_ver,
        'current_version': cur_ver,
    }


def _project_stage_lock_message(progress: UserProgress, task_id: int) -> str | None:
    if not _enforce_project_prerequisite():
        return None
    req = _project_stage_prerequisite(task_id)
    if not req:
        return None
    if req['required_task_id'] in set(progress.completed_tasks):
        return None
    return (
        f'Перед релизом {req["current_version"]} завершите предыдущую версию '
        f'{req["required_version"]}. Откройте project_stage прошлой темы и сдайте его — '
        'после этого этот этап разблокируется автоматически.'
    )


def _cleanup_interactive_sessions() -> None:
    stale: list[InteractiveSession] = []
    now = time.monotonic()
    with INTERACTIVE_LOCK:
        for rid, sess in list(INTERACTIVE_SESSIONS.items()):
            # Важно: не удаляем "просто завершённые" сессии здесь, иначе
            # клиент может не успеть получить финальный done-чанк (теряется
            # последний print/последний шаг input).
            # Удаляем только действительно протухшие/зависшие сессии.
            if sess.is_expired(now):
                INTERACTIVE_SESSIONS.pop(rid, None)
                stale.append(sess)
    for sess in stale:
        try:
            sess.close()
        except Exception:
            pass


@app.route('/interactive/start', methods=['POST'])
@login_required
def interactive_start():
    """Запуск интерактивной сессии c живым poll-стримингом."""
    get_user_progress()
    _cleanup_interactive_sessions()
    data = request.get_json() or {}
    code = data.get('code', '')
    prev = data.get('previous_run_id')
    if prev:
        with INTERACTIVE_LOCK:
            prev_sess = INTERACTIVE_SESSIONS.pop(prev, None)
        if prev_sess:
            prev_sess.close()
    try:
        sess = InteractiveSession.start(code)
    except Exception as exc:
        return jsonify({'success': False, 'message': f'Не удалось запустить: {exc}'}), 500
    with INTERACTIVE_LOCK:
        INTERACTIVE_SESSIONS[sess.run_id] = sess
    phase = sess.poll()
    payload = {'success': True, 'run_id': sess.run_id, **phase}
    if phase.get('status') == 'done':
        payload['stdin_for_check'] = sess.stdin_for_check()
        with INTERACTIVE_LOCK:
            INTERACTIVE_SESSIONS.pop(sess.run_id, None)
        sess.close()
    elif phase.get('status') == 'error':
        with INTERACTIVE_LOCK:
            INTERACTIVE_SESSIONS.pop(sess.run_id, None)
        sess.close()
    return jsonify(payload)


@app.route('/interactive/poll', methods=['POST'])
@login_required
def interactive_poll():
    get_user_progress()
    _cleanup_interactive_sessions()
    data = request.get_json() or {}
    rid = data.get('run_id')
    if not rid:
        return jsonify({'success': False, 'message': 'Нет активного запуска.'}), 400
    with INTERACTIVE_LOCK:
        sess = INTERACTIVE_SESSIONS.get(rid)
    if not sess:
        return jsonify({'success': False, 'message': 'Активный запуск завершён. Нажмите «Выполнить».'}), 400
    phase = sess.poll()
    payload = {'success': True, 'run_id': rid, **phase}
    if phase.get('status') == 'done':
        payload['stdin_for_check'] = sess.stdin_for_check()
        with INTERACTIVE_LOCK:
            INTERACTIVE_SESSIONS.pop(rid, None)
        sess.close()
    return jsonify(payload)


@app.route('/interactive/input', methods=['POST'])
@login_required
def interactive_input():
    get_user_progress()
    _cleanup_interactive_sessions()
    data = request.get_json() or {}
    rid = data.get('run_id')
    if not rid:
        return jsonify({'success': False, 'message': 'Нет активного запуска.'}), 400
    with INTERACTIVE_LOCK:
        sess = INTERACTIVE_SESSIONS.get(rid)
    if not sess:
        return jsonify({'success': False, 'message': 'Запуск завершён. Нажмите «Выполнить» снова.'}), 400
    line = data.get('line', '')
    if line is None:
        line = ''
    line = str(line)
    phase = sess.send_line(line)
    payload = {'success': True, 'run_id': rid, **phase}
    if phase.get('status') == 'done':
        payload['stdin_for_check'] = sess.stdin_for_check()
        with INTERACTIVE_LOCK:
            INTERACTIVE_SESSIONS.pop(rid, None)
        sess.close()
    elif phase.get('status') == 'error':
        with INTERACTIVE_LOCK:
            INTERACTIVE_SESSIONS.pop(rid, None)
        sess.close()
    return jsonify(payload)


@app.route('/interactive/abort', methods=['POST'])
@login_required
def interactive_abort():
    get_user_progress()
    _cleanup_interactive_sessions()
    data = request.get_json(silent=True) or {}
    rid = data.get('run_id')
    if rid:
        with INTERACTIVE_LOCK:
            sess = INTERACTIVE_SESSIONS.pop(rid, None)
        if sess:
            sess.close()
    else:
        with INTERACTIVE_LOCK:
            run_ids = list(INTERACTIVE_SESSIONS.keys())
            sessions = [INTERACTIVE_SESSIONS.pop(k) for k in run_ids]
        for sess in sessions:
            sess.close()
    return jsonify({'success': True})


@app.route('/run_code', methods=['POST'])
def run_code():
    """Запуск кода без проверки задания и без начисления XP."""
    data = request.get_json() or {}
    code = data.get('code', '')
    stdin = data.get('stdin') or ''
    result, duration_ms = _run_with_timing(code, stdin)
    payload = {'success': True, **result.to_api_dict(duration_ms=duration_ms)}
    return jsonify(payload)


@app.route('/check_code', methods=['POST'])
@login_required
def check_code():
    progress = get_user_progress()
    data = request.get_json() or {}
    code = data.get('code', '')
    stdin = data.get('stdin') or ''
    task_id = data.get('task_id')

    task = TASK_BY_ID.get(task_id)
    if not task:
        return jsonify({'error': 'Задание не найдено'}), 400

    if task.get('type', 'code') != 'code':
        return jsonify({'error': 'Для этого задания используйте кнопку «Проверить» под блоком задания, а не проверку кода.'}), 400

    lock_message = _project_stage_lock_message(progress, task_id)
    if lock_message:
        return jsonify({
            'success': False,
            'error': lock_message,
            'expected': 'Сначала завершите предыдущую версию проекта.',
        }), 400

    module_lock = task_access_lock_message(progress, task_id, enforce=_enforce_m1_gate())
    if module_lock:
        return jsonify({'success': False, 'error': module_lock}), 403

    expected = task['expected']

    if task_id in progress.completed_tasks:
        return jsonify({
            'success': True,
            'already_completed': True,
            'message': 'Задание уже выполнено!',
            'output': '',
        })

    project_runs = task.get('project_runs') or []
    use_stepik_runs = task.get('kind') == 'project_stage' and bool(project_runs)
    use_m1_auto_stdin = (
        task.get('kind') == 'project_stage'
        and not use_stepik_runs
        and bool(task_auto_stdin_mode(task))
    )

    if use_stepik_runs:
        ok_tests, test_failures, output, stdin_for_check = validate_project_stage_runs(code, task)
        is_correct = ok_tests
        error_short = None
        error_detail = ''
        if not is_correct and test_failures:
            error_short = test_failures[0]
            error_detail = '\n'.join(test_failures)

        display_stdin = stdin_for_check or ''
        if not display_stdin:
            for scenario in project_runs:
                opts = scenario.get('stdin_options') or [scenario.get('stdin') or '']
                if opts and opts[0]:
                    display_stdin = opts[0]
                    break
        run_fields: dict = {
            'stdout': output,
            'stderr': '',
            'exit_code': 0 if is_correct else 1,
            'timed_out': False,
            'duration_ms': 0,
            'stdin_for_check': display_stdin,
        }
        if display_stdin:
            display_result, duration_ms = _run_with_timing(
                code,
                display_stdin,
                echo_stdin=True,
                timeout_sec=PROJECT_STAGE_TIMEOUT_SEC,
            )
            run_fields['duration_ms'] = duration_ms
            if not display_result.timed_out:
                run_fields['stdout'] = display_result.stdout or output
                run_fields['stderr'] = display_result.stderr or ''
                run_fields['exit_code'] = display_result.exit_code
                run_fields['timed_out'] = display_result.timed_out
    elif use_m1_auto_stdin:
        ok_tests, test_failures, output, stdin_for_check = validate_m1_project_stage(code, task, stdin)
        is_correct = ok_tests
        error_short = None
        error_detail = ''
        if not is_correct and test_failures:
            error_short = test_failures[0]
            error_detail = '\n'.join(test_failures)

        display_stdin = stdin_for_check or stdin
        run_fields: dict = {
            'stdout': output,
            'stderr': '',
            'exit_code': 0 if is_correct else 1,
            'timed_out': False,
            'duration_ms': 0,
            'stdin_for_check': display_stdin,
        }
        if display_stdin:
            display_result, duration_ms = _run_with_timing(
                code,
                display_stdin,
                echo_stdin=True,
                timeout_sec=PROJECT_STAGE_TIMEOUT_SEC,
            )
            run_fields['duration_ms'] = duration_ms
            if not display_result.timed_out:
                run_fields['stdout'] = display_result.stdout or output
                run_fields['stderr'] = display_result.stderr or ''
                run_fields['exit_code'] = display_result.exit_code
                run_fields['timed_out'] = display_result.timed_out
    else:
        result, duration_ms = _run_with_timing(code, stdin)
        output, error_short, error_detail = result.to_legacy_tuple()
        run_fields = {**result.to_api_dict(duration_ms=duration_ms)}
        if stdin.strip():
            display_result, _display_duration_ms = _run_with_timing(code, stdin, echo_stdin=True)
            if not display_result.timed_out and display_result.exit_code == result.exit_code:
                run_fields['stdout'] = display_result.stdout

        is_correct = False
        test_failures: list[str] = []
        if error_short is None:
            if task.get('kind') == 'project_stage':
                ok_tests, test_failures = validate_project_tests(code, output, task.get('project_tests'))
                is_correct = ok_tests
            else:
                is_correct = stdout_matches(output, expected)

    if is_correct:
        progress.complete_task(task_id, task['xp'])
        if task.get('kind') == 'project_stage':
            progress.project_code[progress.current_module] = code
            progress.save()
        current_module = progress.current_module
        module_completed = progress.is_module_completed(current_module)
        keys = sorted(LESSONS.keys())
        next_mid = None
        if module_completed and current_module in keys:
            i = keys.index(current_module)
            if i + 1 < len(keys):
                next_mid = keys[i + 1]
        return jsonify({
            'success': True,
            'output': output,
            'module_completed': module_completed,
            'next_module': next_mid,
            'project_meta': project_meta_for_task(progress, progress.current_module, task_id),
            'project_code_saved': task.get('kind') == 'project_stage',
            **run_fields,
        })

    expected_for_client = expected
    if task.get('kind') == 'project_stage':
        spec = task.get('project_spec') or {}
        expected_for_client = spec.get(
            'expected_result',
            'Проверьте требования проектного этапа выше.',
        )

    payload = {
        'success': False,
        'output': output if output else '(пусто)',
        'expected': expected_for_client,
        'error': error_short,
        'error_detail': error_detail,
        **run_fields,
    }
    if test_failures:
        payload['test_failures'] = test_failures
        payload['error'] = test_failures[0]
    return jsonify(payload)


@app.route('/check_task', methods=['POST'])
@login_required
def check_task():
    progress = get_user_progress()
    data = request.get_json() or {}
    task_id = data.get('task_id')
    answer = data.get('answer')
    task = TASK_BY_ID.get(task_id)
    if not task:
        return jsonify({'error': 'Задание не найдено'}), 400
    if task.get('type', 'code') == 'code':
        return jsonify({'error': 'Для этого задания используйте проверку кода.'}), 400

    lock_message = _project_stage_lock_message(progress, task_id)
    if lock_message:
        return jsonify({
            'success': False,
            'message': lock_message,
        }), 400

    module_lock = task_access_lock_message(progress, task_id, enforce=_enforce_m1_gate())
    if module_lock:
        return jsonify({'success': False, 'message': module_lock}), 403

    if task_id in progress.completed_tasks:
        return jsonify({
            'success': True,
            'already_completed': True,
            'message': 'Задание уже выполнено!',
        })

    if validate_interactive_answer(task, answer):
        progress.complete_task(task_id, task['xp'])
        current_module = progress.current_module
        module_completed = progress.is_module_completed(current_module)
        keys = sorted(LESSONS.keys())
        next_mid = None
        if module_completed and current_module in keys:
            i = keys.index(current_module)
            if i + 1 < len(keys):
                next_mid = keys[i + 1]
        payload = {
            'success': True,
            'module_completed': module_completed,
            'next_module': next_mid,
        }
        if task.get('kind') == 'project_stage':
            payload['project_meta'] = project_meta_for_task(
                progress, progress.current_module, task_id
            )
        return jsonify(payload)

    return jsonify({
        'success': False,
        'message': 'Пока не сходится — проверьте формулировку или подсказку и попробуйте снова.',
    })


def _topic_id_at(module_id: int, task_index: int) -> str | None:
    """topic_id из плоского списка заданий модуля (совпадает с темой в sidebar)."""
    try:
        mid = int(module_id)
        idx = int(task_index)
    except (TypeError, ValueError):
        return None
    tasks = LESSONS.get(mid, {}).get('tasks') or []
    if idx < 0 or idx >= len(tasks):
        return None
    return tasks[idx].get('topic_id')


@app.route('/goto_task', methods=['POST'])
@login_required
def goto_task_route():
    """Переход к заданию внутри текущей темы без смены темы."""
    progress = get_user_progress()
    data = request.get_json() or {}
    task_id = data.get('task_id')
    if task_id is None:
        return jsonify({'success': False, 'message': 'Не указано задание'}), 400

    try:
        task_id = int(task_id)
    except (TypeError, ValueError):
        return jsonify({'success': False, 'message': 'Некорректный id задания'}), 400

    module_num = progress.current_module
    if module_num not in LESSONS:
        return jsonify({'success': False}), 400

    mod = LESSONS[module_num]
    if mod.get('stub') or not mod.get('tasks'):
        return jsonify({'success': False}), 400

    old_topic_id = _topic_id_at(module_num, progress.current_task_index)
    target_topic = topic_by_task_id(module_num, task_id)
    if not target_topic or not old_topic_id or target_topic.get('id') != old_topic_id:
        return jsonify({'success': False, 'message': 'Можно перейти только между заданиями текущей темы'}), 400

    if not _navigate_to_task_by_id(progress, task_id):
        return jsonify({'success': False, 'message': 'Задание не найдено'}), 404

    if progress.current_module != module_num:
        return jsonify({'success': False, 'message': 'Задание в другом модуле'}), 400

    return jsonify({
        'success': True,
        'module': progress.current_module,
        'task_index': progress.current_task_index,
        'topic_changed': False,
        'current_topic_id': old_topic_id,
        'next_topic_id': old_topic_id,
    })


@app.route('/next_task', methods=['POST'])
@login_required
def next_task():
    progress = get_user_progress()
    module_num = progress.current_module
    task_index = progress.current_task_index

    if module_num not in LESSONS:
        return jsonify({'success': False}), 400

    mod = LESSONS[module_num]
    tasks = mod['tasks']

    if mod.get('stub') or not tasks:
        return jsonify({'success': False, 'message': 'Нет шагов для перехода'}), 400

    old_topic_id = _topic_id_at(module_num, task_index)

    if task_index + 1 < len(tasks):
        progress.current_module = module_num
        progress.current_task_index = task_index + 1
    else:
        nxt = None
        for mid in sorted(LESSONS.keys()):
            if mid <= module_num:
                continue
            nxt = mid
            break
        if nxt is not None:
            lock = module_access_lock_message(progress, nxt, enforce=_enforce_m1_gate())
            if lock:
                return jsonify({'success': False, 'message': lock}), 403
            progress.current_module = nxt
            progress.current_task_index = 0
        else:
            return jsonify({'completed': True})

    progress.save()

    new_topic_id = _topic_id_at(progress.current_module, progress.current_task_index)
    topic_changed = bool(
        old_topic_id and new_topic_id and old_topic_id != new_topic_id
    )

    return jsonify({
        'success': True,
        'module': progress.current_module,
        'task_index': progress.current_task_index,
        'topic_changed': topic_changed,
        'current_topic_id': old_topic_id,
        'next_topic_id': new_topic_id,
    })


@app.route('/previous_task', methods=['POST'])
@login_required
def previous_task_route():
    progress = get_user_progress()
    module_num = progress.current_module
    task_index = progress.current_task_index

    if module_num not in LESSONS:
        return jsonify({'success': False}), 400

    mod = LESSONS[module_num]

    old_topic_id = _topic_id_at(module_num, task_index) if mod.get('tasks') else None

    if mod.get('stub') or not mod['tasks']:
        prev_with_tasks = None
        for mid in sorted(LESSONS.keys(), reverse=True):
            if mid >= module_num:
                continue
            m = LESSONS[mid]
            if m['tasks'] and not m.get('stub'):
                prev_with_tasks = mid
                break
        if prev_with_tasks:
            pt = LESSONS[prev_with_tasks]['tasks']
            progress.current_module = prev_with_tasks
            progress.current_task_index = len(pt) - 1
        progress.save()
        new_topic_id = _topic_id_at(progress.current_module, progress.current_task_index)
        topic_changed = bool(
            old_topic_id and new_topic_id and old_topic_id != new_topic_id
        )
        return jsonify({
            'success': True,
            'module': progress.current_module,
            'task_index': progress.current_task_index,
            'topic_changed': topic_changed,
            'current_topic_id': old_topic_id,
            'next_topic_id': new_topic_id,
        })

    if task_index > 0:
        progress.current_module = module_num
        progress.current_task_index = task_index - 1
    else:
        prev_with_tasks = None
        for mid in sorted(LESSONS.keys(), reverse=True):
            if mid >= module_num:
                continue
            m = LESSONS[mid]
            if m['tasks'] and not m.get('stub'):
                prev_with_tasks = mid
                break
        if prev_with_tasks:
            pt = LESSONS[prev_with_tasks]['tasks']
            progress.current_module = prev_with_tasks
            progress.current_task_index = len(pt) - 1
        else:
            return jsonify({'success': False}), 400

    new_topic_id = _topic_id_at(progress.current_module, progress.current_task_index)
    topic_changed = bool(
        old_topic_id and new_topic_id and old_topic_id != new_topic_id
    )

    progress.save()

    return jsonify({
        'success': True,
        'module': progress.current_module,
        'task_index': progress.current_task_index,
        'topic_changed': topic_changed,
        'current_topic_id': old_topic_id,
        'next_topic_id': new_topic_id,
    })


@app.route('/reset_progress', methods=['POST'])
@login_required
def reset_progress():
    progress = get_user_progress()
    progress.reset()
    session.pop('course_started', None)
    return jsonify({'success': True})


@app.route('/load_module/<int:module_id>')
@login_required
def load_module(module_id):
    progress = get_user_progress()
    if module_id in LESSONS and LESSONS[module_id].get('stub'):
        return jsonify({'error': 'Модуль в разработке'}), 403
    lock = module_access_lock_message(progress, module_id, enforce=_enforce_m1_gate())
    if lock:
        flash(lock, 'error')
        return redirect(url_for('learn'))
    if module_id in LESSONS:
        progress.current_module = module_id
        progress.current_task_index = 0
        progress.save()
    return redirect(url_for('learn'))


@app.route('/api/session')
@login_required
def api_session():
    progress = get_user_progress()
    task_id = request.args.get('task_id', type=int)
    if task_id is None:
        tasks = LESSONS.get(progress.current_module, {}).get('tasks') or []
        idx = progress.current_task_index
        if 0 <= idx < len(tasks):
            task_id = tasks[idx].get('id')
    task = TASK_BY_ID.get(task_id) if task_id is not None else None
    topic = topic_by_task_id(progress.current_module, task_id) if task_id is not None else None
    is_project_stage = bool(task and task.get('kind') == 'project_stage')
    is_project_release_task = bool(task and task.get('kind') in ('project_stage', 'project_step'))
    is_locked = bool(_project_stage_lock_message(progress, task_id)) if task_id is not None else False
    focus_topic_num = topic.get('num') if (topic and is_project_release_task and not is_locked) else None
    module_id = progress.current_module
    module_done, module_total = _module_task_counts(progress, module_id)
    payload = {
        'success': True,
        'completed_tasks': len(progress.completed_tasks),
        'total_tasks': TOTAL_TASKS_COUNT,
        'module_completed_tasks': module_done,
        'module_total_tasks': module_total,
        'course_grade': course_grade_meta(progress),
        'module_progress': progress.get_module_progress(module_id),
        'current_module': module_id,
        'project_meta': build_project_meta(progress, module_id, topic_num=focus_topic_num),
    }
    if task_id is not None:
        payload['task_completed'] = task_id in progress.completed_tasks
    return jsonify(payload)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', '').lower() in ('1', 'true', 'yes')
    app.run(host='0.0.0.0', port=port, debug=debug)


def init_database() -> None:
    instance_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
    os.makedirs(instance_dir, exist_ok=True)
    with app.app_context():
        db.create_all()
        from bootstrap_service import ensure_admin_user

        ensure_admin_user()


init_database()