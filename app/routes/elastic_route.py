from app.app import app, db
from Utils.elastic_search import sync_to_elasticsearch

# Trigger Elasticsearch sync manually
@app.route('/elastic_update')
def elastic_update():
    sync_to_elasticsearch(db)
    return "Elastic executed manually!"
