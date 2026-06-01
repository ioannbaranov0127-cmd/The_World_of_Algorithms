# -*- coding: utf-8 -*-
"""Шаги проекта для тем модуля 2 — развитие после версии 1.0."""

from __future__ import annotations

from course_data.project import PROJECT_NAME

MODULE_2_PROJECT: dict[int, dict] = {
    1: {
        'goal': 'После версии 1.0 освежить код калькулятора и подготовить улучшения.',
        'milestone': 'Повторение: ввод, расчёт, if и while — база готового продукта.',
        'feature': 'Модуль 2 — стабилизация версии 1.0 перед новыми функциями',
    },
    2: {
        'goal': 'Добавить в приложение базу продуктов: списки названий и калорийности.',
        'milestone': 'Два списка: products и kcal_list, доступ по индексу.',
        'feature': 'Улучшение: каталог продуктов вместо ручного if на каждый продукт',
    },
    3: {
        'goal': 'Вести историю съеденного: список порций и их количество.',
        'milestone': 'append(), remove() и len() в логике дневника калорий.',
        'feature': 'Улучшение: журнал порций и подсчёт записей за день',
    },
}


def project_step_for_module_2(num: int) -> dict:
    row = MODULE_2_PROJECT.get(num, {})
    return {
        'project': PROJECT_NAME,
        'goal': row.get('goal', ''),
        'milestone': row.get('milestone', ''),
        'feature': row.get('feature', ''),
        'continues_from': '1.0',
    }
