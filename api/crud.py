# crud.py
from sqlalchemy.orm import Session
from sqlalchemy import text
import models
import schemas
import requests

def create_formation(db: Session, formation: schemas.FormationCreate):
    """
    Create a new formation in the database.

    Args:
        db (Session): The SQLAlchemy database session.
        formation (schemas.FormationCreate): The data for the formation to create.

    Returns:
        models.Formation: The created Formation object.
    """
    db_formation = models.Formation(**formation.dict())
    db.add(db_formation)
    db.commit()
    db.refresh(db_formation)
    return db_formation

def create_france_competences(db: Session, france_competences: schemas.FranceCompetencesCreate):
    """
    Create new France competencies in the database.

    Args:
        db (Session): The SQLAlchemy database session.
        france_competences (schemas.FranceCompetencesCreate): The data for the France competencies to create.

    Returns:
        models.FranceCompetences: The created FranceCompetences object.
    """
    db_france_competences = models.FranceCompetences(**france_competences.dict())
    db.add(db_france_competences)
    db.commit()
    db.refresh(db_france_competences)
    return db_france_competences

def create_session(db: Session, session: schemas.SessionCreate):
    """
    Create a new session in the database.

    Args:
        db (Session): The SQLAlchemy database session.
        session (schemas.SessionCreate): The data for the session to create.

    Returns:
        models.Session: The created Session object.
    """
    db_session = models.Session(**session.dict())
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session



def get_formation_by_code_certif(db: Session, code_certif: str):
    """
    Retrieve formations associated with a specific certification code.

    Args:
        db (Session): The SQLAlchemy database session.
        code_certif (str): The certification code to filter formations.

    Returns:
        List[dict] | None: A list of dictionaries representing the formations, or None if an error occurs.
    """
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
    """
    Retrieve format codes associated with a specific certification code.

    Args:
        db (Session): The SQLAlchemy database session.
        code_certif (str): The certification code to filter format codes.

    Returns:
        List[str] | None: A list of format codes, or None if an error occurs.
    """
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