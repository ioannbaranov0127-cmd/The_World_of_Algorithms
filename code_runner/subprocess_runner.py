"""
Изолированное выполнение пользовательского Python-кода в отдельном процессе.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass

from .host import child_preexec, minimal_child_env, runner_temp_dir

# Таймаут по умолчанию (секунды): защита от бесконечных циклов и зависаний на input().
DEFAULT_TIMEOUT_SEC = 8.0

# Ограничение размера вывода в символах (после декодирования), чтобы не раздувать память.
MAX_STDIO_CHARS = 200_000

ECHO_STDIN_HARNESS_TEMPLATE = '''# -*- coding: utf-8 -*-
"""Служебная обёртка для красивого отображения input() при проверке."""
import builtins as _builtins
import sys as _sys

def _edu_input(prompt=""):
    p = "" if prompt is None else str(prompt)
    if p:
        _sys.stdout.write(p)
        _sys.stdout.flush()
    line = _sys.stdin.readline()
    if line == "":
        raise EOFError("ввод закончился")
    value = line.rstrip("\\r\\n")
    _sys.stdout.write(value + "\\n")
    _sys.stdout.flush()
    return value

_builtins.input = _edu_input

_user_path = _sys.argv[1]
with open(_user_path, encoding="utf-8") as _uf:
    _code = _uf.read()
exec(compile(_code, _user_path, "exec"), {"__name__": "__main__", "__builtins__": _builtins})
'''


@dataclass(frozen=True)
class RunResult:
    """Результат запуска кода в дочернем интерпретаторе Python."""

    stdout: str
    stderr: str
    exit_code: int | None
    timed_out: bool

    def to_api_dict(self, *, duration_ms: float | None = None) -> dict:
        """Сериализация для JSON API (запуск и проверка)."""
        out: dict = {
            'stdout': self.stdout,
            'stderr': self.stderr,
            'exit_code': self.exit_code,
            'timed_out': self.timed_out,
        }
        if duration_ms is not None:
            out['duration_ms'] = duration_ms
        return out

    def to_legacy_tuple(self) -> tuple[str, str | None, str | None]:
        """
        Совместимость с прежним run_user_code():
        (вывод для сравнения с эталоном, короткая ошибка или None, подробный текст ошибки или None).
        """
        out = self.stdout.strip()
        if self.timed_out:
            detail = (
                "Программа прервана по истечении времени ожидания.\n"
                "Проверьте бесконечные циклы или ожидание ввода без данных."
            )
            return out, "Превышено время выполнения", detail
        if self.exit_code != 0:
            err = (self.stderr or "").strip()
            if not err:
                err = f"Процесс завершился с кодом {self.exit_code}."
            first = err.split("\n", 1)[0].strip() or "Ошибка выполнения"
            return out, first, err
        return out, None, None


def _truncate(s: str, max_chars: int) -> str:
    if len(s) <= max_chars:
        return s
    return s[:max_chars] + f"\n... (обрезано, всего символов: {len(s)})"


def run_python(
    code: str,
    stdin: str = "",
    *,
    timeout_sec: float = DEFAULT_TIMEOUT_SEC,
    echo_stdin: bool = False,
) -> RunResult:
    """
    Запускает многострочный код в отдельном процессе ``python -X utf8 -I script.py``.

    Parameters
    ----------
    code:
        Исходный код (UTF-8).
    stdin:
        Текст, целиком передаваемый в stdin процесса (построчно читается через ``input()``).
        Каждый вызов ``input()`` обычно читает до конца строки включительно с ``\\n``.
    echo_stdin:
        Если True, служебная обёртка показывает введённые строки после prompt из input().
        Это используется только для понятного вывода проверки, не для сравнения ответа.
    timeout_sec:
        Лимит времени на выполнение процесса.

    Notes
    -----
    Для Windows и консолей без UTF-8 задаются ``PYTHONUTF8``/``PYTHONIOENCODING`` и флаг ``-X utf8``.
    Флаг ``-I`` — изолированный режим интерпретатора (урезанный sys.path, без USER_SITE).
    Это не песочница уровня ОС: доступ к файловой системе остаётся как у обычного Python.
    """
    path: str | None = None
    harness_path: str | None = None
    tmp_dir = runner_temp_dir()
    try:
        fd, path = tempfile.mkstemp(suffix=".py", prefix="usercode_", dir=tmp_dir)
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as tmp:
            tmp.write(code)
        # Файл закрыт — на Windows скрипт можно запускать без блокировки на запись.

        args = [sys.executable, "-X", "utf8", "-I", path]
        if echo_stdin:
            fd_h, harness_path = tempfile.mkstemp(suffix=".py", prefix="usercode_echo_", dir=tmp_dir)
            with os.fdopen(fd_h, "w", encoding="utf-8", newline="\n") as tmp_h:
                tmp_h.write(ECHO_STDIN_HARNESS_TEMPLATE)
            args = [sys.executable, "-X", "utf8", "-I", harness_path, path]

        run_kwargs: dict = {
            "args": args,
            "input": stdin,
            "capture_output": True,
            "text": True,
            "encoding": "utf-8",
            "errors": "replace",
            "timeout": timeout_sec,
            "cwd": tmp_dir,
            "check": False,
            "env": minimal_child_env(),
        }
        preexec = child_preexec(timeout_sec)
        if preexec is not None:
            run_kwargs["preexec_fn"] = preexec
        completed = subprocess.run(**run_kwargs)
        stdout = _truncate(completed.stdout or "", MAX_STDIO_CHARS)
        stderr = _truncate(completed.stderr or "", MAX_STDIO_CHARS)
        return RunResult(
            stdout=stdout,
            stderr=stderr,
            exit_code=completed.returncode,
            timed_out=False,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = _truncate((exc.stdout or "") if isinstance(exc.stdout, str) else "", MAX_STDIO_CHARS)
        stderr = _truncate((exc.stderr or "") if isinstance(exc.stderr, str) else "", MAX_STDIO_CHARS)
        return RunResult(stdout=stdout, stderr=stderr, exit_code=None, timed_out=True)
    except OSError as exc:
        return RunResult(
            stdout="",
            stderr=str(exc),
            exit_code=None,
            timed_out=False,
        )
    finally:
        for p in (path, harness_path):
            if p:
                try:
                    os.unlink(p)
                except OSError:
                    pass
