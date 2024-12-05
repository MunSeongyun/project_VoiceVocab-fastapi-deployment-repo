from pydantic import ConfigDict
from sqlmodel import Field, SQLModel
from pydantic.alias_generators import to_camel


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name:str = Field(default=None)
    google_id:str = Field(default=None)
    email:str = Field(default=None)
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )
    
class AlreadyKnow(SQLModel, table=True):
    id:int|None = Field(default=None,primary_key=True)
    user_id:int = Field(default=None, foreign_key='user.id')
    word:str = Field(default=None)
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )
    
class VocabularyList(SQLModel, table=True):
    id:int|None = Field(default=None,primary_key=True)
    user_id:int = Field(default=None, foreign_key='user.id')
    script_url:str = Field(default=None)
    file_url:str = Field(default=None)
    vocabulary_name:str = Field(default=None)
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )
