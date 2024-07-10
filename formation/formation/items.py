# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FormationItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    rncp = scrapy.Field()
    rs=scrapy.Field()
    nom_session=scrapy.Field()
    date_candidature = scrapy.Field()
    additional_info = scrapy.Field()
    alternance = scrapy.Field()
    duree = scrapy.Field()
    region = scrapy.Field()
    lieu = scrapy.Field()
    date_debut = scrapy.Field()
    
     









class FranceCompetencesItem(scrapy.Item):
    title = scrapy.Field()
    formacodes = scrapy.Field()
    # nom_legal = scrapy.Field()
    # siret = scrapy.Field()
    # nom_commercial = scrapy.Field()
    # site_internet = scrapy.Field()
    certificateur = scrapy.Field() 
    est_actif = scrapy.Field()
    niveau_de_qualification = scrapy.Field()
    date_echeance_enregistrement = scrapy.Field()