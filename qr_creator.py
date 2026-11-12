#!/usr/bin/env python3
"""
Генерация QR-кодов из текстовых файлов по glob-шаблону.

По умолчанию обрабатывает *.conf.
Имена PNG:
  peer-12.conf     → peer-12.png
  peer-11.vpnuri   → peer-11.vpnuri.png
"""

import argparse
import sys
from pathlib import Path

try:
    import qrcode
except ImportError:
    print("Ошибка: библиотека 'qrcode' не установлена.")
    print("Установите её командой: pip install qrcode[pil]")
    sys.exit(1)


def generate_qr(data: str, output_path: Path, box_size: int = 10, border: int = 4) -> None:
    """Создаёт QR-код из строки data и сохраняет в output_path."""
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(output_path)


def output_png_path(source: Path) -> Path:
    """Путь PNG, который не сталкивает разные расширения в одно имя.

    *.conf сохраняет прежнее имя (peer-12.conf → peer-12.png).
    Остальные файлы получают .png в конце (peer-11.vpnuri → peer-11.vpnuri.png).
    """
    if source.suffix.lower() == ".conf":
        return source.with_suffix(".png")
    return source.with_name(source.name + ".png")


def find_source_files(root: Path, pattern: str, recursive: bool) -> list[Path]:
    """Возвращает текстовые исходники по шаблону. Готовые PNG пропускает."""
    iterator = root.rglob(pattern) if recursive else root.glob(pattern)
    return sorted(
        path for path in iterator
        if path.is_file() and path.suffix.lower() != ".png"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Генерация QR-кодов для текстовых файлов по glob-шаблону.",
        epilog=(
            "Примеры:\n"
            "  python qr_creator.py --path C:\\Users\\User\\clients --apply -y\n"
            "  python qr_creator.py --path C:\\Users\\User\\clients --pattern \"*.vpnuri\" --apply\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=Path("."),
        help="Папка с исходными файлами (по умолчанию: текущая директория)",
    )
    parser.add_argument(
        "--pattern",
        default="*.conf",
        help="Glob-шаблон исходных файлов: '*.conf', '*.vpnuri', '*.txt' (по умолчанию: *.conf)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Реально записать QR-коды на диск (без флага — только предпросмотр)",
    )
    parser.add_argument(
        "-y", "--yes",
        action="store_true",
        help="Не запрашивать подтверждение перед записью",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Искать файлы рекурсивно во вложенных папках",
    )
    parser.add_argument(
        "--box-size",
        type=int,
        default=10,
        help="Размер модуля QR-кода в пикселях (по умолчанию: 10)",
    )
    parser.add_argument(
        "--border",
        type=int,
        default=4,
        help="Ширина рамки вокруг QR-кода в модулях (по умолчанию: 4)",
    )

    args = parser.parse_args()

    if not args.path.exists():
        print(f"Ошибка: путь '{args.path}' не существует.")
        sys.exit(1)
    if not args.path.is_dir():
        print(f"Ошибка: '{args.path}' не является директорией.")
        sys.exit(1)

    source_files = find_source_files(args.path, args.pattern, args.recursive)

    if not source_files:
        print(f"В папке '{args.path}' не найдено файлов по шаблону '{args.pattern}'.")
        return

    print(f"Найдено {len(source_files)} файл(ов), шаблон '{args.pattern}':")
    for source in source_files:
        print(f"  - {source} → {output_png_path(source)}")

    if not args.apply:
        print("\n[РЕЖИМ ПРЕДПРОСМОТРА] Ничего не записано. Добавьте флаг --apply для реальной генерации.")
        return

    if not args.yes:
        answer = input("\nПерезаписать существующие QR-коды? [y/N]: ").strip().lower()
        if answer not in ("y", "yes", "н", "да"):
            print("Отменено пользователем.")
            return

    success = 0
    errors = 0
    for source in source_files:
        try:
            content = source.read_text(encoding="utf-8")
            if not content.strip():
                print(f"Пропуск (пустой файл): {source}")
                continue

            png_path = output_png_path(source)
            generate_qr(content, png_path, box_size=args.box_size, border=args.border)
            print(f"✓ {source} → {png_path}")
            success += 1
        except Exception as e:
            print(f"✗ Ошибка при обработке {source}: {e}")
            errors += 1

    print(f"\nГотово: успешно {success}, ошибок {errors}.")


if __name__ == "__main__":
    main()
