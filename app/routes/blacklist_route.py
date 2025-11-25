from app.app import app, db
from flask import jsonify
import csv
import os


BLACKLIST_PATH = './app/static/data/blacklist.csv'


@app.route('/update_blacklist/<software_name>')
def update_blacklist(software_name):
    # Normalize software name
    software_name = software_name.strip().lower()

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
    # Example placeholder (modify for your DB model)
    # from app.models import Blacklist
    #
    # Read CSV and sync with DB

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
