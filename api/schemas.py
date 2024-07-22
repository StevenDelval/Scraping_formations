# schemas.py
from pydantic import BaseModel
from typing import List, Optional

class SessionCreate(BaseModel):
    nom_session: str
    date_candidature: Optional[str] = None
    additional_info: Optional[str] = None
    alternance: Optional[bool] = None
    duree: Optional[str] = None
    region: Optional[str] = None
    lieu: Optional[str] = None
    date_debut: Optional[str] = None
    distanciel: Optional[bool] = None

class FormationCreate(BaseModel):
    titre: str
    a_des_sessions: bool
    a_des_rs_rncp: bool
    sessions: Optional[List[SessionCreate]] = []

class FranceCompetencesCreate(BaseModel):
    code_certif: str
    titre: str
    formacodes: List[str]
    certificateurs: List[str]
    est_actif: bool
    niveau_de_qualification: str
    date_echeance_enregistrement: Optional[str] = None
