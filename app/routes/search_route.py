from app.app import app, db
import os
from flask import render_template, request, jsonify
from elasticsearch import Elasticsearch
from Utils.elastic_search import sync_to_elasticsearch

# Trigger Elasticsearch sync manually
@app.route('/elastic_update')
def elastic_update():
    sync_to_elasticsearch(db)
    return "Elastic executed manually!"

@app.route('/search')
def search_html():
    return render_template('pages/search.html')

@app.route('/api/search_software')
def search():
    elastic_host = os.getenv('ELASTIC_HOST')
    elastic_port = os.getenv('ELASTIC_PORT')

    es = Elasticsearch(hosts=[f"http://{elastic_host}:{elastic_port}"], request_timeout=60)
    query_str = request.args.get("q")
    if not query_str:
        return jsonify({"error": "Missing 'q' query parameter"}), 400

    query_str = query_str.lower()  # lowercase the input for case-insensitive prefix

    query = {
        "query": {
            "prefix": {
                "name.lowercase": query_str
            }
        }
    }

    response = es.search(index="softwares", body=query, size=100)
    results = [hit["_source"] for hit in response["hits"]["hits"]]

    return jsonify(results)


@app.route('/api/search_document')
def search_document():
    elastic_host = os.getenv('ELASTIC_HOST')
    elastic_port = os.getenv('ELASTIC_PORT')

    es = Elasticsearch(hosts=[f"http://{elastic_host}:{elastic_port}"], request_timeout=60)
    query_str = request.args.get("q")
    if not query_str:
        return jsonify({"error": "Missing 'q' query parameter"}), 400

    query = {
        "query": {
            "match": {
                "title": query_str
            }
        }
    }

    response = es.search(index="titles", body=query, size=100)
    results = [hit["_source"] for hit in response["hits"]["hits"]]

    return jsonify(results)

@app.route('/api/search_author')
def search_author():
    elastic_host = os.getenv('ELASTIC_HOST')
    elastic_port = os.getenv('ELASTIC_PORT')

    es = Elasticsearch(hosts=[f"http://{elastic_host}:{elastic_port}"], request_timeout=60)
    query_str = request.args.get("q")
    if not query_str:
        return jsonify({"error": "Missing 'q' query parameter"}), 400

    query_str = query_str.lower()

    query = {
        "query": {
            "bool": {
                "should": [
                    {"prefix": {"first_name": query_str}},
                    {"prefix": {"last_name": query_str}}
                ]
            }
        }
    }

    response = es.search(index="authors", body=query, size=100)
    results = [
        {
            "first_name": hit["_source"]["first_name"],
            "last_name": hit["_source"]["last_name"],
            "author_id": hit["_source"].get("author_id")
        }
        for hit in response["hits"]["hits"]
    ]
    return jsonify(results)

@app.route('/api/search_structure')
def search_structures():
    elastic_host = os.getenv('ELASTIC_HOST')
    elastic_port = os.getenv('ELASTIC_PORT')

    es = Elasticsearch(hosts=[f"http://{elastic_host}:{elastic_port}"], request_timeout=60)
    query_str = request.args.get("q", "").lower().strip()
    if not query_str:
        return jsonify({"error": "Missing 'q' query parameter"}), 400

    query = {
        "query": {
            "bool": {
                "should": [
                    {
                        "prefix": {
                            "struct_acronym": {
                                "value": query_str,
                                "boost": 2.0  # Boost acronym matches
                            }
                        }
                    },
                    {
                        "match": {
                            "structure": {
                                "query": query_str,
                                "operator": "and"
                            }
                        }
                    }
                ],
                "minimum_should_match": 1
            }
        }
    }

    response = es.search(index="structures", body=query, size=100)

    # Deduplicate by structure_id
    seen_ids = set()
    results = []
    for hit in response["hits"]["hits"]:
        source = hit["_source"]
        structure_id = source.get("structure_id")
        if structure_id and structure_id not in seen_ids:
            seen_ids.add(structure_id)
            results.append({
                "structure": source["structure"],
                "struct_acronym": source.get("struct_acronym", ""),
                "structure_id": structure_id
            })

    return jsonify(results)

@app.route('/api/search_url')
def search_url():
    elastic_host = os.getenv('ELASTIC_HOST')
    elastic_port = os.getenv('ELASTIC_PORT')

    es = Elasticsearch(hosts=[f"http://{elastic_host}:{elastic_port}"], request_timeout=60)
    query_str = request.args.get("q", "").lower().strip()
    if not query_str:
        return jsonify([])

    query = {
        "query": {
            "multi_match": {
                "query": query_str,
                "fields": [
                    "url^3",          # autocomplete field (boosted)
                    "url_exact^5"     # exact match strongly boosted
                ],
                "type": "best_fields",
                "fuzziness": "AUTO"
            }
        }
    }

    response = es.search(index="urls", body=query, size=50)

    results = [
        {
            "doc_id": hit["_source"]["doc_id"],
            "url": hit["_source"].get("url_exact", hit["_source"].get("url"))
        }
        for hit in response["hits"]["hits"]
    ]

    return jsonify(results)




