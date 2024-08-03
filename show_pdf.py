import concurrent.futures
import json
import requests
from pdfminer.high_level import extract_text
import os
from PIL import Image
import fitz
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
                model="moonshot-v1-32k",
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


# 从本地 JSON 文件中读取文章数据
def load_articles_from_json(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        articles = json.load(f)
    return articles


# 函数用于检测图像的颜色丰富度
def is_colorful(image, threshold=5000):
    # 将图像转换为RGB模式
    rgb_image = image.convert("RGB")

    # 获取图像的所有像素
    pixels = list(rgb_image.getdata())

    # 计算颜色数量
    colors = set(pixels)

    # 如果颜色数量超过阈值，则判断为颜色丰富
    return len(colors) > threshold

# 创建存储图片的文件夹
output_folder = "top_half_images"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
import os

# 创建存储PDF文件的文件夹
pdf_folder = "pdf_files"
if not os.path.exists(pdf_folder):
    os.makedirs(pdf_folder)

# 处理单篇文章
def process_article(article, index):
    # 下载 PDF 文件
    response = requests.get(article["PDF Link"])
    pdf_filename = f"output_{index}.pdf"
    pdf_path = os.path.join(pdf_folder, pdf_filename)
    with open(pdf_path, "wb") as f:
        f.write(response.content)

    # 提取 PDF 文本信息
    text = extract_text(pdf_path)

    text = text[:25000]

    # 提取文章摘要
    summary_message_1 = [
        {"role": "system", "content": "通俗幽默地用一段连续的200字文字以内介绍这个文章讲了什么，尽量用通俗的语言代替专业词汇，但不要丧失准确性,使用中文。"
                                      "先用一句话在文案的开头给出这个文章的技术可以用来干什么，要有趣的使用。"},
        {"role": "user", "content": f"通俗幽默地用一段连续的200字文字以内介绍这个文章讲了什么，但不要丧失准确性,使用中文。一半内容通俗介绍这个文章技术可以用来干什么，另一半可以介绍一些技术细节。文章内容：{text}。"},
    ]
    summary1 = askLLM(summary_message_1)

    # 提取文章细节
    summary_message_2 = [
        {"role": "system", "content": """你是一名AI领域专家，根据发送给你的论文，直接输出你的论文解读笔记。不要打招呼，直接输出，你需要完成以下任务：
  回答关键问题：
  1. 主要解决了什么问题？
  2. 提出了什么解决方案？
  3. 解决方案中核心的方法/步骤/策略是什么？
  4. 结论是什么？
  5. 有什么限制条件？
  请有条理地分点组织以上信息，确保涵盖每一个点。"""},
        {"role": "user", "content": f"""文章内容：{text}。保证准确性和专业性，但尽可能以容易听懂的方式进行输出。输出不需要特殊的markdown，直接分点输出即可。
                                    Output format:
                                      1. 主要解决了什么问题？
                                      2. 提出了什么解决方案？
                                      3. 解决方案中核心的方法/步骤/策略是什么？
                                      4. 结论是什么？
                                      5. 有什么限制条件？"""},
    ]
    summary2 = askLLM(summary_message_2)

    summary = summary1 + "\n\n\nMore Details:\n\n" + summary2

    # 提取文章标题
    tag_message = [
        {"role": "system", "content": """根据用户发给你的文章摘要，进行文章分类，其中有五个分类：
        机器学习（Machine Learning, ML）：包括各种算法和模型，是AI的基础，涵盖了监督学习、无监督学习、强化学习等。

        深度学习（Deep Learning, DL）：作为ML的一个子集，专注于使用神经网络处理复杂的数据模式，特别是在图像、语音和序列数据上的应用。

        自然语言处理（Natural Language Processing, NLP）：专注于语言的理解和生成，是一个高度专业化的领域，通常需要特定的技术和模型。

        计算机视觉（Computer Vision, CV）：专注于图像和视频的分析和理解，使用DL技术在图像识别、物体检测等方面取得了显著进展。

        智能系统和应用（Intelligent Systems and Applications, ISA）：包括将AI技术应用于特定行业的解决方案，如医疗、金融、交通等，这个分类强调AI技术的实际应用和跨学科整合。
        
        仅输出一个最适合的分类的缩写。
        
        如：CV
        
        直接输出分类的类型，不要输出原因或其它无关的内容。
        
        输出的格式仅有五类，即：ML,DL,NLP,CV,ISA
        """},
        {"role": "user", "content": f"论文摘要内容：\n{article['Abstract']}\n\n"},
    ]
    tag = askLLM(tag_message)

    # 提取文章标题
    title_message = [
        {"role": "system", "content": "用一个幽默且贴近实际使用的语言，为文章取一个有意思的标题.直接输出标题内容，不要输出任何其它无关内容。"},
        {"role": "user", "content": f"用一个幽默且贴近实际使用的语言，为文章取一个有意思的标题。文章摘要内容：\n{summary}\n\n文章专业摘要内容：\n{article['Abstract']}\n\n直接用中文输出标题内容。"},
    ]
    title = askLLM(title_message)

    # 获取PDF的第一页截图并保存为图片文件
    pdf_document = fitz.open(pdf_path)
    page = pdf_document.load_page(0)  # 获取第一页
    pix = page.get_pixmap()

    # 转换为PIL Image对象
    image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    # 检测图像的颜色丰富度
    if is_colorful(image):
        # 如果图像颜色丰富，保存上半部分的截图
        half_height = image.height // 2
        top_half = image.crop((0, 0, image.width, half_height))

        # 为图片建立单独的命名
        image_filename = f"top_half_image_{index}.png"
        image_path = os.path.join(output_folder, image_filename)

        # 保存上半部分的截图
        top_half.save(image_path)

        # 更新文章字典中的路径或其他索引
        article["top_half_image_path"] = image_path

    return {"title": title, "summary": summary, "original_title": article["Title"], "tag": tag}

# 处理每篇文章并将结果写入 JSON 文件
def process_article_concurrent(article, index):
    print(f"reading {index+1}/{len(articles)} papers")
    result = process_article(article, index)
    return {
        "original_title": result['original_title'],
        "title": result['title'],
        "summary": result['summary'],
        "arxiv_link": article['ArXiv Link'],
        "top_half_image_path": article.get("top_half_image_path", None),
        "tag": result['tag']
    }

def process_articles_to_json_concurrent(articles):
    output_data = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(process_article_concurrent, article, i): i for i, article in enumerate(articles)}
        for future in concurrent.futures.as_completed(futures):
            try:
                output_data.append(future.result())
            except Exception as exc:
                print(f"Article {futures[future]} generated an exception: {exc}")

    with open("articles_summary.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)

# 调用处理函数并将结果存入 JSON 文件
articles = load_articles_from_json("unique_data.json")
process_articles_to_json_concurrent(articles)

