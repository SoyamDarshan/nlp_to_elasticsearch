
# --- LLM Utilities ---
import os
import json
import re
from dotenv import load_dotenv
load_dotenv()
import google.generativeai as genai
from google.api_core import exceptions

class GeminiRateLimitExceeded(Exception):
    pass

def fetch_schema_fields():
    """Fetch schema fields from schema-index in Elasticsearch."""
    from elasticsearch import Elasticsearch
    ES_HOST = os.environ.get("ES_HOST", "localhost")
    ES_PORT = os.environ.get("ES_PORT", "9200")
    SCHEMA_INDEX = "schema-index"
    es = Elasticsearch(f"http://{ES_HOST}:{ES_PORT}")
    try:
        schema_doc = es.get(index=SCHEMA_INDEX, id="current")['_source']
        return schema_doc.get('fields', [])
    except Exception:
        return []

def build_system_prompt(schema_fields):
    schema_str = ", ".join(schema_fields) if schema_fields else "id, name, category, value, package.name, package.friendly_name, package.desc, package.version"
    return (
        "You are an expert in Elasticsearch. "
        "Given a user's natural language prompt, generate a minimal Elasticsearch JSON query (no explanations, just the JSON) "
        f"that would retrieve relevant records from an index with these available fields: {schema_str}. "
        "If the prompt is about a CVE, search for the value in all likely fields, including: id, original.cve.epss.cve, original.cve.kev.cveID, original.cve.osv.affected.package.name, and any other field that could contain a CVE identifier. "
        "If the prompt is about a component, search for both root-level fields and nested fields under package.name and package.friendly_name. "
        "For example, if the user prompt is a component name like 'Log4jScanner', match on package.friendly_name and package.name fields. "
        "If the prompt is ambiguous, return a match_all query."
    )

def parse_llm_response(text):
    """Parse LLM response and extract valid Elasticsearch query dict."""
    match = re.search(r'\{[\s\S]*\}', text)
    if match:
        try:
            parsed = json.loads(match.group(0))
            if 'query' in parsed:
                return parsed
            if any(k in parsed for k in ["match", "multi_match", "bool", "match_all"]):
                return {"query": parsed}
        except Exception:
            pass
    return None

def generate_elasticsearch_query(prompt):
    import logging
    logger = logging.getLogger("llm")
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        logger.error("[LLM] No GEMINI_API_KEY found. Cannot generate query.")
        raise RuntimeError("No GEMINI_API_KEY found. LLM query generation is required.")
    genai.configure(api_key=api_key)
    model_name = os.environ.get('GEMINI_MODEL', 'models/gemini-1.5-pro-latest')
    logger.info(f"[LLM] Using Gemini model: {model_name}")
    model = genai.GenerativeModel(model_name)
    schema_fields = fetch_schema_fields()
    logger.info(f"[LLM] Loaded schema fields from schema-index: {schema_fields}")
    system_prompt = build_system_prompt(schema_fields)
    full_prompt = f"{system_prompt}\nPrompt: {prompt}\nElasticsearch Query:"
    try:
        response = model.generate_content(full_prompt)
        text = response.text.strip()
        parsed = parse_llm_response(text)
        if parsed:
            return parsed
        logger.error("[LLM] LLM did not return a valid Elasticsearch query.")
        raise RuntimeError("LLM did not return a valid Elasticsearch query.")
    except exceptions.ResourceExhausted as e:
        raise GeminiRateLimitExceeded(str(e))
    except Exception as e:
        logger.error(f"[LLM] LLM query generation failed: {e}")
        raise RuntimeError("LLM query generation failed.")
