from app.app import app, db
from flask import jsonify
import csv
import os


def delete_document_and_edges(db, doc_id, collection_name):

    edge_collections = [
        'edge_doc_to_struc',
        'edge_auth_to_struc',
        'edge_doc_to_software',
        'edge_doc_to_reference',
        'edge_doc_to_author',
        'edge_auth_to_rel_struc'
    ]

    # Delete all edges connected to this document
    for edge_name in edge_collections:
        edge_col = db[edge_name]
        query = f'''
        FOR edge IN {edge_name}
            FILTER edge._from == "{doc_id}" OR edge._to == "{doc_id}"
            REMOVE edge IN {edge_name}
        '''
        db.AQLQuery(query, rawResults=True)
        print(f"Deleted edges from collection: {edge_name}")

    # Delete the document itself
    collection = db[collection_name]
    doc = collection[doc_id.split('/')[-1]]  # extract the key from _id
    doc.delete()
    print(f"Deleted document: {doc_id}")

BLACKLIST_PATH = './app/static/data/blacklist.csv'


@app.route('/update_blacklist/<software_name>')
def update_blacklist(software_name):
    # Normalize software name
    software_name = software_name

    # Read existing blacklist
    existing = set()
    if os.path.exists(BLACKLIST_PATH):
        with open(BLACKLIST_PATH, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # skip header
            for row in reader:
                if row:
                    existing.add(row[0].lower())

    # Check if already added
    if software_name in existing:
        return jsonify({"message": "Software already in blacklist", "software": software_name})

    # Append new entry
    with open(BLACKLIST_PATH, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([software_name])

    return jsonify({"message": "Software added to blacklist", "software": software_name})


@app.route('/update_db_blacklist')
def update_db_blacklist():

    blacklist = []
    with open(BLACKLIST_PATH, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # skip header
        for row in reader:
            if row:  # skip empty rows
                blacklist.append(row[0])

    query = f'''
            FOR soft IN softwares return [soft._id,soft.software_name.normalizedForm]
            '''
    list_software_documents = db.AQLQuery(query, rawResults=True)
    for software_document in list_software_documents:
        print(software_document)
        if software_document[1] in blacklist:
            software_id = software_document[0]
            print(software_document, software_id)
            print('yo')
            #delete_document_and_edges(db, software_id, "softwares")

    return jsonify({"message": "Database blacklist updated"})


@app.route('/blacklist')
def blacklist():
    blacklist = []
    with open(BLACKLIST_PATH, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # skip header
        for row in reader:
            if row:  # skip empty rows
                blacklist.append(row[0])
    return jsonify(blacklist)
