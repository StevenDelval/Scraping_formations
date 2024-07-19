# Define your item pipelines here
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# useful for handling different item types with a single interface
from urllib.parse import urlparse
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from .models import *
from datetime import datetime
import re

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
    
    def clean_date_echeance_enregistrement(self, item):
        adapter = ItemAdapter(item)
        date_str = adapter.get('date_echeance_enregistrement')
        try:
            date_str = datetime.strptime(date_str, '%d-%m-%Y').strftime('%Y-%m-%d')
            adapter["date_echeance_enregistrement"] = date_str
            return item
        except ValueError:
            return item
    
    def process_item(self, item, spider):

        list_col_text= ["est_actif","date_echeance_enregistrement","niveau_de_qualification","titre"]
        item = self.clean_text(item,list_col_text)
        item = self.clean_est_actif(item)
        item = self.clean_date_echeance_enregistrement(item)

        return item

class FranceCompetencesDatabase:
    def __init__(self):
        self.Session = sessionmaker(bind=engine, autoflush=False)

    def process_item(self, item, spider):
        session = self.Session()
        try:

            # Check if rncp or rs already exists
            rncp_rs= session.query(FranceCompetences).filter_by(
                code_certif=item["code_certif"]
            ).first()
            rncp_rs.nom_titre = item['titre']
            rncp_rs.est_actif = item['est_actif']
            rncp_rs.niveau_de_qualification = item['niveau_de_qualification']
            rncp_rs.date_echeance_enregistrement = item['date_echeance_enregistrement']

    
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

        return item


####################################################################################################


class SimplonPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        sessions = adapter.get('sessions', [])
        for session in sessions:

            session=self.clean_session_data(session)
        
        return item
    
    def clean_session_data(self, session_item):
        adapter = ItemAdapter(session_item)
        
        adapter['date_debut']= self.clean_date_debut(adapter.get('date_debut'))
        adapter['date_candidature']= self.clean_date_candidature(adapter.get('date_candidature'))
        adapter['distanciel']= bool(adapter.get('distanciel'))
        adapter['duree']= self.clean_duree(adapter.get('duree'))
        adapter['lieu']= self.clean_text(adapter.get('lieu'))
        adapter['nom_session']= adapter.get('nom_session')
        adapter['region']= self.clean_text(adapter.get('region'))
        adapter['alternance']= bool(adapter.get('alternance'))
        
        return session_item

    def clean_date_candidature(self, date_str):
        try:
            return datetime.strptime(date_str, '%d/%m/%Y').strftime('%Y-%m-%d')
        except ValueError:
            return date_str

    def clean_date_debut(self, date_str):
        date_str = date_str.strip().replace("Début : ", "")
        try:
            date_obj = datetime.strptime(date_str, '%B %Y')
            return date_obj.strftime('%Y-%m-%d')
        except ValueError:
            month_map = {
                'janvier': '01', 'février': '02', 'mars': '03', 'avril': '04',
                'mai': '05', 'juin': '06', 'juillet': '07', 'août': '08',
                'septembre': '09', 'octobre': '10', 'novembre': '11', 'décembre': '12'
            }
            for month_name, month_num in month_map.items():
                if month_name in date_str.lower():
                    year = re.search(r'\d{4}', date_str).group()
                    return f"{year}-{month_num}-01"
            return date_str

    def clean_duree(self, duree_str):
        try:
            duree_str=duree_str.strip()
            return duree_str
        except:
            return duree_str

    def clean_text(self, text_str):
        return text_str.strip()
        


class SimplonDatabase(object):
    def __init__(self):
        self.Session = sessionmaker(bind=engine, autoflush=False)

    def process_item(self, item, spider):

        try:
            session = self.Session()

            existing_formation= session.query(Formation).filter_by(
                titre=item["titre"]
            ).first()

            if existing_formation:
                formation = existing_formation
            else:
                formation = Formation(
                    titre=item['titre'],
                    a_des_sessions=item['a_des_sessions'],
                    a_des_rs_rncp=item['a_des_rs_rncp']
                )
                session.add(formation)
                session.commit()
            
            liste_rs_rncp =[]
            if item["rncp"]:
                path_segments = urlparse(item["rncp"]).path.split('/')
                code_certif = f"{path_segments[-3].lower()}{path_segments[-2]}"

                # Check if rncp or rs already exists
                existing_rncp_rs= session.query(FranceCompetences).filter_by(
                    code_certif=code_certif
                ).first()

                if existing_rncp_rs:
                    rncp_rs = existing_rncp_rs
                else:
                    rncp_rs = FranceCompetences(
                        code_certif=code_certif,
                    )
                    session.add(rncp_rs)
                    session.commit()
                liste_rs_rncp.append(rncp_rs)
            try: 
                len(item["rs"])
            except:
                pass
            else:
                if len(item["rs"]):
                    for rs in item["rs"]:
                        rs = rs[:-1] if rs[-1] == "/" else rs
                        path_segments = urlparse(rs).path.split('/')
                        code_certif = f"{path_segments[-2].lower()}{path_segments[-1]}"

                        # Check if rncp or rs already exists
                        existing_rncp_rs= session.query(FranceCompetences).filter_by(
                            code_certif=code_certif
                        ).first()

                        if existing_rncp_rs:
                            rncp_rs = existing_rncp_rs
                        else:
                            rncp_rs = FranceCompetences(
                                code_certif=code_certif,
                            )
                            session.add(rncp_rs)
                            session.commit()
                        liste_rs_rncp.append(rncp_rs)

            

                
            try:
                len(item["sessions"])
            except:
                pass
            else:
                if len(item["sessions"]):
                    for session_item in item["sessions"]:

                        existing_session= session.query(Session).filter_by(
                            nom= session_item['nom_session'],
                            region = session_item['region'],
                            date_debut = session_item['date_debut']
                        ).first()

                        if existing_session:
                            session_formation = existing_session
                        else:
                            session_formation = Session(
                                id_formation=formation.id_formation,
                                nom = session_item['nom_session'],
                                lieu = session_item['lieu'],
                                region = session_item['region'],
                                date_fin_candidature = session_item['date_candidature'],
                                date_debut = session_item['date_debut'],
                                est_en_alternance = session_item['alternance'],
                                est_en_distanciel = session_item['distanciel']
                            )
                            session.add(session_formation)
                            session.commit()
                    

            formation.france_competences = list(set(liste_rs_rncp))
            session.add(formation)
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

        return item
    
        # db_item = MyItem(
        #     name=item.get('name'),
        #     description=item.get('description'),
        #     price=item.get('price')
        # )
        # self.session.add(db_item)
        # self.session.commit()
        # return item