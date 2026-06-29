import os
from dotenv import load_dotenv

# 1. Загружаем переменные из файла .env в оперативную память
load_dotenv()

# 2. Достаем переменные из памяти по их именам
client_id = os.getenv("TWITCH_CLIENT_ID")
client_secret = os.getenv("TWITCH_CLIENT_SECRET")

# 3. Проверяем, что всё прочиталось успешно
print("=== ТЕСТ ПОДКЛЮЧЕНИЯ НАСТРОЕК ===")
print(f"Гляди, я нашёл Client ID: {client_id}")

# Из соображений безопасности не будем выводить секрет целиком,
# покажем только первые 4 символа, чтобы убедиться, что он есть.
if client_secret:
    print(f"А это начало твоего Client Secret: {client_secret[:4]}...")
    print("Ура! Всё прочиталось правильно. Мы готовы создавать самого бота!")
else:
    print("Ой-ой... Client Secret не найден. Проверь, правильно ли написаны имена в .env")