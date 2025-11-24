import os
import json
import requests
from flask import request, jsonify
from xml.sax.saxutils import unescape
from xml.dom import minidom
from app.app import app, db
from Utils.db import insert_json_db, update_nb_notification, update_nb_accepted, update_nb_rejected
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
    final_log = {
        "step": "",
        "status": "",
        "hal_id": "",
        "file_name": "",
        "xml_download": "",
        "json_saved": "",
        "db_insertion": "",
        "paths": {},
        "errors": []
    }

    if "file" not in request.files:
        final_log["status"] = "error"
        final_log["errors"].append("No file provided")
        print(jsonify(final_log))
        return jsonify(final_log), 400

    file = request.files["file"]
    hal_id = request.form.get("document_id")
    final_log["hal_id"] = hal_id
    final_log["file_name"] = file.filename

    # -----------------------------
    # DOWNLOAD HAL TEI XML
    # -----------------------------
    final_log["step"] = "Downloading HAL TEI XML"
    url = "https://api.archives-ouvertes.fr/search/"

    if hal_id[-2] == "v":
        hal_id_cleaned_wt_version = hal_id[:-2]
        params = {"q": f"halId_id:{hal_id_cleaned_wt_version}", "fl": "label_xml", "wt": "xml-tei"}
    else:
        params = {"q": f"halId_id:{hal_id}", "fl": "label_xml", "wt": "xml-tei"}

    try:
        response = requests.get(url, params=params, timeout=30)
        if response.status_code != 200:
            final_log["status"] = "error"
            final_log["errors"].append(
                f"Could not download XML (status {response.status_code})"
            )
            print(jsonify(final_log))
            return jsonify(final_log), 500

        decoded_xml = unescape(response.text)
        xml_path = save_xml(hal_id, decoded_xml)
        final_log["xml_download"] = "success"
        final_log["paths"]["xml"] = xml_path

    except Exception as e:
        final_log["status"] = "error"
        final_log["errors"].append(f"Exception while downloading XML: {str(e)}")
        print(jsonify(final_log))
        return jsonify(final_log), 500

    # -----------------------------
    # SAVE JSON FILE
    # -----------------------------
    final_log["step"] = "Saving JSON file"
    try:
        json_path = save_json(file)
        final_log["json_saved"] = "success"
        final_log["paths"]["json"] = json_path
    except Exception as e:
        final_log["status"] = "error"
        final_log["errors"].append(f"Exception while saving JSON: {str(e)}")
        print(jsonify(final_log))
        return jsonify(final_log), 500

    # -----------------------------
    # DATABASE INSERTION
    # -----------------------------
    final_log["step"] = "Database insertion"

    try:
        files_registered = db.AQLQuery(
            f'FOR hal_id IN documents FILTER hal_id.file_hal_id == "{hal_id}" RETURN hal_id._id',
            rawResults=True,
            batchSize=2000
        )

        inserted = len(files_registered) == 0

        insert_json_db("./app/static/data/json", "./app/static/data/xml", db)

        if inserted:
            update_nb_notification(db, hal_id)
            final_log["db_insertion"] = "inserted"
            final_log["status"] = "success"
            final_log["step"] = "Completed"

            print(jsonify(final_log))
            return jsonify(final_log), 201

        else:
            final_log["db_insertion"] = "already_registered"
            final_log["status"] = "conflict"
            final_log["step"] = "Completed"

            print(jsonify(final_log))
            return jsonify(final_log), 409

    except Exception as e:
        final_log["status"] = "error"
        final_log["errors"].append(f"Database insertion failed: {str(e)}")
        print(jsonify(final_log))
        return jsonify(final_log), 500
