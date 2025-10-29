from flask import Flask, render_template
from pyArango.connection import Connection
from Utils.db import insert_json_db
from Utils.home import home_data
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from Utils.elastic_search import sync_to_elasticsearch
import os

app = Flask(__name__,template_folder='templates',static_folder='static')

#app.config['ARANGO_HOST'] = 'arangodb'
app.config['ARANGO_HOST'] = 'coar-notify-inria-hal-arangodb-1'
app.config['ARANGO_PORT'] = 8529
app.config['ARANGO_DB'] = 'SOF-viz-COAR'
app.config['ARANGO_USERNAME'] = os.getenv('ARANGO_LOGIN', 'root')
app.config['ARANGO_PASSWORD'] = os.getenv('ARANGO_PASSWORD', 'changeme')
def init_db():
    global db
    db = Connection(
        arangoURL='http://{host}:{port}'.format(
            host=app.config['ARANGO_HOST'],
            port=app.config['ARANGO_PORT']
        ),
        username=app.config['ARANGO_USERNAME'],
        password=app.config['ARANGO_PASSWORD']
    )
    if not db.hasDatabase('SOF-viz-COAR'):
        db.createDatabase('SOF-viz-COAR')
    db = Connection(
        arangoURL='http://{host}:{port}'.format(
            host=app.config['ARANGO_HOST'],
            port=app.config['ARANGO_PORT']
        ),
        username=app.config['ARANGO_USERNAME'],
        password=app.config['ARANGO_PASSWORD']
    )[app.config['ARANGO_DB']]

init_db()  # Call the init_db function to initialize the db variable


structure = None
global data_dashboard
data_dashboard = None
# data_dashboard = dashboard(db, structure)

# --- Import routes ---
from app.routes import doc_route, dashboard_route, reset_db, software_route, api_route, disambiguate_route, author_route

# --- Scheduler for Elasticsearch Sync ---
scheduler = BackgroundScheduler()
scheduler.add_job(
    func=sync_to_elasticsearch,
    trigger="interval",
    hours=24,
    args=[db]  # Pass the ArangoDB connection to the job
)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

# --- Flask Routes ---
@app.route('/')
def home():
    data = home_data(db)
    return render_template('pages/home.html', data=data[0])

# Trigger Elasticsearch sync manually
@app.route('/elastic_update')
def run_task():
    sync_to_elasticsearch(db)
    return "Elastic executed manually!"
