import os
import subprocess
from langchain_core.documents import Document

def process_file(file_path, progress_callback=None):
    # 处理 TXT 文件的逻辑保持不变
    if file_path.endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        return [Document(page_content=text, metadata={"source": file_path})]

    # 处理 PDF 文件的逻辑 (MinerU 本地解析版)
    elif file_path.endswith('.pdf'):
        # 1. 准备解析结果的存放路径
        pdf_name = os.path.splitext(os.path.basename(file_path))[0]
        output_dir = "output"
        
        # 2. 拼接并在本地运行 MinerU 命令
        print(f"🚀 开始使用 MinerU 本地解析 {pdf_name}.pdf ... (可能需要几十秒到几分钟)")
        cmd = ["magic-pdf", "-p", file_path, "-o", output_dir, "-m", "auto"]
        
        try:
            # 这一步会启动一个完全独立的进程进行运算，并实时捕获输出日志
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            # 逐行读取终端输出，并通过回调函数传给前端
            for line in process.stdout:
                print(line, end="")  # 保持终端打印
                if progress_callback:
                    progress_callback(line)
                    
            process.wait()
            
            if process.returncode != 0:
                print(f"❌ MinerU 解析 PDF 失败，退出码：{process.returncode}")
                return []
                
        except Exception as e:
            print(f"❌ 运行解析进程时出错: {e}")
            return []
            
        # 3. 读取生成的 Markdown 文件
        md_file = os.path.join(output_dir, pdf_name, "auto", f"{pdf_name}.md")
        
        if os.path.exists(md_file):
            with open(md_file, "r", encoding="utf-8") as f:
                md_content = f.read()
            print("✅ MinerU 解析成功！已提取出结构化 Markdown")
            return [Document(page_content=md_content, metadata={"source": file_path})]
        else:
            print("❌ 未能找到生成的 Markdown 文件")
            return []