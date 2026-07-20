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

def init_rag_db(file_paths, progress_callback=None):
    # 延迟加载：把模型的初始化放进函数里，防止 Streamlit 网页在启动时因为下载模型而白屏
    embeddings = HuggingFaceEmbeddings(model_name="shibing624/text2vec-base-chinese")

    all_chunks = []
    for file_path in file_paths:
        if not os.path.exists(file_path):
            print(f"找不到文件: {file_path}")
            continue

        chunks = process_file(file_path, progress_callback)
        if chunks:
            all_chunks.extend(chunks)

    # 移到 for 循环的外面！
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
    
    【重要格式要求】：
    1. 必须使用 Markdown 格式进行输出。
    2. 如果回答中包含数学公式，行内公式必须使用单个美元符号包裹（例如：$E=mc^2$），独立成行的公式块必须使用双美元符号包裹（例如：$$E=mc^2$$）。
    3. 如果回答中包含代码、列表、加粗等，请严格遵循标准的 Markdown 语法。

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