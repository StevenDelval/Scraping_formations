# crud.py
from sqlalchemy.orm import Session
import models
import schemas

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
