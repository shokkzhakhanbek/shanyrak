from fastapi import FastAPI

from app.database import engine, Base
from app.auth.router import router as auth_router
from app.shanyraks.router import router as shanyraks_router
from app.comments.router import router as comments_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Şañıraq.kz", description="MVP маркетплейса жилых помещений")

app.include_router(auth_router)
app.include_router(shanyraks_router)
app.include_router(comments_router)


@app.get("/")
def root():
    return {"message": "Welcome to Şañıraq.kz API"}