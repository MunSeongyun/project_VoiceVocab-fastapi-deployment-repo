import spacy
from convert_translate_word import spacy_model_dic

async def convert(text:str, language_code:str):
    
    nlp = spacy.load(spacy_model_dic.spacy_model[language_code])
    
    doc = nlp(text)
    pos = ['ADJ', 'ADV', 'NOUN', 'PROPN', 'VERB']
    punctuation = ['!', '.', ',', '?', '、', '。', '！', '？']
    
    words = [token.lemma_ for token in doc if token.pos_ in pos and token.text not in punctuation]

    return set(words)