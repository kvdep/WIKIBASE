# Проект по дисциплине «Семантические технологии»
## Контрольная работа №1: База знаний экосистемы библиотек PyTorch

Данный репозиторий содержит материалы выполнения Контрольной работы №1 по проектированию онтологии и базы знаний для предметной области **библиотек глубокого обучения экосистемы PyTorch**.

---

### Структура репозитория

```
├── ontology.ttl                      # Доменная онтология в формате OWL/Turtle
├── knowledge_graph.ttl               # Граф знаний (52 библиотеки + версии + owl:sameAs) в формате Turtle
├── shapes.shacl.ttl                  # Ограничения целостности SHACL (cardinality, class, datatype, pattern)
├── Отчет_Контрольная_работа_1.docx   # Итоговый отчет со всеми разделами и 12 вопросами
├── Сравнение_доменов_Wikidata.xlsx   # Сравнительная таблица доменов с листом 52 библиотек PyTorch
├── data/
│   ├── corpus.jsonl                  # Текстовый корпус по 52 библиотекам (извлечен из README.md на GitHub)
│   ├── libraries_metadata.json       # Метаданные библиотек, выгруженные из Wikidata
│   ├── shacl_validation_report.txt   # Протокол валидации PySHACL
│   └── owlrl_reasoning_summary.txt   # Протокол дедуктивного вывода OWL 2 RL
└── scripts/
    ├── 01_fetch_data_and_corpus.py   # Выгрузка из Wikidata и скачивание README с GitHub
    ├── 02_build_ontology_and_graph.py# Построение ontology.ttl и knowledge_graph.ttl
    ├── 03_validate_shacl_and_infer_owlrl.py # Валидация SHACL и логический вывод owlrl
    ├── 04_test_sparql_questions.py   # Выполнение 6 графовых SPARQL-запросов к графу
    └── 05_generate_docx_report.py    # Автоматическая сборка отчета в формате DOCX
```

---

### 1. Предметная область (Домен)
* **Класс в Wikidata**: `wd:Q29642950` (Python-библиотека).
* **Связь с PyTorch**: `wdt:P1547 wd:Q47509047` (зависит от PyTorch).
* **Фильтр открытого кода**: наличие репозитория `wdt:P1324 ?repo`.
* **Объем выборки**: ровно **52 библиотеки** (удовлетворяет требованию $30 \le N \le 60$).
* **Ключевые библиотеки**: `torchvision`, `torchaudio`, `torchtext`, `PyTorch Lightning`, `accelerate`, `kornia`, `timm`, `pyro-ppl`, `captum`, `fastai`, `gpytorch`, `botorch`, `flair`, `allennlp` и др.
* **Квалификаторы времени**: 1 779 утверждений о версиях содержат квалификатор даты публикации `pq:P577`.

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
* **Общее число триплетов**: 9 223.
* **Число уникальных субъектов**: 1 819.
* У каждого индивида проставлен `owl:sameAs` на URI в Wikidata (`http://www.wikidata.org/entity/Q...`).
* Зафиксировано 1 706 релизов версий с датами выхода.

---

### 4. Проверка (PySHACL) и вывод (OWL 2 RL)
* **SHACL (`shapes.shacl.ttl`)**: проверены 4 типа ограничений (кардинальность `sh:minCount`/`sh:maxCount`, класс значения `sh:class`, тип данных `sh:datatype`, регулярное выражение `sh:pattern`). Выявленные пропуски лицензий исправлены.
* **OWL 2 RL (`owlrl`)**:
  * Исходно: 9 378 триплетов.
  * После логического вывода: 22 201 триплет (+12 823 выведенных факта транзитивности подклассов, наследования свойств и эквивалентности).

---

### 5. Запуск скриптов

Установка зависимостей:
```bash
pip install rdflib pyshacl owlrl python-docx openpyxl requests
```

Последовательное воспроизведение результатов:
```bash
python scripts/01_fetch_data_and_corpus.py
python scripts/02_build_ontology_and_graph.py
python scripts/03_validate_shacl_and_infer_owlrl.py
python scripts/04_test_sparql_questions.py
python scripts/05_generate_docx_report.py
```
