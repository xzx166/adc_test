from airtest.core.api import *

import binascii
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad, pad

from utility.base.adc_api import *
from utility.base.adc_monitor import *

def decrypt(content, aesKey):
    if content and aesKey:
        monitor_print(f"---decrypt_content: {content}")
        try:
            raw = aesKey.encode('utf-8')
            skeySpec = AES.new(raw, AES.MODE_ECB)
            decrypted = skeySpec.decrypt(binascii.unhexlify(content))
            # monitor_print(f"decrypted: {decrypted}")
            result = unpad(decrypted, AES.block_size).decode('utf-8')
            # monitor_print(f"unpad decrypted: {result}")
            return result
        except Exception as e:
            # lx_break_app(ext_info={'key':'120004'},e=e, desc='解密异常')
            return None
    else:
        # lx_break_app(ext_info={'key':'120005'},desc=f"content:{content}或aeskey:{aesKey}为空")
        return None


def encrypt(content, aesKey):
    if content and aesKey:
        try:
            # 将密钥编码为字节
            raw_key = aesKey.encode('utf-8')

            # 创建 AES 加密对象 (ECB 模式)
            cipher = AES.new(raw_key, AES.MODE_ECB)

            # PKCS7 填充明文数据
            padded_data = pad(content.encode('utf-8'), AES.block_size)

            # AES 加密
            encrypted = cipher.encrypt(padded_data)

            # 将二进制密文转换为十六进制字符串
            encrypted_hex = binascii.hexlify(encrypted).decode('utf-8')

            return encrypted_hex
        except Exception as e:
            return None
    else:
        return None
