# main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import crud
import schemas
from models import *


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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
