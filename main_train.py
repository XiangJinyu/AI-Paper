import subprocess

def main():
    # 依次执行三个代码文件
    subprocess.run(["python", "spider.py"])
    print("查找文章完成")
    subprocess.run(["python", "abstract.py"])
    print("查找原文链接完成")
    subprocess.run(["python", "show_pdf.py"])
    print("阅读原文完成")
    subprocess.run(["python", "write_to_html.py"])
    print("排版完成")
    subprocess.run(["python", "save_data.py"])
    print("数据存储完成")

if __name__ == "__main__":
    main()