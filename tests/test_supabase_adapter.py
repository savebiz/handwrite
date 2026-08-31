import os
import sys
import json
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath("."))

from app.backend.db import (
    is_supabase_configured,
    get_supabase_headers,
    get_db_dir,
    save_record,
    load_record,
    list_records,
)
from app.shared.schemas import (
    DocumentRecord,
    DocumentType,
    QualityResult,
    QualityStatus,
    RecordStatusEnum,
)


def build_test_record(doc_id="TEST-DB-001"):
    return DocumentRecord(
        run_id="run-db-test",
        document_id=doc_id,
        document_type=DocumentType.FIELD_INSPECTION,
        document_quality=QualityResult(status=QualityStatus.PASS),
        record_status=RecordStatusEnum.APPROVED,
    )


def test_01_is_supabase_configured():
    with patch.dict(os.environ, {"SUPABASE_URL": "https://test.supabase.co", "SUPABASE_KEY": "testkey123"}):
        assert is_supabase_configured() is True

    with patch.dict(os.environ, {"SUPABASE_URL": "", "SUPABASE_KEY": ""}, clear=True):
        assert is_supabase_configured() is False


def test_02_get_supabase_headers():
    with patch.dict(os.environ, {"SUPABASE_URL": "https://test.supabase.co", "SUPABASE_KEY": "testkey123"}):
        headers = get_supabase_headers()
        assert headers["apikey"] == "testkey123"
        assert headers["Authorization"] == "Bearer testkey123"
        assert headers["Content-Type"] == "application/json"


def test_03_get_db_dir_writable():
    db_dir = get_db_dir()
    assert os.path.exists(db_dir)


def test_04_save_load_list_local_file_fallback():
    with patch.dict(os.environ, {"SUPABASE_URL": "", "SUPABASE_KEY": ""}, clear=True):
        rec = build_test_record("TEST-FALLBACK-001")
        save_record(rec)

        loaded = load_record("TEST-FALLBACK-001")
        assert loaded is not None
        assert loaded.document_id == "TEST-FALLBACK-001"
        assert loaded.document_type == DocumentType.FIELD_INSPECTION

        all_recs = list_records()
        assert any(r.document_id == "TEST-FALLBACK-001" for r in all_recs)


def test_05_supabase_http_mock_save_and_load():
    with patch.dict(os.environ, {"SUPABASE_URL": "https://mock.supabase.co", "SUPABASE_KEY": "mockkey999"}):
        mock_res_save = MagicMock()
        mock_res_save.status = 201

        mock_res_load = MagicMock()
        mock_res_load.status = 200
        mock_record_data = build_test_record("TEST-SUPA-001").model_dump(mode="json")
        mock_res_load.read.return_value = json.dumps([{"record_data": mock_record_data}]).encode("utf-8")

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.return_value.__enter__.return_value = mock_res_save
            save_record(build_test_record("TEST-SUPA-001"))
            assert mock_urlopen.called

            mock_urlopen.return_value.__enter__.return_value = mock_res_load
            loaded = load_record("TEST-SUPA-001")
            assert loaded is not None
            assert loaded.document_id == "TEST-SUPA-001"
