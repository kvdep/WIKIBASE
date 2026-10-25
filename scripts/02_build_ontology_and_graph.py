import json
import os
import sys
from rdflib import Graph, Literal, Namespace, RDF, RDFS, OWL, XSD, URIRef
from rdflib.namespace import FOAF, DCTERMS

sys.stdout.reconfigure(encoding='utf-8')

PTE = Namespace("http://example.org/pytorch-ecosystem#")
WD = Namespace("http://www.wikidata.org/entity/")
WDT = Namespace("http://www.wikidata.org/prop/direct/")

# ==========================================
# 1. BUILD ONTOLOGY (ontology.ttl)
# ==========================================
ont = Graph()
ont.bind("pte", PTE)
ont.bind("owl", OWL)
ont.bind("rdfs", RDFS)
ont.bind("xsd", XSD)
ont.bind("wd", WD)
ont.bind("wdt", WDT)

ontology_uri = URIRef("http://example.org/pytorch-ecosystem")
ont.add((ontology_uri, RDF.type, OWL.Ontology))
ont.add((ontology_uri, RDFS.label, Literal("Онтология экосистемы библиотек PyTorch", lang="ru")))
ont.add((ontology_uri, RDFS.label, Literal("PyTorch Ecosystem Software Libraries Ontology", lang="en")))
ont.add((ontology_uri, RDFS.comment, Literal("Онтология для описания библиотек глубокого обучения, зависящих от PyTorch, их репозиториев, версий и лицензий.", lang="ru")))
ont.add((ontology_uri, RDFS.comment, Literal("Domain ontology describing PyTorch-dependent deep learning libraries, repositories, releases, and licenses.", lang="en")))

# Class definitions
classes_data = [
    ("SoftwareLibrary", None, "Программная библиотека", "Software Library", 
     "Набор скомпилированного или интерпретируемого кода многократного использования.", "Reusable software component.", WD.Q188860),
    ("MachineLearningLibrary", "SoftwareLibrary", "Библиотека машинного обучения", "Machine Learning Library",
     "Программная библиотека, реализующая методы машинного и глубокого обучения.", "Software library implementing machine learning methods.", WD.Q21169670),
    ("ComputerVisionLibrary", "MachineLearningLibrary", "Библиотека компьютерного зрения", "Computer Vision Library",
     "Библиотека для обработки, аугментации и анализа изображений и видео.", "Library for computer vision tasks and image transformations.", None),
    ("NaturalLanguageProcessingLibrary", "MachineLearningLibrary", "Библиотека обработки естественного языка", "NLP Library",
     "Библиотека для анализа, токенизации и моделирования текстов.", "Library for text processing, tokenization and NLP models.", None),
    ("AudioProcessingLibrary", "MachineLearningLibrary", "Библиотека обработки звука", "Audio Processing Library",
     "Библиотека для спектрального анализа и генерации речи/звука.", "Library for audio signals, speech recognition and synthesis.", None),
    ("ProbabilisticAndGraphLibrary", "MachineLearningLibrary", "Вероятностная и графовая библиотека", "Probabilistic and Graph ML Library",
     "Библиотека для байесовского вывода, графовых нейросетей и гауссовских процессов.", "Library for Bayesian inference, GNNs and Gaussian processes.", None),
    ("OptimizationAndTrainingLibrary", "MachineLearningLibrary", "Библиотека оптимизации и обучения", "Optimization and Training Library",
     "Библиотека для масштабирования обучения, оптимизаторов и трекинга метрик.", "Library for training distributed models, custom optimizers and metrics.", None),
    ("SoftwareLicense", None, "Лицензия на программное обеспечение", "Software License",
     "Юридический документ, определяющий условия использования программного обеспечения.", "Legal instrument governing software usage and distribution.", WD.Q207621),
    ("SoftwareVersion", None, "Версия программного обеспечения", "Software Version",
     "Конкретное выпущенное состояние программного пакета.", "Specific released build or state of a software package.", WD.Q341),
    ("Repository", None, "Репозиторий исходного кода", "Source Code Repository",
     "Хранилище файлов с исходным кодом проекта под управлением системы контроля версий.", "Storage location for project source code managed by VCS.", WD.Q474550)
]

for name, parent, ru_lbl, en_lbl, ru_cmt, en_cmt, eq_class in classes_data:
    c_uri = PTE[name]
    ont.add((c_uri, RDF.type, OWL.Class))
    ont.add((c_uri, RDFS.label, Literal(ru_lbl, lang="ru")))
    ont.add((c_uri, RDFS.label, Literal(en_lbl, lang="en")))
    ont.add((c_uri, RDFS.comment, Literal(ru_cmt, lang="ru")))
    ont.add((c_uri, RDFS.comment, Literal(en_cmt, lang="en")))
    if parent:
        ont.add((c_uri, RDFS.subClassOf, PTE[parent]))
    if eq_class:
        ont.add((c_uri, OWL.equivalentClass, eq_class))

# Object Properties
obj_props = [
    ("dependsOnSoftware", "SoftwareLibrary", "SoftwareLibrary", "зависит от программного обеспечения", "depends on software",
     "Связывает библиотеку с другой библиотекой или фреймворком, необходимым для ее функционирования.", WDT.P1547, False),
    ("hasLicense", "SoftwareLibrary", "SoftwareLicense", "имеет лицензию", "has license",
     "Указывает лицензию на использование программной библиотеки.", WDT.P275, False),
    ("hasPrimaryLicense", "SoftwareLibrary", "SoftwareLicense", "имеет основную лицензию", "has primary license",
     "Функциональное отношение: единственная основная лицензия проекта.", None, True),
    ("hasRepository", "SoftwareLibrary", "Repository", "имеет репозиторий", "has repository",
     "Связывает библиотеку с ее репозиторием исходного кода.", WDT.P1324, False),
    ("hasSourceCodeRepository", "SoftwareLibrary", "Repository", "имеет репозиторий исходного кода", "has source code repository",
     "Функциональное отношение: основной репозиторий проекта.", None, True),
    ("hasVersion", "SoftwareLibrary", "SoftwareVersion", "имеет версию", "has version",
     "Связывает библиотеку с ее версией (релизом).", None, False)
]

for name, dom, rng, ru_lbl, en_lbl, cmt, eq_prop, is_func in obj_props:
    p_uri = PTE[name]
    ont.add((p_uri, RDF.type, OWL.ObjectProperty))
    if is_func:
        ont.add((p_uri, RDF.type, OWL.FunctionalProperty))
    ont.add((p_uri, RDFS.domain, PTE[dom]))
    ont.add((p_uri, RDFS.range, PTE[rng]))
    ont.add((p_uri, RDFS.label, Literal(ru_lbl, lang="ru")))
    ont.add((p_uri, RDFS.label, Literal(en_lbl, lang="en")))
    ont.add((p_uri, RDFS.comment, Literal(cmt, lang="ru")))
    if eq_prop:
        ont.add((p_uri, OWL.equivalentProperty, eq_prop))

ont.add((PTE["hasPrimaryLicense"], RDFS.subPropertyOf, PTE["hasLicense"]))
ont.add((PTE["hasSourceCodeRepository"], RDFS.subPropertyOf, PTE["hasRepository"]))

# Datatype Properties
dt_props = [
    ("libraryName", "SoftwareLibrary", XSD.string, "название библиотеки", "library name", "Строковое имя программной библиотеки.", False),
    ("versionNumber", "SoftwareVersion", XSD.string, "номер версии", "version number", "Идентификатор версии в формате semver.", True),
    ("releaseDate", "SoftwareVersion", XSD.dateTime, "дата релиза", "release date", "Точная дата публикации версии (квалификатор времени).", False),
    ("versionType", "SoftwareVersion", XSD.string, "тип версии", "version type", "Статус релиза: stable, alpha, beta.", False),
    ("repositoryURL", "Repository", XSD.anyURI, "URL репозитория", "repository URL", "Веб-адрес репозитория исходного кода.", True),
    ("licenseName", "SoftwareLicense", XSD.string, "название лицензии", "license name", "Текстовое наименование программной лицензии.", True),
    ("versionCount", "SoftwareLibrary", XSD.integer, "число зарегистрированных версий", "version count", "Общее число зафиксированных релизов библиотеки.", True)
]

for name, dom, rng, ru_lbl, en_lbl, cmt, is_func in dt_props:
    p_uri = PTE[name]
    ont.add((p_uri, RDF.type, OWL.DatatypeProperty))
    if is_func:
        ont.add((p_uri, RDF.type, OWL.FunctionalProperty))
    ont.add((p_uri, RDFS.domain, PTE[dom]))
    ont.add((p_uri, RDFS.range, rng))
    ont.add((p_uri, RDFS.label, Literal(ru_lbl, lang="ru")))
    ont.add((p_uri, RDFS.label, Literal(en_lbl, lang="en")))
    ont.add((p_uri, RDFS.comment, Literal(cmt, lang="ru")))

ont.serialize(destination="ontology.ttl", format="turtle")
print(f"Ontology serialized to ontology.ttl ({len(ont)} triples)")

# ==========================================
# 2. POPULATE KNOWLEDGE GRAPH (knowledge_graph.ttl)
# ==========================================
with open('data/libraries_metadata.json', 'r', encoding='utf-8') as f:
    libraries = json.load(f)

kg = Graph()
kg.bind("pte", PTE)
kg.bind("owl", OWL)
kg.bind("rdfs", RDFS)
kg.bind("xsd", XSD)
kg.bind("wd", WD)

# Central entity: PyTorch
pytorch_uri = PTE["PyTorch"]
kg.add((pytorch_uri, RDF.type, PTE["MachineLearningLibrary"]))
kg.add((pytorch_uri, PTE["libraryName"], Literal("PyTorch", datatype=XSD.string)))
kg.add((pytorch_uri, OWL.sameAs, URIRef("http://www.wikidata.org/entity/Q47509047")))

# Subclass classifier mapping
cv_keywords = ["vision", "image", "face", "kornia", "timm", "nerf", "clip", "effdet", "gfpgan", "facexlib", "clean-fid", "lpips", "tomesd"]
nlp_keywords = ["text", "stanza", "flair", "allennlp", "bert", "fschat", "peft", "transformers", "attacut", "snorkel", "stonkgs"]
prob_keywords = ["pyro", "gpytorch", "botorch", "pykeen", "torch-ppr", "pgmpy", "torchdiffeq", "torchsde"]
opt_keywords = ["lightning", "accelerate", "ignite", "torchmetrics", "lion", "optimizer", "triton", "catalyst", "thop", "ranger", "hummingbird"]

def classify_library(name, desc):
    text = (name + " " + desc).lower()
    if any(k in text for k in cv_keywords):
        return PTE["ComputerVisionLibrary"]
    elif any(k in text for k in nlp_keywords):
        return PTE["NaturalLanguageProcessingLibrary"]
    elif any(k in text for k in prob_keywords):
        return PTE["ProbabilisticAndGraphLibrary"]
    elif any(k in text for k in opt_keywords):
        return PTE["OptimizationAndTrainingLibrary"]
    return PTE["MachineLearningLibrary"]

# Known licenses mapping to clean individuals
licenses_map = {
    "MIT License": ("MIT", "http://www.wikidata.org/entity/Q334660"),
    "Apache Software License 2.0": ("Apache-2.0", "http://www.wikidata.org/entity/Q616523"),
    "3-clause BSD License": ("BSD-3-Clause", "http://www.wikidata.org/entity/Q180189"),
    "2-clause BSD License": ("BSD-2-Clause", "http://www.wikidata.org/entity/Q191244")
}

for lic_name, (short_name, lic_wd) in licenses_map.items():
    l_uri = PTE[f"License_{short_name}"]
    kg.add((l_uri, RDF.type, PTE["SoftwareLicense"]))
    kg.add((l_uri, PTE["licenseName"], Literal(lic_name, datatype=XSD.string)))
    kg.add((l_uri, OWL.sameAs, URIRef(lic_wd)))

# Add 52 libraries
for qid, lib in libraries.items():
    safe_name = "".join(c if c.isalnum() else "_" for c in lib['label'])
    lib_uri = PTE[f"Lib_{safe_name}_{qid}"]
    
    # Class assignment
    cls_uri = classify_library(lib['label'], lib['description'])
    kg.add((lib_uri, RDF.type, cls_uri))
    
    # owl:sameAs to Wikidata
    kg.add((lib_uri, OWL.sameAs, URIRef(f"http://www.wikidata.org/entity/{qid}")))
    
    # Basic Datatype properties
    kg.add((lib_uri, PTE["libraryName"], Literal(lib['label'], datatype=XSD.string)))
    kg.add((lib_uri, RDFS.label, Literal(lib['label'], lang="en")))
    if lib['description']:
        kg.add((lib_uri, RDFS.comment, Literal(lib['description'], lang="en")))
    
    # Dependency on PyTorch
    kg.add((lib_uri, PTE["dependsOnSoftware"], pytorch_uri))
    
    # Repository
    if lib['repos']:
        repo_url = lib['repos'][0]
        repo_uri = PTE[f"Repo_{safe_name}_{qid}"]
        kg.add((repo_uri, RDF.type, PTE["Repository"]))
        kg.add((repo_uri, PTE["repositoryURL"], Literal(repo_url, datatype=XSD.anyURI)))
        kg.add((lib_uri, PTE["hasRepository"], repo_uri))
        kg.add((lib_uri, PTE["hasSourceCodeRepository"], repo_uri))
        
    # License
    if lib['licenses']:
        first_lic = lib['licenses'][0]
        lic_key = None
        for k in licenses_map:
            if k.lower() in first_lic.lower() or first_lic.lower() in k.lower():
                lic_key = k
                break
        if lic_key:
            l_uri = PTE[f"License_{licenses_map[lic_key][0]}"]
            kg.add((lib_uri, PTE["hasLicense"], l_uri))
            kg.add((lib_uri, PTE["hasPrimaryLicense"], l_uri))
        else:
            # Custom license individual
            clean_l_name = "".join(c if c.isalnum() else "_" for c in first_lic)
            custom_l_uri = PTE[f"License_{clean_l_name}"]
            kg.add((custom_l_uri, RDF.type, PTE["SoftwareLicense"]))
            kg.add((custom_l_uri, PTE["licenseName"], Literal(first_lic, datatype=XSD.string)))
            kg.add((lib_uri, PTE["hasLicense"], custom_l_uri))
            kg.add((lib_uri, PTE["hasPrimaryLicense"], custom_l_uri))
            
    # Versions & Qualifiers
    versions = lib.get('versions', [])
    kg.add((lib_uri, PTE["versionCount"], Literal(len(versions), datatype=XSD.integer)))
    
    for v_idx, v_data in enumerate(versions):
        v_str = "".join(c if c.isalnum() else "_" for c in v_data['version'])
        v_uri = PTE[f"Ver_{safe_name}_{qid}_{v_str}_{v_idx}"]
        kg.add((v_uri, RDF.type, PTE["SoftwareVersion"]))
        kg.add((v_uri, PTE["versionIdentifier"], Literal(v_data['version'], datatype=XSD.string)))
        kg.add((v_uri, PTE["versionType"], Literal(v_data['vType'], datatype=XSD.string)))
        if v_data['pubDate']:
            # Normalize ISO dateTime
            dt_str = v_data['pubDate']
            if len(dt_str) == 10:
                dt_str += "T00:00:00Z"
            kg.add((v_uri, PTE["releaseDate"], Literal(dt_str, datatype=XSD.dateTime)))
        kg.add((lib_uri, PTE["hasVersion"], v_uri))

kg.serialize(destination="knowledge_graph.ttl", format="turtle")
print(f"Knowledge Graph serialized to knowledge_graph.ttl ({len(kg)} triples)")

# Summary stats
classes_count = {}
for s, p, o in kg.triples((None, RDF.type, None)):
    classes_count[o] = classes_count.get(o, 0) + 1

props_count = {}
for s, p, o in kg:
    props_count[p] = props_count.get(p, 0) + 1

print("\n=== Knowledge Graph Statistics ===")
print(f"Total Triples: {len(kg)}")
print(f"Total Unique Subjects: {len(set(kg.subjects()))}")
print("\nTriples by Class (rdf:type):")
for c, cnt in sorted(classes_count.items(), key=lambda x: -x[1]):
    print(f"  {c.split('#')[-1]}: {cnt}")

print("\nTriples by Property:")
for p, cnt in sorted(props_count.items(), key=lambda x: -x[1])[:10]:
    print(f"  {p.split('#')[-1]}: {cnt}")
