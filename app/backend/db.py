import os
import json
import tempfile
import urllib.request
import urllib.parse
import urllib.error
from typing import List, Optional, Dict, Any

from app.shared.schemas import DocumentRecord


def is_supabase_configured() -> bool:
    url = os.getenv("SUPABASE_URL", "").strip()
    key = os.getenv("SUPABASE_KEY", "") or os.getenv("SUPABASE_SERVICE_ROLE_KEY", "") or os.getenv("SUPABASE_ANON_KEY", "")
    return bool(url and key.strip())


def get_supabase_headers() -> Dict[str, str]:
    key = os.getenv("SUPABASE_KEY", "") or os.getenv("SUPABASE_SERVICE_ROLE_KEY", "") or os.getenv("SUPABASE_ANON_KEY", "")
    key = key.strip()
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }


def get_db_dir() -> str:
    primary_dir = "outputs/db"
    try:
        os.makedirs(primary_dir, exist_ok=True)
        # Test writable check
        test_path = os.path.join(primary_dir, ".write_test")
        with open(test_path, "w") as f:
            f.write("ok")
        os.remove(test_path)
        return primary_dir
    except (OSError, PermissionError):
        tmp_dir = os.path.join(tempfile.gettempdir(), "outputs", "db")
        os.makedirs(tmp_dir, exist_ok=True)
        return tmp_dir


def save_record(record: DocumentRecord) -> None:
    if is_supabase_configured():
        try:
            supabase_url = os.getenv("SUPABASE_URL", "").rstrip("/")
            endpoint = f"{supabase_url}/rest/v1/document_records"
            headers = get_supabase_headers()
            headers["Prefer"] = "resolution=merge-duplicates"

            payload = {
                "document_id": record.document_id,
                "document_type": record.document_type.value,
                "record_status": record.record_status.value,
                "record_data": record.model_dump(mode="json"),
            }

            req = urllib.request.Request(
                endpoint,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=10) as res:
                if res.status in [200, 201, 204]:
                    # Also log to local file as backup if directory is writable
                    _save_record_file(record)
                    return
        except Exception as e:
            # Fallback to local file if Supabase HTTP call fails
            print(f"[Database Warning] Supabase save failed: {e}. Falling back to file store.")

    _save_record_file(record)


def _save_record_file(record: DocumentRecord) -> None:
    try:
        db_dir = get_db_dir()
        path = os.path.join(db_dir, f"{record.document_id}.json")
        with open(path, "w", encoding="utf-8") as f:
            f.write(record.model_dump_json(indent=2))
    except Exception as e:
        print(f"[Database Error] Local file save failed: {e}")


def load_record(doc_id: str) -> Optional[DocumentRecord]:
    if is_supabase_configured():
        try:
            supabase_url = os.getenv("SUPABASE_URL", "").rstrip("/")
            query = urllib.parse.urlencode({"document_id": f"eq.{doc_id}", "select": "record_data"})
            endpoint = f"{supabase_url}/rest/v1/document_records?{query}"
            headers = get_supabase_headers()

            req = urllib.request.Request(endpoint, headers=headers, method="GET")
            with urllib.request.urlopen(req, timeout=10) as res:
                if res.status == 200:
                    data = json.loads(res.read().decode("utf-8"))
                    if data and isinstance(data, list) and len(data) > 0:
                        rec_dict = data[0].get("record_data")
                        if rec_dict:
                            return DocumentRecord.model_validate(rec_dict)
        except Exception as e:
            print(f"[Database Warning] Supabase load failed for '{doc_id}': {e}. Trying file store.")

    return _load_record_file(doc_id)


def _load_record_file(doc_id: str) -> Optional[DocumentRecord]:
    possible_dirs = [get_db_dir(), "outputs/db", os.path.join(tempfile.gettempdir(), "outputs", "db")]
    for db_dir in possible_dirs:
        path = os.path.join(db_dir, f"{doc_id}.json")
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return DocumentRecord.model_validate_json(f.read())
            except Exception:
                continue
    return None


def list_records() -> List[DocumentRecord]:
    records = []
    if is_supabase_configured():
        try:
            supabase_url = os.getenv("SUPABASE_URL", "").rstrip("/")
            endpoint = f"{supabase_url}/rest/v1/document_records?select=record_data"
            headers = get_supabase_headers()

            req = urllib.request.Request(endpoint, headers=headers, method="GET")
            with urllib.request.urlopen(req, timeout=10) as res:
                if res.status == 200:
                    data = json.loads(res.read().decode("utf-8"))
                    if isinstance(data, list):
                        for item in data:
                            rec_dict = item.get("record_data")
                            if rec_dict:
                                try:
                                    records.append(DocumentRecord.model_validate(rec_dict))
                                except Exception:
                                    pass
                        if records:
                            return records
        except Exception as e:
            print(f"[Database Warning] Supabase list failed: {e}. Falling back to file store.")

    # Fallback to local file store
    db_dir = get_db_dir()
    if os.path.exists(db_dir):
        for fname in os.listdir(db_dir):
            if fname.endswith(".json"):
                doc_id = fname[:-5]
                rec = _load_record_file(doc_id)
                if rec:
                    records.append(rec)
    return records
