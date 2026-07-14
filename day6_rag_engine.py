import os
from dotenv import load_dotenv

load_dotenv()
from openai import OpenAI
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from utils.loader import process_file

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

embeddings = HuggingFaceEmbeddings(model_name="shibing624/text2vec-base-chinese")

def init_rag_db(file_paths):

    all_chunks = []
    for file_path in file_paths:
        if not os.path.exists(file_path):
            print(f"找不到文件: {file_path}")
            continue

        chunks = process_file(file_path)
        if chunks:
            all_chunks.extend(chunks)

        if all_chunks:
            vectorstore = Chroma.from_documents(documents=all_chunks, embedding=embeddings)  
            return vectorstore
        else:
            return None

def ask_rag(question, vectorstore):
    if vectorstore is None:
        return "请先加载文档"
    
    result = vectorstore.similarity_search(question,k=3)
    context_text = "\n\n".join([doc.page_content for doc in result])
    prompt = f"""
    你是一个专业的知识库问答助手。请你严格根据下述【参考资料】中的内容，回答用户的【问题】。
    要求：... (省略要求文本)
    【参考资料】
    {context_text}

    【问题】
    {question}
    """
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role":"user","content":prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content