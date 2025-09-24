
import json
import os
import time
from elasticsearch import Elasticsearch


ES_HOST = os.environ.get("ES_HOST", "localhost")
ES_PORT = os.environ.get("ES_PORT", "9200")
INDEX_NAME = os.environ.get("ES_INDEX", "nlp_index")
SCHEMA_INDEX = "schema-index"
def extract_field_paths(doc, prefix=""):
    """Recursively extract all unique field paths from a document."""
    paths = set()
    if isinstance(doc, dict):
        for k, v in doc.items():
            full_key = f"{prefix}.{k}" if prefix else k
            paths.add(full_key)
            paths.update(extract_field_paths(v, full_key))
    elif isinstance(doc, list):
        for item in doc:
            paths.update(extract_field_paths(item, prefix))
    return paths

def update_schema_index(es, index_name, docs):
    """Update the schema-index with the set of unique field paths from all docs."""
    all_paths = set()
    for doc in docs:
        all_paths.update(extract_field_paths(doc))
    schema_doc = {
        "fields": sorted(list(all_paths)),
        "doc_count": len(docs)
    }
    # Use a fixed id so we always overwrite
    es.index(index=SCHEMA_INDEX, id="current", body=schema_doc)
    print(f"[populate] Updated schema-index with {len(all_paths)} fields.")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOG4_PATH = os.path.join(DATA_DIR, "log4.json")
CVE_PATH = os.path.join(DATA_DIR, "cve.json")

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def transform_log4(doc):
    # doc is the full log4.json, which contains 'components' array
    # This function is no longer used for single doc, but kept for compatibility
    return doc

def transform_cve(doc):
    osv = doc.get("cve", {}).get("osv", {})
    cve_id = osv.get("id") or doc.get("cve", {}).get("kev", {}).get("cveID")
    description = osv.get("details") or doc.get("cve", {}).get("kev", {}).get("shortDescription")
    affected = osv.get("affected", [])
    packages = []
    for aff in affected:
        pkg = aff.get("package", {})
        if pkg:
            packages.append({
                "ecosystem": pkg.get("ecosystem"),
                "name": pkg.get("name"),
                "purl": pkg.get("purl")
            })
    flat = {
        "id": cve_id or "CVE-UNKNOWN",
        "type": "cve",
        "description": description,
        "affected_packages": packages,
        "original": doc
    }
    return flat

def get_es_client():
    return Elasticsearch(f"http://{ES_HOST}:{ES_PORT}")

def wait_for_es(es, timeout=180, interval=2):
    """Wait for Elasticsearch to be available before proceeding."""
    start = time.time()
    while True:
        try:
            if es.ping():
                print("Elasticsearch is available.")
                return True
        except Exception as e:
            print(f"Waiting for Elasticsearch... {e}")
        if time.time() - start > timeout:
            raise RuntimeError("Timed out waiting for Elasticsearch to be available.")
        time.sleep(interval)

def reset_index(es, index_name):
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
    es.indices.create(index=index_name, ignore=400)

def index_document(es, index_name, doc):
    es.index(index=index_name, id=doc["id"], body=doc)

def process_and_index_file(es, path, transform_func, collected_docs=None):
    doc = load_json(path)
    # Special handling for log4.json: index each component as a separate doc
    if path.endswith("log4.json") and isinstance(doc, dict) and "components" in doc:
        for comp in doc["components"]:
            comp["type"] = "component"
            # Use sbom_id or package.name+version as id if available
            doc_id = comp.get("sbom_id") or comp.get("package", {}).get("name") or None
            if not doc_id:
                doc_id = str(hash(json.dumps(comp)))
            es.index(index=INDEX_NAME, id=doc_id, body=comp)
            if collected_docs is not None:
                collected_docs.append(comp)
    else:
        doc = transform_func(doc)
        index_document(es, INDEX_NAME, doc)
        if collected_docs is not None:
            collected_docs.append(doc)

def populate():
    es = get_es_client()
    wait_for_es(es)
    reset_index(es, INDEX_NAME)
    # Also reset schema-index
    if es.indices.exists(index=SCHEMA_INDEX):
        es.indices.delete(index=SCHEMA_INDEX)
    es.indices.create(index=SCHEMA_INDEX, ignore=400)
    # Collect all docs for schema extraction
    all_docs = []
    process_and_index_file(es, LOG4_PATH, transform_log4, collected_docs=all_docs)
    process_and_index_file(es, CVE_PATH, transform_cve, collected_docs=all_docs)
    update_schema_index(es, INDEX_NAME, all_docs)

if __name__ == "__main__":
    populate()
