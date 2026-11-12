#!/usr/bin/env python3
"""
Генерация QR-кодов из файлов WireGuard (.conf).
Перезаписывает существующие PNG с тем же именем.
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


def find_conf_files(root: Path, recursive: bool) -> list[Path]:
    """Возвращает список файлов *.conf в зависимости от флага recursive."""
    if recursive:
        return list(root.rglob("*.conf"))
    return list(root.glob("*.conf"))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Генерация QR-кодов для всех файлов *.conf в указанной папке.",
        epilog="Пример: python qr_creator.py --path C:\\Users\\User\\clients --apply -y",
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=Path("."),
        help="Папка с файлами .conf (по умолчанию: текущая директория)",
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
        help="Искать .conf рекурсивно во вложенных папках",
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

    conf_files = find_conf_files(args.path, args.recursive)

    if not conf_files:
        print(f"В папке '{args.path}' не найдено файлов *.conf.")
        return

    print(f"Найдено {len(conf_files)} файл(ов) .conf:")
    for f in conf_files:
        print(f"  - {f}")

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
    for conf_path in conf_files:
        try:
            content = conf_path.read_text(encoding="utf-8")
            if not content.strip():
                print(f"Пропуск (пустой файл): {conf_path}")
                continue

            png_path = conf_path.with_suffix(".png")
            generate_qr(content, png_path, box_size=args.box_size, border=args.border)
            print(f"✓ {conf_path} → {png_path}")
            success += 1
        except Exception as e:
            print(f"✗ Ошибка при обработке {conf_path}: {e}")
            errors += 1

    print(f"\nГотово: успешно {success}, ошибок {errors}.")


if __name__ == "__main__":
    main()
