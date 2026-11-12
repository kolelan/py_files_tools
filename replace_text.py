#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Замена текста в файлах (Python 3.11+).

По умолчанию — DRY-RUN (ничего не пишет, только показывает план).
Реальная запись — только с флагом --apply.

Примеры:
    # Показать, что будет изменено в *.conf (текущая папка, без рекурсии)
    python replace_text.py --find "старый_текст" --replace "новый_текст"

    # Применить в *.conf
    python replace_text.py --find "old" --replace "new" --apply

    # Только первое вхождение в каждом файле, *.txt, рекурсивно
    python replace_text.py --find "old" --replace "new" --pattern "*.txt" -r --first --apply

    # Вообще во всех читаемых файлах (бинарные автоматически пропускаются)
    python replace_text.py --find "old" --replace "new" --pattern "*" -r
"""

import argparse
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Работа с файлами
# ---------------------------------------------------------------------------

def read_file(path: Path):
    """
    Читает файл. Возвращает (text, encoding, bom) либо (None, None, None),
    если файл бинарный или в неизвестной кодировке.
    """
    try:
        raw = path.read_bytes()
    except OSError:
        return None, None, None

    # Бинарные файлы обычно содержат нулевые байты — пропускаем
    if b"\x00" in raw and not raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        return None, None, None

    # UTF-16 (с BOM)
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        try:
            return raw.decode("utf-16"), "utf-16", b""
        except UnicodeDecodeError:
            return None, None, None

    # UTF-8 с BOM
    bom = b""
    body = raw
    if raw.startswith(b"\xef\xbb\xbf"):
        bom = b"\xef\xbb\xbf"
        body = raw[3:]

    for enc in ("utf-8", "cp1251"):
        try:
            return body.decode(enc), enc, bom
        except UnicodeDecodeError:
            continue

    return None, None, None


def write_file(path: Path, text: str, encoding: str, bom: bytes) -> None:
    """Пишет файл в исходной кодировке (с тем же BOM, что был)."""
    data = bom + text.encode(encoding)
    path.write_bytes(data)


# ---------------------------------------------------------------------------
# Поиск файлов
# ---------------------------------------------------------------------------

def iter_files(root: Path, pattern: str, recursive: bool):
    it = root.rglob(pattern) if recursive else root.glob(pattern)
    for p in it:
        if p.is_file():
            yield p


# ---------------------------------------------------------------------------
# Предпросмотр одной затронутой строки
# ---------------------------------------------------------------------------

def preview_line(text: str, needle: str):
    """Возвращает строку, в которой есть совпадение (для наглядности)."""
    idx = text.find(needle)
    if idx < 0:
        return ""
    start = text.rfind("\n", 0, idx) + 1
    end = text.find("\n", idx)
    if end == -1:
        end = len(text)
    return text[start:end]


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(
        description="Замена текста в файлах. По умолчанию — dry-run (без записи).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Примеры:\n"
            "  python replace_text.py --find old --replace new\n"
            "  python replace_text.py --find old --replace new --apply\n"
            "  python replace_text.py --find old --replace new --first --pattern '*.conf' -r --apply\n"
            "  python replace_text.py --find old --replace new --pattern '*' -r\n"
        ),
    )
    ap.add_argument("--path", default=".", help="Папка для поиска (по умолчанию: текущая)")
    ap.add_argument("--pattern", default="*.conf",
                    help="Glob-шаблон: '*.conf', '*.txt', '*' (по умолчанию: *.conf)")
    ap.add_argument("-r", "--recursive", action="store_true", help="Искать рекурсивно")
    ap.add_argument("--find", required=True, help="Текст, который ищем")
    ap.add_argument("--replace", required=True, help="Текст, на который заменяем")
    ap.add_argument("--first", action="store_true",
                    help="Заменять только первое вхождение в каждом файле (по умолчанию — все)")
    ap.add_argument("--apply", action="store_true",
                    help="Реально записать изменения (без флага — только план)")
    ap.add_argument("-y", "--yes", action="store_true",
                    help="Не спрашивать подтверждение при --apply")
    ap.add_argument("--max-preview", type=int, default=10,
                    help="Сколько файлов показать в предпросмотре (по умолчанию 10)")
    args = ap.parse_args()

    if not args.find:
        print("ОШИБКА: --find не может быть пустым", file=sys.stderr)
        return 2

    root = Path(args.path)
    if not root.is_dir():
        print(f"ОШИБКА: путь не найден или не папка: {root}", file=sys.stderr)
        return 2

    files = list(iter_files(root, args.pattern, args.recursive))
    if not files:
        print(f"Файлы по шаблону {args.pattern!r} в {root!r} не найдены.")
        return 0

    # ---- Сбор плана ------------------------------------------------------
    plan = []          # (path, enc, bom, old_text, new_text, total_matches, will_replace)
    total_replacements = 0
    total_matches = 0
    skipped_binary = 0

    for p in files:
        text, enc, bom = read_file(p)
        if text is None:
            skipped_binary += 1
            continue

        n = text.count(args.find)
        if n == 0:
            continue

        if args.first:
            new_text = text.replace(args.find, args.replace, 1)
            will = 1
        else:
            new_text = text.replace(args.find, args.replace)
            will = n

        plan.append((p, enc, bom, text, new_text, n, will))
        total_matches += n
        total_replacements += will

    # ---- Отчёт ------------------------------------------------------------
    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"\n=== Режим: {mode} ===")
    print(f"Папка       : {root.resolve()}")
    print(f"Шаблон      : {args.pattern}{'  (рекурсивно)' if args.recursive else ''}")
    print(f"Искать      : {args.find!r}")
    print(f"Заменить на : {args.replace!r}")
    print(f"Режим замены: {'только первое вхождение в файле' if args.first else 'все вхождения'}")
    print(f"Файлов просканировано : {len(files)}")
    print(f"Файлов с совпадениями : {len(plan)}")
    print(f"Всего совпадений      : {total_matches}")
    print(f"Будет заменено        : {total_replacements}")
    if skipped_binary:
        print(f"Пропущено (бинарные/нечитаемые): {skipped_binary}")

    if not plan:
        print("\nСовпадений не найдено.")
        return 0

    print("\n--- Файлы ---")
    for i, (p, enc, bom, old_text, new_text, n, will) in enumerate(plan):
        if i >= args.max_preview:
            print(f"... и ещё {len(plan) - i} файл(ов)")
            break
        rel = p.relative_to(root) if p.is_relative_to(root) else p
        print(f"\n[{i + 1}] {rel}  (кодировка={enc}, совпадений={n}, заменим={will})")
        before = preview_line(old_text, args.find)
        after  = preview_line(new_text, args.replace)
        print(f"    было : {before}")
        print(f"    стало: {after}")

    if not args.apply:
        print("\nDry-run завершён. Ничего не записано.")
        print("Для реальной записи запустите с флагом --apply")
        return 0

    # ---- Подтверждение ----------------------------------------------------
    if not args.yes:
        try:
            ans = input("\nПрименить эти изменения? [y/N]: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nОтменено.")
            return 1
        if ans not in ("y", "yes", "д", "да"):
            print("Отменено.")
            return 1

    # ---- Запись -----------------------------------------------------------
    written = 0
    errors = 0
    for p, enc, bom, old_text, new_text, n, will in plan:
        try:
            write_file(p, new_text, enc, bom)
            written += 1
        except OSError as e:
            print(f"ОШИБКА записи {p}: {e}", file=sys.stderr)
            errors += 1

    print(f"\nГотово. Записано файлов: {written}, ошибок: {errors}")
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())