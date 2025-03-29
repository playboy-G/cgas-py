from openai import OpenAI

def openai_sdk():
    client = OpenAI(api_key="sk-0f0b92504f7244daa75870008d1092e1", base_url="https://api.deepseek.com")

    response = client.chat.completions.create(
        # model="deepseek-chat",
        model="deepseek-reasoner",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "wangzg"},
        ],
        stream=False
    )

    print(response.choices[0].message.content)

if __name__ == '__main__':
    openai_sdk()