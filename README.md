# Проект по дисциплине «Семантические технологии»
## Контрольная работа №1: База знаний экосистемы библиотек PyTorch

Данный репозиторий содержит материалы выполнения Контрольной работы №1 по проектированию онтологии и базы знаний для предметной области **библиотек глубокого обучения экосистемы PyTorch**.

---

### Структура репозитория

```
├── ontology.ttl                      # Доменная онтология в формате OWL/Turtle
├── knowledge_graph.ttl               # Граф знаний (52 библиотеки, PyTorch и релизы) в формате Turtle
├── shapes.shacl.ttl                  # Ограничения целостности SHACL
├── Сравнение_доменов_Wikidata.xlsx   # Сравнительная таблица доменов с листом 52 библиотек PyTorch
├── Резы/
│   ├── задание_1.ipynb               # Ноутбук с верификацией всех пунктов Задания 1
│   ├── задание_2.ipynb               # 12 вопросов к графу и текстовому корпусу с проверкой ответов
 │   ├── задания_3-4.ipynb             # Матрица вопросов и проверка сборки онтологии и графа
│   ├── Отчёт_задание_2.docx          # Отдельный отчёт по заданию 2
│   └── Отчет_Контрольная_работа_1.docx # Итоговый отчет со всеми разделами и 12 вопросами
├── data/
│   ├── corpus.jsonl                  # Текстовый корпус по 52 библиотекам (извлечен из README.md на GitHub)
│   ├── libraries_metadata.json       # Метаданные библиотек, выгруженные из Wikidata
│   ├── task1_entities.json           # Список 52 сущностей с QID, названиями и репозиториями
│   ├── shacl_validation_report.txt   # Протокол валидации PySHACL
│   └── owlrl_reasoning_summary.txt   # Протокол дедуктивного вывода OWL 2 RL
└── scripts/
    ├── 01_fetch_data_and_corpus.py   # Выгрузка из Wikidata и скачивание README с GitHub
    ├── 02_build_ontology_and_graph.py# Построение ontology.ttl и knowledge_graph.ttl
    ├── 03_validate_shacl_and_infer_owlrl.py # Валидация SHACL и логический вывод owlrl
    ├── 04_test_sparql_questions.py   # Выполнение 6 графовых SPARQL-запросов к графу
    └── 05_generate_docx_report.py    # Автоматическая сборка отчета в формате DOCX
```

- [Ноутбук задания 2](Резы/задание_2.ipynb)
- [Ноутбук заданий 3–4](Резы/задания_3-4.ipynb)
- [Ноутбук заданий 5–6](Резы/задания_5-6.ipynb) — сборка корпуса из сохранённых README, пять видов ограничений SHACL и полный список троек, добавленных OWL 2 RL. Результаты сохраняются в `data/tasks_5_6/`.
- [Отдельный отчёт по заданию 2](Резы/Отчёт_задание_2.docx)
- [Общий отчёт по контрольной работе №1](Резы/Отчет_Контрольная_работа_1.docx)

---

### 1. Предметная область (Домен)
* **Класс в Wikidata**: `wd:Q29642950` (Python-библиотека).
* **Связь с PyTorch**: `wdt:P1547 wd:Q47509047` (зависит от PyTorch).
* **Фильтр открытого кода**: наличие репозитория `wdt:P1324 ?repo`.
* **Объем выборки**: ровно **52 библиотеки** (удовлетворяет требованию $30 \le N \le 60$).
* **Ключевые библиотеки**: `torchvision`, `torchaudio`, `torchtext`, `PyTorch Lightning`, `accelerate`, `kornia`, `timm`, `pyro-ppl`, `captum`, `fastai`, `gpytorch`, `botorch`, `flair`, `allennlp` и др.
* Даты публикации версий получены из квалификатора Wikidata `pq:P577`.

---

### 2. Онтология (`ontology.ttl`)
* **Пространство имен**: `http://example.org/pytorch-ecosystem#` (префикс `pte:`).
* **Классы (10)**:
  * `pte:SoftwareLibrary`
    * `pte:MachineLearningLibrary`
      * `pte:ComputerVisionLibrary`
      * `pte:NaturalLanguageProcessingLibrary`
      * `pte:AudioProcessingLibrary`
      * `pte:ProbabilisticAndGraphLibrary`
      * `pte:OptimizationAndTrainingLibrary`
  * `pte:SoftwareLicense`
  * `pte:SoftwareVersion`
  * `pte:Repository`
* **Свойства**:
  * **Object Properties**: `dependsOnSoftware`, `hasLicense`, `hasPrimaryLicense` (Functional), `hasRepository`, `hasSourceCodeRepository` (Functional), `hasVersion`.
  * **Datatype Properties**: `libraryName`, `versionIdentifier`, `releaseDate` (xsd:dateTime), `versionType`, `repositoryURL` (xsd:anyURI), `licenseName`, `versionCount` (xsd:integer).
* **Эквивалентность Wikidata**:
  * `pte:SoftwareLibrary owl:equivalentClass wd:Q188860`
  * `pte:MachineLearningLibrary owl:equivalentClass wd:Q21169670`
  * `pte:SoftwareLicense owl:equivalentClass wd:Q207621`
  * `pte:SoftwareVersion owl:equivalentClass wd:Q341`
  * `pte:hasRepository owl:equivalentProperty wdt:P1324`
  * `pte:hasLicense owl:equivalentProperty wdt:P275`
  * `pte:dependsOnSoftware owl:equivalentProperty wdt:P1547`

---

### 3. Граф знаний (`knowledge_graph.ttl`)
* В графе 9 302 триплета и 1 834 уникальных субъекта.
* Все 52 библиотеки выборки, PyTorch и четыре лицензии связаны с соответствующими сущностями Wikidata через `owl:sameAs`.
* В графе 1 719 записей о релизах с датами публикации и 53 узла репозиториев с 52 уникальными URL.

---

### 4. Проверка (PySHACL) и вывод (OWL 2 RL)
* **Валидация SHACL (`shapes.shacl.ttl`)** завершилась с результатом `Conforms: True` и 0 нарушений. Проверены кардинальность (`sh:minCount` и `sh:maxCount`), класс значения (`sh:class`), тип данных (`sh:datatype`), нижняя граница (`sh:minInclusive`) и шаблон URL (`sh:pattern`).
* **Вывод OWL 2 RL (`owlrl`)** расширил объединённый граф онтологии и данных с 9 457 до 22 381 триплета, добавив 12 924 триплета.

---

### 5. Запуск скриптов

Установка зависимостей:
```bash
pip install rdflib pyshacl owlrl python-docx openpyxl requests
```

Чтобы воспроизвести сохранённый снимок, выполните команды из корня репозитория.

```bash
python scripts/02_build_ontology_and_graph.py
python scripts/03_validate_shacl_and_infer_owlrl.py
python scripts/04_test_sparql_questions.py
python scripts/05_generate_docx_report.py
```

Скрипты используют сохранённые данные из `data/` и отдельный отчёт по заданию 2. Скрипт `04` выполняет шесть графовых запросов из ноутбука, а скрипт `05` записывает `Отчет_Контрольная_работа_1.docx` в корень репозитория.

Для обновления исходных данных из Wikidata и GitHub отдельно запустите `python scripts/01_fetch_data_and_corpus.py`. Эта команда перезаписывает `data/libraries_metadata.json` и `data/corpus.jsonl`, поэтому результаты могут измениться.
