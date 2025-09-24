import os
import logging
import subprocess
import json
from flask import Blueprint, request, jsonify
from elasticsearch import Elasticsearch
from llm import generate_elasticsearch_query, GeminiRateLimitExceeded

ES_HOST = os.environ.get("ES_HOST", "elasticsearch")
ES_PORT = os.environ.get("ES_PORT", "9200")
ES_INDEX = os.environ.get("ES_INDEX", "nlp_index")
es = Elasticsearch(f'http://{ES_HOST}:{ES_PORT}')
api_bp = Blueprint('api', __name__)
logger = logging.getLogger("api")

def repopulate_es_index():
    """Call the ES repopulation script and return (success, output)."""
    try:
        result = subprocess.run(['python', 'populate_elasticsearch.py'], capture_output=True, text=True, cwd=os.path.dirname(__file__))
        logger.info(f"[API] Repopulate ES output: {result.stdout}")
        if result.returncode == 0:
            return True, result.stdout
        else:
            logger.error(f"[API] Repopulate ES error: {result.stderr}")
            return False, result.stderr
    except Exception as e:
        logger.error(f"[API] Repopulate ES exception: {e}")
        return False, f"Exception: {type(e).__name__}: {e}"


# --- Template schemas ---

def schema_template_a(hit):
    # Component/Package: type == 'component' (strict)
    src = hit.get('_source', {})
    return src.get('type', '').lower() == 'component'

def schema_template_b(hit):
    # CVE: type == 'cve' (strict)
    src = hit.get('_source', {})
    return src.get('type', '').lower() == 'cve'

def parse_hits_with_template(hits):
    parsed = []
    for hit in hits:
        if schema_template_b(hit):
            parsed.append({'template': 'TemplateB', 'data': hit})
        elif schema_template_a(hit):
            parsed.append({'template': 'TemplateA', 'data': hit})
        else:
            parsed.append({'template': 'Unknown', 'data': hit})
    return parsed

def detect_intent_from_response(hits):
    if not hits:
        return 'package'
    all_b = all(schema_template_b(hit) for hit in hits)
    if all_b:
        return 'cve'
    all_a = all(schema_template_a(hit) for hit in hits)
    if all_a:
        return 'package'
    return 'mixed'

@api_bp.route('/repopulate-es', methods=['POST'])
def repopulate_es():
    try:
        success, output = repopulate_es_index()
        if success:
            return jsonify({"status": "success", "output": output})
        else:
            logger.error(f"[API] Repopulate ES failed: {output}")
            return jsonify({"status": "error", "error": output}), 500
    except Exception as e:
        logger.error(f"[API] Repopulate ES endpoint exception: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500





def get_system_prompt():
    return (
        "You are an expert in Elasticsearch. "
        "Given a user's natural language prompt, generate a minimal Elasticsearch JSON query (no explanations, just the JSON) "
        "that would retrieve relevant records from an index with fields: id, name, category, value, and also nested fields like components.package.name, components.package.desc, components.package.friendly_name, components.package.version. "
        "If the prompt is about a CVE, search for the id field (e.g., CVE-2020-1472). "
        "If the prompt is about a component, search for both root-level fields and nested fields under components.package.*. "
        "If the prompt is ambiguous, return a match_all query."
    )

def log_llm_prompt(prompt):
    system_prompt = get_system_prompt()
    full_prompt = f"{system_prompt}\nPrompt: {prompt}\nElasticsearch Query:"
    logger.info(f"[API] LLM full prompt sent to Gemini:\n{full_prompt}")

def get_es_query(prompt):
    try:
        es_query = generate_elasticsearch_query(prompt)
        logger.info(f"[API] LLM-generated ES query: {json.dumps(es_query, indent=2)}")
        return es_query, None
    except GeminiRateLimitExceeded as e:
        logger.error("[API] Gemini rate-limit exceeded, raising error.")
        return None, str(e)

def execute_es_query(es_query):
    logger.info(f"[API] Executing ES query: {json.dumps(es_query, indent=2)}")
    results = es.search(index=ES_INDEX, body=es_query, size=100)
    # Convert ObjectApiResponse to dict for logging/processing
    if hasattr(results, 'body'):
        results_dict = results.body
    else:
        results_dict = dict(results)
    logger.info(f"[API] Raw ES response: {json.dumps(results_dict, indent=2)[:2000]}")
    hits = results_dict['hits']['hits']
    logger.info(f"[API] ES hits returned: {json.dumps(hits, indent=2)}")
    return hits

def handle_show_all(hits):
    parsed_hits = parse_hits_with_template(hits)
    intent = detect_intent_from_response(hits)
    response = {'intent': intent, 'results': parsed_hits}
    logger.info(f"[API] Sending all ES docs: {len(parsed_hits)} docs")
    return jsonify(response)

def handle_single_result(hits):
    if hits:
        parsed_hit = parse_hits_with_template([hits[0]])[0]
        intent = detect_intent_from_response([hits[0]])
    else:
        parsed_hit = None
        intent = detect_intent_from_response([])
    logger.info(f"[API] ES search hit: {hits[0] if hits else None}")
    response = {'intent': intent, 'results': parsed_hit}
    logger.info(f"[API] Sending single ES doc response: {response}")
    return jsonify(response)

@api_bp.route('/process', methods=['POST'])
def process():
    try:
        data = request.json
        prompt = data.get('prompt', '')
        logger.info(f"[API] Received prompt: {prompt}")
        log_llm_prompt(prompt)
        es_query, rate_limit_error = get_es_query(prompt)
        if rate_limit_error:
            return jsonify({'intent': 'error', 'results': None, 'error': 'Gemini rate-limit exceeded: ' + rate_limit_error}), 500
        try:
            hits = execute_es_query(es_query)
            if prompt.strip().lower() in ["show all", "show all documents", "show all es docs", "show all elasticsearch documents"]:
                return handle_show_all(hits)
            return handle_single_result(hits)
        except Exception as e:
            logger.error(f"[API] ES search failed ({e})")
            response = {"intent": "error", "results": None}
            logger.info(f"[API] Sending ES response: {response}")
            return jsonify(response), 500
    except Exception as e:
        logger.error(f"[API] Unexpected error in /process: {e}")
        response = {"intent": "error", "results": None, "error": str(e)}
        return jsonify(response), 500
