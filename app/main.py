import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
review_analysis_path = os.path.join(project_root, 'review_analysis')

sys.path.append(project_root)
sys.path.append(review_analysis_path)

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn

from app.user.user_router import user
from app.config import PORT

from app.review.review_router import review

app = FastAPI()
static_path = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

app.include_router(user)

app.include_router(review)

@app.get("/")
def read_root():
    return {"message": "FastAPI is running!"}

if __name__=="__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)
