# Analytics Automation Workspace

## Описание проекта

Analytics Automation Workspace — система автоматизации аналитических отчетов.

Основная задача проекта:

- автоматическая загрузка исходных Excel-файлов;
- определение GEO;
- загрузка данных в Google Sheets;
- запуск пересчета формул;
- создание архивных копий отчетов;
- подготовка основы для масштабирования новых отчетов и проектов.

---

# Архитектура проекта

```text
Analytics-Automation-Workspace/

├── app/
│   ├── connectors/
│   │   ├── excel_connector.py
│   │   ├── file_connector.py
│   │   └── google_sheets_connector.py
│   │
│   ├── core/
│   │   ├── config_loader.py
│   │   ├── exceptions.py
│   │   ├── logger.py
│   │   ├── pipeline.py
│   │   └── startup.py
│   │
│   ├── reports/
│   │   └── btag_report/
│   │       ├── calculator.py
│   │       ├── formatter.py
│   │       ├── processor.py
│   │       └── validator.py
│   │
│   └── services/
│       ├── geo_detector.py
│       └── google_sheet_archive.py
│
├── configs/
│   ├── geos.yaml
│   ├── projects.yaml
│   ├── reports.yaml
│   ├── settings.yaml
│   └── sheets.yaml
│
├── data/
│   ├── incoming/
│   │   └── btag/
│   ├── processed/
│   └── archive/
│
├── credentials/
├── logs/
├── output/

├── main.py
└── requirements.txt
Текущий отчет
BTAG Report

Текущая реализация:

Проект: 1xBet
Отчет: BTAG

Поддерживаемые GEO:

Bolivia
Mexico
Guatemala
Jamaica
Процесс обработки
Берется последний Excel-файл из:
data/incoming/btag
Определяется GEO по столбцу:
Страна

Поддерживаются:

русский язык;
английский язык.
Выбирается соответствующая Google Sheets таблица.
Данные загружаются в рабочий лист:
Sheet1
После пересчета формул создаются архивы:
Отчет_YYYY-MM-DD
Методы_YYYY-MM-DD
Конфигурация

Все настройки находятся в:

configs/

Основные файлы:

geos.yaml

Список поддерживаемых GEO.

projects.yaml

Список проектов.

sheets.yaml

Google Sheets ID и настройки отчетов.

settings.yaml

Общие настройки проекта.

Установка

Создание виртуального окружения:

python -m venv venv

Активация:

Mac:

source venv/bin/activate

Установка зависимостей:

python -m pip install -r requirements.txt
Запуск

После активации окружения:

python main.py
Добавление нового GEO
Добавить GEO в:
configs/geos.yaml
Добавить соответствия:
app/services/geo_detector.py
Добавить Google Sheets ID:
configs/sheets.yaml
Добавление нового отчета

Новый отчет создается отдельно:

app/reports/

Каждый отчет содержит собственную бизнес-логику:

processor.py — обработка данных;
validator.py — проверки;
calculator.py — расчеты;
formatter.py — форматирование.
Git workflow

Проверка изменений:

git status

Добавление изменений:

git add .

Создание версии:

git commit -m "Описание изменений"

Отправка на GitHub:

git push
Безопасность

Файлы с доступами не должны попадать в GitHub:

credentials/

Также исключаются:

venv/
logs/
output/
data/incoming/
План развития

Следующие этапы:

автоматическая обработка нескольких отчетов;
единый pipeline для всех отчетов;
автоматическое перемещение обработанных файлов;
расширение поддержки новых проектов;
автоматизация дополнительных аналитических отчетов.