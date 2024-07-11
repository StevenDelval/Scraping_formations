
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

# Define association tables first
film_acteur = Table(
    'film_acteur', Base.metadata,
    Column('film_titre', String),
    Column('film_date', date_type),
    Column('film_realisateur', String),
    Column('acteur_id', Integer, ForeignKey('acteurs.acteur_id')),
    ForeignKeyConstraint(['film_titre', 'film_date', 'film_realisateur'], 
                         ['film.titre', 'film.date', 'film.realisateur']),
    PrimaryKeyConstraint('film_titre', 'film_date', 'film_realisateur', 'acteur_id')
)



# Define your classes
class Formation(Base):
    __tablename__ = 'formation'
    id_formation = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    a_des_sessions = Column(String)
    a_des_rs_rncp = Column(String)


class  France_competences(Base):
        __tablename__ = 'france_competence'
        code_certif=Column(String, primary_key=True)
        nom_titre=Column(String )
        est_actif=Column(Integer )
        niveau_de_qualification=Column(String )
        date_de_decision=Column(date_type )
        duree_enregistrement_en_annees=Column(Integer  )
        date_echeance_enregistrement=Column(date_type )
        Date_derniere_delivrance_possible=Column(date_type  )
    
class Formacode(Base):
        __tablename__ = 'formacode'
        formacode=Column(Integer, primary_key=True)  
        nom=Column(String) 

class Session(Base):
        __tablename__ ='session'
        id_session=Column(Integer, primary_key=True, autoincrement=True ) 
        id_formation=Column(Integer ) 
        nom=Column(String )
        lieu=Column(String )
        region=Column(String )
        date_fin_candidature=Column(date_type )
        date_debut=Column(date_type )
        est_en_alternance=Column(Integer )
        est_en_distanciel=Column(Integer )
    
class lien_formation_france_competences(Base):
        int id_formation PK,FK
        string code_certif PK,FK


        
class   lien_france_competences_formacode(Base):
        string code_certif PK,FK
        int formacode PK,FK

class lien_france_competences_certificateur(Base):
        string code_certif PK,FK
        int id_certificateur PK,FK
      


    # acteurs = relationship('Acteur', secondary=film_acteur, 
    #                        primaryjoin="and_(Film.titre == film_acteur.c.film_titre, "
    #                                    "Film.date == film_acteur.c.film_date, "
    #                                    "Film.realisateur == film_acteur.c.film_realisateur)",
    #                        secondaryjoin="film_acteur.c.acteur_id == Acteur.acteur_id",
    #                        backref='films')
    
# Configuration de la base de données (remplacez 'sqlite:///database.db' par votre base de données)
engine = create_engine(bdd_path)
Base.metadata.create_all(engine)