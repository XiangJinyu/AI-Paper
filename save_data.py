import json
from datetime import date

# 加载已有的papers数据
with open('total_papers.json', 'r') as file:
    papers = json.load(file)

with open('extracted_data.json', 'r') as file:
    new_papers = json.load(file)

# 检查新的papers是否已存在于已有的papers中
for new_paper in new_papers:
    title_exists = False
    for paper in papers:
        if paper["Title"] == new_paper["Title"]:
            title_exists = True
            break
    if not title_exists:
        new_paper["Date"] = str(date.today())
        papers.append(new_paper)

# 将更新后的papers保存回文件中
with open('total_papers.json', 'w') as file:
    json.dump(papers, file, indent=4)
