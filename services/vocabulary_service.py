from fastapi import UploadFile
from sqlmodel import Session, select  
from DB import connection, models
from convert_translate_word import google_cloud
from common import types
from convert_translate_word import translate_word
from tempfile import TemporaryFile


async def japan(file: UploadFile, user_id: int):
    voice_file_url, words, script = await google_cloud.speech_to_text(file,'ja-JP')
    
    with Session(connection.engine) as session:
        statement = select(models.AlreadyKnow).where(models.AlreadyKnow.user_id == user_id)
        alreadyKnows = session.exec(statement).all()
    
    setWord = set([i.word for i in alreadyKnows])
    word_list = words - setWord
    
    return voice_file_url, word_list, script
        
async def save(body: types.SaveBody, user_name: str):
    with Session(connection.engine) as session:
        for word in body.known_word_list:
            new_word = models.AlreadyKnow(user_id=1, word=word)
            session.add(new_word)
        session.commit()
        
    translated = translate_word.translate_word(body.word_list) 
    with TemporaryFile('w+t', encoding='utf-8') as fp:
        for key,value in translated.items():
            fp.write(f'{key},{value}\n')
        csv_file_url, _ = google_cloud.upload_text_to_gcs(fp,user_name,'.csv')
        
    with TemporaryFile('w+t',encoding='utf-8') as fp:
        fp.write(body.script)
        txt_file_url, _ = google_cloud.upload_text_to_gcs(fp, user_name, '.txt')
    
    with Session(connection.engine) as session:
        new_voca = models.VocabularyList(user_id=1, script_url=txt_file_url, file_url=csv_file_url, vocabulary_name=txt_file_url)
        session.add(new_voca)
        session.commit()
        
async def get_list(user_id:int):
    with Session(connection.engine) as session:
        statement = select(models.VocabularyList).where(models.VocabularyList.user_id == user_id)
        voca_list = session.exec(statement).all()
        
    return voca_list

async def update_list_name(list_id:int, name: str):
    with Session(connection.engine) as session:
        statement = select(models.VocabularyList).where(models.VocabularyList.id == list_id)
        results = session.exec(statement)
        voca_list = results.one()
        voca_list.vocabulary_name = name
        session.add(voca_list)
        session.commit()
        session.refresh(voca_list)

async def append_known(user_id:int, word:str):
    with Session(connection.engine) as session:
        new_known = models.AlreadyKnow(user_id=user_id, word=word)
        session.add(new_known)
        session.commit()
    
async def known_list(user_id:int):
    with Session(connection.engine) as session:
        statement = select(models.AlreadyKnow).where(models.AlreadyKnow.user_id == user_id)
        alreadyKnows = session.exec(statement).all()
        
    return alreadyKnows