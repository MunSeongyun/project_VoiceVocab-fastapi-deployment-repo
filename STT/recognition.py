import speech_recognition as sr
from pydub import AudioSegment
import spacy
from fastapi import UploadFile
import io
from boto3 import client
# 음성 인식기를 생성
recognizer = sr.Recognizer()


async def japan(file: UploadFile):
    return await convert(file, 'ja-JP', 'ja_core_news_sm' )
        
async def convert(file:UploadFile, language, spaCy_model):
    nlp = spacy.load(spaCy_model)

    try:
        audio_data = await file.read()
        audio = AudioSegment.from_file(io.BytesIO(audio_data),'m4a')
        wav_io = io.BytesIO()
        audio.export(wav_io, format='wav')
        wav_io.seek(0)
        
        with sr.AudioFile(wav_io) as source:
            audio_data = recognizer.record(source)
            
        text = recognizer.recognize_google(audio_data, language=language)
        doc = nlp(text)
        pos = ['ADJ', 'ADV', 'NOUN', 'PROPN', 'VERB']
        words = [token.lemma_ for token in doc if token.pos_ in pos]
        return set(words), text, 'https://example.com'
    except sr.UnknownValueError:
        print('음성을 인식할 수 없습니다.')
        return None
    except sr.RequestError as e:
        print(f'Google Web Speech API 요청 오류: {e}')
        return None
    