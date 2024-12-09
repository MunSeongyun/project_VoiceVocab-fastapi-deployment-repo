from io import TextIOWrapper
from dotenv import load_dotenv
from google.cloud import storage
from google.oauth2 import service_account
from google.cloud import speech
from fastapi import UploadFile
from convert_translate_word import use_spacy
from datetime import datetime
import os

load_dotenv()

KEY_PATH = os.getenv('KEY_PATH')
BUCKET_NAME = os.getenv('BUCKET_NAME')
credentials = service_account.Credentials.from_service_account_file(KEY_PATH)
storageClient = storage.Client(credentials=credentials, project=credentials.project_id)
bucket = storageClient.bucket(BUCKET_NAME)
speechClient = speech.SpeechClient(credentials=credentials)

async def speech_to_text(file: UploadFile,language_code:str):
    voice_file_url, voice_file_uri = upload_wav_to_gcs(file)  

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code=language_code
    )
    audio = speech.RecognitionAudio(uri=voice_file_uri)
    operation = speechClient.long_running_recognize(config=config, audio=audio)
    
    response = operation.result()
    
    words = set([])
    script = ''
    for result in response.results:
        transcript = result.alternatives[0].transcript
        script += transcript
        script += '\n'
        convert_result = await use_spacy.convert(transcript, language_code)
        words = words | convert_result
    
    return voice_file_url, words, script

def upload_wav_to_gcs(file: UploadFile):
    print(file.file)
    blob = bucket.blob(file.filename)
    blob.upload_from_file(file.file)
    file_url = f'https://storage.cloud.google.com/{BUCKET_NAME}/{file.filename}'
    file_uri = f'gs://{BUCKET_NAME}/{file.filename}'
    return file_url, file_uri

def upload_text_to_gcs(file: TextIOWrapper, user_name:str, type:str):
    file.seek(0)
    current_time = datetime.now().strftime("%Y-%m-%d%H:%M:%S")
    blob = bucket.blob(user_name + current_time+type)
    blob.upload_from_file(file)
    file_url = f'https://storage.cloud.google.com/{BUCKET_NAME}/{user_name + current_time + type}'
    file_uri = f'gs://{BUCKET_NAME}/{user_name + current_time + type}'
    return file_url, file_uri
