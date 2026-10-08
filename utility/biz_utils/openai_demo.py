import os
import cv2
import base64
import json

from openai import OpenAI



def chat():
    img = cv2.imread("img.png")

    _, encode_img = cv2.imencode(".jpg", img)
    img_bytes = encode_img.tobytes()
    b64_img = base64.b64encode(img_bytes).decode("utf-8")

    client = OpenAI(
        base_url="https://idealab.alibaba-inc.com/api/openai/v1",
        api_key='b9a80cded36af7a450df1a5f16588aae'
    )

    messages = [
        {'role': 'system',
        'content': 'You are a professional image content review AI, equipped with capabilities in object detection, OCR text recognition, '
                    'and image analysis. You need to process images provided by users strictly according to the following steps.'},
        {'role': 'user', 'content': [
            {"type": "text",
            "text": f"【风暴怒折20101，意志捍卫20103】是ocr识别出潮汐守望者的区服信息， 请帮确认下这些识别的结果是出现在图片中，或者识别的文字是否准确如果准确，直接返回正确，如果错误，请纠正后返回结果\n 注意严格遵循以下指令：1. 按照以下格式返回 {{'ocr_res':'风暴怒折20101','ai_res:'纠正后的结果'}} 2. 不要做任何多余的解释"},
            {
                "type": "image_url",
                "image_url": {
                    "url":f"data:image/jpeg;base64,{b64_img}"
                }
            }
        ]}]
    completion = client.chat.completions.create(
        model="claude35_sonnet2",
        messages=messages
    )
    print(completion)
    chat_json = json.loads(completion.model_dump_json())
    print(chat_json)
    print(type(chat_json))

    content = chat_json['choices'][0]['message']['content']
    try:
        content = json.loads(content)
        print(type(content))
        print(content)
    except Exception as e:
        pass



if __name__ == '__main__':
    chat()