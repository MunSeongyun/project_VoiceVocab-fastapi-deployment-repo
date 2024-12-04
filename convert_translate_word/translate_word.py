from translate import Translator
from typing import List

def translate_word(words: List[str]):
    word_list = {}
    translator = Translator(from_lang='ja', to_lang='ko')
    for i in words:
        word_list[i]=(translator.translate(i))
    return word_list