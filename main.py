from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy import create_engine


class ScoreModel(BaseModel):
    name : str
    status : str


class ResponseScore(BaseModel):
    name : str
    score : int


engine = create_engine('sqlite:///databse.db', connect_args={'check_same_thread': False})
Base = declarative_base()
sessionlocal = sessionmaker(bind=engine, autoflush=False)
session = sessionlocal()


class Scores(Base):
    __tablename__ = 'scores'
    id = Column('id', Integer, unique=True, primary_key=True, index=True)
    user_name = Column('user_name', String, unique=True)
    score = Column('score', Integer, default=0)


Base.metadata.create_all(engine)


app = FastAPI()



@app.post('/', response_model=ResponseScore)
def updete_score(request: ScoreModel):
    name = request.name
    status = request.status

    user = session.query(Scores).filter(Scores.user_name == name).first()
    if not user:
        user = Scores(
            user_name = name
        )

    score = user.score
    
    session.add(user)
    session.commit()
    session.refresh(user)

    if (status == 'WIN'):
        score = score + 1
    else:
        score = score - 1

    user.score = score

    session.commit()

    response = {
        'name' : name ,
        'score': score
    }
    
    return response


    