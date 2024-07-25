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

@app.post("/formations/", response_model=schemas.FormationCreate)
def create_formation(formation: schemas.FormationCreate, db: Session = Depends(get_db)):
    return crud.create_formation(db=db, formation=formation)

@app.post("/france_competences/", response_model=schemas.FranceCompetencesCreate)
def create_france_competences(france_competences: schemas.FranceCompetencesCreate, db: Session = Depends(get_db)):
    return crud.create_france_competences(db=db, france_competences=france_competences)



@app.get("/formation/{code_certif}", response_model=List[FormationDetail])
def read_formation(code_certif: str, db: Session = Depends(get_db)):
    formations = crud.get_formation_by_code_certif(db, code_certif)
    if not formations:
        raise HTTPException(status_code=404, detail="Formation not found")
    return formations

@app.get("/format_code/{code_certif}", response_model=schemas.FormatCodeResponse)
def read_format_code(code_certif: str, db: Session = Depends(get_db)):
    format_code = crud.get_format_code_by_code_certif(db, code_certif)
    conc = nettoyage(appel_api(code_certif))
    print(conc)
    if format_code is None:
        raise HTTPException(status_code=404, detail="Format code not found")
    return {"format_code": format_code}


@app.get("/data/{code_certif}")#, #response_model=schemas.DataResponse)
def get_data(code_certif: str, db: Session = Depends(get_db)):
    
    formation_concurante_api = appel_api(code_certif)
    formation_conc = nettoyage(formation_concurante_api)
    
    format_code_query = text("""
        SELECT lffc.formacode
        FROM lien_france_competences_formacode lffc
        WHERE lffc.code_certif = :code_certif
    """)
    format_codes = [row[0] for row in db.execute(format_code_query, {'code_certif': code_certif})]

    formation_query = text("""
        SELECT f.titre, f.a_des_sessions, f.a_des_rs_rncp, 
                f.titre AS session_titre, s.lieu AS session_lieu, s.region AS session_region, 
                s.date_debut AS session_date_debut, s.date_fin_candidature AS session_date_fin_candidature,
                fc.nom_titre AS info_nom, fc.niveau_de_qualification AS info_niveau, 
                fc.date_echeance_enregistrement AS info_certification
        FROM formation f
        LEFT JOIN session s ON f.id_formation = s.id_formation
        JOIN france_competences fc ON fc.code_certif = fc.code_certif
        WHERE fc.code_certif = :code_certif
    """)
    result = db.execute(formation_query, {'code_certif': code_certif})
    formation_data = result.mappings().all()

    if not formation_data and formation_conc:
        data = {
     
        "formation_concurante": formation_conc
    }
    
        return {"data": data}

    if not formation_data and not formation_conc:
        raise HTTPException(status_code=404, detail="Data not found")
    
    formation_row = formation_data[0]

    data = {
        "format_code": format_codes,
        "formation": {
            "titre": formation_row['titre'],
            "a_des_sessions": formation_row['a_des_sessions'],
            "a_des_rs_rncp": formation_row['a_des_rs_rncp']
        },
        "session": {
            "titre": formation_row['session_titre'],
            "lieu": formation_row['session_lieu'],
            "region": formation_row['session_region'],
            "date_debut": formation_row['session_date_debut'],
            "date_fin_candidature": formation_row['session_date_fin_candidature']
        },
        "info_titre": {
            "nom": formation_row['info_nom'],
            "niveau": formation_row['info_niveau'],
            "certification": formation_row['info_certification']
        },
        "formation_concurante": formation_conc
    }
    
    return {"data": data}
