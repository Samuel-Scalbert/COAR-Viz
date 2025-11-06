from flask import Flask, render_template
from pyArango.connection import Connection
from Utils.db import insert_json_db
from Utils.home import home_data
import os
from Utils.elastic_search import sync_to_elasticsearch

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
sync_to_elasticsearch(db)

structure = None
global data_dashboard
data_dashboard = None
#data_dashboard = dashboard(db, structure)

from app.routes import doc_route, dashboard_route,reset_db, software_route, api_route, disambiguate_route, author_route, search_route, inbox, elastic_route

@app.route('/')
def home():
    data = home_data(db)
    return render_template('pages/home.html', data=data[0])