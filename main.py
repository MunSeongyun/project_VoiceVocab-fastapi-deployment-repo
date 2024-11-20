from fastapi import FastAPI
from routers import vocabulary
from STT import recognition
app = FastAPI()

app.include_router(vocabulary.router)

@app.get('/')
async def main():
    recognition.hello()
    return {
        'message':'hello'
    }