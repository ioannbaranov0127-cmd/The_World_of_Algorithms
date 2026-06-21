# -*- coding: utf-8 -*-

from __future__ import annotations

import ast

from course_data.constants import DEFAULT_CODE_EDITOR_PLACEHOLDER


def stdout_matches(output: str, expected: str) -> bool:
    output_lines = [line.strip() for line in output.split('\n') if line.strip()]
    expected_lines = [line.strip() for line in expected.split('\n') if line.strip()]
    return output_lines == expected_lines


def validate_project_tests(code: str, output: str, tests: list[dict] | None) -> tuple[bool, list[str]]:
    """Гибкие проверки этапа разработки: код + важные фрагменты вывода."""
    if not tests:
        return True, []
    failures: list[str] = []
    src = code or ''
    out = output or ''
    tree = None
    parse_error = False

    def parsed_tree():
        nonlocal tree, parse_error
        if parse_error:
            raise SyntaxError
        if tree is None:
            try:
                tree = ast.parse(src)
            except SyntaxError:
                parse_error = True
                raise
        return tree

    def _names_in_tree(parsed: ast.AST) -> set[str]:
        return {n.id for n in ast.walk(parsed) if isinstance(n, ast.Name)}

    def _call_names(parsed: ast.AST) -> set[str]:
        found: set[str] = set()
        for node in ast.walk(parsed):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                found.add(node.func.id)
        return found

    def _method_calls(parsed: ast.AST) -> set[str]:
        found: set[str] = set()
        for node in ast.walk(parsed):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                found.add(node.func.attr)
        return found

    def _has_div_by_100(node: ast.AST) -> bool:
        for sub in ast.walk(node):
            if isinstance(sub, ast.BinOp) and isinstance(sub.op, (ast.Div, ast.FloorDiv)):
                right = sub.right
                if isinstance(right, ast.Constant) and right.value in (100, 100.0):
                    return True
        return False

    def _list_literals(parsed: ast.AST) -> list[ast.List]:
        return [n for n in ast.walk(parsed) if isinstance(n, ast.List)]

    def _dict_literals(parsed: ast.AST) -> list[ast.Dict]:
        return [n for n in ast.walk(parsed) if isinstance(n, ast.Dict)]

    def _function_defs(parsed: ast.AST) -> list[ast.FunctionDef]:
        return [n for n in ast.walk(parsed) if isinstance(n, ast.FunctionDef)]

    for i, rule in enumerate(tests, start=1):
        check = rule.get('check')
        msg = rule.get('message') or f'Тест {i} не пройден'
        try:
            if check == 'contains':
                if rule.get('value', '') not in src:
                    failures.append(msg)
            elif check == 'contains_any':
                values = rule.get('values') or []
                if not any(str(value) in src for value in values):
                    failures.append(msg)
            elif check == 'contains_at_least':
                values = rule.get('values') or []
                min_count = int(rule.get('count', 1))
                found = sum(1 for value in values if str(value) in src)
                if found < min_count:
                    failures.append(msg)
            elif check == 'output_contains':
                if rule.get('value', '') not in out:
                    failures.append(msg)
            elif check == 'output_contains_any':
                values = rule.get('values') or []
                if not any(str(value) in out for value in values):
                    failures.append(msg)
            elif check == 'output_contains_at_least':
                values = rule.get('values') or []
                min_count = int(rule.get('count', 1))
                found = sum(1 for value in values if str(value) in out)
                if found < min_count:
                    failures.append(msg)
            elif check == 'output_line_count_at_least':
                min_count = int(rule.get('count', 1))
                lines = [line.strip() for line in out.split('\n') if line.strip()]
                if len(lines) < min_count:
                    failures.append(msg)
            elif check == 'not_contains':
                if rule.get('value', '') in src:
                    failures.append(msg)
            elif check == 'uses_name':
                parsed = parsed_tree()
                if rule.get('name') not in _names_in_tree(parsed):
                    failures.append(msg)
            elif check == 'uses_any_name':
                parsed = parsed_tree()
                expected_names = set(rule.get('names') or [])
                if not _names_in_tree(parsed).intersection(expected_names):
                    failures.append(msg)
            elif check == 'uses_call':
                parsed = parsed_tree()
                if rule.get('name', '') not in _call_names(parsed):
                    failures.append(msg)
            elif check == 'uses_any_call':
                parsed = parsed_tree()
                expected = set(rule.get('names') or [])
                if not _call_names(parsed).intersection(expected):
                    failures.append(msg)
            elif check == 'uses_any_method':
                parsed = parsed_tree()
                expected = set(rule.get('methods') or [])
                if not _method_calls(parsed).intersection(expected):
                    failures.append(msg)
            elif check == 'ast_has_while':
                parsed = parsed_tree()
                if not any(isinstance(n, ast.While) for n in ast.walk(parsed)):
                    failures.append(msg)
            elif check == 'ast_has_break':
                parsed = parsed_tree()
                if not any(isinstance(n, ast.Break) for n in ast.walk(parsed)):
                    failures.append(msg)
            elif check == 'ast_has_for':
                parsed = parsed_tree()
                if not any(isinstance(n, ast.For) for n in ast.walk(parsed)):
                    failures.append(msg)
            elif check == 'ast_has_if':
                parsed = parsed_tree()
                if not any(isinstance(n, ast.If) for n in ast.walk(parsed)):
                    failures.append(msg)
            elif check == 'ast_def_count_min':
                parsed = parsed_tree()
                min_count = int(rule.get('count', 1))
                if len(_function_defs(parsed)) < min_count:
                    failures.append(msg)
            elif check == 'ast_has_def_with_return':
                parsed = parsed_tree()
                ok = False
                for fn in _function_defs(parsed):
                    if any(isinstance(n, ast.Return) for n in ast.walk(fn)):
                        ok = True
                        break
                if not ok:
                    failures.append(msg)
            elif check == 'ast_has_portion_formula':
                parsed = parsed_tree()
                ok = _has_div_by_100(parsed)
                if not ok:
                    failures.append(msg)
            elif check == 'ast_has_subscript':
                parsed = parsed_tree()
                if not any(isinstance(n, ast.Subscript) for n in ast.walk(parsed)):
                    failures.append(msg)
            elif check == 'ast_has_nested_subscript':
                parsed = parsed_tree()
                ok = False
                for node in ast.walk(parsed):
                    if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Subscript):
                        ok = True
                        break
                    if isinstance(node, ast.Subscript):
                        sl = node.slice
                        if isinstance(sl, ast.Constant) and sl.value in (0, 1):
                            ok = True
                            break
                if not ok:
                    failures.append(msg)
            elif check == 'ast_list_literal_min':
                parsed = parsed_tree()
                min_count = int(rule.get('count', 1))
                lists = _list_literals(parsed)
                ok = any(len(lst.elts) >= min_count for lst in lists)
                if not ok:
                    failures.append(msg)
            elif check == 'ast_two_lists_min':
                parsed = parsed_tree()
                min_count = int(rule.get('count', 3))
                lists = _list_literals(parsed)
                big = [lst for lst in lists if len(lst.elts) >= min_count]
                if len(big) < 2:
                    failures.append(msg)
            elif check == 'ast_has_nested_list':
                parsed = parsed_tree()
                ok = any(
                    any(isinstance(elt, (ast.List, ast.Tuple)) for elt in lst.elts)
                    for lst in _list_literals(parsed)
                )
                if not ok:
                    failures.append(msg)
            elif check == 'ast_dict_literal_min':
                parsed = parsed_tree()
                min_count = int(rule.get('count', 1))
                ok = any(
                    len([k for k in dct.keys if k is not None]) >= min_count
                    for dct in _dict_literals(parsed)
                )
                if not ok and '{' in src and src.count(':') >= min_count:
                    ok = True
                if not ok:
                    failures.append(msg)
            elif check == 'ast_has_dict_subscript_or_get':
                parsed = parsed_tree()
                has_get = 'get' in _method_calls(parsed)
                has_sub_on_dict = any(
                    isinstance(n, ast.Subscript) for n in ast.walk(parsed)
                )
                if not (has_get or has_sub_on_dict):
                    failures.append(msg)
            elif check == 'ast_has_dict_write':
                parsed = parsed_tree()
                ok = 'update' in _method_calls(parsed)
                if not ok:
                    for node in ast.walk(parsed):
                        if isinstance(node, ast.Assign):
                            for target in node.targets:
                                if isinstance(target, ast.Subscript):
                                    ok = True
                                    break
                        if ok:
                            break
                if not ok:
                    failures.append(msg)
            elif check == 'ast_has_add_to_total':
                parsed = parsed_tree()
                total_names = set(rule.get('names') or ['total', 'itog', 'itogo', 'summa', 'summ', 'sum_kcal'])
                ok = False
                for node in ast.walk(parsed):
                    if isinstance(node, ast.AugAssign) and isinstance(node.target, ast.Name):
                        if node.target.id in total_names and isinstance(node.op, (ast.Add,)):
                            ok = True
                            break
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if not isinstance(target, ast.Name) or target.id not in total_names:
                                continue
                            if isinstance(node.value, ast.BinOp) and isinstance(node.value.op, ast.Add):
                                ok = True
                                break
                            if isinstance(node.value, ast.Name):
                                ok = True
                                break
                    if ok:
                        break
                if not ok and '+' in src:
                    ok = bool(_names_in_tree(parsed).intersection(total_names))
                if not ok:
                    failures.append(msg)
        except SyntaxError:
            failures.append('Сначала исправьте синтаксис программы.')
            break
    return len(failures) == 0, failures


def topic_by_task_id(module_id: int, task_id: int) -> dict | None:
    from course_data.loader import LESSONS

    mod = LESSONS.get(module_id)
    if not mod:
        return None
    for topic in mod.get('topics') or []:
        for t in topic.get('tasks') or []:
            if t['id'] == task_id:
                return topic
    return None


def task_client_payload(task: dict) -> dict:
    ttype = task.get('type', 'code')
    base: dict = {
        'id': task['id'],
        'type': ttype,
        'text': task['text'],
        'hint': task.get('hint', ''),
        'xp': task.get('xp', 0),
        'kind': task.get('kind', ttype),
    }
    if ttype == 'code':
        sc = task.get('starter_code')
        if sc is None or not str(sc).strip():
            base['starter_code'] = DEFAULT_CODE_EDITOR_PLACEHOLDER
        else:
            base['starter_code'] = sc
    elif ttype == 'quiz':
        base['options'] = task['options']
    elif ttype == 'ordering':
        base['items'] = list(task['items'])
    elif ttype == 'matching':
        base['left'] = list(task['left'])
        base['right'] = list(task['right'])
    elif ttype == 'fill_gaps':
        base['template'] = task['template']
        base['blank_count'] = len(task.get('answers') or [])
    return base


def validate_interactive_answer(task: dict, answer) -> bool:
    ttype = task.get('type', 'code')
    if ttype == 'code':
        return False
    if ttype == 'quiz':
        return answer == task.get('correct')
    if ttype == 'ordering':
        return answer == task.get('correct_order')
    if ttype == 'matching':
        exp = task.get('correct_pairs')
        if not isinstance(answer, list) or len(answer) != len(exp):
            return False
        return list(answer) == list(exp)
    if ttype == 'fill_gaps':
        exp = task.get('answers')
        if not isinstance(answer, list) or len(answer) != len(exp):
            return False
        return [str(x).strip() for x in answer] == [str(x).strip() for x in exp]
    return False
