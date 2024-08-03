import requests
from bs4 import BeautifulSoup
import json

# 读取本地 JSON 文件
with open('papers.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 新建一个空列表，用于存储提取的信息
extracted_data = []

# 遍历每个数据项
for item in data:
    # 发送HTTP GET请求
    response = requests.get(item['Link'])

    # 检查请求是否成功
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # 提取标题
        title = soup.find('h1').get_text()

        # 提取摘要
        abstract = soup.find('p', class_='text-gray-700 dark:text-gray-400').get_text()

        # 找到包含ArXiv链接的<a>标签
        arxiv_link = soup.find('a', href=lambda href: href and 'arxiv.org/abs' in href)

        # 找到包含ArXiv链接的<a>标签
        pdf_link = soup.find('a', href=lambda href: href and 'arxiv.org/pdf' in href)

        # 提取链接
        if arxiv_link:
            arxiv_url = arxiv_link['href']
        else:
            arxiv_url = None

        # 提取链接
        if pdf_link:
            pdf_url = pdf_link['href']
        else:
            pdf_url = None

        # 构造新的数据项
        extracted_item = {
            'Title': title,
            'Abstract': abstract,
            'ArXiv Link': arxiv_url,
            'PDF Link': pdf_url,
            'Upvotes': item['Upvotes']
        }

        # 将新数据项添加到提取的数据列表中
        extracted_data.append(extracted_item)

# 将提取的数据保存到新的 JSON 文件中
with open('extracted_data.json', 'w', encoding='utf-8') as f:
    json.dump(extracted_data, f, ensure_ascii=False, indent=4)
