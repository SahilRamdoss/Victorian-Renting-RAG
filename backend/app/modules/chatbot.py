from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.schema import UserQuery
from langchain_openai import OpenAIEmbeddings
from sqlalchemy.orm import Session, selectinload
from app.models import Chunk
from app.schema import ChatbotResponse
from sqlalchemy import select

class ChatBot:

    def __init__(self, llm_model: str, embedder:str, temperature: float):
        self.llm = init_chat_model(model=llm_model, temperature=temperature)
        self.embedder = OpenAIEmbeddings(model=embedder)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """
                You are a polite and helpful assistant who answers questions based on Victorian renting laws in Australia.

                If the context does not contain sufficient information to answer the question reliably, clearly state concisely that you cannot answer it reliably. 
                Do not invent information or rely on unsupported assumptions.
                
                """),
            ("user", """
                Use the following context to answer the question.

                Context:
                {context}

                Question:
                {query}
            """)
        ])

        self.rag_chain = self.prompt | self.llm | StrOutputParser()

    def ask(self, db: Session, user_query: UserQuery, k: int = 4) -> ChatbotResponse:
        search_vector = self.embedder.embed_query(user_query.query)
        context = ""

        stmt = (
            select(Chunk)
            .options(selectinload(Chunk.document))
            .order_by(Chunk.embedding.cosine_distance(search_vector))
            .limit(k)
        )

        top_k_chunks = db.scalars(stmt).all()
        sources = set()

        for chunk in top_k_chunks:
            context = context + chunk.content + " "
            sources.add(chunk.document.url)

        model_reponse = self.rag_chain.invoke({"context": context, "query": user_query.query})

        return ChatbotResponse(response=model_reponse, sources=sources)

