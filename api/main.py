# main.py
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import crud
import schemas
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