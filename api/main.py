# main.py
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import crud
import schemas
from sqlalchemy import text
from models import *
from typing import List, Optional
from api_requete_fc import *

# Crée les tables dans la base de données
Session_db = sessionmaker(bind=engine, autoflush=False)

app = FastAPI()

# Dépendance pour obtenir une session de base de données
def get_db():
    db = Session_db()
    try:
        yield db
    finally:
        db.close()


def verifier_code_certif(code_certif):
    """
    Vérifie si le code de certification fourni respecte le format attendu.

    Le code de certification doit commencer par 'rs' ou 'rncp' suivi d'un nombre.

    Args:
        code_certif (str): Le code de certification à vérifier.

    Returns:
        bool: Retourne True si le code de certification correspond au format requis, False sinon.
    """
    # Définir l'expression régulière pour vérifier le format
    pattern = r'^(rs|rncp)\d+$'
    
    # Vérifier si code_certif correspond au pattern
    match = re.match(pattern, code_certif)
    
    return True if match is not None else False

@app.post("/formations/", response_model=schemas.FormationCreate)
def create_formation(formation: schemas.FormationCreate, db: Session = Depends(get_db)):
    """
    Create a new formation in the database.

    Args:
        formation (schemas.FormationCreate): The data for the formation to create.
        db (Session): The SQLAlchemy database session.

    Returns:
        schemas.FormationCreate: The created Formation object.
    """
    return crud.create_formation(db=db, formation=formation)

@app.post("/france_competences/", response_model=schemas.FranceCompetencesCreate)
def create_france_competences(france_competences: schemas.FranceCompetencesCreate, db: Session = Depends(get_db)):
    """
    Create new France competencies in the database.

    Args:
        france_competences (schemas.FranceCompetencesCreate): The data for the France competencies to create.
        db (Session): The SQLAlchemy database session.

    Returns:
        schemas.FranceCompetencesCreate: The created FranceCompetences object.
    """
    return crud.create_france_competences(db=db, france_competences=france_competences)



@app.get("/formation/{code_certif}", response_model=List[FormationDetail])
def read_formation(code_certif: str, db: Session = Depends(get_db)):
    """
    Retrieve formations associated with a specific certification code.

    Args:
        code_certif (str): The certification code to filter formations.
        db (Session): The SQLAlchemy database session.

    Returns:
        List[schemas.FormationDetail]: A list of formation details.
    """
    formations = crud.get_formation_by_code_certif(db, code_certif)
    if not formations:
        raise HTTPException(status_code=404, detail="Formation not found")
    return formations

@app.get("/format_code/{code_certif}", response_model=schemas.FormatCodeResponse)
def read_format_code(code_certif: str, db: Session = Depends(get_db)):
    """
    Retrieve format codes associated with a specific certification code.

    Args:
        code_certif (str): The certification code to filter format codes.
        db (Session): The SQLAlchemy database session.

    Returns:
        dict: A dictionary containing the format codes.
    """
    format_code = crud.get_format_code_by_code_certif(db, code_certif)
    conc = nettoyage(appel_api(code_certif))
    print(conc)
    if format_code is None:
        raise HTTPException(status_code=404, detail="Format code not found")
    return {"format_code": format_code}


@app.get("/data/{code_certif}")#, #response_model=schemas.DataResponse)
def get_data(code_certif: str, db: Session = Depends(get_db)):
    """
    Retrieve comprehensive data related to a specific certification code, including format codes, formations, sessions, and additional information.

    Args:
        code_certif (str): The certification code to filter data.
        db (Session): The SQLAlchemy database session.

    Returns:
        dict: A dictionary containing the data related to the certification code, including format codes, formations, sessions, and additional information.
    """
    code_certif = code_certif.lower()
    if not verifier_code_certif(code_certif):
        raise HTTPException(status_code=400, detail="Invalid code_certif format. It should start with 'rs' or 'rncp' followed by digits.")
    
    formation_concurante_api = appel_api(code_certif)
    formation_conc = nettoyage(formation_concurante_api)
    
    format_code_query = text("""
        SELECT lffc.formacode , f.nom
        FROM lien_france_competences_formacode lffc
        JOIN formacode f ON lffc.formacode = f.formacode
        WHERE lffc.code_certif = :code_certif
    """)
    
    format_codes = [{row.formacode:row.nom} for row in db.execute(format_code_query, {'code_certif': code_certif})]

    titre_info_query=text("""
        SELECT fc.code_certif, fc.nom_titre, fc.niveau_de_qualification, fc.est_actif 
        FROM france_competences fc
        WHERE fc.code_certif = :code_certif
    """)
    titre_info = db.execute(titre_info_query, {'code_certif': code_certif}).mappings().first()
    if not titre_info:
        titre_info = {"formation":"Aucune titre rncp ou rs trouvée"}


    id_formation_query = text("""
        SELECT llfc.id_formation
        FROM lien_formation_france_competences llfc 
        WHERE llfc.code_certif = :code_certif
    """)

    set_id_foramtion = {row.id_formation for row in db.execute(id_formation_query, {'code_certif': code_certif})}
    formation_query = text("""
        SELECT f.id_formation, f.titre, f.a_des_sessions, f.a_des_rs_rncp
        FROM formation f
        WHERE f.id_formation = :id_formation
    """)
    session_query =text("""
        SELECT s.id_formation, s.id_session, s.nom, s.lieu, s.region, s.date_fin_candidature, s.est_en_alternance, s.est_en_distanciel
        FROM session s
        WHERE s.id_formation = :id_formation
    """)
    liste_foramtion = []
    liste_session = []
    for id_formation in set_id_foramtion:
        liste_foramtion.append(db.execute(formation_query, {'id_formation': id_formation}).first()._mapping)
        liste_session.append(db.execute(session_query, {'id_formation': id_formation}).mappings().all())
    
    flat_liste_session = [item for sublist in liste_session for item in sublist]

    data = {
        "format_code": format_codes,
        "formations": liste_foramtion,
        "session": flat_liste_session,
        "info_titre": {
            **titre_info
        },
        "formation_concurante": formation_conc
    }
    
    return {"data": data}
