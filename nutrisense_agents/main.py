from fastapi import FastAPI
from nutrisense_agents.api import router as api_router

app = FastAPI()
app.include_router(api_router)