from typing import List
from pydantic import BaseModel

class SaveBody(BaseModel):
    script: str
    wordList: List[str]
    knownWordList: List[str]
    
class UpdateListName(BaseModel):
    name: str