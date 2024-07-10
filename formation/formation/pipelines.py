# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from sqlalchemy.orm import sessionmaker
import sqlite3
import re

class FormationPipeline:
    def process_item(self, item, spider):
        return item

class DatabasePipeline(object):
    # def __init__(self):
    #     self.Session = sessionmaker(bind=engine)

    def open_spider(self, spider):
        self.connection = sqlite3.connect('formation.db')
        self.cursor = connection.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXIST formation(
                id_formation INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT
                
            )
        ''')
        self.connection.commit()

    def close_spider(self, spider):
        self.session.close()

    def process_item(self, item, spider):

        self.cursor.execute('''
            INSERT INTO formation(
                id_formation,
                title
               )
                VALUES (?,?)'''
                ,(item['title']))
        
        self.connection.commit()

        return item
    
        # db_item = MyItem(
        #     name=item.get('name'),
        #     description=item.get('description'),
        #     price=item.get('price')
        # )
        # self.session.add(db_item)
        # self.session.commit()
        # return item