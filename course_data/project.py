# -*- coding: utf-8 -*-
"""
Проектная линия «Калькулятор калорий».

10 основных версий (0.1 … 1.0) — короткие названия для панели прогресса.
"""

PROJECT_NAME = 'Калькулятор калорий'
PROJECT_SLUG = 'calorie_calculator'

# num темы → шаг (версия растёт после сдачи project_stage)
PROJECT_LINE: dict[int, dict] = {
    1: {
        'feature': 'Схема алгоритма калькулятора',
        'goal': 'Понять алгоритм калькулятора как цепочку шагов.',
        'version': '0.1',
        'version_label': '0.1',
    },
    2: {
        'feature': 'print — название проекта',
        'goal': 'Запуск программы и первый вывод.',
        'version': '0.2',
        'version_label': '0.2',
    },
    3: {
        'feature': 'Приветствие пользователю',
        'goal': 'Название и приветствие пользователю.',
        'version': '0.3',
        'version_label': '0.3',
    },
    4: {
        'feature': 'input — продукт и граммы',
        'goal': 'Ввод продукта и граммов.',
        'version': '0.4',
        'version_label': '0.4',
    },
    5: {
        'feature': 'Переменные str, int, float',
        'goal': 'Хранение данных в переменных.',
        'version': '0.5',
        'version_label': '0.5',
    },
    6: {
        'feature': 'Формула: калории × граммы',
        'goal': 'Расчёт калорий по формуле.',
        'version': '0.6',
        'version_label': '0.6',
    },
    7: {
        'feature': 'if — калорийность продукта',
        'goal': 'Выбор продукта через if/elif.',
        'version': '0.7',
        'version_label': '0.7',
    },
    8: {
        'feature': 'Совет: мало / норма / много',
        'goal': 'Рекомендации по итоговым калориям.',
        'version': '0.8',
        'version_label': '0.8',
    },
    9: {
        'feature': 'while — повтор расчёта',
        'goal': 'Калькулятор работает в цикле while.',
        'version': '0.9',
        'version_label': '0.9',
    },
    10: {
        'feature': 'Готовый калькулятор v1.0',
        'goal': 'Полноценный калькулятор калорий.',
        'version': '1.0',
        'version_label': '1.0',
    },
}


def project_step_for_topic(num: int) -> dict:
    row = PROJECT_LINE.get(num, PROJECT_LINE.get(10, {}))
    return {
        'project': PROJECT_NAME,
        'goal': row.get('goal', ''),
        'feature': row.get('feature', ''),
        'version': row.get('version', ''),
    }
