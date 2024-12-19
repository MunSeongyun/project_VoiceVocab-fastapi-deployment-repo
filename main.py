from fastapi import FastAPI
from routers import vocabulary, auth, test
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    'http://localhost:5173',
    'http://localhost:8080',
    'http://localhost'
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