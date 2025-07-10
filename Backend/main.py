
from fastapi import FastAPI
from routes import agent 
from fastapi.middleware.cors import CORSMiddleware
from routes import auth


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(agent.router, prefix="/api")
