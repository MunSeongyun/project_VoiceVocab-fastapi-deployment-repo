from fastapi import FastAPI
from routers import vocabulary, auth, test
from fastapi.middleware.cors import CORSMiddleware
from common import data_for_swagger
app = FastAPI(
    title='VoiceVocab',
    openapi_tags=data_for_swagger.tags_metadata
)

origins = [
    'http://localhost:5173',
    'http://localhost:8080',
    'http://localhost',
    'https://www.bapull.store',
    'https://www.voicevocab.store'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(vocabulary.router)
app.include_router(auth.router)
app.include_router(test.router)
@app.get('/')
async def main():
    return {
        'message':'hello'
    }