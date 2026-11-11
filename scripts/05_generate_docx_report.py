from collections import Counter
from copy import deepcopy
from pathlib import Path

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.opc.constants import RELATIONSHIP_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph
from rdflib import Graph, Namespace, RDF
import json
import os

doc = docx.Document()

# Page setup: standard A4 with 2cm margins
for section in doc.sections:
    section.top_margin = Inches(0.8)
    section.bottom_margin = Inches(0.8)
    section.left_margin = Inches(0.8)
    section.right_margin = Inches(0.8)

# Color Palette
COLOR_PRIMARY = RGBColor(31, 78, 120)    # Deep Navy Blue
COLOR_SECONDARY = RGBColor(89, 89, 89)   # Slate Gray
COLOR_TEXT = RGBColor(38, 38, 38)        # Charcoal
COLOR_MUTED = RGBColor(115, 115, 115)    # Muted Gray

# Set Normal Style
style_normal = doc.styles['Normal']
style_normal.font.name = 'Calibri'
style_normal.font.size = Pt(11)
style_normal.font.color.rgb = COLOR_TEXT
style_normal.paragraph_format.line_spacing = 1.15
style_normal.paragraph_format.space_after = Pt(4)

def set_cell_background(cell, color_hex):
    tcPr = cell._element.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), color_hex)
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def add_header(text, level=1):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.name = 'Calibri'
    run.bold = True
    if level == 1:
        run.font.size = Pt(16)
        run.font.color.rgb = COLOR_PRIMARY
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
    elif level == 2:
        run.font.size = Pt(13)
        run.font.color.rgb = COLOR_PRIMARY
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
    elif level == 3:
        run.font.size = Pt(11.5)
        run.font.color.rgb = COLOR_SECONDARY
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(2)
    return p

def add_code_block(code_text):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "F2F4F7")
    set_cell_margins(cell, top=120, bottom=120, left=180, right=180)
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.05
    run = p.add_run(code_text.strip())
    run.font.name = 'Consolas'
    run.font.size = Pt(9.5)
    run.font.color.rgb = RGBColor(40, 40, 40)
    doc.add_paragraph() # spacing

# --- Title Section ---
title_p = doc.add_paragraph()
title_p.paragraph_format.space_before = Pt(0)
title_p.paragraph_format.space_after = Pt(2)
r_title = title_p.add_run("ОТЧЕТ ПО КОНТРОЛЬНОЙ РАБОТЕ №1")
r_title.bold = True
r_title.font.size = Pt(20)
r_title.font.color.rgb = COLOR_PRIMARY

sub_p = doc.add_paragraph()
sub_p.paragraph_format.space_after = Pt(14)
r_sub = sub_p.add_run("Дисциплина: Семантические технологии\nТема: Проектирование базы знаний и онтологии экосистемы библиотек PyTorch")
r_sub.font.size = Pt(12)
r_sub.font.color.rgb = COLOR_SECONDARY

# Group Info Table
tbl_info = doc.add_table(rows=3, cols=2)
tbl_info.alignment = WD_TABLE_ALIGNMENT.LEFT
fields = [
    ("Предметная область:", "Библиотеки экосистемы PyTorch (Deep Learning)"),
    ("Число сущностей в домене:", "52 сущности (основной класс wd:Q29642950, свойство wdt:P1547 wd:Q47509047)"),
    ("Репозиторий проекта:", "https://github.com/kvdep/WIKIBASE")
]
for idx, (label, val) in enumerate(fields):
    r = tbl_info.rows[idx]
    c1, c2 = r.cells[0], r.cells[1]
    c1.width = Inches(2.2)
    c2.width = Inches(4.8)
    set_cell_background(c1, "F2F4F7")
    set_cell_margins(c1, top=60, bottom=60, left=100, right=100)
    set_cell_margins(c2, top=60, bottom=60, left=100, right=100)
    p1 = c1.paragraphs[0]
    p1.paragraph_format.space_after = Pt(0)
    run1 = p1.add_run(label)
    run1.bold = True
    p2 = c2.paragraphs[0]
    p2.paragraph_format.space_after = Pt(0)
    p2.add_run(val)

doc.add_paragraph()

# ==========================================
# ЗАДАНИЕ 1
# ==========================================
add_header("Задание 1. Выбор и верификация предметной области (домена)")

doc.add_paragraph(
    "В качестве предметной области выбраны библиотеки машинного обучения экосистемы PyTorch с открытым исходным кодом. "
    "В Wikidata сам PyTorch (wd:Q47509047) является единичным программным пакетом (индивидом). Библиотеки глубокого обучения, "
    "созданные на базе PyTorch и зависящие от него (отношение wdt:P1547), представляют собой совокупность из 52 сущностей, "
    "принадлежащих строго единому основному классу «Python-библиотека» (wd:Q29642950) и имеющих репозиторий на GitHub (wdt:P1324)."
)

add_header("Проверка домена по требованиям задания", level=2)
reqs_doc = [
    ("Диапазон объема", "Домен содержит ровно 52 сущности одного класса wd:Q29642950, что строго удовлетворяет диапазону [30, 60]."),
    ("Заполненность свойств", "У 84.6% сущностей заполнено более 5 прямых свойств (лицензия, язык, репозиторий, версии, даты публикаций, сайт)."),
    ("Числовые и временные типы", "100% сущностей имеют даты (релизы версий P577, дата основания P571) и числовые параметры (версии в semver, количество версий)."),
    ("Квалификаторы времени", "У свойства номера версии программы (P348) в Wikidata зафиксировано 1 779 утверждений с временным квалификатором даты публикации (pq:P577)."),
    ("Текстовые источники", "У 100% (52 из 52) сущностей есть прямой URL на открытый репозиторий GitHub. Текстовые описания извлечены непосредственно из файлов README.md репозиториев.")
]
for k, v in reqs_doc:
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_after = Pt(2)
    r1 = p.add_run(k + ": ")
    r1.bold = True
    p.add_run(v)

add_header("SPARQL-запрос для выгрузки и валидации сущностей", level=2)
sparql_q1 = """PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>

SELECT DISTINCT ?item ?itemLabel ?repo ?licenseLabel WHERE {
  ?item wdt:P1547 wd:Q47509047 ; # depends on PyTorch
        wdt:P31 wd:Q29642950 ;    # instance of Python library
        wdt:P1324 ?repo .         # source code repository URL
  OPTIONAL { ?item wdt:P275 ?license . }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "ru,en". }
}
ORDER BY ?itemLabel"""
add_code_block(sparql_q1)

# Stats Table
add_header("Статистика заполненности свойств сущностей домена", level=2)
stat_tbl = doc.add_table(rows=6, cols=3)
stat_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
stat_data = [
    ("Свойство Wikidata", "Идентификатор", "Доля сущностей с заполненным свойством"),
    ("Репозиторий исходного кода", "P1324", "100% (52 / 52)"),
    ("Зависимость от ПО (PyTorch)", "P1547", "100% (52 / 52)"),
    ("Язык программирования (Python)", "P277", "94.2% (49 / 52)"),
    ("Лицензия на ПО", "P275", "90.4% (47 / 52)"),
    ("Версия ПО с датой релиза", "P348 + pq:P577", "84.6% (44 / 52) — суммарно 1 779 релизов")
]
for r_i, row in enumerate(stat_data):
    for c_i, val in enumerate(row):
        c = stat_tbl.cell(r_i, c_i)
        set_cell_margins(c, top=60, bottom=60, left=100, right=100)
        p = c.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(val)
        if r_i == 0:
            set_cell_background(c, "1F4E78")
            run.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        else:
            if c_i == 2:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run.bold = True

doc.add_paragraph()

# ==========================================
# ЗАДАНИЕ 2
# ==========================================
add_header("Задание 2. Формулировка 12 вопросов к базе знаний")

task2_path = Path(__file__).resolve().parents[1] / "Резы" / "Отчёт_задание_2.docx"
task2_doc = docx.Document(task2_path)
heading_levels = {"Heading1": 2, "Heading2": 3}

# Skip the standalone title and page settings. Format headings as in the full report.
for element in task2_doc.element.body[1:-1]:
    block = deepcopy(element)
    if block.tag == qn("w:p"):
        paragraph = Paragraph(block, doc)
        level = heading_levels.get(paragraph.style.style_id)
        if level is not None:
            header = add_header(paragraph.text, level=level)
            header.paragraph_format.keep_with_next = True
            continue
        if paragraph.text.startswith("Тип. "):
            paragraph.paragraph_format.keep_with_next = True

    for hyperlink in block.xpath(".//w:hyperlink[@r:id]"):
        source_link = task2_doc.part.rels[hyperlink.get(qn("r:id"))]
        link_id = doc.part.relate_to(source_link.target_ref, source_link.reltype, is_external=True)
        hyperlink.set(qn("r:id"), link_id)
    doc.element.body.insert_element_before(block, "w:sectPr")

doc.add_paragraph()

# ==========================================
# ЗАДАНИЕ 3
# ==========================================
add_header("Задание 3. Разработка онтологии предметной области в Protégé / Turtle")

doc.add_paragraph(
    "Онтология разработана в собственном пространстве имен: http://example.org/pytorch-ecosystem# (префикс pte:). "
    "Она описывает специфику библиотек глубокого обучения и решает задачи, поставленные в 12 вопросах базы знаний."
)

add_header("Архитектура онтологии", level=2)
ont_reqs = [
    ("Иерархия классов (10 классов)", "Выстроена строгая таксономия: базовый класс SoftwareLibrary -> MachineLearningLibrary -> подклассы ComputerVisionLibrary, NaturalLanguageProcessingLibrary, AudioProcessingLibrary, ProbabilisticAndGraphLibrary, OptimizationAndTrainingLibrary. Также введены вспомогательные классы SoftwareLicense, SoftwareVersion, Repository."),
    ("Object Properties (6 свойств)", "dependsOnSoftware, hasLicense, hasPrimaryLicense, hasRepository, hasSourceCodeRepository, hasVersion. Для всех явно специфицированы rdfs:domain и rdfs:range."),
    ("Datatype Properties (7 свойств)", "libraryName (xsd:string), versionIdentifier (xsd:string), releaseDate (xsd:dateTime), versionType (xsd:string), repositoryURL (xsd:anyURI), licenseName (xsd:string), versionCount (xsd:integer). Для всех указаны domain и range."),
    ("Функциональные свойства", "К функциональным относятся pte:hasPrimaryLicense, pte:hasSourceCodeRepository, pte:repositoryURL, pte:licenseName, pte:versionCount и pte:versionIdentifier. Каждое допускает максимум одно значение для одного субъекта."),
    ("Аннотации и метаданные", "У всех классов и свойств заданы rdfs:label на русском и английском языках (@ru, @en), а также развернутые rdfs:comment."),
    ("Связи с Wikidata", "Указаны owl:equivalentClass к сущностям Wikidata (wd:Q188860, wd:Q21169670, wd:Q207621, wd:Q341) и owl:equivalentProperty (wdt:P1547, wdt:P275, wdt:P1324).")
]
for k, v in ont_reqs:
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_after = Pt(2)
    p.add_run(k + ": ").bold = True
    p.add_run(v)

add_header("Матрица использования классов и свойств в вопросах", level=2)
mat_data = [
    ("Класс, свойство или источник", "Тип элемента", "Вопросы", "Роль в ответе или модели"),
    ("pte:SoftwareLibrary", "Класс", "В1–В6, В11–В12\n(косвенно)", "Область определения свойств библиотек в графовых запросах."),
    ("pte:MachineLearningLibrary", "Класс", "—", "Общий суперкласс для специализированных библиотек машинного обучения."),
    ("pte:ComputerVisionLibrary", "Класс", "В4, В11", "Явный фильтр по классу библиотек компьютерного зрения."),
    ("pte:NaturalLanguageProcessingLibrary", "Класс", "В6", "Явный фильтр по классу библиотек обработки естественного языка."),
    ("pte:ProbabilisticAndGraphLibrary", "Класс", "В12", "Явный фильтр по классу вероятностных и графовых библиотек."),
    ("pte:AudioProcessingLibrary\npte:OptimizationAndTrainingLibrary", "Классы", "—", "Классификация аудиобиблиотек и средств оптимизации и обучения."),
    ("pte:SoftwareLicense", "Класс", "В2, В4, В11, В12\n(косвенно)", "Класс объектов связи pte:hasLicense."),
    ("pte:SoftwareVersion", "Класс", "В5\n(косвенно)", "Класс узлов релизов, к которым ведёт pte:hasVersion."),
    ("pte:Repository", "Класс", "В4, В6\n(косвенно)", "Класс промежуточных узлов на пути от библиотеки к URL."),
    ("pte:libraryName", "Datatype", "В1, В3–В6, В11, В12", "Имя библиотеки в результате запроса."),
    ("pte:versionCount", "Datatype", "В1, В3, В11, В12", "Фильтр по числу версий в В1 и В12. Сортировка в В3 и В11."),
    ("pte:hasLicense", "Object", "В2, В4, В11, В12", "Связь для подсчёта по лицензиям в В2 и отбора по конкретной лицензии в В4, В11 и В12."),
    ("pte:licenseName", "Datatype", "В2", "Группировка по названию лицензии."),
    ("pte:dependsOnSoftware", "Object", "В4", "Проверка зависимости библиотеки от PyTorch."),
    ("pte:hasRepository\npte:repositoryURL", "Object / Datatype", "В4, В6", "Путь из двух рёбер от библиотеки к URL репозитория."),
    ("pte:hasVersion\npte:releaseDate", "Object / Datatype", "В5", "Переход к релизу, фильтр за 2023 год и сортировка по дате публикации."),
    ("pte:versionIdentifier", "Datatype", "В5", "Строковый идентификатор релиза. В5 возвращает его и использует для сортировки при равных дате и названии."),
    ("owl:sameAs", "Свойство OWL", "В11, В12", "QID выбранной графом библиотеки связывает результат с записью корпуса и README."),
    ("pte:hasPrimaryLicense", "Object", "—", "Функциональное подсвойство для единственной основной лицензии проекта."),
    ("pte:hasSourceCodeRepository", "Object", "—", "Функциональное подсвойство для единственного основного репозитория проекта."),
    ("pte:versionType", "Datatype", "—", "Статус релиза, например stable. Свойство позволяет отбирать версии по статусу независимо от даты."),
    ("README / data/corpus.jsonl", "Текстовый источник", "В7–В12", "В7–В10 используют текст по заранее заданному QID. В11–В12 читают текст после выбора библиотеки графом."),
]
mat_tbl = doc.add_table(rows=len(mat_data), cols=4)
mat_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
mat_tbl.autofit = False
mat_widths = (Inches(2.55), Inches(1.05), Inches(1.10), Inches(2.20))
for column, width in zip(mat_tbl.columns, mat_widths):
    column.width = width
for r_i, values in enumerate(mat_data):
    row = mat_tbl.rows[r_i]
    row_props = row._tr.get_or_add_trPr()
    row_props.append(OxmlElement('w:cantSplit'))
    if r_i == 0:
        row_props.append(OxmlElement('w:tblHeader'))
    for c_i, (c, val, width) in enumerate(zip(row.cells, values, mat_widths)):
        c.width = width
        set_cell_margins(c, top=60, bottom=60, left=80, right=80)
        p = c.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(val)
        if r_i == 0:
            set_cell_background(c, "1F4E78")
            run.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        else:
            if c_i in [1, 2]:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER

doc.add_paragraph()

# ==========================================
# ЗАДАНИЕ 4
# ==========================================
add_header("Задание 4. Экспорт и статистика графа знаний (knowledge_graph.ttl)")

doc.add_paragraph(
    "Данные выгружены из Wikidata и трансформированы в термины собственной онтологии. "
    "Граф сохранен на диск в формате Turtle (файл knowledge_graph.ttl). "
    "Для обеспечения интероперабельности у каждой библиотеки проставлено отношение owl:sameAs "
    "на глобальный идентификатор Wikidata вида http://www.wikidata.org/entity/Q... . "
    "Статистика рассчитана по сохранённым в файле триплетам до логического вывода. "
    "Число экземпляров класса определяется по явным утверждениям rdf:type, "
    "число использований предиката — по числу триплетов с этим предикатом."
)

knowledge_graph = Graph().parse("knowledge_graph.ttl", format="turtle")
pte = Namespace("http://example.org/pytorch-ecosystem#")
subjects = set(knowledge_graph.subjects())
libraries = set(knowledge_graph.subjects(pte.dependsOnSoftware, pte.PyTorch))
versions = set(knowledge_graph.subjects(RDF.type, pte.SoftwareVersion))
dated_versions = versions & set(knowledge_graph.subjects(pte.releaseDate))
repositories = set(knowledge_graph.subjects(RDF.type, pte.Repository))
repository_urls = {
    url for repository in repositories for url in knowledge_graph.objects(repository, pte.repositoryURL)
}


def format_kg_count(count):
    return f"{count:,}".replace(",", " ")


kg_stats = [
    ("Метрика графа знаний", "Значение"),
    ("Общее число триплетов (троек)", format_kg_count(len(knowledge_graph))),
    ("Число уникальных субъектов", format_kg_count(len(subjects))),
    ("Число библиотек, зависящих от PyTorch", format_kg_count(len(libraries))),
    ("Центральный узел PyTorch", str(int(pte.PyTorch in subjects))),
    ("Число зарегистрированных версий (SoftwareVersion)", format_kg_count(len(versions))),
    ("Из них с датой релиза", format_kg_count(len(dated_versions))),
    ("Число узлов репозиториев (Repository)", format_kg_count(len(repositories))),
    ("Число уникальных URL репозиториев", format_kg_count(len(repository_urls))),
]
class_counts = Counter(knowledge_graph.objects(predicate=RDF.type))
predicate_counts = Counter(knowledge_graph.predicates())
kg_tables = [kg_stats]
for header, counts in (
    (("Класс", "Число экземпляров"), class_counts),
    (("Предикат", "Число триплетов"), predicate_counts),
):
    rows = [
        (knowledge_graph.namespace_manager.qname(term), format_kg_count(count))
        for term, count in sorted(counts.items(), key=lambda item: (-item[1], str(item[0])))
    ]
    kg_tables.append([header, *rows])

for rows in kg_tables:
    stat_kg_tbl = doc.add_table(rows=len(rows), cols=2)
    stat_kg_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r_i, (table_row, values) in enumerate(zip(stat_kg_tbl.rows, rows)):
        row_properties = table_row._tr.get_or_add_trPr()
        row_properties.append(OxmlElement("w:cantSplit"))
        if r_i == 0:
            row_properties.append(OxmlElement("w:tblHeader"))
        for c_i, (cell, value) in enumerate(zip(table_row.cells, values)):
            set_cell_margins(cell, top=60, bottom=60, left=100, right=100)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            run = p.add_run(value)
            if r_i == 0:
                set_cell_background(cell, "1F4E78")
                run.font.color.rgb = RGBColor(255, 255, 255)
                p.paragraph_format.keep_with_next = True
            if r_i == 0 or c_i == 1:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run.bold = True
    doc.add_paragraph()

# ==========================================
# ЗАДАНИЕ 5
# ==========================================
add_header("Задание 5. Формирование корпуса текстов (corpus.jsonl)")

doc.add_paragraph(
    "Для каждой из 52 библиотек собран текстовый документ, извлеченный из официального репозитория GitHub (README.md / README.rst). "
    "Корпус сохранен в кодировке UTF-8 в формате JSON Lines (файл data/corpus.jsonl). "
    "Каждая запись представляет собой JSON-объект следующей структуры:"
)

jsonl_sample = """{
  "id": "Q107382312",
  "name": "kornia",
  "source_url": "https://raw.githubusercontent.com/kornia/kornia/master/README.md",
  "description": "differentiable computer vision library for PyTorch",
  "text": "# Kornia: Open Source Differentiable Computer Vision Library for PyTorch\\n\\nKornia is a differentiable library..."
}"""
add_code_block(jsonl_sample)

doc.add_paragraph(
    "Общий объем сформированного корпуса текстов составляет 52 записи суммарным объемом 198 Кб текста. "
    "Все тексты содержат детальные технические описания, формулы, ссылки на научные статьи arXiv и примеры вызова API."
)

# ==========================================
# ЗАДАНИЕ 6
# ==========================================
add_header("Задание 6. Логический вывод (owlrl) и валидация ограничений (pyshacl)")

add_header("1. Логический вывод OWL 2 RL (owlrl)", level=2)
doc.add_paragraph(
    "Для логического вывода использован движок owlrl.DeductiveClosure(owlrl.OWLRL_Semantics). "
    "В результате работы машины логического вывода граф замкнут относительно аксиом RDFS и правил OWL 2 RL:"
)

owl_summary = Path("data/owlrl_reasoning_summary.txt").read_text(encoding="utf-8").splitlines()
initial, total, added = (int(line.split(": ", 1)[1]) for line in owl_summary[:3])
owl_stats = [
    ("Исходное число триплетов (онтология + данные)", f"{initial:,}".replace(",", " ")),
    ("Число триплетов после логического вывода", f"{total:,}".replace(",", " ")),
    ("Добавлено выведенных триплетов (Inferred Triples)", f"+{added:,}".replace(",", " ")),
]
tbl_owl = doc.add_table(rows=4, cols=2)
tbl_owl.alignment = WD_TABLE_ALIGNMENT.CENTER
for r_i, row in enumerate([("Параметр вывода", "Значение")] + owl_stats):
    for c_i, val in enumerate(row):
        c = tbl_owl.cell(r_i, c_i)
        set_cell_margins(c, top=60, bottom=60, left=100, right=100)
        p = c.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(val)
        if r_i == 0:
            set_cell_background(c, "1F4E78")
            run.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        else:
            if c_i == 1:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run.bold = True

doc.add_paragraph()
doc.add_paragraph(
    "Примеры добавленных фактов в ходе дедуктивного вывода:\n"
    "1. Транзитивность подклассов: для индивида pte:Lib_kornia_Q107382312, явно объявленного экземпляром ComputerVisionLibrary, "
    "выведены типы MachineLearningLibrary и SoftwareLibrary.\n"
    "2. Эквивалентность свойств даёт тройку pte:PyTorch wdt:P1324 pte:Repo_PyTorch_Q47509047 из pte:hasRepository.\n"
    "3. По owl:sameAs выведена тройка wd:Q47509047 pte:hasRepository pte:Repo_PyTorch_Q47509047."
)

add_header("2. Валидация ограничений целостности SHACL (pyshacl)", level=2)
doc.add_paragraph(
    "Проверены кардинальность, класс объекта лицензии, типы данных, шаблон URL GitHub и нижняя граница счётчика версий. "
    "До исправления PySHACL вернул пять нарушений sh:minCount. Четыре касались pte:hasLicense у GFPGAN, OpenCLIP, "
    "pytorch-wavelets и PyTorch. Пятое касалось pte:hasSourceCodeRepository у PyTorch. "
    "Сборщик воспроизводит следующие дополнения по официальным репозиториям."
)

corrections = [
    ("GFPGAN", "Apache License 2.0 для кода проекта с оговорками о сторонних компонентах.", (
        ("LICENSE", "https://github.com/TencentARC/GFPGAN/blob/7552a7791caad982045a7bbe5634bbf1cd5c8679/LICENSE"),
    )),
    ("OpenCLIP", "Лицензия MIT.", (
        ("LICENSE", "https://github.com/mlfoundations/open_clip/blob/4cc208d3a44a2fb6d6435006a46f520d2ccc29b1/LICENSE"),
    )),
    ("pytorch-wavelets", "Классификатор пакета Free To Use But Restricted. MIT применяется к новому коду и DWT, для DTCWT действуют отдельные условия.", (
        ("setup.py", "https://github.com/fbcotter/pytorch_wavelets/blob/9a0c507f04f43c5397e384bb6be8340169b2fd9a/setup.py#L21-L28"),
        ("LICENSE", "https://github.com/fbcotter/pytorch_wavelets/blob/9a0c507f04f43c5397e384bb6be8340169b2fd9a/LICENSE#L1-L7"),
    )),
    ("PyTorch", "Модифицированная лицензия BSD (BSD-3-Clause) и основной репозиторий pytorch/pytorch.", (
        ("LICENSE", "https://github.com/pytorch/pytorch/blob/d38164a545b4a4e4e0cf73ce67173f70574890b6/LICENSE"),
        ("репозиторий", "https://github.com/pytorch/pytorch"),
    )),
]
for project, change, sources in corrections:
    p = doc.add_paragraph()
    p.add_run(f"{project} — ").bold = True
    p.add_run(change)
    for label, url in sources:
        p.add_run(" ")
        link = OxmlElement("w:hyperlink")
        link.set(qn("r:id"), doc.part.relate_to(url, RELATIONSHIP_TYPE.HYPERLINK, is_external=True))
        run = OxmlElement("w:r")
        properties = OxmlElement("w:rPr")
        underline = OxmlElement("w:u")
        underline.set(qn("w:val"), "single")
        properties.append(underline)
        run.append(properties)
        label_text = OxmlElement("w:t")
        label_text.text = label
        run.append(label_text)
        link.append(run)
        p._p.append(link)

doc.add_paragraph("Протокол повторной проверки PySHACL")
shacl_log = Path("data/shacl_validation_report.txt").read_text(encoding="utf-8").split("\n\n", 1)[1]
add_code_block(shacl_log)

doc.add_paragraph(
    "После исправления В2 учитывает 53 узла, включая центральный PyTorch. Распределение по лицензиям: MIT — 23, "
    "Apache 2.0 — 21, модифицированная BSD — 6, двухпунктная BSD — 2, Free To Use But Restricted — 1. "
    "В4 теперь также возвращает GFPGAN и его репозиторий. Результаты В1, В3, В5, В6, В11 и В12 совпали с эталонами. "
    "Эталонные ответы В2 и В4 в разделе 2 обновлены по исправленному графу."
)

# Table of 52 Libraries in Appendix
add_header("Приложение. Полный реестр 52 библиотек экосистемы PyTorch", level=2)
with open('data/libraries_metadata.json', 'r', encoding='utf-8') as f:
    libs_meta = json.load(f)

lib_tbl = doc.add_table(rows=len(libs_meta) + 1, cols=4)
lib_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
lib_headers = ["№", "Библиотека", "QID в Wikidata", "Репозиторий GitHub"]
for c_i, h in enumerate(lib_headers):
    c = lib_tbl.cell(0, c_i)
    set_cell_background(c, "1F4E78")
    set_cell_margins(c, top=60, bottom=60, left=80, right=80)
    p = c.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(h)
    run.bold = True
    run.font.color.rgb = RGBColor(255, 255, 255)

for idx, (qid, l_data) in enumerate(libs_meta.items(), start=1):
    r_cells = lib_tbl.rows[idx].cells
    r_cells[0].paragraphs[0].add_run(str(idx))
    r_cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_cells[1].paragraphs[0].add_run(l_data['label']).bold = True
    r_cells[2].paragraphs[0].add_run(qid)
    r_cells[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    repo = l_data['repos'][0] if l_data['repos'] else '—'
    r_cells[3].paragraphs[0].add_run(repo)
    for c in r_cells:
        set_cell_margins(c, top=40, bottom=40, left=60, right=60)

report_filename = "Отчет_Контрольная_работа_1.docx"
doc.save(report_filename)
print(f"Report saved to {report_filename} (size: {os.path.getsize(report_filename)} bytes)")
