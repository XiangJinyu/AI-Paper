import json

# 从本地读取JSON文件
with open('extracted_data.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# 使用字典来去除重复项
unique_data = {}
for entry in data:
    arxiv_link = entry['ArXiv Link']
    if arxiv_link not in unique_data:
        unique_data[arxiv_link] = entry

# 转换为列表
unique_data_list = list(unique_data.values())

# 将去重后的数据写回到一个新的JSON文件
with open('unique_data.json', 'w', encoding='utf-8') as file:
    json.dump(unique_data_list, file, indent=4)

print("去重后的数据已保存到 'unique_data.json' 文件中")
