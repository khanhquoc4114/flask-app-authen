import os
from dotenv import load_dotenv

# Load biến môi trường từ file .env (ở cùng thư mục hoặc chỉ định path)
load_dotenv()

# Lấy giá trị
client_id = os.getenv("GOOGLE_CLIENT_ID")
client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")
print (f"Client ID: {client_id}")
print(f"Client Secret: {client_secret}")
