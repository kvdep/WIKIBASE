import os
import sys
import copy
import asyncio
from pathlib import Path
import nbformat
from nbclient import NotebookClient

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

project_dir = Path(r"C:\Users\jack_\MAIN\ВУЗ\СемТех Блохин\КР")
os.chdir(project_dir)

def load_nb(rel_path):
    with open(project_dir / rel_path, "r", encoding="utf-8") as f:
        return nbformat.read(f, as_version=4)

print("Загрузка исходных ноутбуков из папки Резы...")
nb1 = load_nb("Резы/задание_1.ipynb")
nb2 = load_nb("Резы/задание_2.ipynb")
nb34 = load_nb("Резы/задания_3-4.ipynb")
nb56 = load_nb("Резы/задания_5-6.ipynb")

combined_nb = nbformat.v4.new_notebook()
combined_nb.metadata = copy.deepcopy(nb56.metadata)

new_cells = []

# Титульный блок
title_cell = nbformat.v4.new_markdown_cell(
"""# Контрольная работа №1: База знаний экосистемы библиотек PyTorch
## Проектирование онтологии, построение графа знаний, текстовый корпус, SHACL-валидация и вывод OWL 2 RL

**Дисциплина:** Семантические технологии  
**Предметная область:** Открытые Python-библиотеки глубокого обучения экосистемы PyTorch (52 сущности класса `wd:Q29642950`, связанные через `wdt:P1547` с `wd:Q47509047` и обладающие репозиторием `wdt:P1324`).

### Содержание отчета:
1. **Глава 1. Выбор и верификация предметной области (Задание 1)**
   - 1.0. Выгрузка данных из Wikidata SPARQL endpoint
   - 1.1. Свойства домена
   - 1.2. Проверка домена по критериям контрольной работы
   - 1.3. Обязательная статистика домена
2. **Глава 2. Формулировка 12 вопросов к базе знаний (Задание 2)**
   - 2.1. Инициализация графа знаний и текстового корпуса
   - 2.2. Вопросы к графу знаний (Вопросы 1–6)
   - 2.3. Вопросы к текстовому корпусу (Вопросы 7–10)
   - 2.4. Комбинированные вопросы (Вопросы 11–12)
3. **Глава 3. Разработка онтологии предметной области в Protégé (Задание 3)**
   - 3.1. Моделирование онтологии и архитектура классов
   - 3.2. Верификация сборки онтологии `ontology.ttl`
4. **Глава 4. Построение, статистика и верификация графа знаний (Задание 4)**
   - 4.1. Сборка и верификация графа знаний `knowledge_graph.ttl`
   - 4.2. Верификация наличия `owl:sameAs` для сущностей домена
   - 4.3. Статистика графа знаний: тройки, сущности, разбивка по классам и свойствам
   - 4.4. Верификация графа знаний целевыми SPARQL-запросами
   - 4.5. Итоги выполнения заданий 3 и 4
5. **Глава 5. Сбор текстовой информации по сущностям (Задание 5)**
   - 5.1. Источники и структура текстового корпуса
   - 5.2. Источник текстовой информации для каждой сущности
6. **Глава 6. Проверка данных (SHACL) и логический вывод (OWL 2 RL) (Задание 6)**
   - 6.1. Ограничения целостности SHACL
   - 6.2. Результат pyshacl на исходных данных
   - 6.3. Контрольный эксперимент: выявление пяти типов нарушений
   - 6.4. Решения по каждому типу нарушения и повторная проверка
   - 6.5. Дедуктивный логический вывод OWL 2 RL
   - 6.6. Анализ добавленных троек и механизмов вывода
   - 6.7. Итоговые проверки выполнения заданий 5 и 6
7. **Глава 7. Сводная таблица итоговых показателей проекта**
"""
)
new_cells.append(title_cell)

# Блок инициализации путей
setup_code = nbformat.v4.new_code_cell(
"""# Инициализация рабочей среды и привязка к корневой директории проекта
import os
import sys
from pathlib import Path

# Поиск корневой директории проекта с графом знаний и онтологией
project = next(
    p for p in [Path.cwd(), *Path.cwd().parents]
    if (p / 'knowledge_graph.ttl').is_file() and (p / 'data/corpus.jsonl').is_file()
)
os.chdir(project)
print(f"Корень проекта: {project.resolve()}")
assert (project / 'knowledge_graph.ttl').is_file(), "Файл knowledge_graph.ttl не найден!"
assert (project / 'ontology.ttl').is_file(), "Файл ontology.ttl не найден!"
assert (project / 'shapes.shacl.ttl').is_file(), "Файл shapes.shacl.ttl не найден!"
"""
)
new_cells.append(setup_code)

# =========================================================================
# ГЛАВА 1 (Задание 1)
# =========================================================================
for i, cell in enumerate(nb1.cells):
    c = copy.deepcopy(cell)
    c.outputs = []
    c.execution_count = None
    if c.cell_type == 'markdown':
        src = c.source
        if i == 0:
            c.source = "# Глава 1. Выбор и верификация предметной области (Задание 1)\n\n## 1.0. Скачивание и обработка\n\nВыгрузка данных из Wikidata SPARQL endpoint для открытых библиотек Python экосистемы PyTorch и их локальное сохранение."
        elif src.startswith("# 1. Свойства домена"):
            c.source = "## 1.1. Свойства домена"
        elif src.startswith("## 1.1. Все свойства"):
            c.source = "### 1.1.1. Все свойства всех сущностей домена"
        elif src.startswith("## 1.2. Распределение"):
            c.source = "### 1.1.2. Распределение сущностей по числу свойств"
        elif src.startswith("## 1.3. Сущности с экстремальным"):
            c.source = "### 1.1.3. Сущности с экстремальным числом свойств (минимум и максимум)"
        elif src.startswith("## 1.4. Полный список"):
            c.source = "### 1.1.4. Полный список всех сущностей, ранжированных по количеству свойств"
        elif src.startswith("# 2. Проверка домена"):
            c.source = "## 1.2. Проверка домена по критериям контрольной работы\n\n" + "\n".join(src.splitlines()[1:])
        elif src.startswith("## 2.1. домен содержит"):
            c.source = "### 1.2.1. Домен содержит 30–60 сущностей одного основного класса в Wikidata"
        elif src.startswith("## 2.2. заполнены хотя бы"):
            c.source = "### 1.2.2. Заполнены хотя бы 5 свойств"
        elif src.startswith("### 2.2.1. Есть даты"):
            c.source = "#### 1.2.2.1. Наличие дат"
        elif src.startswith("### 2.2.2. Есть числа"):
            c.source = "#### 1.2.2.2. Наличие чисел"
        elif src.startswith("## 2.3. Свойство с квалификатором"):
            c.source = "### 1.2.3. Свойство с квалификатором времени"
        elif src.startswith("## 2.4. Текстовые описания"):
            c.source = "### 1.2.4. Текстовые описания"
        elif src.startswith("# 3. Обязательная статистика"):
            c.source = "## 1.3. Обязательная статистика домена\n\n" + "\n".join(src.splitlines()[1:])
        elif src.startswith("## 3.1. статистика по основным"):
            c.source = "### 1.3.1. Статистика по основным свойствам"
        elif src.startswith("## 3.2. набор свойств"):
            c.source = "### 1.3.2. Набор свойств, имеющих квалификатор времени"
        elif src.startswith("## 3.3. ссылка на источник"):
            c.source = "### 1.3.3. Ссылки на источники текстовой информации"
    new_cells.append(c)

# =========================================================================
# ГЛАВА 2 (Задание 2)
# =========================================================================
for i, cell in enumerate(nb2.cells):
    c = copy.deepcopy(cell)
    c.outputs = []
    c.execution_count = None
    if c.cell_type == 'markdown':
        src = c.source
        if i == 0:
            c.source = "# Глава 2. Формулировка 12 вопросов к базе знаний (Задание 2)\n\n" + "\n".join(src.splitlines()[1:])
    elif c.cell_type == 'code':
        if i == 1:
            c.source = c.source.replace('project = Path("..")', 'project = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "knowledge_graph.ttl").is_file() and (p / "data/corpus.jsonl").is_file())')
    new_cells.append(c)

# =========================================================================
# ГЛАВА 3 и ГЛАВА 4 (Задания 3 и 4)
# =========================================================================
c_imports_34 = copy.deepcopy(nb34.cells[1])
c_imports_34.outputs = []
c_imports_34.execution_count = None

c_ch3_md = copy.deepcopy(nb34.cells[2])
c_ch3_md.source = "# Глава 3. Разработка онтологии предметной области в Protégé (Задание 3)\n\n" + c_ch3_md.source

c_ch3_code = copy.deepcopy(nb34.cells[3])
c_ch3_code.outputs = []
c_ch3_code.execution_count = None

new_cells.append(c_ch3_md)
new_cells.append(c_imports_34)
new_cells.append(c_ch3_code)

c_ch4_md = copy.deepcopy(nb34.cells[4])
c_ch4_md.source = "# Глава 4. Построение, статистика и верификация графа знаний (Задание 4)\n\n" + c_ch4_md.source
new_cells.append(c_ch4_md)

for i in range(5, len(nb34.cells)):
    c = copy.deepcopy(nb34.cells[i])
    c.outputs = []
    c.execution_count = None
    if c.cell_type == 'markdown':
        src = c.source
        if src.startswith("### 4.1."):
            c.source = "## 4.1. Верификация наличия `owl:sameAs` для сущностей домена\n\n" + "\n".join(src.splitlines()[1:])
        elif src.startswith("### 4.2."):
            c.source = "## 4.2. Статистика графа знаний: тройки, сущности, разбивка по классам и свойствам\n\n" + "\n".join(src.splitlines()[1:])
        elif src.startswith("### 4.3."):
            c.source = "## 4.3. Верификация графа знаний целевыми SPARQL-запросами\n\n" + "\n".join(src.splitlines()[1:])
        elif src.startswith("## Итоги выполнения заданий 3 и 4"):
            c.source = "## 4.4. Итоги выполнения заданий 3 и 4\n\n" + "\n".join(src.splitlines()[1:])
    new_cells.append(c)

# =========================================================================
# ГЛАВА 5 (Задание 5)
# =========================================================================
c_env_code = copy.deepcopy(nb56.cells[1])
c_env_code.outputs = []
c_env_code.execution_count = None

c_ch5_md = copy.deepcopy(nb56.cells[2])
c_ch5_md.source = "# Глава 5. Сбор текстовой информации по сущностям (Задание 5)\n\n" + c_ch5_md.source.replace("## Задание 5. Сбор текстовой информации по сущностям", "")

c_corpus_code = copy.deepcopy(nb56.cells[3])
c_corpus_code.outputs = []
c_corpus_code.execution_count = None

c_src_md = copy.deepcopy(nb56.cells[4])
c_src_code = copy.deepcopy(nb56.cells[5])
c_src_code.outputs = []
c_src_code.execution_count = None

new_cells.append(c_ch5_md)
new_cells.append(c_env_code)
new_cells.append(c_corpus_code)
new_cells.append(c_src_md)
new_cells.append(c_src_code)

# =========================================================================
# ГЛАВА 6 (Задание 6)
# =========================================================================
c_ch6_md = copy.deepcopy(nb56.cells[6])
c_ch6_md.source = "# Глава 6. Проверка данных (SHACL) и логический вывод (OWL 2 RL) (Задание 6)\n\n" + c_ch6_md.source.replace("## Задание 6. Проверка данных и логический вывод", "")
new_cells.append(c_ch6_md)

for i in range(7, len(nb56.cells)):
    c = copy.deepcopy(nb56.cells[i])
    c.outputs = []
    c.execution_count = None
    if c.cell_type == 'markdown':
        src = c.source
        if src.startswith("### 6.2."):
            c.source = "## 6.2. Результат pyshacl на исходных данных\n\n" + "\n".join(src.splitlines()[1:])
        elif src.startswith("### 6.3."):
            c.source = "## 6.3. Контрольный эксперимент: выявление пяти типов нарушений\n\n" + "\n".join(src.splitlines()[1:])
        elif src.startswith("### 6.4."):
            c.source = "## 6.4. Решения по каждому типу нарушения и повторная проверка\n\n" + "\n".join(src.splitlines()[1:])
        elif src.startswith("### 6.5."):
            c.source = "## 6.5. Дедуктивный логический вывод OWL 2 RL\n\n" + "\n".join(src.splitlines()[1:])
        elif src.startswith("### 6.6."):
            c.source = "## 6.6. Анализ добавленных троек и механизмов вывода\n\n" + "\n".join(src.splitlines()[1:])
        elif src.startswith("## Итоги выполнения заданий 5 и 6"):
            c.source = "## 6.7. Итоги выполнения заданий 5 и 6\n\n" + "\n".join(src.splitlines()[1:])
    new_cells.append(c)

# =========================================================================
# ГЛАВА 7: Итоговая сводка
# =========================================================================
summary_cell = nbformat.v4.new_markdown_cell(
"""# Глава 7. Сводная таблица итоговых показателей проекта

В таблице ниже сведены ключевые количественные и качественные характеристики созданной базы знаний экосистемы PyTorch по всем разделам контрольной работы.

| Раздел / Компонент | Метрика / Критерий | Значение | Статус проверки |
| :--- | :--- | :--- | :--- |
| **Домен (Задание 1)** | Число библиотек выборки | **52** (в диапазоне 30–60) | Выполнено |
| | Основной класс Wikidata | `wd:Q29642950` (Python library) | Выполнено |
| | Связь с экосистемой | `wdt:P1547 wd:Q47509047` (PyTorch) | Выполнено |
| | Сущностей с $\\ge 5$ свойствами | **52 (100%)** | Выполнено |
| | Свойство с квалификатором даты | `P348` (версия), квалификатор `pq:P577` (дата) | Выполнено |
| **Вопросы (Задание 2)** | Вопросы к графу (SPARQL) | **6 вопросов** (фильтры, агрегация, сортировка, пути) | Проверено |
| | Вопросы к текстовому корпусу | **4 вопроса** (цитаты и источники из README) | Проверено |
| | Комбинированные вопросы | **2 вопроса** (граф $\\to$ сущность $\\to$ текст) | Проверено |
| **Онтология (Задание 3)** | Классы онтологии | **10 классов** (иерархия библиотек, лицензии, релизы) | Выполнено |
| | Свойства онтологии | **13 свойств** (6 Object Properties, 7 Datatype Properties) | Выполнено |
| | Число троек онтологии | **155 троек** (`ontology.ttl`) | Выполнено |
| **Граф знаний (Задание 4)**| Общее количество троек | **9 302 тройки** (`knowledge_graph.ttl`) | Выполнено |
| | Уникальные субъекты | **1 834 субъекта** | Выполнено |
| | Записи о версиях релизов | **1 719 записей** | Выполнено |
| | Связи тождества `owl:sameAs` | **57 связей** (52 библиотеки + PyTorch + 4 лицензии) | Выполнено |
| **Корпус (Задание 5)** | Число документов | **52 документа** (100% охват выборки) | Выполнено |
| | Источник описаний | Официальные `README.md` с GitHub (Raw URL) | Выполнено |
| | Контрольные суммы текстов | SHA-256 проверены на совпадение | Выполнено |
| **Валидация SHACL (Задание 6)** | Ограничения в `shapes.shacl.ttl` | **7 ограничений** (5 типов: кардинальность, класс, тип, шаблон, диапазон) | Выполнено |
| | Валидация исходного графа | `Conforms: True` (0 нарушений) | Выполнено |
| | Контрольный эксперимент | 5 нарушений искусственно внесены, зафиксированы и исправлены | Выполнено |
| **Логический вывод (Задание 6)**| Исходный объединённый граф | **9 457 троек** (9 302 граф + 155 онтология) | Выполнено |
| | Граф после вывода OWL 2 RL | **22 381 тройка** | Выполнено |
| | Выведено новых троек | **+12 924 тройки** | Выполнено |
"""
)
new_cells.append(summary_cell)

combined_nb.cells = new_cells
print(f"Всего подготовлено ячеек: {len(combined_nb.cells)}")

# Выполнение ноутбука
print("Начало сквозного выполнения всех ячеек в ядре Python...")
client = NotebookClient(
    combined_nb,
    timeout=600,
    kernel_name="python3",
    resources={"metadata": {"path": str(project_dir)}},
)
client.execute()
print("Все ячейки успешно выполнены!")

# Проверка на наличие ошибок в ячейках
error_count = 0
for idx, c in enumerate(combined_nb.cells):
    if c.cell_type == 'code':
        for out in c.outputs:
            if out.output_type == 'error':
                error_count += 1
                print(f"Ошибка в ячейке {idx}: {out.ename}: {out.evalue}")

if error_count == 0:
    print("Проверка пройдена: 0 ошибок выполнения!")
else:
    print(f"Внимание: обнаружено {error_count} ошибок!")
    sys.exit(1)

# Сохранение в корень и в Резы
out_root = project_dir / "Отчет.ipynb"
with open(out_root, "w", encoding="utf-8") as f:
    nbformat.write(combined_nb, f)
print(f"Итоговый выполненный отчет сохранен: {out_root}")

out_rezy = project_dir / "Резы" / "Отчет.ipynb"
with open(out_rezy, "w", encoding="utf-8") as f:
    nbformat.write(combined_nb, f)
print(f"Копия отчета сохранена в: {out_rezy}")
