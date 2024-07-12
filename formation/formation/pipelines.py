# Define your item pipelines here
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from sqlalchemy.orm import sessionmaker
from .models import *

class FranceCompetencesPipeline:
    pass

class FranceCompetencesDatabase:
    def __init__(self):
        self.Session = sessionmaker(bind=engine, autoflush=False)

    def process_item(self, item, spider):
        pass


####################################################################################################


class SimplonPipeline:
    def process_item(self, item, spider):
        return item

class SimplonDatabase(object):
    def __init__(self):
        self.Session = sessionmaker(bind=engine, autoflush=False)

    def process_item(self, item, spider):

        session = self.Session()
        
        formation = Formation(
            title=item['title'],
            a_des_sessions=item['a_des_sessions'],
            a_des_rs_rncp=item['a_des_rs_rncp']
        )
        session.add(formation)
        session.commit()
        

        return item
    
        # db_item = MyItem(
        #     name=item.get('name'),
        #     description=item.get('description'),
        #     price=item.get('price')
        # )
        # self.session.add(db_item)
        # self.session.commit()
        # return item