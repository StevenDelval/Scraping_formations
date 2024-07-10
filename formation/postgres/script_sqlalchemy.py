from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base 
import csv
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class FormationItem(Base):
    __tablename__ = 'Formation'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(Integer)
    rncp = Column(String)
    rs = Column(String)


POSTGRES_URL = os.getenv('POSTGRES_URL')  #à changer par url postgres

# Configuration de la base de données
engine = create_engine('sqlite:///scrapy_items.db') #à enlever
# engine = create_engine(POSTGRES_URL) 

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()






# la suite est inutile pour ce projet?????????

# def import_books_from_csv(csv_file_path):
#     with open(csv_file_path, newline='', encoding='ISO-8859-1') as csvfile:
#         csvreader =  csv.DictReader(csvfile, delimiter=';', quotechar='"', escapechar='\\')
#         for row in csvreader:
#             book = Book(
#                 ISBN=row['ISBN'],
#                 Book_Title=row['Book-Title'],
#                 Book_Author=row['Book-Author'],
#                 Year_Of_Publication=int(row['Year-Of-Publication']),
#                 Publisher=row['Publisher'],
#                 Image_URL_S=row['Image-URL-S'],
#                 Image_URL_M=row['Image-URL-M'],
#                 Image_URL_L=row['Image-URL-L']
#             )
#             session.add(book)
#         session.commit()

# if __name__ == '__main__':
#     # Chemin vers le fichier CSV
#     csv_file_path = 'data/books.csv'
#     # import_books_from_csv(csv_file_path)
