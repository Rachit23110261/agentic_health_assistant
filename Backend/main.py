from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth, agent
from database import engine
from models import Base  # make sure this imports the Base used by your models

app = FastAPI()

# ✅ CORS middleware - FIXED: removed trailing slash from origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://agentic-health-assistant.vercel.app"],  # NO trailing slash
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Auto-create tables on startup (dev use only)
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# ✅ Route registration
app.include_router(auth.router, prefix="/api")
app.include_router(agent.router, prefix="/api")
