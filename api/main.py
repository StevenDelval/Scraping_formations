# main.py
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import crud
import schemas
from sqlalchemy import text
from models import *
# from crud import get_formation_by_code_certif, get_format_code_by_code_certif
#from schemas import FormationDetail, FormatCodeResponse
from typing import List, Optional

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

@app.post("/formations/", response_model=schemas.FormationCreate)
def create_formation(formation: schemas.FormationCreate, db: Session = Depends(get_db)):
    return crud.create_formation(db=db, formation=formation)

@app.post("/france_competences/", response_model=schemas.FranceCompetencesCreate)
def create_france_competences(france_competences: schemas.FranceCompetencesCreate, db: Session = Depends(get_db)):
    return crud.create_france_competences(db=db, france_competences=france_competences)

# @app.get("/details_by_code_certif/", response_model=schemas.FormationDetail)
# def get_details_by_code_certif(code_certif: str, db: Session = Depends(get_db)):
#     details = crud.get_details_by_code_certif(db, code_certif)
#     if not details:
#         raise HTTPException(status_code=404, detail="Formation not found")
#     return details

@app.get("/formation/{code_certif}", response_model=List[FormationDetail])
def read_formation(code_certif: str, db: Session = Depends(get_db)):
    formations = crud.get_formation_by_code_certif(db, code_certif)
    if not formations:
        raise HTTPException(status_code=404, detail="Formation not found")
    return formations

@app.get("/format_code/{code_certif}", response_model=schemas.FormatCodeResponse)
def read_format_code(code_certif: str, db: Session = Depends(get_db)):
    format_code = crud.get_format_code_by_code_certif(db, code_certif)
    if format_code is None:
        raise HTTPException(status_code=404, detail="Format code not found")
    return {"format_code": format_code}


@app.get("/data/{code_certif}", response_model=schemas.DataResponse)
def get_data(code_certif: str, db: Session = Depends(get_db)):
    try:
        format_code_query = text("""
            SELECT lffc.formacode
            FROM lien_france_competences_formacode lffc
            WHERE lffc.code_certif = :code_certif
        """)
        format_codes = [row[0] for row in db.execute(format_code_query, {'code_certif': code_certif})]

        formation_query = text("""
            SELECT f.titre, f.a_des_sessions, f.a_des_rs_rncp, 
                   s.titre AS session_titre, s.lieu AS session_lieu, s.region AS session_region, 
                   s.date_debut AS session_date_debut, s.date_fin_candidature AS session_date_fin_candidature,
                   fc.nom_titre AS info_nom, fc.niveau_de_qualification AS info_niveau, 
                   fc.date_echeance_enregistrement AS info_certification
            FROM formation f
            LEFT JOIN session s ON f.id_formation = s.id_formation
            JOIN france_competences fc ON fc.code_certif = fc.code_certif
            WHERE f.code_certif = :code_certif
        """)
        result = db.execute(formation_query, {'code_certif': code_certif}).fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Data not found")

        data = {
            "format_code": format_codes,
            "formation": {
                "titre": result['titre'],
                "a_des_sessions": result['a_des_sessions'],
                "a_des_rs_rncp": result['a_des_rs_rncp']
            },
            "session": {
                "titre": result['session_titre'],
                "lieu": result['session_lieu'],
                "region": result['session_region'],
                "date_debut": result['session_date_debut'],
                "date_fin_candidature": result['session_date_fin_candidature']
            },
            "info_titre": {
                "nom": result['info_nom'],
                "niveau": result['info_niveau'],
                "certification": result['info_certification']
            }
        }

        return {"data": data}

    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")