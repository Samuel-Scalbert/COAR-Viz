import os
import json
import requests

def send_directory_to_inbox(directory_path, api_url="http://localhost:5000/insert_json"):
    """
    Sends all JSON files inside a directory to the /insert_json inbox endpoint.
    Each file is posted as multipart/form-data:
        - file (JSON file)
        - document_id (extracted from filename or JSON)
    """

    log_summary = {
        "directory": directory_path,
        "sent": 0,
        "success": 0,
        "failed": 0,
        "results": []
    }

    if not os.path.isdir(directory_path):
        return {"error": f"Path is not a directory: {directory_path}"}

    for filename in os.listdir(directory_path):
        if not filename.lower().endswith(".json"):
            continue

        json_path = os.path.join(directory_path, filename)
        base_name = os.path.splitext(filename)[0]

        # Try to extract HAL ID from filename: tel-01234567v1.json -> tel-01234567v1
        document_id = base_name

        # Optional: read JSON file in case HAL ID is inside
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                json_content = json.load(f)
                document_id = json_content.get("hal_id", document_id)
        except Exception:
            pass  # fallback to filename

        files = {
            "file": (filename, open(json_path, "rb"), "application/json")
        }
        data = {
            "document_id": document_id
        }

        print(f"➡️ Sending {filename} as {document_id} ...")

        try:
            response = requests.post(api_url, files=files, data=data, timeout=60)
            log_summary["sent"] += 1

            if response.status_code in (200, 201):
                print(f"   🟩 Success ({response.status_code})")
                log_summary["success"] += 1
            else:
                print(f"   🟥 Failed ({response.status_code}) -> {response.text}")
                log_summary["failed"] += 1

            log_summary["results"].append({
                "file": filename,
                "document_id": document_id,
                "status_code": response.status_code,
                "response": response.text
            })

        except Exception as e:
            print(f"   🟥 Error sending {filename}: {e}")
            log_summary["failed"] += 1
            log_summary["results"].append({
                "file": filename,
                "document_id": document_id,
                "error": str(e)
            })

    print("\n====== SUMMARY ======")
    print(json.dumps(log_summary, indent=4, ensure_ascii=False))
    print("=====================\n")

    return log_summary

send_directory_to_inbox("sandbox/json_files")
