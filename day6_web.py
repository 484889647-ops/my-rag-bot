import streamlit as st
from day6_rag_engine import init_rag_db, ask_rag
st.title("🤖 知识库问答助手")
if "messages" not in st.session_state:
    st.session_state.messages=[]
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None
if "loaded_files" not in st.session_state:
    st.session_state.loaded_files = []
# 2. 画一个侧边栏
with st.sidebar:
    st.header("📚 知识库管理")
    file_path = st.text_input("请输入 TXT/PDF 文件路径：", value="docs/三体.txt")
    
    if st.button("加载文档"):
        with st.spinner("正在努力阅读并建立知识库..."):
            st.session_state.vectorstore = init_rag_db([file_path])
            
            # 记录成功加载的文件
            if file_path not in st.session_state.loaded_files:
                st.session_state.loaded_files.append(file_path)
                
            st.success("加载完成！可以开始提问啦。")
            
    # 画一条分割线，显示列表
    st.divider()
    st.subheader("📁 已加载的知识库")
    if st.session_state.loaded_files:
        for f in st.session_state.loaded_files:
            st.write(f"- {f}")
    else:
        st.write("空空如也~")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
user_input = st.chat_input("请基于加载的文档向我提问...")

if user_input:
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("assistant"):
        if st.session_state.vectorstore is None:
            answer = "请先在左侧输入文件路径并点击【加载文档】哦！"
            st.write(answer)
        else:
            with st.spinner("正在翻阅资料寻找答案..."):
                answer = ask_rag(user_input, st.session_state.vectorstore)
                st.write(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})