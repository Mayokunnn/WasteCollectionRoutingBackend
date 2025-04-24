from fastapi import FastAPI
from src.api.routes import algorithm_routes

app = FastAPI()

app.include_router(algorithm_routes.router)

@app.get("/")
def home():
    return {"message": "Routing API is live!"}


