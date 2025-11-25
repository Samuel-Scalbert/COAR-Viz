from app.app import app, db
import csv


@app.route('/update_blacklist/<software_name>')
def update_blacklist(software_name):
    return

@app.route('/update_db_blacklist')
def update_db_blacklist():
    return

@app.route('/blacklist')
def blacklist():
    blacklist = []
    with open('./app/static/data/blacklist.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # skip header
        for row in reader:
            if row:  # skip empty rows
                blacklist.append(row[0])
    return blacklist