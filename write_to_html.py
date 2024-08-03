from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import json
from openai import OpenAI
import time
from config import API_KEY, BASE_URL

client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL,
)

def askLLM(message, retries=10, delay=8):
    """
    发送消息给LLM，如果失败则等待一段时间后重试。

    :param message: 发送到LLM的消息列表
    :param retries: 重试次数，默认为3次
    :param delay: 重试之间的延迟时间，单位为秒，默认为2秒
    :return: LLM的响应内容或者在所有重试失败后返回None
    """
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model="moonshot-v1-128k",
                temperature=0.7,
                max_tokens=2000,
                messages=message,
            )
            # 检查response是否包含所需的数据
            if response.choices and response.choices[0].message.content:
                return response.choices[0].message.content
            else:
                raise ValueError("Response from LLM is missing content.")
        except Exception as e:
            print(f"Attempt {attempt + 1} failed with error: {e}")
            if attempt < retries - 1:
                print(f"Waiting {delay} seconds before retrying...")
                time.sleep(delay)
            else:
                print("Max retries reached. No response received from LLM.")
                return None

# 读取 JSON 数据
with open('articles_summary.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

content = str(data)
content = content[:50000]

message_1 =[
        {"role": "system", "content": "根据Json中的本周AI论文信息，通俗幽默地用连续100字以内分点介绍本周论文看点摘要，不需要每篇论文都介绍，只节选部分有趣的内容作为看点,使用中文。"
                                      "尽可能避免使用专业词汇，用通俗易懂的语言进行代替。充分使用不同的emoji表情。例如（🔬,🥇，🎉，🎮️等emoji）"},
        {"role": "user", "content": f"根据Json中的本周AI论文信息，通俗幽默地用一段100字文字分点总结出本周论文看点，不需要每篇论文都介绍，精选部分有趣的作为看点,使用中文，充分使用不同的emoji表情。Json内容：{content}。"
                                    f"Output format（100字以内！精选3～5篇论文即可）:"
                                    f"本周AI论文看点如下："
                                    f"[emoji1] ..."
                                    f"[emoji2] ..."
                                    f"[emoji3] ..."
                                    f"......"
                                    f"更多关于本周论文的详细信息，让我们接着看下去吧～"},
    ]


# 设置 Jinja2 模板环境
env = Environment(loader=FileSystemLoader(''), autoescape=True)

# 添加单独的字段到渲染上下文中
summary = askLLM(message_1)

# 获取当前日期
current_date = datetime.now().date()

# 将日期格式化为字符串
time = current_date.strftime('%Y-%m-%d')

# 加载 HTML 模板
template = env.get_template('news_template.html')

# 渲染 HTML 模板，并将额外字段传递给模板
output = template.render(articles=data, summary=summary, time=time)

# 将渲染结果写入 HTML 文件
with open('output.html', 'w', encoding='utf-8') as f:
    f.write(output)

# 群公告文案
message_2 =[
        {"role": "system", "content": "根据本周AI论文信息，通俗幽默地用分点的方式重新排版输出，并按照规定格式，使用丰富的emoji表情。"},
        {"role": "user", "content": f"""根据提供的周报摘要以及输出模板，整理出本周周报信息。使用丰富的emoji表情
                                    周报摘要：{summary}
                                    输出格式：
本周AI论文关键词：xxx xxx xxx
特别看点
：
1
2
3"""},
    ]

notice = askLLM(message_2)

notice = f"🔥 {time} 特工宇宙AI论文周报\n\n" + notice

print(notice)
