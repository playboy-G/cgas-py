# base64加密
import base64

class Base64Utils:

    def __init__(self):
        print('__init__')

    def base64_encode(data):
        encoded_bytes = base64.b64encode(data.encode('utf-8'))
        encoded_string = encoded_bytes.decode()
        return encoded_string

    # base64解密
    def base64_decode(data):
        decoded_bytes = base64.b64decode(data)
        decoded_string = decoded_bytes.decode()
        return decoded_string