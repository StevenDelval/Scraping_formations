# schemas.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import date

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

class FormationBase(BaseModel):
    titre: str
    a_des_sessions: bool
    a_des_rs_rncp: bool

class FormationCreate(BaseModel):
    titre: str
    a_des_sessions: bool
    a_des_rs_rncp: bool
    code_certif: str  # Ajout de code_certif
    sessions: Optional[List[SessionCreate]] = []

class FranceCompetencesBase(BaseModel):
    code_certif: str
    titre: str
    formacodes: List[str]
    certificateurs: List[str]
    est_actif: bool
    niveau_de_qualification: str
    date_echeance_enregistrement: Optional[str] = None
    rncp_code: Optional[str] = None
    rs_code: Optional[str] = None


class FranceCompetencesCreate(BaseModel):
    code_certif: str
    titre: str
    formacodes: List[str]
    certificateurs: List[str]
    est_actif: bool
    niveau_de_qualification: str
    date_echeance_enregistrement: Optional[str] = None


class Session(BaseModel):
    nom: str
    lieu: str
    region: str

    class Config:
        from_attributes = True

class FormationBase(BaseModel):
    titre: str
    a_des_sessions: bool
    a_des_rs_rncp: bool

    class Config:
        from_attributes = True

class FormationDetail(BaseModel):
    id_formation: int
    titre: str
    a_des_sessions: bool
    a_des_rs_rncp: bool

class SessionInfo(BaseModel):
    id_session: int
    nom: str
    lieu: str
    region: str
    date_fin_candidature: Optional[str] = None
    date_debut: Optional[str] = None
    est_en_alternance: Optional[bool] = None
    est_en_distanciel: Optional[bool] = None

class FormatCodeResponse(BaseModel):
    format_code: List
    