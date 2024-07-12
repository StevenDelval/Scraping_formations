# Define your item pipelines here
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from .models import *

class FranceCompetencesPipeline:

    def clean_text(self,item,list_col):
        adapter = ItemAdapter(item)
        for currency_col in list_col:
            currency_str = adapter.get(currency_col)
            if currency_str is not None:
                currency_str = currency_str.strip()
                adapter[currency_col] = currency_str
        return item
    
    def clean_est_actif(self, item):
        adapter = ItemAdapter(item)
        currency_est_actif = adapter.get("est_actif")
        if currency_est_actif == "Active":
            currency_est_actif = 1
        else:
            currency_est_actif = 0
        adapter["est_actif"] = currency_est_actif
        return item
    
    def process_item(self, item, spider):

        list_col_text= ["est_actif","date_echeance_enregistrement","niveau_de_qualification","title"]
        item = self.clean_text(item,list_col_text)
        item = self.clean_est_actif(item)

        return item

class FranceCompetencesDatabase:
    def __init__(self):
        self.Session = sessionmaker(bind=engine, autoflush=False)

    def process_item(self, item, spider):
        session = self.Session()
        try:

            # Check if rncp or rs already exists
            existing_rncp_rs= session.query(FranceCompetences).filter_by(
                code_certif=item["code_certif"]
            ).first()

            if existing_rncp_rs:
                rncp_rs = existing_rncp_rs
            else:
                rncp_rs = FranceCompetences(
                    code_certif=item["code_certif"],
                    nom_titre=item['title'],
                    est_actif=item['est_actif'],
                    niveau_de_qualification=item['niveau_de_qualification'],
                    date_echeance_enregistrement=item['date_echeance_enregistrement']
                )
                session.add(rncp_rs)
                session.commit()

            ## Formacode
            rncp_rs_formacode_list =[]
            if len(item["formacodes"]):
                for formacode in item["formacodes"]:
                    formacode_split = formacode.split(":")
                    formacode_code = int(formacode_split[0].strip())
                    formacode_nom = formacode_split[1].strip()
                    formacode_in_base = session.query(Formacode).filter_by(
                        formacode = formacode_code
                    ).first()
                    if not formacode_in_base:
                        formacode_in_base = Formacode(
                            formacode = formacode_code,
                            nom = formacode_nom
                        )
                        session.add(formacode_in_base)
                        session.commit()
                    rncp_rs_formacode_list.append(formacode_in_base)

               

            ## Certificateur
            rncp_rs_certificateur_list =[]
            if len(item["certificateurs"]):
                for certificateur in item["certificateurs"]:
                    nom_legal = certificateur[0]
                    siret = int(certificateur[1])
                    nom_commercial = certificateur[2]
                    site_internet = certificateur[3]
                    certificateur_in_base = session.query(Certificateur).filter_by(
                        siret = siret
                    ).first()
                    if not certificateur_in_base:
                        certificateur_in_base = Certificateur(
                            siret = siret,
                            nom_legal = nom_legal,
                            nom_commercial = nom_commercial,
                            site_internet = site_internet,
                        )
                        session.add(certificateur_in_base)
                        session.commit()
                    rncp_rs_certificateur_list.append(certificateur_in_base)


              
            rncp_rs.formacodes = rncp_rs_formacode_list
            rncp_rs.certificateurs = rncp_rs_certificateur_list

            session.add(rncp_rs)
            session.commit()   

        except IntegrityError as e:
            session.rollback()
            print(f"Error saving item due to integrity error: {e}")
            raise DropItem(f"Error saving item due to integrity error: {e}")
        except Exception as e:
            session.rollback()
            print(f"Error processing item: {e}")
            raise DropItem(f"Error processing item: {e}")
        finally:
            session.close()


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