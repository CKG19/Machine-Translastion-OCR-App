from ui import UserInterface
from db import TranslationApplicationDatabase
from mtl_model import MyMTLModels
from ocr_model import MyOCRModels

if __name__ == "__main__":
    host = 'localhost'
    user = 'root'
    password = ''
    database = 'translation_app_database'

    mydatabase = TranslationApplicationDatabase(
        host=host,
        user=user,
        password=password,
        database=database
    )
    mtl_model = MyMTLModels()
    ocr_model = MyOCRModels()
    ui = UserInterface(mydatabase, mtl_model, ocr_model)