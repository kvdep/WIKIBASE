import urllib.request
import urllib.parse
import json
import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

os.makedirs('data', exist_ok=True)
os.makedirs('scripts', exist_ok=True)

# 1. SPARQL query to get the exact 52 libraries and their properties
sparql_url = 'https://query.wikidata.org/sparql'

query = """
SELECT DISTINCT ?item ?itemLabel ?itemDescription ?repo ?license ?licenseLabel ?inception WHERE {
  ?item wdt:P1547 wd:Q47509047 . # depends on PyTorch
  ?item wdt:P31 wd:Q29642950 .    # Python library
  ?item wdt:P1324 ?repo .         # code repository
  OPTIONAL { ?item wdt:P275 ?license . }
  OPTIONAL { ?item wdt:P571 ?inception . }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "ru,en". }
}
ORDER BY ?itemLabel
"""

headers = {'User-Agent': 'SemTechProject/1.0 (Student coursework; contact: student@edu.ru)'}
req = urllib.request.Request(sparql_url + '?' + urllib.parse.urlencode({'query': query, 'format': 'json'}), headers=headers)

print("Fetching libraries from Wikidata SPARQL...")
with urllib.request.urlopen(req) as resp:
    sparql_res = json.loads(resp.read().decode('utf-8'))

bindings = sparql_res['results']['bindings']
print(f"Retrieved {len(bindings)} library records.")

# Deduplicate by QID (some items have multiple repos or licenses)
libraries = {}
for b in bindings:
    qid = b['item']['value'].split('/')[-1]
    if qid not in libraries:
        libraries[qid] = {
            'qid': qid,
            'uri': b['item']['value'],
            'label': b.get('itemLabel', {}).get('value', qid),
            'description': b.get('itemDescription', {}).get('value', ''),
            'repos': set(),
            'licenses': set(),
            'inception': b.get('inception', {}).get('value', None)
        }
    if 'repo' in b:
        libraries[qid]['repos'].add(b['repo']['value'])
    if 'licenseLabel' in b:
        libraries[qid]['licenses'].add(b['licenseLabel']['value'])

print(f"Unique libraries: {len(libraries)}")

# Fetch versions and temporal qualifiers for each library
print("Fetching versions with temporal qualifiers (P348 + pq:P577)...")
q_versions = """
SELECT ?item ?version ?pubDate ?vTypeLabel WHERE {
  ?item wdt:P1547 wd:Q47509047 ;
        wdt:P31 wd:Q29642950 ;
        wdt:P1324 ?repo .
  ?item p:P348 ?statement .
  ?statement ps:P348 ?version .
  OPTIONAL { ?statement pq:P577 ?pubDate . }
  OPTIONAL { ?statement pq:P548 ?vType . }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "ru,en". }
}
"""
req_v = urllib.request.Request(sparql_url + '?' + urllib.parse.urlencode({'query': q_versions, 'format': 'json'}), headers=headers)
with urllib.request.urlopen(req_v) as resp:
    res_v = json.loads(resp.read().decode('utf-8'))

versions_by_qid = {}
for b in res_v['results']['bindings']:
    qid = b['item']['value'].split('/')[-1]
    v_num = b['version']['value']
    p_date = b.get('pubDate', {}).get('value', None)
    v_type = b.get('vTypeLabel', {}).get('value', 'stable')
    if qid not in versions_by_qid:
        versions_by_qid[qid] = []
    versions_by_qid[qid].append({
        'version': v_num,
        'pubDate': p_date,
        'vType': v_type
    })

for qid in libraries:
    libraries[qid]['repos'] = list(libraries[qid]['repos'])
    libraries[qid]['licenses'] = list(libraries[qid]['licenses'])
    libraries[qid]['versions'] = versions_by_qid.get(qid, [])

# Save metadata json
with open('data/libraries_metadata.json', 'w', encoding='utf-8') as f:
    json.dump(libraries, f, ensure_ascii=False, indent=2)

print(f"Saved metadata for {len(libraries)} libraries to data/libraries_metadata.json")

# 2. Download README for each library to create corpus.jsonl
print("\nFetching text information (README.md) for corpus.jsonl...")
corpus_records = []

for qid, lib in libraries.items():
    repo_url = lib['repos'][0] if lib['repos'] else ''
    text_content = ""
    source_url = repo_url
    
    if "github.com" in repo_url:
        # Extract owner/repo
        parts = repo_url.rstrip('/').split('/')
        if len(parts) >= 5:
            owner, repo_name = parts[-2], parts[-1]
            raw_candidates = [
                f"https://raw.githubusercontent.com/{owner}/{repo_name}/master/README.md",
                f"https://raw.githubusercontent.com/{owner}/{repo_name}/main/README.md",
                f"https://raw.githubusercontent.com/{owner}/{repo_name}/master/README.rst",
                f"https://raw.githubusercontent.com/{owner}/{repo_name}/main/README.rst"
            ]
            for raw_url in raw_candidates:
                try:
                    raw_req = urllib.request.Request(raw_url, headers={'User-Agent': 'SemTechBot/1.0'})
                    with urllib.request.urlopen(raw_req, timeout=5) as r_resp:
                        text_content = r_resp.read().decode('utf-8', errors='ignore')
                        source_url = raw_url
                        break
                except Exception:
                    continue

    if not text_content:
        # Fallback to description + metadata summary
        text_content = f"{lib['label']} is an open-source Python library designed for machine learning workflows with PyTorch. {lib['description']}. Repository: {repo_url}."

    # Keep a reasonable excerpt for JSONL (up to 4000 characters to keep it compact and clean)
    corpus_records.append({
        "id": qid,
        "name": lib['label'],
        "source_url": source_url,
        "description": lib['description'],
        "text": text_content[:4000]
    })
    print(f"  [+] {lib['label']} ({qid}): text length {len(corpus_records[-1]['text'])} chars")

with open('data/corpus.jsonl', 'w', encoding='utf-8') as f:
    for rec in corpus_records:
        f.write(json.dumps(rec, ensure_ascii=False) + '\n')

print(f"\nCorpus created with {len(corpus_records)} records at data/corpus.jsonl")
