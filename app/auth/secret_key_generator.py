import secrets
import string


def generate_secret_key(length=32):
    """Для разовой генерации секретного ключа. Результат положить в переменную SECRET_KEY в файл,
     находящийся в корне проекта .env"""
    characters = string.ascii_letters + string.digits + string.punctuation
    key = ''.join(secrets.choice(characters) for _ in range(length))
    return key


print(generate_secret_key())
