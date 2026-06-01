import os
import secrets
import threading
import time

from flask import Flask, jsonify, redirect, render_template, request, send_from_directory, session, url_for

from code_runner import run_python
from code_runner.interactive_session import InteractiveSession
from course_data.constants import DEFAULT_CODE_EDITOR_PLACEHOLDER
from course_data.project_state import build_project_meta, project_meta_for_task
from course_data import (
    ACHIEVEMENTS,
    LESSONS,
    TASK_BY_ID,
    TOTAL_TASKS_COUNT,
    XP_PER_LEVEL,
    task_client_payload,
    topic_by_task_id,
    validate_interactive_answer,
    validate_project_tests,
    stdout_matches,
)

app = Flask(__name__, static_folder='CSS', template_folder='HTML')
app.secret_key = os.environ.get('FLASK_SECRET_KEY') or secrets.token_hex(32)


@app.route('/health')
def health():
    """Проверка для Railway и других PaaS (без сессии и без запуска кода)."""
    return 'ok', 200

user_progress = {}

INTERACTIVE_SESSIONS: dict[str, InteractiveSession] = {}
INTERACTIVE_LOCK = threading.Lock()


class UserProgress:
    def __init__(self):
        self.completed_tasks = []
        self.total_xp = 0
        self.current_module = 1
        self.current_task_index = 0
        self.project_code: dict[int, str] = {}

    def complete_task(self, task_id, xp):
        if task_id not in self.completed_tasks:
            self.completed_tasks.append(task_id)
            self.total_xp += xp
            return True
        return False

    def get_module_progress(self, module_id):
        if module_id not in LESSONS:
            return 0
        mod = LESSONS[module_id]
        tasks = mod['tasks']
        if mod.get('stub') and not tasks:
            return 0
        if not tasks:
            return 0
        completed = sum(1 for task in tasks if task['id'] in self.completed_tasks)
        return int((completed / len(tasks)) * 100)

    def is_module_completed(self, module_id):
        if module_id not in LESSONS:
            return False
        mod = LESSONS[module_id]
        if mod.get('stub') and not mod['tasks']:
            return True
        tasks = mod['tasks']
        if not tasks:
            return False
        return self.get_module_progress(module_id) == 100

    def get_next_module(self):
        for i in sorted(LESSONS.keys()):
            mod = LESSONS[i]
            if mod.get('stub') and not mod['tasks']:
                continue
            if not self.is_module_completed(i):
                return i
        return None


def get_user_progress():
    user_id = session.get('user_id')
    if not user_id:
        user_id = secrets.token_hex(8)
        session['user_id'] = user_id
    if user_id not in user_progress:
        user_progress[user_id] = UserProgress()
    return user_progress[user_id]


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
                progress.current_module = mid
                progress.current_task_index = i
                return True
    return False


def build_modules_stats(progress):
    return [
        {
            'id': i,
            'title': LESSONS[i]['title'],
            'icon': LESSONS[i]['icon'],
            'progress': progress.get_module_progress(i),
            'is_locked': bool(LESSONS[i].get('stub')),
            'is_stub': bool(LESSONS[i].get('stub')),
        }
        for i in sorted(LESSONS.keys())
        if i in LESSONS
    ]


def level_meta(total_xp):
    level = total_xp // XP_PER_LEVEL + 1
    in_level = total_xp % XP_PER_LEVEL
    pct = int(in_level * 100 / XP_PER_LEVEL) if XP_PER_LEVEL else 0
    return {
        'level': level,
        'xp_in_level': in_level,
        'xp_to_next': XP_PER_LEVEL,
        'level_pct': pct,
        'total_xp': total_xp,
    }


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
            'text': 'Откройте модуль в разделе заданий.',
            'task_id': None,
        }
    if idx >= len(tasks):
        return None
    t = tasks[idx]
    return {
        'module_title': mod['title'],
        'module_icon': mod['icon'],
        'text': t['text'],
        'task_id': t['id'],
    }


def achievement_list(completed_n, total_n):
    frac = completed_n / total_n if total_n else 0.0
    out = []
    for a in ACHIEVEMENTS:
        unlocked = False
        if 'min_completed' in a:
            unlocked = completed_n >= a['min_completed']
        elif 'min_fraction' in a:
            unlocked = frac >= a['min_fraction'] - 1e-9
        out.append({
            'id': a['id'],
            'icon': a['icon'],
            'title': a['title'],
            'description': a['description'],
            'unlocked': unlocked,
        })
    return out


@app.route('/')
def home():
    progress = get_user_progress()
    completed_tasks = len(progress.completed_tasks)
    has_progress = completed_tasks > 0 or progress.total_xp > 0
    lm = level_meta(progress.total_xp)
    overall_pct = int(completed_tasks * 100 / TOTAL_TASKS_COUNT) if TOTAL_TASKS_COUNT else 0
    return render_template(
        'index.html',
        user=progress,
        modules_stats=build_modules_stats(progress),
        total_tasks=TOTAL_TASKS_COUNT,
        completed_tasks=completed_tasks,
        has_progress=has_progress,
        level_info=lm,
        next_task=next_task_preview(progress),
        achievements=achievement_list(completed_tasks, TOTAL_TASKS_COUNT),
        overall_progress_pct=overall_pct,
    )


@app.route('/theory_schemes/<path:filename>')
def theory_schemes_file(filename: str):
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'theory_schemes')
    return send_from_directory(base, filename)


@app.route('/learn')
def learn():
    progress = get_user_progress()
    task_id_arg = request.args.get('task_id', type=int)
    if task_id_arg is not None and _navigate_to_task_by_id(progress, task_id_arg):
        return redirect(url_for('learn'))

    current_module = progress.current_module
    current_task_index = progress.current_task_index

    if current_module in LESSONS:
        tasks = LESSONS[current_module]['tasks']
        mod_obj = LESSONS[current_module]
        if mod_obj.get('stub') or not tasks:
            lm = level_meta(progress.total_xp)
            return render_template(
                'learn_stub.html',
                user=progress,
                current_module=mod_obj,
                current_module_num=current_module,
                modules_stats=build_modules_stats(progress),
                total_tasks=TOTAL_TASKS_COUNT,
                completed_tasks=len(progress.completed_tasks),
                level_info=lm,
                project_meta=build_project_meta(progress, current_module),
            )
        if current_task_index >= len(tasks):
            current_task_index = max(0, len(tasks) - 1)
            progress.current_task_index = current_task_index

    if current_module not in LESSONS:
        current_module = 1
        progress.current_module = 1
        current_task_index = 0

    module = LESSONS[current_module]
    tasks = module['tasks']
    if module.get('stub') or not tasks:
        lm = level_meta(progress.total_xp)
        return render_template(
            'learn_stub.html',
            user=progress,
            current_module=module,
            current_module_num=current_module,
            modules_stats=build_modules_stats(progress),
            total_tasks=TOTAL_TASKS_COUNT,
            completed_tasks=len(progress.completed_tasks),
            level_info=lm,
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

    task_done = current_task['id'] in progress.completed_tasks
    lm = level_meta(progress.total_xp)
    topic_num = current_topic.get('num') if current_topic else None
    project_meta = build_project_meta(progress, current_module, topic_num=topic_num)
    saved_project = progress.project_code.get(current_module, '')
    is_project_stage = current_task.get('kind') == 'project_stage'
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
        task_already_done=task_done,
        level_info=lm,
        safe_task=task_client_payload(current_task),
        topics=topics,
        default_code_placeholder=DEFAULT_CODE_EDITOR_PLACEHOLDER,
        project_meta=project_meta,
        project_code=saved_project,
        is_project_stage=is_project_stage,
        project_spec=project_spec,
        topic_tasks_nav=topic_tasks_nav,
    )


def _run_with_timing(code: str, stdin: str):
    t0 = time.perf_counter()
    result = run_python(code, stdin=stdin)
    duration_ms = round((time.perf_counter() - t0) * 1000.0, 2)
    return result, duration_ms


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

    expected = task['expected']

    if task_id in progress.completed_tasks:
        return jsonify({
            'success': True,
            'already_completed': True,
            'message': 'Задание уже выполнено!',
            'output': '',
            'xp_gained': 0,
            'total_xp': progress.total_xp,
        })

    result, duration_ms = _run_with_timing(code, stdin)
    output, error_short, error_detail = result.to_legacy_tuple()
    run_fields = {**result.to_api_dict(duration_ms=duration_ms)}

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
            'xp_gained': task['xp'],
            'total_xp': progress.total_xp,
            'module_completed': module_completed,
            'next_module': next_mid,
            'level': level_meta(progress.total_xp),
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

    if task_id in progress.completed_tasks:
        return jsonify({
            'success': True,
            'already_completed': True,
            'message': 'Задание уже выполнено!',
            'xp_gained': 0,
            'total_xp': progress.total_xp,
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
            'xp_gained': task['xp'],
            'total_xp': progress.total_xp,
            'module_completed': module_completed,
            'next_module': next_mid,
            'level': level_meta(progress.total_xp),
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
            progress.current_module = nxt
            progress.current_task_index = 0
        else:
            return jsonify({'completed': True})

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

    return jsonify({
        'success': True,
        'module': progress.current_module,
        'task_index': progress.current_task_index,
        'topic_changed': topic_changed,
        'current_topic_id': old_topic_id,
        'next_topic_id': new_topic_id,
    })


@app.route('/reset_progress', methods=['POST'])
def reset_progress():
    uid = session.get('user_id')
    if uid:
        user_progress[uid] = UserProgress()
    return jsonify({'success': True})


@app.route('/load_module/<int:module_id>')
def load_module(module_id):
    progress = get_user_progress()
    if module_id in LESSONS and LESSONS[module_id].get('stub'):
        return jsonify({'error': 'Модуль в разработке'}), 403
    if module_id in LESSONS:
        progress.current_module = module_id
        progress.current_task_index = 0
    return redirect(url_for('learn'))


@app.route('/api/session')
def api_session():
    progress = get_user_progress()
    task_id = request.args.get('task_id', type=int)
    payload = {
        'success': True,
        'total_xp': progress.total_xp,
        'completed_tasks': len(progress.completed_tasks),
        'total_tasks': TOTAL_TASKS_COUNT,
        'module_progress': progress.get_module_progress(progress.current_module),
        'current_module': progress.current_module,
        'level': level_meta(progress.total_xp),
        'project_meta': project_meta_for_task(
            progress, progress.current_module, task_id
        ),
    }
    if task_id is not None:
        payload['task_completed'] = task_id in progress.completed_tasks
    return jsonify(payload)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', '').lower() in ('1', 'true', 'yes')
    app.run(host='0.0.0.0', port=port, debug=debug)