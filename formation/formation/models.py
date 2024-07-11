
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

# # Define association tables first
# film_acteur = Table(
#     'film_acteur', Base.metadata,
#     Column('film_titre', String),
#     Column('film_date', date_type),
#     Column('film_realisateur', String),
#     Column('acteur_id', Integer, ForeignKey('acteurs.acteur_id')),
#     ForeignKeyConstraint(['film_titre', 'film_date', 'film_realisateur'], 
#                          ['film.titre', 'film.date', 'film.realisateur']),
#     PrimaryKeyConstraint('film_titre', 'film_date', 'film_realisateur', 'acteur_id')
# )

# film_genre = Table(
#     'film_genre', Base.metadata,
#     Column('film_titre', String),
#     Column('film_date', date_type),
#     Column('film_realisateur', String),
#     Column('genre_id', Integer, ForeignKey('genre.genre_id')),
#     ForeignKeyConstraint(['film_titre', 'film_date', 'film_realisateur'], 
#                          ['film.titre', 'film.date', 'film.realisateur']),
#     PrimaryKeyConstraint('film_titre', 'film_date', 'film_realisateur', 'genre_id')
# )

# film_langue = Table(
#     'film_langue', Base.metadata,
#     Column('film_titre', String),
#     Column('film_date', date_type),
#     Column('film_realisateur', String),
#     Column('langue_id', Integer, ForeignKey('langue.langue_id')),
#     ForeignKeyConstraint(['film_titre', 'film_date', 'film_realisateur'], 
#                          ['film.titre', 'film.date', 'film.realisateur']),
#     PrimaryKeyConstraint('film_titre', 'film_date', 'film_realisateur', 'langue_id')
# )

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
        est_actif=Column(int )
        niveau_de_qualification=Column(String )
        date_de_decision=Column(Date )
        duree_enregistrement_en_annees=Column(int  )
        date_echeance_enregistrement=Column(Date )
        Date_derniere_delivrance_possible=Column(Date  )
    
class    Formacode(Base):
        __tablename__ = 'formacode'
        formacode=Column(int, primary_key=True)  
        nom=Column(String) 

class Session(Base):
        __tablename__ ='session'
        id_session=Column(int, primary_key=True ) 
        id_formation=Column(int ) 
        nom=Column(String )
        lieu=Column(String )
        region=Column(String )
        date_fin_candidature=Column(Date )
        date_debut=Column(Date )
        est_en_alternance=Column(int )
        est_en_distanciel=Column(int )
    

    # acteurs = relationship('Acteur', secondary=film_acteur, 
    #                        primaryjoin="and_(Film.titre == film_acteur.c.film_titre, "
    #                                    "Film.date == film_acteur.c.film_date, "
    #                                    "Film.realisateur == film_acteur.c.film_realisateur)",
    #                        secondaryjoin="film_acteur.c.acteur_id == Acteur.acteur_id",
    #                        backref='films')
    
    # genres = relationship('Genre', secondary=film_genre,
    #                       primaryjoin="and_(Film.titre == film_genre.c.film_titre, "
    #                                   "Film.date == film_genre.c.film_date, "
    #                                   "Film.realisateur == film_genre.c.film_realisateur)",
    #                       secondaryjoin="film_genre.c.genre_id == Genre.genre_id",
    #                       backref='films')

    # langues = relationship('Langue', secondary=film_langue,
    #                        primaryjoin="and_(Film.titre == film_langue.c.film_titre, "
    #                                    "Film.date == film_langue.c.film_date, "
    #                                    "Film.realisateur == film_langue.c.film_realisateur)",
    #                        secondaryjoin="film_langue.c.langue_id == Langue.langue_id",
    #                        backref='films')

# class Acteur(Base):
#     __tablename__ = 'acteurs'

#     acteur_id = Column(Integer, primary_key=True, autoincrement=True)
#     acteur_first_name = Column(String)
#     acteur_last_name = Column(String)

# class Genre(Base):
#     __tablename__ = 'genre'

#     genre_id = Column(Integer, primary_key=True, autoincrement=True)
#     genre_name = Column(String)

# class Langue(Base):
#     __tablename__ = 'langue'

#     langue_id = Column(Integer, primary_key=True, autoincrement=True)
#     langue_name = Column(String)

# Configuration de la base de données (remplacez 'sqlite:///database.db' par votre base de données)
engine = create_engine(bdd_path)
Base.metadata.create_all(engine)