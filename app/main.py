from __future__ import annotations

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.database import init_db
from app.review_engine import review_code, review_files
from app.schemas import CodeReviewRequest, ReviewResponse
from app.storage import get_review, list_reviews, save_review

app = FastAPI(title="AI Code Review Tool", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/")
def index() -> FileResponse:
    return FileResponse("app/static/index.html")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/review/code", response_model=ReviewResponse)
def review_code_endpoint(request: CodeReviewRequest) -> dict:
    result = review_code(request.code, file_path=request.file_path, language=request.language)
    review_id = save_review(result)
    return {**result, "id": review_id}


@app.post("/review/files", response_model=ReviewResponse)
async def review_files_endpoint(files: list[UploadFile] = File(...)) -> dict:
    inputs = []
    for file in files:
        content = await file.read()
        inputs.append({"file_path": file.filename, "code": content.decode("utf-8", errors="replace")})

    result = review_files(inputs)
    review_id = save_review(result)
    return {**result, "id": review_id}


@app.get("/reviews")
def reviews() -> list[dict]:
    return list_reviews()


@app.get("/reviews/{review_id}")
def review_detail(review_id: int) -> dict:
    return get_review(review_id)
