
from sqlalchemy import create_engine, Column, String, Integer, Float, Date, ForeignKey, Table, PrimaryKeyConstraint,ForeignKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import os 
from dotenv import load_dotenv
load_dotenv()


if bool(int(os.getenv("IS_POSTGRES"))):
    username = os.getenv("DB_USERNAME")
    hostname = os.getenv("DB_HOSTNAME")
    port = os.getenv("DB_PORT")
    database_name = os.getenv("DB_NAME")
    password = os.getenv("DB_PASSWORD")
    bdd_path = f"postgresql://{username}:{password}@{hostname}:{port}/{database_name}"
else:
    bdd_path = 'sqlite:///database.db'

engine = create_engine(bdd_path)
Base = declarative_base()
print(engine.dialect.name)
if engine.dialect.name == 'sqlite':
    date_type = String
else:
    date_type = Date
    
# Association Tables
lien_formation_france_competences = Table(
    'lien_formation_france_competences', Base.metadata,
    Column('id_formation', Integer, ForeignKey('formation.id_formation'), primary_key=True),
    Column('code_certif', String, ForeignKey('france_competences.code_certif'), primary_key=True)
)

lien_france_competences_formacode = Table(
    'lien_france_competences_formacode', Base.metadata,
    Column('code_certif', String, ForeignKey('france_competences.code_certif'), primary_key=True),
    Column('formacode', Integer, ForeignKey('formacode.formacode'), primary_key=True)
)

lien_france_competences_certificateur = Table(
    'lien_france_competences_certificateur', Base.metadata,
    Column('code_certif', String, ForeignKey('france_competences.code_certif'), primary_key=True),
    Column('siret', Integer, ForeignKey('certificateur.siret'), primary_key=True)
)


# Models
class Formation(Base):
    __tablename__ = 'formation'
    id_formation = Column(Integer, primary_key=True)
    titre = Column(String, nullable=False)
    a_des_sessions = Column(Integer, nullable=False)
    a_des_rs_rncp = Column(Integer, nullable=False)

    france_competences = relationship('FranceCompetences', secondary=lien_formation_france_competences, back_populates='formations')

class FranceCompetences(Base):
    __tablename__ = 'france_competences'
    code_certif = Column(String, primary_key=True)
    nom_titre = Column(String, nullable=True)
    est_actif = Column(Integer, nullable=True)
    niveau_de_qualification = Column(String, nullable=True)
    date_echeance_enregistrement = Column(date_type, nullable=True)

    formations = relationship('Formation', secondary=lien_formation_france_competences, back_populates='france_competences')
    formacodes = relationship('Formacode', secondary=lien_france_competences_formacode, back_populates='france_competences')
    certificateurs = relationship('Certificateur', secondary=lien_france_competences_certificateur, back_populates='france_competences')

class Formacode(Base):
    __tablename__ = 'formacode'
    formacode = Column(Integer, primary_key=True)
    nom = Column(String, nullable=False)

    france_competences = relationship('FranceCompetences', secondary=lien_france_competences_formacode, back_populates='formacodes')

class Certificateur(Base):
    __tablename__ = 'certificateur'
    siret = Column(Integer, primary_key=True)
    nom_legal = Column(String, nullable=False)
    nom_commercial = Column(String, nullable=False)
    site_internet = Column(String, nullable=False)

    france_competences = relationship('FranceCompetences', secondary=lien_france_competences_certificateur, back_populates='certificateurs')

class Session(Base):
    __tablename__ = 'session'
    id_session = Column(Integer, primary_key=True)
    id_formation=Column(Integer, ForeignKey('formation.id_formation'), nullable=False)
    nom = Column(String, nullable=False)
    lieu = Column(String, nullable=True)
    region = Column(String, nullable=True)
    date_fin_candidature = Column(date_type, nullable=True)
    date_debut = Column(date_type, nullable=True)
    est_en_alternance = Column(Integer, nullable=False)
    est_en_distanciel = Column(Integer, nullable=False)
    

# Database connection
engine = create_engine(bdd_path)
Base.metadata.create_all(engine)