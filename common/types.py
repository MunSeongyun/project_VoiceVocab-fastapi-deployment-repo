from typing import List, Dict
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

class SaveBody(BaseModel):
    script: str
    word_list: List[str]
    known_word_list: List[str]
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )
    
class UpdateListName(BaseModel):
    name: str 

class AppendKnownWord(BaseModel):
    word:str
