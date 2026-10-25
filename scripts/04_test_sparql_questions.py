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
    SELECT ?name ?cnt WHERE {
      ?lib a ?cls ;
           pte:libraryName ?name ;
           pte:versionCount ?cnt .
      FILTER(?cnt > 20)
    }
    ORDER BY DESC(?cnt)
    """),
    
    # 2. Aggregation
    ("2. Число библиотек по типам лицензий", """
    PREFIX pte: <http://example.org/pytorch-ecosystem#>
    SELECT ?licName (COUNT(DISTINCT ?lib) AS ?libCount) WHERE {
      ?lib pte:hasLicense ?lic .
      ?lic pte:licenseName ?licName .
    }
    GROUP BY ?licName
    ORDER BY DESC(?libCount)
    """),

    # 3. Sorting & Limit
    ("3. Топ-5 библиотек по числу версий", """
    PREFIX pte: <http://example.org/pytorch-ecosystem#>
    SELECT ?name ?cnt WHERE {
      ?lib pte:libraryName ?name ;
           pte:versionCount ?cnt .
    }
    ORDER BY DESC(?cnt)
    LIMIT 5
    """),

    # 4. Multi-hop (>= 2 edges)
    ("4. Библиотеки CV с лицензией Apache 2.0 и их репозитории", """
    PREFIX pte: <http://example.org/pytorch-ecosystem#>
    SELECT ?name ?repoUrl WHERE {
      ?lib a pte:ComputerVisionLibrary ;
           pte:libraryName ?name ;
           pte:hasLicense ?lic ;
           pte:hasRepository ?repo .
      ?lic pte:licenseName "Apache Software License 2.0" .
      ?repo pte:repositoryURL ?repoUrl .
    }
    ORDER BY ?name
    """),

    # 5. Temporal qualifier (releaseDate in 2023)
    ("5. Версии библиотек, вышедшие в 2023 году (временной квалификатор)", """
    PREFIX pte: <http://example.org/pytorch-ecosystem#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    SELECT ?name ?vNum ?date WHERE {
      ?lib pte:libraryName ?name ;
           pte:hasVersion ?v .
      ?v pte:versionIdentifier ?vNum ;
         pte:releaseDate ?date .
      FILTER(?date >= "2023-01-01T00:00:00Z"^^xsd:dateTime && ?date < "2024-01-01T00:00:00Z"^^xsd:dateTime)
    }
    ORDER BY ?date
    LIMIT 10
    """),

    # 6. NLP libraries
    ("6. Библиотеки обработки естественного языка (NLP)", """
    PREFIX pte: <http://example.org/pytorch-ecosystem#>
    SELECT ?name ?repoUrl WHERE {
      ?lib a pte:NaturalLanguageProcessingLibrary ;
           pte:libraryName ?name ;
           pte:hasRepository ?repo .
      ?repo pte:repositoryURL ?repoUrl .
    }
    ORDER BY ?name
    """)
]

for title, q_str in queries:
    print(f"\n==========================================")
    print(f"=== {title} ===")
    res = g.query(q_str)
    for row in res:
        print("  " + " | ".join(str(val) for val in row))
