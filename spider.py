import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta

# 获取今天的日期
today = datetime.now().date()

# 创建一个列表来存储所有论文数据
all_papers_data = []

# 循环从七天前到今天
for i in range(7):
    # 计算日期
    date = (today - timedelta(days=i)).strftime('%Y-%m-%d')

    # 构造目标网址
    url = f'https://huggingface.co/papers?date={date}'

    # 发送HTTP GET请求
    response = requests.get(url)

    # 检查请求是否成功
    if response.status_code == 200:
        # 使用BeautifulSoup解析HTML内容
        soup = BeautifulSoup(response.text, 'html.parser')

        # 提取所有论文的信息
        papers = soup.find_all('article', class_='relative flex flex-col overflow-hidden rounded-xl border')

        for paper in papers:
            # 提取链接
            link = paper.find('a', class_='shadow-alternate-sm')['href']

            # 提取标题
            title = paper.find('h3').find('a').get_text(strip=True)

            # 提取点赞数
            leading_none_divs = paper.select('div.leading-none')
            for div in leading_none_divs:
                upvotes = div.get_text(strip=True)
                print(upvotes)

            # 将结果添加到列表中
            all_papers_data.append({
                'Title': title,
                'Link': f"https://huggingface.co{link}",
                'Upvotes': upvotes,
                'Date': date
            })
    else:
        print(f'Failed to retrieve the webpage for {date}')

# 将列表转换为JSON格式的字符串
json_data = json.dumps(all_papers_data, indent=4)

# 写入JSON文件
with open('papers.json', 'w') as json_file:
    json_file.write(json_data)

print('Data for the past 7 days written to papers.json successfully.')