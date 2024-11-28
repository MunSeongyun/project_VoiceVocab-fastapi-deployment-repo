from typing import List, Set
import spacy
from fastapi import UploadFile
from google.cloud import storage
from google.oauth2 import service_account
from google.cloud import speech
from google.longrunning.operations_pb2 import Operations
from STT import spacy_model_dic
from translate import Translator

KEY_PATH = '/app/config/key.json'
credentials = service_account.Credentials.from_service_account_file(KEY_PATH)
storageClient = storage.Client(credentials=credentials, project=credentials.project_id)
bucket = storageClient.bucket('voice-vocab-wav-file')
speechClient = speech.SpeechClient(credentials=credentials)



async def japan(file: UploadFile):
    voice_file_url, words, script = await speech_to_text(file,'ja-JP')
    return voice_file_url, words, script
        
async def convert(text:str, language_code:str):
    nlp = spacy.load(spacy_model_dic.spacy_model[language_code])
    
    doc = nlp(text)
    pos = ['ADJ', 'ADV', 'NOUN', 'PROPN', 'VERB']
    words = [token.lemma_ for token in doc if token.pos_ in pos]
    return set(words)
    
    
async def speech_to_text(file: UploadFile,language_code:str):
    #script, script_url, voice_file_url
    blob = bucket.blob(file.filename)
    blob.upload_from_file(file.file)
    voice_file_url = f'https://storage.cloud.google.com/voice-vocab-wav-file/{file.filename}'

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code=language_code
    )
    audio = speech.RecognitionAudio(uri=f'gs://voice-vocab-wav-file/{file.filename}')
    operation = speechClient.long_running_recognize(config=config, audio=audio)
    
    response = operation.result()
    
    words = set([])
    script = ''
    for result in response.results:
        transcript = result.alternatives[0].transcript
        script += transcript
        script += '\n'
        convert_result = await convert(transcript, language_code)
        words = words | convert_result
    
    return voice_file_url, words, script

def translate_word(words: List[str]):
    word_list = {}
    translator = Translator(from_lang='ja', to_lang='ko')
    for i in words:
        word_list[i]=(translator.translate(i))
    return word_list
