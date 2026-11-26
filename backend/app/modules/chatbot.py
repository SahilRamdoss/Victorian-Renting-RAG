from langchain.chat_models import init_chat_model
from langchain_classic.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class ChatBot:

    def __init__(self, llm_model: str, temperature: int):
        self.llm = init_chat_model(model=llm_model, temperature=temperature)
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