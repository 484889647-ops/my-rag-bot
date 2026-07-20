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
    file_path = st.text_input("请输入 TXT/PDF 文件路径：", value="docs/三体.pdf")
    
    if st.button("加载文档"):
        progress_bar = st.progress(0.0)
        status_text = st.empty()
        
        def update_progress(line):
            import re
            # 捕获类似 "Layout Predict:  91%|█████████▏| 126/138" 的进度百分比
            match = re.search(r'(\d+)%', line)
            if match:
                pct = int(match.group(1))
                # Streamlit progress bar 接受 0.0 到 1.0 的浮点数
                progress_bar.progress(pct / 100.0)
                
            # 根据 MinerU 的输出关键字动态更新状态文本
            if "Layout Predict" in line:
                status_text.text(f"阶段 1/3：正在分析文档版面... {match.group(1) + '%' if match else ''}")
            elif "MFD Predict" in line or "MFR Predict" in line:
                status_text.text(f"阶段 2/3：正在识别数学公式... {match.group(1) + '%' if match else ''}")
            elif "OCR Predict" in line:
                status_text.text(f"阶段 3/3：正在进行文字识别(OCR)... {match.group(1) + '%' if match else ''}")

        with st.spinner("正在努力阅读并建立知识库..."):
            st.session_state.vectorstore = init_rag_db([file_path], progress_callback=update_progress)
            
            # 进度完成后清理掉进度条组件
            progress_bar.empty()
            status_text.empty()
            
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
        st.markdown(msg["content"])
user_input = st.chat_input("请基于加载的文档向我提问...")

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("assistant"):
        if st.session_state.vectorstore is None:
            answer = "请先在左侧输入文件路径并点击【加载文档】哦！"
            st.markdown(answer)
        else:
            with st.spinner("正在翻阅资料寻找答案..."):
                answer = ask_rag(user_input, st.session_state.vectorstore)
                st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})