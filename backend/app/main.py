from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from app.core.db import engine
from app.models import Base
from app import models
from app.schema import UserQuery
from app.modules.chatbot import ChatBot
from typing import Annotated
from sqlalchemy.orm import Session
from app.core.db import get_db



@asynccontextmanager
async def lifespan(app:FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)

chatbot = ChatBot(llm_model="openai:gpt-5.4-nano", embedder="text-embedding-3-small", temperature=0)

@app.post("/chat")
def query_chatbot(user_query: UserQuery, db: Annotated[Session, Depends(get_db)]):
    return chatbot.ask(db=db, user_query=user_query)