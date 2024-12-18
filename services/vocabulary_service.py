from fastapi import HTTPException, UploadFile, status
import requests
from sqlmodel import Session, select  
from DB import connection, models
from convert_translate_word import google_cloud
from common import types
from convert_translate_word import translate_word
from tempfile import TemporaryFile
from datetime import datetime as dt
import requests
from convert_translate_word import use_spacy
async def japan(file: UploadFile, user_id: int):
    voice_file_url, words, script = await google_cloud.speech_to_text(file,'ja-JP')
    
    with Session(connection.engine) as session:
        statement = select(models.AlreadyKnow).where(models.AlreadyKnow.user_id == user_id)
        alreadyKnows = session.exec(statement).all()
    
    setWord = set([i.word for i in alreadyKnows])
    word_list = words - setWord
    
    return voice_file_url, word_list, script
        
async def save(body: types.SaveBody, user_name: str, user_id: int):
    file_name = user_name+dt.now().strftime("%Y-%m-%d%H:%M:%S")
    with Session(connection.engine) as session:
        for word in body.known_word_list:
            new_word = models.AlreadyKnow(user_id=user_id, word=word)
            session.add(new_word)
        session.commit()
        
    translated = translate_word.translate_word(body.word_list) 
    with TemporaryFile('w+t', encoding='utf-8') as fp:
        for key,value in translated.items():
            fp.write(f'{key},{value}\n')
        google_cloud.upload_text_to_gcs(fp,file_name,'.csv')
        
    with TemporaryFile('w+t',encoding='utf-8') as fp:
        fp.write(body.script)
        google_cloud.upload_text_to_gcs(fp, file_name, '.txt')
    
    current_time = dt.now().strftime('%Y/%m/%d,%H:%M:%S')
    
    with Session(connection.engine) as session:
        new_voca = models.VocabularyList(user_id=user_id, file_name=file_name, vocabulary_name=f'{user_name}의{current_time}에 제작된 단어장')
        session.add(new_voca)
        session.commit()
     
async def japan_text(text:str, user_id=int):
    words = await use_spacy.convert(text=text,language_code='ja-JP')
    
    with Session(connection.engine) as session:
        statement = select(models.AlreadyKnow).where(models.AlreadyKnow.user_id == user_id)
        alreadyKnows = session.exec(statement).all()
        
    setWord = set([i.word for i in alreadyKnows])
    word_list = words - setWord
    return word_list
        
async def get_list(user_id:int):
    with Session(connection.engine) as session:
        statement = select(
            models.VocabularyList.vocabulary_name,
            models.VocabularyList.id
        ).where(models.VocabularyList.user_id == user_id)
        voca_list = session.exec(statement).all()
    result =[]
    temp = {}
    count = 0
    for i in voca_list:
        for item in i:
            try:
                count+=1
                temp['id'] = int(item)
            except:
                count+=1
                temp['vocabularyName'] = item
        
        if count >= 2:
            result.append(temp)
            temp = {}
            count = 0 
            
    return result

async def update_list_name(list_id:int, name: str, user_id:str):
    with Session(connection.engine) as session:
        statement = select(models.VocabularyList).where(models.VocabularyList.id == list_id)
        results = session.exec(statement)
        voca_list = results.one()
        if voca_list.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource"
            )
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

async def get_voca_or_script(vocabulary_id:int, user_id:int, target:str):
    file_type = ''
    if target == 'voca':
        file_type = '.csv'
    elif target == 'script':
        file_type = '.txt'
    
    with Session(connection.engine) as session:
        statement = select(models.VocabularyList).where(models.VocabularyList.id == vocabulary_id)
        voca = session.exec(statement).first()
    if not voca:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='not found'
        )
    if voca.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You do not have permission to access this resource'
        )
        
    file_name = voca.file_name + file_type
    
    return google_cloud.download_csv_or_txt_from_gcs(file_name)
    
    
def update_csv(user_id:int, content:str,vocabulary_id:int):
    with Session(connection.engine) as session:
        statement = select(models.VocabularyList).where(models.VocabularyList.id == vocabulary_id)
        voca = session.exec(statement).first()
    if not voca:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='not found'
        )
    if voca.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You do not have permission to access this resource'
        )
    return google_cloud.update_csv(content,voca.file_name)