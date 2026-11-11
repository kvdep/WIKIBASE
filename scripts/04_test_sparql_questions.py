import sys
from rdflib import Graph, Namespace

sys.stdout.reconfigure(encoding='utf-8')

g = Graph()
g.parse("knowledge_graph.ttl", format="turtle")
g.parse("ontology.ttl", format="turtle")

PTE = Namespace("http://example.org/pytorch-ecosystem#")

queries = [
    # 1. Filter by number
    ("1. Библиотеки с versionCount > 20", """
PREFIX pte: <http://example.org/pytorch-ecosystem#>
SELECT ?name ?count WHERE {
  ?library pte:libraryName ?name ; pte:versionCount ?count .
  FILTER(?count > 20)
}
ORDER BY DESC(?count) LCASE(STR(?name)) ?name
"""),
    
    # 2. Aggregation
    ("2. Число библиотек по типам лицензий", """
PREFIX pte: <http://example.org/pytorch-ecosystem#>
SELECT ?licenseName (COUNT(DISTINCT ?library) AS ?count) WHERE {
  ?library pte:hasLicense ?license .
  ?license pte:licenseName ?licenseName .
}
GROUP BY ?licenseName
ORDER BY DESC(?count) ?licenseName
"""),

    # 3. Sorting & Limit
    ("3. Топ-5 библиотек по числу версий", """
PREFIX pte: <http://example.org/pytorch-ecosystem#>
SELECT ?name ?count WHERE {
  ?library pte:libraryName ?name ; pte:versionCount ?count .
}
ORDER BY DESC(?count) LCASE(STR(?name)) ?name
LIMIT 5
"""),

    # 4. Multi-hop (>= 2 edges)
    ("4. Библиотеки CV с лицензией Apache 2.0 и их репозитории", """
PREFIX pte: <http://example.org/pytorch-ecosystem#>
SELECT DISTINCT ?name ?repoUrl WHERE {
  ?library a pte:ComputerVisionLibrary ;
           pte:libraryName ?name ;
           pte:dependsOnSoftware pte:PyTorch ;
           pte:hasLicense pte:License_Apache_License_2_0 ;
           pte:hasRepository/pte:repositoryURL ?repoUrl .
}
ORDER BY ?name ?repoUrl
"""),

    # 5. Temporal qualifier (releaseDate in 2023)
    ("5. Версии библиотек, вышедшие в 2023 году (временной квалификатор)", """
PREFIX pte: <http://example.org/pytorch-ecosystem#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT DISTINCT ?name ?version ?date WHERE {
  ?library pte:libraryName ?name ; pte:hasVersion ?release .
  ?release pte:versionIdentifier ?version ; pte:releaseDate ?date .
  FILTER(?date >= "2023-01-01T00:00:00Z"^^xsd:dateTime &&
         ?date < "2024-01-01T00:00:00Z"^^xsd:dateTime)
}
ORDER BY ?date ?name ?version
LIMIT 10
"""),

    # 6. NLP libraries
    ("6. Библиотеки обработки естественного языка (NLP)", """
PREFIX pte: <http://example.org/pytorch-ecosystem#>
SELECT DISTINCT ?name ?repoUrl WHERE {
  ?library a pte:NaturalLanguageProcessingLibrary ;
           pte:libraryName ?name ;
           pte:hasRepository/pte:repositoryURL ?repoUrl .
}
ORDER BY ?name ?repoUrl
""")
]

for title, q_str in queries:
    print(f"\n==========================================")
    print(f"=== {title} ===")
    res = g.query(q_str)
    for row in res:
        print("  " + " | ".join(str(val) for val in row))
