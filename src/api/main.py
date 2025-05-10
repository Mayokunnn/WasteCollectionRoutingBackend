from fastapi import FastAPI
from src.api.routes import algorithm_routes
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(algorithm_routes.router)

@app.get("/")
def home():
    return {"message": "Routing API is live!"}


