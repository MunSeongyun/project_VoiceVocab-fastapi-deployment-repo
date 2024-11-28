from fastapi import APIRouter, Path, UploadFile , File
from fastapi.background import P
from pydantic import BaseModel
from sqlmodel import Session, select  
from STT import recognition
from typing import List
from DB import connection, models

router = APIRouter(prefix='/vocabulary')

class SaveBody(BaseModel):
    script: str
    wordList: List[str]
    knownWordList: List[str]

@router.post('/generate')
async def generate(file: UploadFile = File(...)):
    
    voice_file_url, words, script = await recognition.japan(file)
    
    with Session(connection.engine) as session:
        statement = select(models.AlreadyKnow).where(models.AlreadyKnow.user_id == 1)
        alreadyKnows = session.exec(statement).all()
    
    setWord = set([i.word for i in alreadyKnows])
    word_list = words - setWord
    
    return {
        'message':'단어 목록을 생성했습니다.',
        'wordList': word_list,
        'voice_file_url': voice_file_url,
        'script': script
    }

@router.post('/save')
async def save(body: SaveBody):
    with Session(connection.engine) as session:
        for word in body.knownWordList:
            newWord = models.AlreadyKnow(user_id=1, word=word)
            session.add(newWord)
        session.commit()
    translated = recognition.translate_word(body.wordList) 
    return translated

@router.get('/list/{user_id}')
async def list(user_id:int = Path(title='유저의 아이디', gt=0)):
    return await '유저가 단어장 목록을 확인하기 위해, 전체 vacabulary_list를 반환하는 api 필요'

@router.get('/csv/{vocabulary_id}')
async def csv(vocabulary_id:int = Path(title='단어장의 아이디', gt=0)):
    return await '하나의 단어장을 확인하기 위해, 유저가 id를 보내면, 권환 확인후 s3버킷에 있는 csv파일 전송'

@router.get('/script/{vocabulary_id}')
async def script(vocabulary_id:int = Path(title='단어장의 아이디', gt=0)):
    return await '단어장의 스크립트를 확인하기 위해 유저가 id를 보내면, 권한 확인 후 s3버킷에 있는 스크립트 파일 전송'

# body 사용함
@router.get('/known')
async def known():
    return await '유저가 단어장에서 이제 알겠다고 한 단어들은, 이미 알고있는 단어들 테이블에 추가하는 api'

@router.get('/knwon-list')
async def knwon_list():
    return await '유저에게 이미 알고있는 단어 전체를 보내주는 api'