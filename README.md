# py_files_tools

Набор утилит для текстовых файлов и конфигов WireGuard.

| Скрипт | Назначение | Описание |
|---|---|---|
| `replace_text.py` | Замена текста с безопасным предпросмотром | [replace_text.py](docs/replace_text.md) |
| `qr_creator.py` | QR-коды из текстовых файлов по шаблону `--pattern` | [qr_creator.py](docs/qr_creator.md) |

Работает на **Python 3.11+** (проверено на 3.11.9, Windows PowerShell).

## Установка

```powershell
python --version
# Python 3.11.9

python -m pip install -r requirements.txt
```

`requirements.txt` ставит `qrcode` и Pillow (extra `[pil]`). Они нужны только `qr_creator.py`. `replace_text.py` работает без сторонних пакетов.

## Документация

- [Замена текста — replace_text.py](docs/replace_text.md)
- [QR-коды — qr_creator.py](docs/qr_creator.md)

## Лицензия

Свободно используйте и модифицируйте.
