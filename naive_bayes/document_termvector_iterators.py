"""
Document termvector iterators iterate over training or test documents and their termvectors.
"""

import csv

import requests

ELASTIC_SEARCH_TERMVECTORS = "{protocol}://{address}:{port}/{index_name}/{index_type}/_termvectors"
ELASTIC_SEARCH_DOCUMENT_TERMVECTORS = "{protocol}://{address}:{port}/{index_name}/{index_type}/{i}/_termvectors"
ELASTIC_SEARCH_DOCUMENT = "{protocol}://{address}:{port}/{index_name}/{index_type}/{i}"
ELASTIC_SEARCH_COUNT = "{protocol}://{address}:{port}/{index_name}/{index_type}/_count"


def elasticsearch_dti(index_name, index_type, max_docs=None, protocol="http", address="localhost", port=9200):
    session = requests.Session()
    answer = session.get(ELASTIC_SEARCH_COUNT.format(**locals()))
    doc_count = 0
    if "count" in answer.json():
        doc_count = answer.json()["count"]
    else:
        raise Exception("ElasticSearch did not respond with the number of documents for index %s" % index_name)
    if max_docs is not None:
        doc_count = min(doc_count, max_docs)
    for i in range(1, doc_count + 1):
        answer = session.get(ELASTIC_SEARCH_DOCUMENT.format(**locals()))
        document = answer.json()["_source"]
        query = {
            "fields": [
                "tweet"
            ],
            "positions": False,
            "offsets": False,
            "field_statistics": False,
            "term_statistics": False
        }
        answer = session.get(ELASTIC_SEARCH_DOCUMENT_TERMVECTORS.format(**locals()), json=query)
        term_vector = {key: value["term_freq"] for key, value in
                       answer.json()["term_vectors"]["tweet"]["terms"].items()}
        yield document, term_vector, doc_count


def csv_elasticsearch_dti(data_path, index_name, index_type, max_docs=None, protocol="http", address="localhost",
                          port=9200):
    session = requests.Session()
    documents = []

    with open(data_path, "rb") as data_file:
        reader = csv.DictReader(data_file)
        documents = list(reader)
    doc_count = len(documents)
    if max_docs is not None:
        doc_count = min(doc_count, max_docs)
    for document in documents[:doc_count]:
        query = {
            "doc": {
                "tweet": document["tweet"]
            },
            "fields": [
                "tweet"
            ],
            "positions": False,
            "offsets": False,
            "field_statistics": False,
            "term_statistics": False
        }
        answer = session.get(ELASTIC_SEARCH_TERMVECTORS.format(**locals()), json=query)
        term_vector = {key: value["term_freq"] for key, value in
                       answer.json()["term_vectors"]["tweet"]["terms"].items()}
        yield document, term_vector, doc_count
