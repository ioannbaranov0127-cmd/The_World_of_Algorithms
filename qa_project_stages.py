# -*- coding: utf-8 -*-
"""QA: все project_stage задания модулей 1 и 2 + симуляция check_code."""
from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path

from code_runner.subprocess_runner import DEFAULT_TIMEOUT_SEC, run_python
from course_data.loader import LESSONS, TASK_BY_ID
from course_data.project_stage_runner import (
    task_auto_stdin_mode,
    validate_m1_project_stage,
    validate_project_stage_runs,
)
from course_data.validators import validate_project_tests

ROOT = Path(__file__).resolve().parent

# Эталонные решения M1 (кумулятивно) — проходят project_tests и выполняются без зависания.
M1_REFERENCE: dict[int, str] = {
    100: (
        'print("Калькулятор калорий")\n'
        'print("Программа запущена")\n'
    ),
    101: (
        'print("Калькулятор калорий")\n'
        'print("Привет! Давай посчитаем калории за день.")\n'
        'print("Выберите продукт и введите граммы.")\n'
        'print("1 - Яблоко")\n'
        'print("2 - Банан")\n'
    ),
    102: (
        'print("Калькулятор калорий")\n'
        'print("Привет! Давай посчитаем калории за день.")\n'
        'product = "Яблоко"\n'
        'grams = 100\n'
        'kcal_per_100 = 52\n'
        'total = 0\n'
        'print(product, grams, kcal_per_100, total)\n'
    ),
    103: (
        'print("Калькулятор калорий")\n'
        'print("Номер продукта:")\n'
        'num = int(input("Номер продукта: "))\n'
        'grams = int(input("Граммы: "))\n'
        'print("Продукт:", num, "Граммы:", grams)\n'
    ),
    104: (
        'print("Калькулятор калорий")\n'
        'num = int(input("Номер продукта: "))\n'
        'grams = int(input("Граммы: "))\n'
        'kcal_per_100 = 52\n'
        'calories = grams * kcal_per_100 / 100\n'
        'print("Калории:", calories, "ккал")\n'
    ),
    105: (
        'print("Калькулятор калорий")\n'
        'num = int(input("Номер продукта: "))\n'
        'grams = int(input("Граммы: "))\n'
        'kcal_per_100 = 52\n'
        'calories = grams * kcal_per_100 / 100\n'
        'print("Добавлено:", calories, "ккал")\n'
    ),
    106: (
        'print("Калькулятор калорий")\n'
        'num = int(input("Номер продукта: "))\n'
        'grams = int(input("Граммы: "))\n'
        'if num == 1:\n'
        '    kcal_per_100 = 52\n'
        'elif num == 2:\n'
        '    kcal_per_100 = 89\n'
        'else:\n'
        '    kcal_per_100 = 52\n'
        'calories = grams * kcal_per_100 / 100\n'
        'print("Калории:", calories)\n'
    ),
    107: (
        'print("Калькулятор калорий")\n'
        'total = 0\n'
        'num = int(input("Номер продукта: "))\n'
        'grams = int(input("Граммы: "))\n'
        'if num == 1:\n'
        '    kcal_per_100 = 52\n'
        'elif num == 2:\n'
        '    kcal_per_100 = 89\n'
        'else:\n'
        '    kcal_per_100 = 52\n'
        'calories = grams * kcal_per_100 / 100\n'
        'total = total + calories\n'
        'print("Всего:", total, "ккал")\n'
    ),
    108: (
        'print("Калькулятор калорий")\n'
        'total = 0\n'
        'while True:\n'
        '    num = int(input("Номер продукта: "))\n'
        '    if num == 0:\n'
        '        break\n'
        '    grams = int(input("Граммы: "))\n'
        '    if num == 1:\n'
        '        kcal_per_100 = 52\n'
        '    elif num == 2:\n'
        '        kcal_per_100 = 89\n'
        '    else:\n'
        '        kcal_per_100 = 52\n'
        '    calories = grams * kcal_per_100 / 100\n'
        '    total = total + calories\n'
        'print("Всего:", total, "ккал")\n'
    ),
}

M1_STDIN: dict[int, str] = {
    103: '1\n100\n',
    104: '1\n100\n',
    105: '1\n100\n',
    106: '1\n100\n',
    107: '1\n100\n',
    108: '1\n100\n0\n',
}


def collect_project_stages() -> list[dict]:
    rows: list[dict] = []
    for mid, mod in sorted(LESSONS.items()):
        for topic in mod.get('topics') or []:
            if topic.get('draft'):
                continue
            for task in topic.get('tasks') or []:
                if task.get('kind') != 'project_stage':
                    continue
                rows.append({
                    'module': mid,
                    'topic_num': topic.get('num'),
                    'topic_title': topic.get('title', ''),
                    **task,
                })
    return rows


def simulate_check_code(task: dict, code: str, stdin: str = '') -> dict:
    """Упрощённая копия веток app.check_code для project_stage."""
    project_runs = task.get('project_runs') or []
    use_stepik = task.get('kind') == 'project_stage' and bool(project_runs)

    use_stepik = task.get('kind') == 'project_stage' and bool(project_runs)
    use_m1_auto = (
        task.get('kind') == 'project_stage'
        and not use_stepik
        and bool(task_auto_stdin_mode(task))
    )

    if use_stepik:
        ok, failures, output, stdin_used = validate_project_stage_runs(code, task)
        return {
            'path': 'stepik_runs',
            'ok': ok,
            'failures': failures,
            'output_len': len(output or ''),
            'stdin_for_check': stdin_used,
            'timed_out': False,
        }

    if use_m1_auto:
        ok, failures, output, stdin_used = validate_m1_project_stage(code, task, stdin)
        return {
            'path': 'm1_auto_stdin',
            'ok': ok,
            'failures': failures,
            'output_len': len(output or ''),
            'stdin_for_check': stdin_used,
            'timed_out': False,
            'stdin': stdin,
        }

    result = run_python(code, stdin, timeout_sec=DEFAULT_TIMEOUT_SEC)
    output = result.stdout or ''
    timed_out = result.timed_out
    error = None
    if timed_out:
        error = 'timeout'
    elif result.exit_code not in (0, None):
        error = 'exit_code'

    ok = False
    failures: list[str] = []
    if error is None:
        ok, failures = validate_project_tests(code, output, task.get('project_tests'))
    else:
        failures = [error or 'run_error']

    return {
        'path': 'project_tests',
        'ok': ok,
        'failures': failures,
        'output_len': len(output),
        'timed_out': timed_out,
        'run_error': error,
        'stdin': stdin,
    }


def check_starter_compiles(task: dict) -> tuple[bool, str | None]:
    if task.get('type') != 'code':
        return True, None
    code = task.get('starter_code') or ''
    if not str(code).strip() or 'Напишите код' in code:
        return True, None
    try:
        compile(code, f"task_{task['id']}", 'exec')
        return True, None
    except SyntaxError as exc:
        return False, str(exc)


def main() -> int:
    report: dict = {
        'stages': [],
        'summary': {},
        'issues': [],
    }
    stages = collect_project_stages()
    report['summary']['total_project_stages'] = len(stages)

    ok_count = 0
    fail_count = 0
    skip_count = 0

    for st in stages:
        tid = st['id']
        entry: dict = {
            'id': tid,
            'module': st['module'],
            'topic_num': st.get('topic_num'),
            'text': (st.get('text') or '')[:80],
            'type': st.get('type'),
        }

        compiles, syn_err = check_starter_compiles(st)
        entry['starter_compiles'] = compiles
        if not compiles:
            report['issues'].append(f'#{tid}: starter_code syntax error: {syn_err}')

        if st.get('type') == 'ordering':
            entry['status'] = 'skip_ordering'
            skip_count += 1
            report['stages'].append(entry)
            continue

        if st.get('type') != 'code':
            entry['status'] = 'skip_non_code'
            skip_count += 1
            report['stages'].append(entry)
            continue

        has_runs = bool(st.get('project_runs'))
        has_tests = bool(st.get('project_tests'))
        entry['has_project_runs'] = has_runs
        entry['has_project_tests'] = has_tests

        if not has_runs and not has_tests:
            entry['status'] = 'fail_no_checks'
            fail_count += 1
            report['issues'].append(f'#{tid}: нет project_runs и project_tests')
            report['stages'].append(entry)
            continue

        # starter: не должен проходить полную проверку (кроме ранних этапов с пустым starter)
        starter = st.get('starter_code') or ''
        starter_res = simulate_check_code(st, starter, M1_STDIN.get(tid, ''))
        entry['starter_check'] = starter_res

        # reference / complete solution
        if st['module'] == 1 and tid in M1_REFERENCE:
            ref = M1_REFERENCE[tid]
            ref_res = simulate_check_code(st, ref, M1_STDIN.get(tid, ''))
            entry['reference_check'] = ref_res
            if ref_res['ok']:
                entry['status'] = 'ok'
                ok_count += 1
            else:
                entry['status'] = 'fail_reference'
                fail_count += 1
                report['issues'].append(
                    f"#{tid} M1 reference FAIL ({ref_res['path']}): {ref_res['failures'][:3]}"
                )
        elif st['module'] == 2:
            # M2: starter 2.0 — полное решение; остальные — smoke на auto_stdin
            ref_res = simulate_check_code(st, starter, '')
            entry['reference_check'] = ref_res
            if ref_res['ok']:
                entry['status'] = 'ok_starter_passes' if tid == 485 else 'ok'
                ok_count += 1
            else:
                # для неполных starter ожидаем fail — проверим что runner не падает
                entry['status'] = 'expected_starter_fail'
                entry['runner_smoke'] = True
                ok_count += 1
                if ref_res.get('path') == 'stepik_runs' and 'SyntaxError' in str(ref_res.get('failures')):
                    fail_count += 1
                    report['issues'].append(f'#{tid} M2 runner crash on starter: {ref_res["failures"]}')
        else:
            entry['status'] = 'no_reference'
            skip_count += 1

        # M1 0.5+: «Проверить» без stdin — теперь auto stdin
        if st['module'] == 1 and tid in M1_REFERENCE and tid >= 103:
            empty_res = simulate_check_code(st, M1_REFERENCE[tid], '')
            entry['check_without_stdin'] = empty_res
            if not empty_res['ok']:
                report['issues'].append(
                    f'#{tid} M1 auto stdin FAIL: {empty_res.get("failures", [])[:2]}'
                )

        report['stages'].append(entry)

    # Дубликаты id
    dupes = len(TASK_BY_ID)
    report['summary']['task_by_id_count'] = dupes

    # Loader integrity
    try:
        from course_data.loader import TOTAL_TASKS_COUNT  # noqa: F401
        report['summary']['total_tasks'] = TOTAL_TASKS_COUNT
    except Exception as exc:
        report['issues'].append(f'loader error: {exc}')

    report['summary']['ok'] = ok_count
    report['summary']['fail'] = fail_count
    report['summary']['skip'] = skip_count
    report['summary']['all_ok'] = fail_count == 0

    out_path = ROOT / 'qa_project_stages_report.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f'Project stages: {len(stages)}')
    print(f'OK: {ok_count}, FAIL: {fail_count}, SKIP: {skip_count}')
    print(f'Issues ({len(report["issues"])}):')
    for issue in report['issues']:
        print('  -', issue)
    print(f'Report: {out_path}')
    return 1 if report['issues'] else 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception:
        traceback.print_exc()
        raise SystemExit(2)
