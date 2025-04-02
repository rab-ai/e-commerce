import os

class Config:
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://rabiasahincs:G075cFEiv6gjHLiJ@assignment1.lvx4kdh.mongodb.net/?retryWrites=true&w=majority&appName=assignment1")
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-default-secret-key')