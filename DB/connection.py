from sqlmodel import Session, create_engine, SQLModel
from DB import models

engine = create_engine('mysql+pymysql://root:1234@db/vocabulary', echo=True)

SQLModel.metadata.create_all(engine)
