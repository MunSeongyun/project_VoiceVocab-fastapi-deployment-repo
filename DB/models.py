from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name:str = Field(default=None)
    google_id:str = Field(default=None)
    
class AlreadyKnow(SQLModel, table=True):
    id:int|None = Field(default=None,primary_key=True)
    user_id:int = Field(default=None, foreign_key='user.id')
    word:str = Field(default=None)
    
class VocabularyList(SQLModel, table=True):
    id:int|None = Field(default=None,primary_key=True)
    user_id:int = Field(default=None, foreign_key='user.id')
    script_url:str = Field(default=None)
    file_url:str = Field(default=None)
    vocabulary_name:str = Field(default=None)
    
class WaitingResult(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    operation_id:str = Field(default=None)
    user_id:int = Field(default=None, foreign_key='user.id')
    language_code:str= Field(default=None)
    voice_file_url:str= Field(default=None)