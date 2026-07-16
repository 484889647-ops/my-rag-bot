import warnings
from langchain_core.document import Document
from llama_prase import LlamaParse
import nest_asyncio
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

warnings.filterwarnings("ignore")

nest_asyncio.apply()

async def process_file(file_path):
    print(f"[工具] 正在加载并清洗文件: {file_path} ...")

    try:
       if file_path.endswith('.pdf'):
            print("🚀 正在调用 LlamaParse 视觉大模型解析 PDF，请稍候...")
            parser = LlamaParse(
                 result_type="markdown",
                 language="zh"
            )
            llama_docs = parser.load_data(file_path)
            pages = []
            for doc in llama_docs:
                 pages.append(Document(page_content=doc.metadata))
       elif file_path.endswith('.txt'):
            # 【关键修改】LangChain 的 TextLoader 在遇到编码错误时会抛出 RuntimeError 而不是 UnicodeDecodeError
            try:
                loader = TextLoader(file_path, encoding='utf-8')
                pages = loader.load()
            except Exception as inner_e:
                # 只要 UTF-8 读取失败，我们就尝试用 GBK 兜底
                print("⚠️ UTF-8 解码失败，尝试使用 GBK 编码读取...")
                loader = TextLoader(file_path, encoding='gbk')
                pages = loader.load()
       else:
            print("❌ 不支持的文件格式")  
            return []
       
    except Exception as e:
        print(f"❌ 加载失败，请检查文件是否存在。错误信息：{e}")
        return[]
    
    for page in pages:
            text = page.page_content
            text = text.replace("\n\n","<段落>")
            text = text.replace("\n","")
            text = text.replace("<段落>","\n\n")
            page.page_content = text

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 500,
        chunk_overlap = 50,
        separators = ["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(pages)
    return chunks