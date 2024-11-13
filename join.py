import json
import os

import requests
import hashlib
import base64
import time
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
# Get the public key
public_key_str = """
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAzMKFQ/g2cv0avUOlSptg
DiGSFZMrW6R4qBeUWUdF1smCStnpA90wWBT3sp3DqZauj10SdCM1Or1jsre5jPZP
7ANmHTkFsywfufcKTSbDgMOfIgGy5+d8+22Z3zwH1WvAMeOFob4frHZConjzYSdX
+rlKSPFr6lBfIkc0O4DWTYL0oDvMCGNOHZBAZS4Qsv1bDJN7gRq+UKHMJrjTKiUt
nlRcgFXdN4hSStrgfynp2EwEJtQ8MgYsKCQYQXlYXlMHdaN+8RqKxdLRc9LDGXNt
8Y8L3AuBE8lhVizok6XXGI5LVZPGGfh0nLON/NlqFmxxEiCDa2L+TtIV+fJpF1mu
wQIDAQAB
-----END PUBLIC KEY-----
"""
# 从字符串加载公钥
public_key = serialization.load_pem_public_key(
    public_key_str.encode()
)

# 使用公钥加密消息
def encrypt_message(message):
    return public_key.encrypt(
        message.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

# 要发送的消息
# 当前时间戳 精确到分钟 秒数为 00
# 例如 2021-09-01 12:34:00
# 生成的 token 为 202109011234
# 时区为 UTC+8
timezone = 8
token = str(int(time.time() / 60) * 60 + 60 * timezone)  # 生成 token

# 设定 API 的 URL
url = "https://ac-hk.tzpro.uk/user/add"

# 设定 headers
headers = {
    "Authorization": token,
    "Content-Type": "application/json"
}

username = "Austin-152"

# 加密用户名
encrypted_username = encrypt_message(username).hex()  # 这个 hex() 是为了将 bytes 转换为字符串

data = json.dumps({
    "username": encrypted_username
})

# 发起 POST 请求
response = requests.post(url, headers=headers, data=data)

# 打印响应
print(response.text)
