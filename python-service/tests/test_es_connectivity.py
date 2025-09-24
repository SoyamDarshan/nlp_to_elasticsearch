import requests
import os

ES_HOST = os.environ.get('ES_HOST', 'elasticsearch')
ES_PORT = os.environ.get('ES_PORT', '9200')

url = f'http://{ES_HOST}:{ES_PORT}'

try:
    print(f'Testing connection to {url} ...')
    resp = requests.get(url, timeout=10)
    print(f'Status code: {resp.status_code}')
    print(f'Body: {resp.text}')
except Exception as e:
    print(f'Error connecting to Elasticsearch: {e}')
