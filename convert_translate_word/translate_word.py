from translate import Translator
from typing import List

# 단어 번역
def translate_word(words: List[str], from_lang:str):
    word_list = {}
    translator = Translator(from_lang=from_lang, to_lang='ko')
    for i in words:
        word_list[i]=(translator.translate(i))
    return word_list