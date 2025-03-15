import json
import requests
from openai import OpenAI
from decouple import config

TOKEN = config("TOKEN")
API_KEY = config("API_KEY")

templates = {
    5390: {"name": "思想品德-感动感悟", "index": 1},
    5399: {"name": "学术志趣与偏好", "index": 2},
    5408: {"name": "心理素质展示", "index": 3},
}

prefix_prompt = "我正在填写综合评价，请你根据以下内容要求以及格式进行填写。要求：评价正文字数不要超过50字，题目需要自拟而非照抄，水文而已。"

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.siliconflow.cn/v1",
)

for template_id, template in templates.items():
    # 读取文本文件
    file_name = f"{template['name']}.txt"
    with open(file_name, "r", encoding="utf-8") as f:
        text = prefix_prompt
        text += f.read()

    response = client.chat.completions.create(
        model="Qwen/Qwen2.5-7B-Instruct",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant designed to output JSON.",
            },
            {"role": "user", "content": text},
        ],
        response_format={"type": "json_object"},
    )

    # 解析AI返回的JSON
    generated_content = json.loads(response.choices[0].message.content)
    print(generated_content)
    title = generated_content.get("title", "")
    content = generated_content.get("content", "")

    # 构造请求体
    data = {
        "categoryId": template["index"],
        "recordTemplate": template_id,
        "title": title,
        "content": content,
        "type": 0,
        "isSelfVisible": "false",
        "eventTimeType": 1,
        "sign": "6219983b0e07be0f0380fcdc0af63974eb51d4c6",
        "application": "student",
        "system-env": "heilongjiang-gz",
    }

    # 发送POST请求
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "authorization": "Bearer " + TOKEN,
        "content-type": "application/x-www-form-urlencoded",
        "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Microsoft Edge";v="134"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "version-time": "0.0.9",
    }

    response = requests.post(
        "https://api-gzpj.hljedu.gov.cn/record/publish",
        headers=headers,
        data=data
    )

    print(response.status_code)
    print(response.json())

