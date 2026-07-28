# Analytics Automation Workspace

## Описание проекта

Analytics Automation Workspace — система автоматизации аналитических отчетов.

Основная задача проекта:

- автоматическая обработка входящих Excel-файлов;
- определение GEO;
- загрузка данных в Google Sheets;
- запуск пересчета формул;
- создание архивных копий отчетов;
- масштабирование под новые отчеты и проекты.

Архитектура построена по принципу разделения:

- общая инфраструктура находится в `app/`;
- каждый отчет имеет собственную бизнес-логику в `app/reports/`;
- `main.py` используется только как точка запуска.


---

# Архитектура проекта


Analytics-Automation-Workspace/

├── app/
│
│ ├── connectors/
│ │ ├── excel_connector.py
│ │ ├── file_connector.py
│ │ └── google_sheets_connector.py
│ │
│ ├── core/
│ │ ├── config_loader.py
│ │ ├── exceptions.py
│ │ ├── logger.py
│ │ └── pipeline.py
│ │
│ ├── reports/
│ │
│ │ ├── btag_report/
│ │ │ └── report.py
│ │
│ │ └── future_reports/
│ │
│ └── services/
│   ├── geo_detector.py
│   └── google_sheet_archive.py
│
├── configs/
│ ├── settings.yaml
│ ├── sheets.yaml
│ ├── geos.yaml
│ └── projects.yaml
│
├── data/
│ ├── incoming/
│ │ └── btag/
│ ├── processed/
│ └── archive/
│
├── credentials/
│
├── logs/
├── output/
│
├── main.py
└── requirements.txt


---

# Архитектура отчетов


Каждый отчет имеет собственный модуль:


app/reports/


Пример:

btag_report/

└── report.py


В будущем:


payments_report/

└── report.py


affiliate_report/

└── report.py



Каждый отчет отвечает только за свою бизнес-логику.

Общие функции:

- работа с файлами;
- Google Sheets;
- конфигурация;
- GEO;

остаются в общих модулях.


---

# Текущий отчет

## BTAG Report


Реализован:

- Проект: 1xBet
- Отчет: BTAG
- GEO:

  - Bolivia
  - Mexico
  - Guatemala
  - Jamaica


Процесс:


1. Система получает Excel-файлы из:


data/incoming/btag


2. Для каждого файла:

- загружает данные;
- определяет страну;
- определяет GEO;
- выбирает соответствующий Google Sheet.


3. Данные загружаются:


Google Sheets → Sheet1


4. После пересчета формул создаются архивы:


Отчет_YYYY-MM-DD

Методы_YYYY-MM-DD


---

# Запуск проекта


Активация окружения:


```bash
source venv/bin/activate

Запуск:

python main.py
Добавление нового GEO

Для добавления GEO:

Добавить GEO в конфигурацию:
configs/geos.yaml
Добавить Google Sheet:
configs/sheets.yaml
Проверить определение GEO:
app/services/geo_detector.py
Добавление нового отчета

Новый отчет создается отдельно:

app/reports/new_report/

Например:

app/reports/payments_report/report.py

Логика одного отчета не должна находиться в:

main.py

main.py отвечает только за запуск.

Git workflow

Проверить изменения:

git status

Добавить:

git add .

Создать версию:

git commit -m "Описание изменений"

Отправить:

git push
Безопасность

Не добавляются в GitHub:

credentials/
venv/
logs/
output/
data/incoming/

Следующие этапы развития: перенос расчетов из Google Sheets в Python;
добавление calculator.py для бизнес-формул;
добавление validator.py для проверок;
добавление formatter.py для подготовки отчетов;
единый pipeline для всех отчетов;
автоматическая обработка нескольких проектов.