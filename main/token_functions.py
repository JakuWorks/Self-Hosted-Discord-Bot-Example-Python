from platform import node
from typing import Union

from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from getmac import get_mac_address
from cpuinfo import get_cpu_info
from helper_functions import predictable_shuffle_string, b64encode_utf8, my_b64utf8_decode
from config_reads import config_reads


def get_salt() -> bytes:
    salt_encoded: str = config_reads.salt_base64encoded_utf8

    if not salt_encoded:
        raise RuntimeError("Tried to get_salt that didn't exist!")

    return my_b64utf8_decode(salt_encoded)


def set_new_salt() -> None:
    salt_bytes: bytes = get_random_bytes(32)
    salt_base64encoded_utf8 = b64encode_utf8(salt_bytes)
    config_reads.edit_key(section=config_reads.config_main_n, key=config_reads.salt_base64encoded_utf8_n, value=salt_base64encoded_utf8)


def generate_encryption_password(generate_new_salt: bool) -> bytes:
    secret_string1: str = r"LDg52tmeNQ59*%F957dEpT#6!mk$"
    secret_string2: str = r"Q6DtyVJ45je!NVJ*3^%&^E4uFF5Kqd7%4"
    secret_string3: str = r"NxaQVw8vu9uU9cz5WEn#jdNznk7!pPC4"

    cpu_info: dict = get_cpu_info()

    cpu_brand: str = cpu_info["brand_raw"]
    cpu_model: str = str(cpu_info["model"])
    system_hostname: str = node()
    mac_info: str | None = get_mac_address()

    if mac_info is None:
        raise RuntimeError("Error during inputless Encryption token generation! Couldn't get_mac_address!")

    # epf - Encryption Password Foundation
    # s - Step

    epf_s1: str = secret_string1.join([cpu_brand, cpu_model])
    epf_s2: str = secret_string2.join([epf_s1, system_hostname])
    epf_s3: str = secret_string3.join([epf_s2, mac_info])
    epf_s4: str = predictable_shuffle_string(epf_s3)

    if generate_new_salt:
        set_new_salt()

    salt = get_salt()

    encryption_password: bytes = PBKDF2(epf_s4, dkLen=32, salt=salt)

    return encryption_password


def get_cipher(generate_new_salt: bool, cipher_iv: Union[bytes, None] = None):
    if cipher_iv:
        return AES.new(generate_encryption_password(generate_new_salt=generate_new_salt), AES.MODE_CBC, iv=cipher_iv)

    return AES.new(generate_encryption_password(generate_new_salt=generate_new_salt), AES.MODE_CBC)


def try_get_saved_token() -> str | None:
    ciphered_token_iv: bytes = my_b64utf8_decode(config_reads.token_ciphered_iv_base64encoded_utf8)
    ciphered_token: bytes = my_b64utf8_decode(config_reads.token_ciphered_base64encoded_utf8)

    if not ciphered_token_iv or not ciphered_token:
        return None

    cipher = get_cipher(generate_new_salt=False, cipher_iv=ciphered_token_iv)

    token_bytes_padded: bytes = cipher.decrypt(ciphered_token)
    token_bytes: bytes = unpad(token_bytes_padded, AES.block_size)

    token_utf8: str = token_bytes.decode(encoding='utf-8')

    return token_utf8


def save_token(token: str) -> None:
    token_bytes: bytes = token.encode(encoding='utf-8')
    token_bytes_padded: bytes = pad(token_bytes, AES.block_size)

    cipher = get_cipher(generate_new_salt=True)

    ciphered_token = cipher.encrypt(token_bytes_padded)

    ciphered_token_iv = cipher.iv
    ciphered_token_data = ciphered_token

    ciphered_token_iv_b64utf8 = b64encode_utf8(ciphered_token_iv)
    ciphered_token_data_b64utf8 = b64encode_utf8(ciphered_token_data)

    config_reads.edit_key(value=ciphered_token_iv_b64utf8,
                          section=config_reads.config_main_n,
                          key=config_reads.token_ciphered_iv_base64encoded_utf8_n)
    config_reads.edit_key(value=ciphered_token_data_b64utf8,
                          section=config_reads.config_main_n,
                          key=config_reads.token_ciphered_base64encoded_utf8_n)
