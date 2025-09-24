import unittest
import os
from unittest.mock import patch, MagicMock
from populate_elasticsearch import (
    load_json, transform_log4, transform_cve, get_es_client, reset_index, index_document, process_and_index_file, LOG4_PATH, CVE_PATH
)

class TestPopulateElasticsearch(unittest.TestCase):
    def test_load_json_log4(self):
        loaded = load_json(LOG4_PATH)
        self.assertIsInstance(loaded, dict)
        self.assertEqual(loaded["id"], "log4jscanner")
        self.assertEqual(loaded["type"], "component")

    def test_load_json_cve(self):
        loaded = load_json(CVE_PATH)
        self.assertIsInstance(loaded, dict)
        self.assertIn("cve", loaded)
        self.assertIn("osv", loaded["cve"])

    def test_transform_log4_real(self):
        doc = load_json(LOG4_PATH)
        result = transform_log4(dict(doc))
        self.assertEqual(result["type"], "component")
        self.assertEqual(result["id"], "log4jscanner")
        self.assertIn("description", result)

    def test_transform_cve_real(self):
        doc = load_json(CVE_PATH)
        result = transform_cve(doc)
        self.assertEqual(result["type"], "cve")
        self.assertIn("id", result)
        self.assertIn("affected_packages", result)
        self.assertIn("original", result)
        self.assertIsInstance(result["affected_packages"], list)

    @patch("populate_elasticsearch.Elasticsearch")
    def test_reset_index(self, mock_es):
        es = mock_es.return_value
        es.indices.exists.return_value = True
        reset_index(es, "test_index")
        es.indices.delete.assert_called_with(index="test_index")
        es.indices.create.assert_called_with(index="test_index", ignore=400)

    @patch("populate_elasticsearch.Elasticsearch")
    def test_index_document(self, mock_es):
        es = mock_es.return_value
        doc = {"id": "foo", "type": "bar"}
        index_document(es, "test_index", doc)
        es.index.assert_called_with(index="test_index", id="foo", body=doc)

    @patch("populate_elasticsearch.index_document")
    @patch("populate_elasticsearch.load_json")
    def test_process_and_index_file(self, mock_load_json, mock_index_document):
        # Use real log4.json data for this test
        real_doc = load_json(LOG4_PATH)
        mock_load_json.return_value = real_doc
        process_and_index_file(MagicMock(), LOG4_PATH, transform_log4)
        mock_load_json.assert_called_with(LOG4_PATH)
        mock_index_document.assert_called()

if __name__ == "__main__":
    unittest.main()
