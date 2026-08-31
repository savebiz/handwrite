from __future__ import annotations
import os
import sys
import traceback

# Ensure root directory is on sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

try:
    from app.backend.main import app
    handler = app
except Exception as err:
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse

    app = FastAPI(title="HandWrite Verify API (Error Fallback)")

    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
    async def catch_all(path: str):
        tb = traceback.format_exc()
        return JSONResponse(
            status_code=500,
            content={
                "error": "Serverless Function Startup Error",
                "detail": str(err),
                "traceback": tb.split("\n"),
            },
        )
    handler = app
