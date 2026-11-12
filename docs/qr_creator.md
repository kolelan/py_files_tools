# qr_creator.py

Генерирует QR-код из содержимого текстового файла и сохраняет PNG рядом с ним.

[К оглавлению](../README.md)

Нужен Python 3.11+ и пакет из `requirements.txt` (`qrcode[pil]`, вместе с ним ставится Pillow).

Без флага `--apply` скрипт только показывает, какие файлы нашёл и куда запишет PNG.

## Имена PNG

| Исходный файл | PNG |
|---|---|
| `peer-12.conf` | `peer-12.png` |
| `peer-11.vpnuri` | `peer-11.vpnuri.png` |
| `note.txt` | `note.txt.png` |

Для `*.conf` расширение заменяется на `.png` — так уже лежат коды рядом с конфигами WireGuard. Для любого другого расширения `.png` дописывается в конец имени, чтобы QR конфига и QR vpnuri не затирали друг друга.

Существующий PNG с тем же именем перезаписывается. Готовые `*.png` не используются как исходники.

Пустые файлы пропускаются. Текст читается как UTF-8. Уровень коррекции ошибок QR — `M`.

## Быстрый старт

### Конфиги WireGuard (шаблон по умолчанию `*.conf`)

```powershell
python qr_creator.py --path "C:\Users\User\clients"
python qr_creator.py --path "C:\Users\User\clients" --apply
```

### Файлы vpnuri

В PowerShell маску нужно передавать в кавычках:

```powershell
python qr_creator.py --path "C:\Users\User\clients" --pattern "*.vpnuri"
python qr_creator.py --path "C:\Users\User\clients" --pattern "*.vpnuri" --apply
```

Будет запрошено подтверждение. Для запуска без вопросов добавьте `-y`.

### Другой шаблон и вложенные папки

```powershell
python qr_creator.py --path "C:\Users\User\clients" --pattern "*.txt" --recursive --box-size 12 --border 4 --apply -y
```

## Аргументы

| Аргумент | По умолчанию | Описание |
|---|---|---|
| `--path` | `.` | Папка с исходными файлами |
| `--pattern` | `*.conf` | Glob-шаблон: `*.conf`, `*.vpnuri`, `*.txt` |
| `--apply` | выкл. | Записать PNG (иначе — только предпросмотр) |
| `-y`, `--yes` | выкл. | Не спрашивать подтверждение при `--apply` |
| `--recursive` | выкл. | Искать во вложенных папках |
| `--box-size` | `10` | Размер модуля QR-кода в пикселях |
| `--border` | `4` | Ширина рамки в модулях |
| `-h`, `--help` | — | Справка |

## Пример предпросмотра

```
Найдено 2 файл(ов), шаблон '*.vpnuri':
  - C:\Users\User\clients\peer-11.vpnuri → C:\Users\User\clients\peer-11.vpnuri.png
  - C:\Users\User\clients\peer-12.vpnuri → C:\Users\User\clients\peer-12.vpnuri.png

[РЕЖИМ ПРЕДПРОСМОТРА] Ничего не записано. Добавьте флаг --apply для реальной генерации.
```

## Возможные проблемы

### `ModuleNotFoundError` или сообщение, что библиотека `qrcode` не установлена

Зависимость не установлена в тот интерпретатор, которым запускается скрипт:

```powershell
python -m pip install -r requirements.txt
python --version
where.exe python
```

### `Ошибка: путь не существует`

Проверьте `--path`: это должна быть существующая папка.

### В папке ничего не найдено

Шаблон не совпал с именами файлов, либо PowerShell раскрыл `*` до запуска Python. Передайте маску в кавычках: `--pattern "*.vpnuri"`.
