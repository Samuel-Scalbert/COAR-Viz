import os
import json
import requests
from flask import request, jsonify
from xml.sax.saxutils import unescape
from xml.dom import minidom
from app.app import app, db
from Utils.db import insert_json_db
import re

'''@app.before_request
def debug_request():
    print("=== Incoming Request Debug ===")
    print("Path:", request.path)
    print("Method:", request.method)
    print("Content-Type:", request.content_type)
    print("Headers:", dict(request.headers))
    print("Form keys:", list(request.form.keys()))
    print("Files keys:", list(request.files.keys()))
    print("================================\n")'''


def ensure_folder(path):
    os.makedirs(path, exist_ok=True)
    return path


def save_xml(hal_id, xml_content, folder="./app/static/data/xml"):
    ensure_folder(folder)
    xml_path = os.path.join(folder, f"{hal_id}.xml")

    # Unescape XML entities first (HAL sometimes double-encodes)
    decoded_xml = unescape(xml_content)

    # Escape stray ampersands not part of a valid entity
    # (matches & not followed by # or a word+semicolon)
    safe_xml = re.sub(r'&(?!#?\w+;)', '&amp;', decoded_xml)

    try:
        xml_parsed = minidom.parseString(safe_xml)
        pretty_xml = xml_parsed.toprettyxml(indent="  ", encoding="utf-8")
    except Exception as e:
        pretty_xml = safe_xml.encode("utf-8")

    with open(xml_path, "wb") as f:
        f.write(pretty_xml)

    return xml_path


def save_json(file, folder="./app/static/data/json"):
    ensure_folder(folder)
    if hasattr(file, "read"):
        file.seek(0)
        data_json = json.load(file)
        file_name = getattr(file, "filename", "unnamed").replace(".software.json", "")
    else:
        data_json = file
        file_name = data_json.get("file_hal_id", "unnamed")
    json_path = os.path.join(folder, f"{file_name}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data_json, f, ensure_ascii=False, indent=4)
    return json_path


@app.route('/insert_json', methods=['POST'])
def insert_json():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    hal_id = request.form.get("document_id")
    hal_id = hal_id.replace('"', "")

    # Download HAL TEI XML
    url = "https://api.archives-ouvertes.fr/search/"
    if hal_id[-2] == "v":
        hal_id_cleaned_wt_version = hal_id[:-2]
        params = {"q": f"halId_id:{hal_id_cleaned_wt_version}", "fl": "label_xml", "wt": "xml-tei"}
    else:
        params = {"q": f"halId_id:{hal_id}", "fl": "label_xml", "wt": "xml-tei"}
    try:
        response = requests.get(url, params=params, timeout=30)
        if response.status_code != 200:
            return jsonify(
                {"error": f"Could not download XML for the file {hal_id}, status code: {response.status_code}"}), 500
        data = response.text
        decoded_xml = unescape(data)
        xml_path = save_xml(hal_id, decoded_xml)
    except Exception as e:
        return jsonify({"error": f"Exception while downloading XML: {str(e)}"}), 500

    try:
        json_path = save_json(file)
    except Exception as e:
        return jsonify({"error": f"Exception while saving JSON: {str(e)}"}), 500

    print(os.listdir("./app/static/data/json"), os.listdir("./app/static/data/xml"))

    try:
        print(insert_json_db("./app/static/data/json", "./app/static/data/xml", db))
        print('id:',hal_id)
        listinserted = db.AQLQuery(f'FOR hal_id in documents RETURN hal_id.file_hal_id', rawResults=True, batchSize=2000)
        print('list inserted:',listinserted)
        files_registered = db.AQLQuery(f'FOR hal_id in documents filter hal_id.file_hal_id == "{hal_id}" RETURN hal_id._id', rawResults=True, batchSize=2000)
        print('answer query:',files_registered)
        inserted = True
        if inserted == True:
            try:
                if os.path.exists(xml_path):
                    os.remove(xml_path)
                if os.path.exists(json_path):
                    os.remove(json_path)
            except Exception as e:
                print(f"Error deleting files: {e}")
            return jsonify({
                "status": "inserted",
                "file": file.filename,
                "xml_path": xml_path,
                "json_path": json_path
            }), 201
        elif inserted == False:
            return jsonify({"status": "already registered", "file": file.filename}), 409
        else:
            return jsonify({"error": f"Database insertion failed: {str(inserted)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Database insertion failed: {str(e)}"}), 500