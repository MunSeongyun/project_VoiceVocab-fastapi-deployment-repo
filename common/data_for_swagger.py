from typing import List

from pydantic import BaseModel


tags_metadata = [
    {
        "name": "vocabulary",
        "description":"create, modify, and delete word lists"
    },
    {
        "name":"auth",
        "description":"login and get user info"
    }
]

class PostVocabulary(BaseModel):
    message:str
    wordList: List[str]
    voiceFileUrl: str
    language:str
    script: str

class PostGenerateToText(BaseModel):
    message:str
    wordList:List[str]
    script:str
    language:str
    
class MessageOnly(BaseModel):
    message:str
    
class VocabListItem(BaseModel):
    vocabularyName:str
    id:int
class GetList(BaseModel):
    message:str
    data:List[VocabListItem]
    
class GetKnownList(BaseModel):
    userId: int
    word:str
    id:int
    
class GetTarget(BaseModel):
    message:str
    data:str
    
class User(BaseModel):
    sub: str
    name: str
    email:str
    iat: int
    exp: int
class GetUserInfo(BaseModel):
    user: User