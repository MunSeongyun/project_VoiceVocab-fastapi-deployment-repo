from fastapi import HTTPException, UploadFile, status
from sqlmodel import Session, select  
from DB import connection, models
from convert_translate_word import google_cloud
from common import types
from convert_translate_word import translate_word
from tempfile import TemporaryFile
from datetime import datetime as dt
from convert_translate_word import use_spacy

# wav 파일에서 단어 목록 생성
async def generate_wav(file: UploadFile, user_id: int, language:str):
    # google stt를 사용해서, 파일링크, 단어목록, 스크립트 생성
    voice_file_url, words, script = await google_cloud.speech_to_text(file,language)
    
    # 유저가 이미 알고있는 단어 불러오기
    with Session(connection.engine) as session:
        statement = select(models.AlreadyKnow).where(models.AlreadyKnow.user_id == user_id)
        alreadyKnows = session.exec(statement).all()
    
    # 생성된 단어 목록에서 이미 알고있는 단어 제거
    setWord = set([i.word for i in alreadyKnows])
    word_list = words - setWord
    
    return voice_file_url, word_list, script

# 단어장 저장
async def save(body: types.SaveBody, user_name: str, user_id: int):
    file_name = user_name+dt.now().strftime("%Y-%m-%d%H:%M:%S") # 파일 이름 생성
    # 유저가 선택한 알고있는 단어를 AlreadyKnow에 추가
    with Session(connection.engine) as session:
        for word in body.known_word_list:
            new_word = models.AlreadyKnow(user_id=user_id, word=word)
            session.add(new_word)
        session.commit()
    # 단어 번역하기
    translated = translate_word.translate_word(body.word_list, from_lang=body.language[0:2]) 
    # 임시파일 생성해서 csv파일을 생성하고 gcs에 업로드
    with TemporaryFile('w+t', encoding='utf-8') as fp:
        for key,value in translated.items():
            fp.write(f'{key},{value}\n')
        google_cloud.upload_text_to_gcs(fp,file_name,'.csv')
    # 임시파일 생성해서 txt파일을 생성하고 gcs에 업로드
    with TemporaryFile('w+t',encoding='utf-8') as fp:
        fp.write(body.script)
        google_cloud.upload_text_to_gcs(fp, file_name, '.txt')
    
    current_time = dt.now().strftime('%Y/%m/%d,%H:%M:%S')
    # 단어장 저장
    with Session(connection.engine) as session:
        new_voca = models.VocabularyList(user_id=user_id, file_name=file_name, vocabulary_name=f'{user_name}의{current_time}에 제작된 단어장')
        session.add(new_voca)
        session.commit()
# 텍스트에서 단어 목록 생성
async def generate_text(text:str, user_id:int,language:str):
    words = await use_spacy.convert(text=text,language_code=language) # 단어 추출 
    
    # 단어 목록에서 이미 알고 있는 단어 제거 
    with Session(connection.engine) as session:
        statement = select(models.AlreadyKnow).where(models.AlreadyKnow.user_id == user_id)
        alreadyKnows = session.exec(statement).all()
        
    setWord = set([i.word for i in alreadyKnows])
    word_list = words - setWord
    return word_list

# 단어장 목록 불러오기 
async def get_list(user_id:int):
    with Session(connection.engine) as session:
        statement = select(
            models.VocabularyList.vocabulary_name,
            models.VocabularyList.id
        ).where(models.VocabularyList.user_id == user_id)
        voca_list = session.exec(statement).all()
    
    # db에서 가져온 정보 형식 변환 
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

# 단어장 이름 업데이트
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

# 알고있는 단어 목록 추가
async def append_known(user_id:int, word:str):
    with Session(connection.engine) as session:
        new_known = models.AlreadyKnow(user_id=user_id, word=word)
        session.add(new_known)
        session.commit()

# 알고있는 단어 목록 불러오기  
async def known_list(user_id:int):
    with Session(connection.engine) as session:
        statement = select(models.AlreadyKnow).where(models.AlreadyKnow.user_id == user_id)
        alreadyKnows = session.exec(statement).all()
        
    return alreadyKnows

# gcs에서 단어장이나 스크립트 가져오기
async def get_voca_or_script(vocabulary_id:int, user_id:int, target:str):
    # 파일 형식 설정
    file_type = ''
    if target == 'voca':
        file_type = '.csv'
    elif target == 'script':
        file_type = '.txt'
    
    # db에서 filename 가져오기
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
    
# csv에서 알고있는 단어 제거
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


