.PHONY: init replace_text qr_creator

init:
	python -m pip install -r requirements.txt

# replace_text — замена текста. Пока APPLY=0, файлы не меняются: скрипт только показывает план.
#
# Меняйте значения ниже или передавайте их в команде:
#   make replace_text FIND=old REPLACE=new
#   make replace_text FIND=old REPLACE=new APPLY=1
#   make replace_text FIND=old REPLACE=new PATTERN=*.txt RECURSIVE=1 FIRST=1 APPLY=1 YES=1
#
# FIND          текст, который ищем                         (обязательный)
# REPLACE       текст, на который меняем                    (может быть пустым)
# SEARCH_PATH   папка поиска                                (по умолчанию .)
# PATTERN       glob-шаблон: *.conf, *.txt, *               (по умолчанию *.conf)
# RECURSIVE     1 — заходить в подпапки, 0 — только папка   (по умолчанию 0)
# FIRST         1 — только первое вхождение в файле         (по умолчанию 0, то есть все)
# APPLY         1 — записать изменения, 0 — только план     (по умолчанию 0)
# YES           1 — не спрашивать подтверждение при записи  (по умолчанию 0)
# MAX_PREVIEW   сколько файлов показать в плане             (по умолчанию 10)

SEARCH_PATH ?= .
PATTERN     ?= *.conf
FIND        ?=
REPLACE     ?=
RECURSIVE   ?= 0
FIRST       ?= 0
APPLY       ?= 0
YES         ?= 0
MAX_PREVIEW ?= 10

# Флаги собираются только для переменных со значением 1.
REPLACE_FLAGS = $(if $(filter 1,$(RECURSIVE)),-r) $(if $(filter 1,$(FIRST)),--first) $(if $(filter 1,$(APPLY)),--apply) $(if $(filter 1,$(YES)),-y)

replace_text:
	$(if $(strip $(FIND)),,$(error Укажите FIND. Пример: make replace_text FIND=old REPLACE=new))
	python replace_text.py --path "$(SEARCH_PATH)" --pattern "$(PATTERN)" --find "$(FIND)" --replace "$(REPLACE)" --max-preview "$(MAX_PREVIEW)" $(REPLACE_FLAGS)

# qr_creator — QR-коды из текстовых файлов. Пока APPLY=0, PNG не пишутся: скрипт только показывает план.
#
# Общие переменные описаны выше: SEARCH_PATH, PATTERN, RECURSIVE, APPLY, YES.
# Свои переменные:
#   BOX_SIZE   размер модуля QR в пикселях   (по умолчанию 10)
#   BORDER     ширина рамки в модулях        (по умолчанию 4)
#
#   make qr_creator
#   make qr_creator PATTERN=*.vpnuri
#   make qr_creator PATTERN=*.vpnuri APPLY=1 YES=1
#   make qr_creator SEARCH_PATH=C:/Users/User/clients PATTERN=*.conf RECURSIVE=1 BOX_SIZE=12 BORDER=4 APPLY=1

BOX_SIZE ?= 10
BORDER   ?= 4

# Флаги собираются только для переменных со значением 1.
QR_FLAGS = $(if $(filter 1,$(RECURSIVE)),--recursive) $(if $(filter 1,$(APPLY)),--apply) $(if $(filter 1,$(YES)),-y)

qr_creator:
	python qr_creator.py --path "$(SEARCH_PATH)" --pattern "$(PATTERN)" --box-size "$(BOX_SIZE)" --border "$(BORDER)" $(QR_FLAGS)
