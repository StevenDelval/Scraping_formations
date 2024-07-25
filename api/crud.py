# crud.py
from sqlalchemy.orm import Session
from sqlalchemy import text
import models
import schemas
import requests

def create_formation(db: Session, formation: schemas.FormationCreate):
    db_formation = models.Formation(**formation.dict())
    db.add(db_formation)
    db.commit()
    db.refresh(db_formation)
    return db_formation

def create_france_competences(db: Session, france_competences: schemas.FranceCompetencesCreate):
    db_france_competences = models.FranceCompetences(**france_competences.dict())
    db.add(db_france_competences)
    db.commit()
    db.refresh(db_france_competences)
    return db_france_competences

def create_session(db: Session, session: schemas.SessionCreate):
    db_session = models.Session(**session.dict())
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session



def get_formation_by_code_certif(db: Session, code_certif: str):
    try:
        result = db.execute(text("""
            SELECT f.id_formation, f.titre, f.a_des_sessions, fc.est_actif, fc.nom_titre,
                   s.nom, s.lieu, s.region, s.date_debut, f.a_des_rs_rncp
            FROM formation f
            JOIN lien_formation_france_competences lffc ON f.id_formation = lffc.id_formation
            JOIN france_competences fc ON lffc.code_certif = fc.code_certif
            LEFT JOIN session s ON f.id_formation = s.id_formation
            WHERE lffc.code_certif = :code_certif
        """), {'code_certif': code_certif})
        
        # Convertir les résultats en dictionnaires
        formations = [dict(row) for row in result.mappings().all()]
        
        return formations

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def get_format_code_by_code_certif(db: Session, code_certif: str):
    try:
        result = db.execute(text("""
            SELECT lffc.formacode
            FROM lien_france_competences_formacode lffc
            JOIN france_competences fc ON lffc.code_certif = fc.code_certif
            WHERE lffc.code_certif = :code_certif
        """), {'code_certif': code_certif}).all()
       
        # Convertir les résultats en dictionnaires et accéder à formacode
        
        if result:
            result_dict = [r[0] for r in result ]
            return result_dict
        else:
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None