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

class users(BaseModel):
    name1: str
    name2: str


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
origins = [ 
     "http://localhost:3000", 
     "http://127.0.0.1:8000" # Add your front-end URL here 
 ] 
  
app.add_middleware( 

     allow_origins=origins,  # Reflect the allowed origins 
     allow_credentials=True, 
     allow_methods=["*"],  # Allows all methods 
     allow_headers=["*"],  # Allows all headers 
 )



@app.post('/socrs', response_model=ResponseScore)
def updete_score(request: ScoreModel):
    name = request.name
    status = request.status

    user = session.query(Scores).filter(Scores.user_name == name).first()
    if not user:
        user = Scores(
            user_name = name
        )
    
    session.add(user)
    session.commit()
    score = user.score

    if (status == 'WIN'):
        score = score + 1
    elif(status == 'LOSE'):
        score = score - 1

    user.score = score

    session.commit()

    response = {
        'name' : name ,
        'score': score
    }
    
    return response


@app.post('/users')
def create_users(request: users):
    name1 = request.name1
    name2 = request.name2
    try:
        user1 = Scores(user_name=name1)
        user2 = Scores(user_name=name2)
        
        session.add(user1)
        session.add(user2)
        
        session.commit()
        
        return {"message": "Users successfully created"}
    except Exception as e:
        session.rollback()  

   
     
@app.get('/top-users')
def get_top_users():
    top_users = session.query(Scores).order_by(Scores.score.desc()).limit(10).all()
    return [{"name": user.user_name, "score": user.score} for user in top_users]
    