# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SessionsItem(scrapy.Item):
    nom_session=scrapy.Field()
    date_candidature = scrapy.Field()
    additional_info = scrapy.Field()
    alternance = scrapy.Field()
    duree = scrapy.Field()
    region = scrapy.Field()
    lieu = scrapy.Field()
    date_debut = scrapy.Field()
    distanciel = scrapy.Field()

class FormationItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    rncp = scrapy.Field()
    rs = scrapy.Field()
    sessions = scrapy.Field()
    nom_session=scrapy.Field()
    a_des_sessions = scrapy.Field()
    a_des_rs_rncp = scrapy.Field()

class FranceCompetencesItem(scrapy.Item):
    code_certif = scrapy.Field()
    title = scrapy.Field()
    formacodes = scrapy.Field()
    # nom_legal = scrapy.Field()
    # siret = scrapy.Field()
    # nom_commercial = scrapy.Field()
    # site_internet = scrapy.Field()
    certificateurs = scrapy.Field() 
    est_actif = scrapy.Field()
    niveau_de_qualification = scrapy.Field()
    date_echeance_enregistrement = scrapy.Field()