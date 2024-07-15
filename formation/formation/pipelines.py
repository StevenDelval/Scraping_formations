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

        list_col_text= ["est_actif","date_echeance_enregistrement","niveau_de_qualification","titre"]
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
            session_adapter = ItemAdapter(session)
            session_adapter['alternance'] = bool(session_adapter['alternance'])
            session_adapter['distanciel'] = bool(session_adapter['distanciel'])
        return item

        


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
                    

            formation.france_competences = liste_rs_rncp
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