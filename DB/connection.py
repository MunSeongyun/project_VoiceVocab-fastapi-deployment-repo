from sqlmodel import Session, create_engine, SQLModel
from DB import models
import os




DB_USERNAME=os.getenv('DB_USERNAME')
DB_PASSWORD=os.getenv('DB_PASSWORD')
DB_HOST=os.getenv('DB_HOST')
engine = create_engine(f'mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/vocabulary', echo=True)

SQLModel.metadata.create_all(engine)
