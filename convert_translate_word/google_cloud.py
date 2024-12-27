from io import TextIOWrapper
from tempfile import TemporaryFile

from google.cloud import storage
from google.oauth2 import service_account
from google.cloud import speech
from fastapi import UploadFile
from convert_translate_word import use_spacy
from datetime import datetime
import os



KEY_PATH = os.getenv('KEY_PATH') # 구글 클라우드에 접속하기 위한 인증정보 json 파일이 있는 경로
BUCKET_NAME = os.getenv('BUCKET_NAME') # 구글 클라우드 버킷 이름
credentials = service_account.Credentials.from_service_account_file(KEY_PATH) # KEY_PATH에서 가져와서 생성한 유저 인증정보
storageClient = storage.Client(credentials=credentials, project=credentials.project_id) # 스토리지에 접근 가능한 클라이언트
bucket = storageClient.bucket(BUCKET_NAME) # 버킷 설정
speechClient = speech.SpeechClient(credentials=credentials) # STT에 접근 가능한 클라이언트

# WAV파일을 TEXT로 변환하는 함수
async def speech_to_text(file: UploadFile,language_code:str):
    voice_file_url, voice_file_uri = upload_wav_to_gcs(file)  # 파일 업로드

    # stt 설정
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code=language_code
    )
    audio = speech.RecognitionAudio(uri=voice_file_uri)
    operation = speechClient.long_running_recognize(config=config, audio=audio)
    
    response = operation.result()
    
    # 변환결과를 spacy를 사용해서 변환하고, 단어를 뽑아냄
    words = set([]) # 중복 제거를 위해 set 사용용
    script = ''
    for result in response.results:
        transcript = result.alternatives[0].transcript
        script += transcript
        script += '\n'
        convert_result = await use_spacy.convert(transcript, language_code)
        words = words | convert_result
    
    return voice_file_url, words, script

# wav를 gcs에 업로드하고, url/uri를 받아오는 함수
def upload_wav_to_gcs(file: UploadFile):
    blob = bucket.blob(file.filename)
    blob.upload_from_file(file.file)
    file_url = f'https://storage.cloud.google.com/{BUCKET_NAME}/{file.filename}'
    file_uri = f'gs://{BUCKET_NAME}/{file.filename}'
    return file_url, file_uri

# text를 gcs에 업로드하고, url/uri를 받아오는 함수
def upload_text_to_gcs(file: TextIOWrapper,file_name:str, type:str):
    file.seek(0)
    blob = bucket.blob(file_name+type)
    blob.upload_from_file(file)
    file_url = f'https://storage.cloud.google.com/{BUCKET_NAME}/{file_name + type}'
    file_uri = f'gs://{BUCKET_NAME}/{file_name + type}'
    return file_url, file_uri

# 단어장이나 스크립트를 gcs에서 다운 하는 함수
def download_csv_or_txt_from_gcs(file_name:str):
    blob = bucket.blob(file_name)
    content = blob.download_as_text(encoding='utf-8')
    return content
# csv로 업로드 되어있는 단어장에서 사용자가 알겠다고 선택한 단어를 제거하는 함수
def update_csv(content:str, file_name:str):
    target = download_csv_or_txt_from_gcs(file_name+'.csv')
    target = target.split('\n')
    with TemporaryFile('w+t', encoding='utf-8') as fp:
        for line in target:
            if(line==content):
                continue
            fp.write(f'{line}\n')
        upload_text_to_gcs(fp,file_name,'.csv')