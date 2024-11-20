import speech_recognition as sr
from pydub import AudioSegment
import spacy
# 음성 인식기를 생성
recognizer = sr.Recognizer()
nlp = spacy.load('ja_core_news_sm')

def hello():
    
    audio_file_path = '/app/test/japan.m4a'
    
    sound = AudioSegment.from_file(audio_file_path)
    wav_file_path = '/app/test/japan.wav'
    sound.export(wav_file_path, format='wav')
    # 음성 파일을 로드
    audio_file = sr.AudioFile(wav_file_path)

    with audio_file as source:
        audio_data = recognizer.record(source)

    # 음성을 텍스트로 변환
    try:
        text = recognizer.recognize_google(audio_data, language='ja-JP')
        #print('텍스트: ' + text)
        doc = nlp(text)
        pos = ['ADJ', 'ADV', 'NOUN', 'PROPN', 'VERB']
        words = [token.lemma_ for token in doc if token.pos_ in pos]
        print(text)
        print(set(words))
    except sr.UnknownValueError:
        print('음성을 인식할 수 없습니다.')
    except sr.RequestError as e:
        print(f'Google Web Speech API 요청 오류: {e}')