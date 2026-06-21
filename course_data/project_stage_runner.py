# -*- coding: utf-8 -*-
"""
Проверка project_stage «как на Stepik»: скрытые сценарии ввода и гибкая проверка поведения.

Главный критерий — программа реально работает и решает задачу этапа, а не совпадение
имён переменных или точный текст вывода.
"""

from __future__ import annotations

import ast
import re

from code_runner.subprocess_runner import run_python

PROJECT_STAGE_TIMEOUT_SEC = 20.0

_NUM_RE = re.compile(r'-?\d+(?:[.,]\d+)?')


def _parse_stdin_portions(stdin: str) -> list[tuple[int, int]]:
    """Разбирает ввод меню: пары (номер_продукта, граммы) до нуля."""
    lines = [ln.strip() for ln in (stdin or '').splitlines() if ln.strip() != '']
    portions: list[tuple[int, int]] = []
    i = 0
    while i < len(lines):
        try:
            num = int(float(lines[i].replace(',', '.')))
        except ValueError:
            i += 1
            continue
        if num == 0:
            break
        if i + 1 >= len(lines):
            break
        try:
            grams = int(float(lines[i + 1].replace(',', '.')))
        except ValueError:
            break
        portions.append((num, grams))
        i += 2
    return portions


def _parse_dish_dict(node: ast.Dict) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for key_node, val_node in zip(node.keys or [], node.values or []):
        if not isinstance(key_node, ast.Constant) or not isinstance(key_node.value, str):
            continue
        names: list[str] = []
        if isinstance(val_node, ast.List):
            for elt in val_node.elts:
                if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                    names.append(elt.value)
                elif isinstance(elt, (ast.List, ast.Tuple)) and elt.elts:
                    first = elt.elts[0]
                    if isinstance(first, ast.Constant) and isinstance(first.value, str):
                        names.append(first.value)
        if names:
            result[key_node.value] = names
    return result


def extract_products_dict(code: str) -> dict[str, float]:
    """Словарь «продукт → ккал на 100 г» из кода ученика."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return {}

    best: dict[str, float] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue
        parsed: dict[str, float] = {}
        for key_node, val_node in zip(node.keys or [], node.values or []):
            if not isinstance(key_node, ast.Constant) or not isinstance(key_node.value, str):
                continue
            if isinstance(val_node, ast.Constant) and isinstance(val_node.value, (int, float)):
                parsed[key_node.value] = float(val_node.value)
        if len(parsed) > len(best):
            best = parsed
    return best


def extract_nested_kcals(code: str) -> list[float]:
    """Ккал из products = [[имя, kcal], …] в порядке списка."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []

    best: list[float] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.List) or len(node.elts) < 2:
            continue
        if not all(isinstance(e, (ast.List, ast.Tuple)) and len(e.elts) >= 2 for e in node.elts):
            continue
        vals: list[float] = []
        for e in node.elts:
            kcal_elt = e.elts[1]
            if isinstance(kcal_elt, ast.Constant) and isinstance(kcal_elt.value, (int, float)):
                vals.append(float(kcal_elt.value))
        if len(vals) > len(best):
            best = vals
    return best


def extract_parallel_kcals(code: str) -> list[float]:
    """Ккал из kcal_per_100 = [52, 89, …]."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []

    best: list[float] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if not isinstance(target, ast.Name):
                continue
            if target.id.lower() not in ('kcal_per_100', 'kcals', 'calories_per_100'):
                continue
            if isinstance(node.value, ast.List):
                nums: list[float] = []
                for elt in node.value.elts:
                    if isinstance(elt, ast.Constant) and isinstance(elt.value, (int, float)):
                        nums.append(float(elt.value))
                if len(nums) > len(best):
                    best = nums
    return best


def extract_kcal_catalog(code: str) -> list[float]:
    """Ккал на 100 г в порядке меню: индекс 0 — продукт №1."""
    nested = extract_nested_kcals(code)
    if len(nested) >= 2:
        return nested

    parallel = extract_parallel_kcals(code)
    if len(parallel) >= 2:
        return parallel

    products = extract_products_dict(code)
    if len(products) >= 2:
        return [float(v) for v in products.values()]

    legacy = extract_menu_kcals(code)
    return legacy or []


def infer_product_count(code: str, kcals: list[float] | None) -> int:
    if kcals:
        return len(kcals)
    products = extract_products_dict(code)
    if len(products) >= 2:
        return len(products)
    nested = extract_nested_kcals(code)
    if nested:
        return len(nested)
    parallel = extract_parallel_kcals(code)
    if parallel:
        return len(parallel)
    return 4


def build_exit_stdins(n_products: int) -> list[str]:
    """Сценарии немедленного выхода (Stepik: система сама подставляет ввод)."""
    opts = ['0\n']
    if n_products >= 1:
        opts.append(f'{n_products + 1}\n0\n')
    return list(dict.fromkeys(opts))


def build_one_portion_stdins(n_products: int) -> list[str]:
    """Одна порция и выход через 0."""
    n = max(n_products, 1)
    opts: list[str] = []
    for num in (1, 2, min(n, 3)):
        opts.append(f'{num}\n100\n0\n')
    opts.append('1\n150\n0\n')
    if n >= 2:
        opts.append(f'{n}\n100\n0\n')
    return list(dict.fromkeys(opts))


def build_m1_single_stdins() -> list[str]:
    """M1 (0.5–0.9): одна порция без цикла — номер или название + граммы."""
    return [
        '1\n100\n',
        '1\n150\n',
        '2\n100\n',
        '2\n80\n',
        'яблоко\n100\n',
        'Яблоко\n100\n',
        'банан\n100\n',
    ]


def build_two_portion_stdins(n_products: int) -> list[str]:
    """Две порции подряд и выход."""
    n = max(n_products, 2)
    opts = [
        '1\n100\n2\n50\n0\n',
        '1\n100\n2\n80\n0\n',
    ]
    if n >= 3:
        opts.append('1\n100\n3\n60\n0\n')
    opts.append(f'2\n100\n1\n50\n0\n')
    return list(dict.fromkeys(opts))


def _parse_dish_stdin(stdin: str) -> tuple[int, list[int]] | None:
    lines = [ln.strip() for ln in (stdin or '').splitlines() if ln.strip() != '']
    if not lines:
        return None
    try:
        dish_num = int(float(lines[0].replace(',', '.')))
    except ValueError:
        return None
    grams: list[int] = []
    for line in lines[1:]:
        try:
            grams.append(int(float(line.replace(',', '.'))))
        except ValueError:
            break
    if not grams:
        return None
    return dish_num, grams


def build_dish_stdin_by_index(
    dishes: dict[str, list[str]],
    dish_index: int,
    *,
    grams_per_ingredient: int = 100,
) -> str:
    items = list(dishes.items())
    if dish_index < 1 or dish_index > len(items):
        return ''
    _name, ingredients = items[dish_index - 1]
    gram_block = '\n'.join(str(grams_per_ingredient) for _ in ingredients) + '\n'
    return f'{dish_index}\n' + gram_block


def build_dish_stdin_all_dishes(
    dishes: dict[str, list[str]],
    *,
    grams_per_ingredient: int = 100,
) -> list[str]:
    return [
        build_dish_stdin_by_index(dishes, idx, grams_per_ingredient=grams_per_ingredient)
        for idx in range(1, len(dishes) + 1)
    ]


def resolve_stdin_options(
    scenario: dict,
    *,
    code: str,
    kcals: list[float] | None,
    dishes: dict[str, list[str]] | None,
) -> list[str]:
    """Универсальная подстановка stdin: явные stdin_options или auto_stdin по каталогу из кода."""
    explicit = scenario.get('stdin_options')
    if explicit:
        return list(explicit)

    single = scenario.get('stdin')
    if single is not None:
        return [single]

    n = infer_product_count(code, kcals)
    mode = scenario.get('auto_stdin') or scenario.get('stdin_mode') or ''

    if scenario.get('mode') == 'dish' and dishes:
        grams = int(scenario.get('grams_per_ingredient', 100))
        dish_index = scenario.get('dish_index')
        if mode == 'all_dishes':
            return build_dish_stdin_all_dishes(dishes, grams_per_ingredient=grams)
        if dish_index is not None:
            stdin = build_dish_stdin_by_index(dishes, int(dish_index), grams_per_ingredient=grams)
            return [stdin] if stdin else build_dish_stdin_options(dishes, grams_per_ingredient=grams)
        return build_dish_stdin_options(dishes, grams_per_ingredient=grams)

    if mode in ('exit', 'exit_only'):
        return build_exit_stdins(n)
    if mode in ('one_portion', 'one_with_total', 'menu', 'one', 'm1_loop', 'm1_while'):
        return build_one_portion_stdins(n)
    if mode in ('two_portions', 'two'):
        return build_two_portion_stdins(n)
    if mode in ('m1_single', 'm1_inputs', 'single_input'):
        return build_m1_single_stdins()

    return ['']


def expected_dish_metrics(
    products: dict[str, float],
    ingredients: list[str],
    grams_list: list[int],
) -> tuple[float, float, float] | None:
    if not ingredients or len(ingredients) != len(grams_list):
        return None
    total_kcal = 0.0
    total_weight = 0.0
    for ing, grams in zip(ingredients, grams_list):
        total_kcal += products.get(ing, 0.0) * grams / 100.0
        total_weight += grams
    if total_weight <= 0:
        return None
    per100 = total_kcal * 100.0 / total_weight
    return total_kcal, total_weight, per100


def extract_dishes(code: str) -> dict[str, list[str]]:
    """Словарь «блюдо → список ингредиентов» из кода ученика."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return {}

    candidates: list[dict[str, list[str]]] = []
    dish_name_hints = ('dish', 'recipe', 'blud', 'recept', 'menu', 'receipt')

    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            parsed = _parse_dish_dict(node)
            if parsed:
                candidates.append(parsed)
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if not isinstance(target, ast.Name):
                    continue
                lowered = target.id.lower()
                if any(h in lowered for h in dish_name_hints) and isinstance(node.value, ast.Dict):
                    parsed = _parse_dish_dict(node.value)
                    if parsed:
                        candidates.append(parsed)

    if not candidates:
        return {}

    def score(d: dict[str, list[str]]) -> tuple[int, int]:
        ing_count = sum(len(v) for v in d.values())
        return len(d), ing_count

    return max(candidates, key=lambda d: score(d))


def build_dish_stdin_options(
    dishes: dict[str, list[str]],
    *,
    grams_per_ingredient: int = 100,
) -> list[str]:
    if not dishes:
        return []
    dish_name = next(iter(dishes))
    ingredients = dishes[dish_name]
    gram_block = '\n'.join(str(grams_per_ingredient) for _ in ingredients) + '\n'
    return [
        '1\n' + gram_block,
        f'{dish_name}\n' + gram_block,
    ]


def expected_dish_kcal(
    products: dict[str, float],
    ingredients: list[str],
    grams_per_ingredient: int,
) -> float | None:
    if not products or not ingredients:
        return None
    total = 0.0
    for ing in ingredients:
        total += products.get(ing, 0.0) * grams_per_ingredient / 100.0
    return total if total > 0 else None


def extract_menu_kcals(code: str) -> list[float] | None:
    """Пытается извлечь калорийность продуктов из кода (для точной проверки чисел)."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None

    for node in ast.walk(tree):
        if isinstance(node, ast.Dict) and len(node.keys or []) >= 2:
            vals: list[float] = []
            for v in node.values or []:
                if isinstance(v, ast.Constant) and isinstance(v.value, (int, float)):
                    vals.append(float(v.value))
            if len(vals) >= 2:
                return vals

    for node in ast.walk(tree):
        if isinstance(node, ast.List) and len(node.elts) >= 2:
            if all(isinstance(e, (ast.List, ast.Tuple)) and len(e.elts) >= 2 for e in node.elts):
                vals = []
                for e in node.elts:
                    kcal_elt = e.elts[1]
                    if isinstance(kcal_elt, ast.Constant) and isinstance(kcal_elt.value, (int, float)):
                        vals.append(float(kcal_elt.value))
                if len(vals) >= 2:
                    return vals

    numeric_lists: list[list[float]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.List) or len(node.elts) < 2:
            continue
        nums: list[float] = []
        for e in node.elts:
            if isinstance(e, ast.Constant) and isinstance(e.value, (int, float)):
                nums.append(float(e.value))
        if len(nums) == len(node.elts) and len(nums) >= 2:
            numeric_lists.append(nums)

    if numeric_lists:
        candidates = [lst for lst in numeric_lists if max(lst) >= 20]
        if not candidates:
            candidates = numeric_lists
        best = max(candidates, key=len)
        return best

    return None


def _numbers_in_output(output: str) -> list[float]:
    found: list[float] = []
    for m in _NUM_RE.finditer(output or ''):
        try:
            found.append(float(m.group().replace(',', '.')))
        except ValueError:
            pass
    return found


def _output_has_number_near(output: str, target: float, *, tolerance: float = 1.0) -> bool:
    if target <= 0:
        return any(abs(v) <= tolerance for v in _numbers_in_output(output))
    for v in _numbers_in_output(output):
        if abs(v - target) <= tolerance:
            return True
        if abs(round(v) - round(target)) <= tolerance:
            return True
    return False


def _expected_total(kcals: list[float] | None, portions: list[tuple[int, int]]) -> float | None:
    if not kcals or not portions:
        return None
    total = 0.0
    for num, grams in portions:
        idx = num - 1
        if 0 <= idx < len(kcals):
            total += kcals[idx] * grams / 100.0
    return total if total > 0 else None


def _count_numbered_menu_lines(output: str) -> int:
    count = 0
    for line in (output or '').splitlines():
        if re.match(r'^\s*\d+[\).\s]', line.strip()):
            count += 1
    return count


def _check_run_output(
    output: str,
    checks: list[dict],
    *,
    stdin: str,
    kcals: list[float] | None,
    dish_expected: float | None = None,
    dish_weight_expected: float | None = None,
    dish_per100_expected: float | None = None,
) -> list[str]:
    failures: list[str] = []
    portions = _parse_stdin_portions(stdin)
    expected = _expected_total(kcals, portions)

    for rule in checks:
        check = rule.get('check')
        msg = rule.get('message') or 'Сценарий не пройден'

        if check in ('no_crash', 'exit_ok'):
            continue

        if check == 'output_contains_any':
            values = [str(v) for v in (rule.get('values') or [])]
            if not any(v in (output or '') for v in values):
                failures.append(msg)

        elif check == 'output_has_number':
            if not _numbers_in_output(output):
                failures.append(msg)

        elif check == 'output_kcal_hint':
            hints = rule.get('values') or ['ккал', 'Ккал', 'кcal', 'Kcal', 'кКал']
            if not any(h in (output or '') for h in hints) and not _numbers_in_output(output):
                failures.append(msg)

        elif check == 'has_portion_or_total':
            if expected is not None:
                if not _output_has_number_near(output, expected):
                    failures.append(msg)
            elif not _numbers_in_output(output):
                failures.append(msg)

        elif check == 'computed_total':
            if expected is None:
                if not _numbers_in_output(output):
                    failures.append(msg)
            elif not _output_has_number_near(output, expected):
                failures.append(msg)

        elif check == 'computed_total_min':
            min_total = float(rule.get('min', 1))
            if expected is not None:
                if expected < min_total or not _output_has_number_near(output, expected):
                    failures.append(msg)
            elif not any(v >= min_total for v in _numbers_in_output(output)):
                failures.append(msg)

        elif check == 'journal_hint':
            hints = rule.get('values') or ['2', 'запис', 'Запис', 'журнал', 'Журнал', 'порци']
            if not any(h in (output or '') for h in hints):
                if expected is None or not _output_has_number_near(output, expected):
                    failures.append(msg)

        elif check == 'menu_lines_min':
            min_count = int(rule.get('count', 2))
            if rule.get('auto_count') and kcals:
                min_count = max(min_count, len(kcals))
            if _count_numbered_menu_lines(output) < min_count:
                failures.append(msg)

        elif check == 'dish_weight':
            if dish_weight_expected is not None:
                if not _output_has_number_near(output, dish_weight_expected, tolerance=2.0):
                    failures.append(msg)
            elif not _numbers_in_output(output):
                failures.append(msg)

        elif check == 'dish_per100':
            if dish_per100_expected is not None:
                if not _output_has_number_near(output, dish_per100_expected, tolerance=1.5):
                    failures.append(msg)
            else:
                hints = rule.get('values') or ['100', 'На 100', 'на 100']
                if not any(h in (output or '') for h in hints) and not _numbers_in_output(output):
                    failures.append(msg)

        elif check == 'output_line_count_at_least':
            min_count = int(rule.get('count', 1))
            lines = [ln.strip() for ln in (output or '').split('\n') if ln.strip()]
            if len(lines) < min_count:
                failures.append(msg)

        elif check == 'dish_total':
            expected = dish_expected if dish_expected is not None else rule.get('expected')
            if expected is None:
                if not _numbers_in_output(output):
                    failures.append(msg)
            elif not _output_has_number_near(output, float(expected), tolerance=2.0):
                failures.append(msg)

        elif check == 'dish_ingredients_flow':
            hints = rule.get('values') or ['грамм', 'Грамм', 'GRAM']
            hits = sum(1 for h in hints if h in (output or ''))
            min_hits = int(rule.get('min_hits', 2))
            if hits < min_hits and _count_numbered_menu_lines(output) < 1:
                failures.append(msg)

    return failures


def _run_one_scenario(
    code: str,
    scenario: dict,
    *,
    kcals: list[float] | None,
    products: dict[str, float] | None = None,
    dishes: dict[str, list[str]] | None = None,
) -> tuple[bool, list[str], str, str]:
    name = scenario.get('name') or 'тест'
    checks = scenario.get('checks') or [{'check': 'no_crash'}]
    failures: list[str] = []
    best_output = ''
    used_stdin = ''

    stdins = resolve_stdin_options(
        scenario,
        code=code,
        kcals=kcals,
        dishes=dishes,
    )

    dish_items = list((dishes or {}).items())

    for stdin in stdins:
        if not stdin and scenario.get('mode') != 'dish':
            continue

        dish_expected: float | None = None
        dish_weight_expected: float | None = None
        dish_per100_expected: float | None = None

        if scenario.get('mode') == 'dish' and dishes and products:
            grams_default = int(scenario.get('grams_per_ingredient', 100))
            parsed = _parse_dish_stdin(stdin)
            if parsed:
                dish_num, grams_list = parsed
                if 1 <= dish_num <= len(dish_items):
                    _dname, ingredients = dish_items[dish_num - 1]
                    if len(grams_list) == len(ingredients):
                        metrics = expected_dish_metrics(products, ingredients, grams_list)
                        if metrics:
                            dish_expected, dish_weight_expected, dish_per100_expected = metrics
            if dish_expected is None:
                dish_index = scenario.get('dish_index', 1)
                if 1 <= int(dish_index) <= len(dish_items):
                    _dname, ingredients = dish_items[int(dish_index) - 1]
                    dish_expected = expected_dish_kcal(products, ingredients, grams_default)
                    dish_weight_expected = float(grams_default * len(ingredients))
                    if dish_weight_expected > 0 and dish_expected is not None:
                        dish_per100_expected = dish_expected * 100.0 / dish_weight_expected

        result = run_python(code, stdin, timeout_sec=PROJECT_STAGE_TIMEOUT_SEC)
        output = result.stdout or ''
        if output:
            best_output = output
        if stdin:
            used_stdin = stdin

        if result.timed_out:
            failures = [
                scenario.get('message_timeout')
                or f'«{name}»: программа слишком долго ждала ввод. '
                'Проверьте цикл по ингредиентам и количество input().'
            ]
            continue

        if result.exit_code not in (0, None):
            err = (result.stderr or '').strip()
            detail = f' {err[:180]}' if err else ''
            failures = [
                scenario.get('message_error')
                or f'«{name}»: программа завершилась с ошибкой.{detail}'
            ]
            continue

        run_failures = _check_run_output(
            output,
            checks,
            stdin=stdin,
            kcals=kcals,
            dish_expected=dish_expected,
            dish_weight_expected=dish_weight_expected,
            dish_per100_expected=dish_per100_expected,
        )
        if not run_failures:
            return True, [], output, used_stdin
        failures = run_failures

    return False, failures, best_output, used_stdin


def validate_project_stage_runs(code: str, task: dict) -> tuple[bool, list[str], str, str]:
    """
    Stepik-подобная проверка project_stage по сценариям ``project_runs``.

    Returns
    -------
    ok, failures, combined_output, stdin_for_check
    """
    runs = task.get('project_runs') or []
    if not runs:
        return False, ['Для задания не заданы сценарии проверки.'], '', ''

    src = code or ''
    if not src.strip():
        return False, ['Напишите код программы.'], '', ''

    try:
        ast.parse(src)
    except SyntaxError as exc:
        return False, [f'Сначала исправьте синтаксис: {exc.msg} (строка {exc.lineno}).'], '', ''

    kcals = extract_kcal_catalog(src)
    products = extract_products_dict(src)
    dishes = extract_dishes(src)
    all_failures: list[str] = []
    outputs: list[str] = []
    stdin_for_check = ''

    for scenario in runs:
        ok, failures, output, used_stdin = _run_one_scenario(
            src,
            scenario,
            kcals=kcals,
            products=products,
            dishes=dishes,
        )
        if output:
            outputs.append(output)
        if used_stdin and not stdin_for_check:
            stdin_for_check = used_stdin
        if not ok:
            all_failures.extend(failures)

    combined = '\n'.join(outputs).strip()
    return len(all_failures) == 0, all_failures, combined, stdin_for_check


def task_auto_stdin_mode(task: dict) -> str:
    """Режим auto stdin на задании или в первом project_run."""
    mode = task.get('auto_stdin') or task.get('stdin_mode') or ''
    if mode:
        return str(mode)
    for scenario in task.get('project_runs') or []:
        mode = scenario.get('auto_stdin') or scenario.get('stdin_mode') or ''
        if mode:
            return str(mode)
    return ''


def validate_m1_project_stage(
    code: str,
    task: dict,
    client_stdin: str = '',
) -> tuple[bool, list[str], str, str]:
    """
    M1 project_stage с project_tests: подставляет stdin как на Stepik, затем гибкие проверки.
    """
    tests = task.get('project_tests') or []
    if not tests:
        return False, ['Для задания не заданы проверки project_tests.'], '', ''

    src = code or ''
    if not src.strip():
        return False, ['Напишите код программы.'], '', ''

    try:
        ast.parse(src)
    except SyntaxError as exc:
        return False, [f'Сначала исправьте синтаксис: {exc.msg} (строка {exc.lineno}).'], '', ''

    from course_data.validators import validate_project_tests

    mode = task_auto_stdin_mode(task)
    kcals = extract_kcal_catalog(src)

    stdin_candidates: list[str] = []
    if (client_stdin or '').strip():
        stdin_candidates.append(client_stdin)
    if mode:
        stdin_candidates.extend(
            resolve_stdin_options({'auto_stdin': mode}, code=src, kcals=kcals, dishes=None)
        )
    if not stdin_candidates:
        stdin_candidates = ['']

    seen: set[str] = set()
    unique_stdins: list[str] = []
    for item in stdin_candidates:
        if item not in seen:
            seen.add(item)
            unique_stdins.append(item)

    last_output = ''
    last_failures: list[str] = []
    used_stdin = ''

    for stdin in unique_stdins:
        result = run_python(src, stdin, timeout_sec=PROJECT_STAGE_TIMEOUT_SEC)
        output = result.stdout or ''
        if output:
            last_output = output
        if stdin:
            used_stdin = stdin

        if result.timed_out:
            last_failures = [
                'Программа слишком долго ждала ввод. '
                'Проверьте input() и выход из цикла (0 или «стоп»).'
            ]
            continue

        if result.exit_code not in (0, None):
            err = (result.stderr or '').strip()
            detail = f' {err[:180]}' if err else ''
            last_failures = [f'Программа завершилась с ошибкой.{detail}']
            continue

        ok, failures = validate_project_tests(src, output, tests)
        if ok:
            return True, [], output, used_stdin
        last_failures = failures

    if not last_failures:
        last_failures = ['Не удалось проверить программу — добавьте input() и вывод результата.']

    return False, last_failures, last_output, used_stdin
