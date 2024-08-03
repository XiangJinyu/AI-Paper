import subprocess
import sys
import os

def main():
    # 获取虚拟环境的 Python 解释器路径
    venv_python = sys.executable

    # 依次执行代码文件
    subprocess.run([venv_python, "spider.py"], check=True)
    print("查找文章完成")
    subprocess.run([venv_python, "abstract.py"], check=True)
    print("查找原文链接完成")
    subprocess.run([venv_python, "unique_data.py"], check=True)
    print("去除重复内容完成")
    subprocess.run([venv_python, "show_pdf.py"], check=True)
    print("阅读原文完成")
    subprocess.run([venv_python, "write_to_html.py"], check=True)
    print("排版完成")
    subprocess.run([venv_python, "save_data.py"], check=True)
    print("数据存储完成")

if __name__ == "__main__":
    main()
