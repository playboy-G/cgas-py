import requests
import json

def json_sample():
  url = "https://api.deepseek.com/chat/completions"

  payload = json.dumps({
    "messages": [
      {
        "content": "You are a helpful assistant",
        "role": "system"
      },
      {
        "content": "Hi",
        "role": "user"
      }
    ],
    # 使用的模型的ID：[deepseek-chat] [deepseek-reasoner]
    "model": "deepseek-chat",
    # 介于 -2.0 和 2.0 之间的数字。如果该值为正，那么新 token 会根据其在已有文本中的出现频率受到相应的惩罚，降低模型重复相同内容的可能性 default:0
    "frequency_penalty": 0,
    # 介于 1 到 8192 间的整数，限制一次请求中模型生成 completion 的最大 token 数。输入 token 和输出 token 的总长度受模型的上下文长度的限制。 default:4096
    "max_tokens": 2048,
    "presence_penalty": 0,
    "response_format": {
      "type": "text"
    },
    "stop": None,
    "stream": False,
    "stream_options": None,
    "temperature": 1,
    "top_p": 1,
    "tools": None,
    "tool_choice": "none",
    "logprobs": False,
    "top_logprobs": None
  })
  headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': 'Bearer sk-0f0b92504f7244daa75870008d1092e1'
  }

  response = requests.request("POST", url, headers=headers, data=payload)

  print(response.text)

