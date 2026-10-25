import sys
import os
from rdflib import Graph, Namespace, RDF, RDFS, OWL, XSD, URIRef
import pyshacl
import owlrl

sys.stdout.reconfigure(encoding='utf-8')

# 1. Create SHACL Shapes (shapes.shacl.ttl)
shacl_shapes_turtle = """
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix pte: <http://example.org/pytorch-ecosystem#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

# Shape 1: Library constraints
pte:LibraryShape
    a sh:NodeShape ;
    sh:targetClass pte:SoftwareLibrary, pte:MachineLearningLibrary, 
                   pte:ComputerVisionLibrary, pte:NaturalLanguageProcessingLibrary,
                   pte:ProbabilisticAndGraphLibrary, pte:OptimizationAndTrainingLibrary ;
    
    # 1. Cardinality constraint: must have exactly 1 library name
    sh:property [
        sh:path pte:libraryName ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:datatype xsd:string ;
        sh:message "Библиотека должна иметь ровно одно строковое название (libraryName)."@ru ;
    ] ;

    # 2. Value class constraint: license must be an instance of SoftwareLicense
    sh:property [
        sh:path pte:hasLicense ;
        sh:minCount 1 ;
        sh:class pte:SoftwareLicense ;
        sh:message "Лицензия библиотеки должна быть объектом класса SoftwareLicense."@ru ;
    ] ;

    # 3. Cardinality constraint: must have at least 1 repository
    sh:property [
        sh:path pte:hasSourceCodeRepository ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:message "У библиотеки должен быть указан ровно один основной репозиторий исходного кода."@ru ;
    ] ;

    # 4. Pattern constraint: version count must be a non-negative integer
    sh:property [
        sh:path pte:versionCount ;
        sh:datatype xsd:integer ;
        sh:minInclusive 0 ;
        sh:message "Число версий должно быть неотрицательным целым числом."@ru ;
    ] .

# Shape 2: Repository constraints
pte:RepositoryShape
    a sh:NodeShape ;
    sh:targetClass pte:Repository ;
    
    # 5. Pattern constraint: GitHub URL pattern
    sh:property [
        sh:path pte:repositoryURL ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:datatype xsd:anyURI ;
        sh:pattern "^https://github\\\\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/?$" ;
        sh:message "URL репозитория должен указывать на валидный адрес GitHub репозитория."@ru ;
    ] .

# Shape 3: SoftwareVersion constraints
pte:VersionShape
    a sh:NodeShape ;
    sh:targetClass pte:SoftwareVersion ;
    
    # 6. Datatype constraint on releaseDate
    sh:property [
        sh:path pte:releaseDate ;
        sh:datatype xsd:dateTime ;
        sh:message "Дата публикации версии должна иметь тип xsd:dateTime."@ru ;
    ] ;

    # 7. Pattern constraint on semver string
    sh:property [
        sh:path pte:versionIdentifier ;
        sh:minCount 1 ;
        sh:datatype xsd:string ;
        sh:message "Идентификатор версии должен быть строкой."@ru ;
    ] .
"""

with open("shapes.shacl.ttl", "w", encoding="utf-8") as f:
    f.write(shacl_shapes_turtle)

print("Created shapes.shacl.ttl with 7 constraints across 4 constraint types.")

# 2. Validate Knowledge Graph using pyshacl
print("\n--- Running PySHACL Validation ---")
data_graph = Graph()
data_graph.parse("knowledge_graph.ttl", format="turtle")

shapes_graph = Graph()
shapes_graph.parse("shapes.shacl.ttl", format="turtle")

conforms, results_graph, results_text = pyshacl.validate(
    data_graph=data_graph,
    shacl_graph=shapes_graph,
    inference='rdfs',
    abort_on_first=False,
    meta_shacl=False,
    advanced=False,
    debug=False
)

print(f"SHACL Conforms: {conforms}")
print("\nValidation Results Summary:")
print(results_text[:1500])

with open("data/shacl_validation_report.txt", "w", encoding="utf-8") as f:
    f.write(f"Conforms: {conforms}\n\n")
    f.write(results_text)

# 3. Run OWL 2 RL Reasoning using owlrl
print("\n--- Running OWL 2 RL Reasoning (owlrl) ---")
infer_graph = Graph()
infer_graph.parse("ontology.ttl", format="turtle")
infer_graph.parse("knowledge_graph.ttl", format="turtle")

initial_triples = len(infer_graph)
print(f"Initial Triples (Ontology + Graph): {initial_triples}")

# Expand with OWL 2 RL Semantics
owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(infer_graph)

inferred_triples = len(infer_graph)
added_triples = inferred_triples - initial_triples
print(f"Total Triples after OWL 2 RL reasoning: {inferred_triples}")
print(f"Added Inferred Triples: {added_triples}")

# Sample inferred triples
print("\nSample Inferred Triples:")
PTE = Namespace("http://example.org/pytorch-ecosystem#")
sample_count = 0
inferred_sample_text = []
for s, p, o in infer_graph:
    # Look for inferred superclass relationships
    if p == RDF.type and o in [PTE.SoftwareLibrary, PTE.MachineLearningLibrary]:
        inferred_sample_text.append(f"  {s.split('#')[-1]} rdf:type {o.split('#')[-1]}")
        sample_count += 1
        if sample_count >= 10:
            break

print("\n".join(inferred_sample_text))

with open("data/owlrl_reasoning_summary.txt", "w", encoding="utf-8") as f:
    f.write(f"Initial Triples: {initial_triples}\n")
    f.write(f"Total Triples after reasoning: {inferred_triples}\n")
    f.write(f"Added Triples: {added_triples}\n\n")
    f.write("Sample Inferred Triples (Superclass & Subproperty inheritance):\n")
    f.write("\n".join(inferred_sample_text))

print("\nSaved SHACL report and OWLRL summary to data/")
