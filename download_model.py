import os
from dotenv import load_dotenv

# 加载环境变量（必须放在最前面，确保读到国内镜像源）
load_dotenv()

print(f"当前使用的镜像源: {os.getenv('HF_ENDPOINT', '官方源')}")
print("开始下载/验证本地模型，请稍候...")

try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
    # 这一步会触发下载并缓存到本地
    embeddings = HuggingFaceEmbeddings(model_name="shibing624/text2vec-base-chinese")
    print("\n✅ 模型下载并加载成功！现在你可以放心运行 Streamlit 网页了。")
except Exception as e:
    print(f"\n❌ 下载失败: {e}")
