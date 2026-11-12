.PHONY: init replace_text

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
