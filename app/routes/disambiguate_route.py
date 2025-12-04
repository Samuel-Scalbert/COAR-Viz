from app.app import app, db
from flask import render_template, request, jsonify
from Utils.disambiguate import disambiguate_from_software, fetch_for_software


@app.route('/disambiguate')
def disambiguate():
    return render_template('pages/disambiguate.html')

@app.route('/api/disambiguate/list_software_search')
def list_software():
    query = f'''
            for software in softwares
            return distinct software.software_name.rawForm
            '''
    response = db.AQLQuery(query, rawResults=True, batchSize=2000)
    return list(response)

@app.route('/api/disambiguate/list_dup_software/<softwareName>')
def retrieve(softwareName):
    result = disambiguate_from_software(softwareName)
    return jsonify({'result': result})

@app.route('/api/disambiguate/fetch_data/<softwareName>/<docid>')
def fetch_data(softwareName, docid):
    result = fetch_for_software(softwareName,docid)
    return jsonify(result)
