import threading
import uuid

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.importer import PartsFileError, import_parts
from app.search import vocabulary
from app.vision import provider_status

router = APIRouter(prefix="/api/admin", tags=["admin"])

MAX_IMPORT_BYTES = 200 * 1024 * 1024
_jobs: dict[str, dict] = {}
_import_lock = threading.Lock()


def _run_import(job_id: str, data: bytes, filename: str, sheet: str | None) -> None:
    job = _jobs[job_id]

    def progress(stage: str, info: dict) -> None:
        job["stage"] = stage
        job["info"] = info

    try:
        with _import_lock:
            job["stats"] = import_parts(data, filename, sheet, progress=progress)
        job["status"] = "done"
        vocabulary.invalidate()
    except PartsFileError as exc:
        job.update(status="error", error=str(exc))
    except Exception as exc:  # surfaced to the admin UI
        job.update(status="error", error=f"{type(exc).__name__}: {exc}")


@router.post("/import-parts", status_code=202)
async def start_import(file: UploadFile = File(...), sheet: str | None = Form(None)):
    name = (file.filename or "").lower()
    if not name.endswith((".xlsx", ".xlsm", ".xls", ".xlsb", ".csv")):
        raise HTTPException(415, "Upload an Excel or CSV file")
    data = await file.read()
    if len(data) > MAX_IMPORT_BYTES:
        raise HTTPException(413, "File too large (max 200 MB)")
    if _import_lock.locked():
        raise HTTPException(409, "Another import is already running")
    job_id = uuid.uuid4().hex[:12]
    _jobs[job_id] = {"id": job_id, "status": "running", "stage": "queued", "info": {}, "stats": None, "error": None}
    threading.Thread(target=_run_import, args=(job_id, data, file.filename, sheet or None), daemon=True).start()
    return _jobs[job_id]


@router.get("/import-jobs/{job_id}")
def import_job(job_id: str):
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(404, "Unknown import job")
    return job


@router.get("/config")
def config():
    provider, configured = provider_status()
    return {"vision_provider": provider, "vision_configured": configured}
