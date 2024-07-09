```mermaid
erDiagram
    formation {
        int id_formation PK
        string titre 
        float score
        date date PK
       
    }
    france_competences {
        string code_certif PK
        string nom_titre
        int est_actif
        string niveau_de_qualification
        date date_de_decision
        int duree_enregistrement_en_annees 
        date date_echeance_enregistrement
        date Date_derniere_delivrance_possible 


    }
    lien_formation_france_competences {
        int id_formation PK,FK
        string code_certif PK,FK
    }
    formacode{
        int formacode PK
        string nom
    }

    lien_france_competences_formacode {
        string code_certif PK,FK
        int formacode PK,FK
    }

    certificateur{
        int id_certificateur PK
        string nom_legal
        int siret
        string nom_commercial
        string site_internet 
    }

    lien_france_competences_certificateur{
        string code_certif PK,FK
        int id_certificateur PK,FK
    }
    session{
        int id_session PK
        string nom
        string lieu
        string region
        date date_fin_candidature
        date date_debut
        int est_en_alternance
        int est_en_distanciel
    }

    lien_formation_session{
        int id_formation PK,FK
        int id_session PK,FK
    }
    

    formation ||--o{ lien_formation_france_competences : ""
    france_competences ||--o{ lien_formation_france_competences : ""
    
    france_competences ||--o{ lien_france_competences_formacode : ""
    formacode ||--o{ lien_france_competences_formacode : ""
    
    france_competences ||--o{ lien_france_competences_certificateur : ""
    certificateur ||--o{ lien_france_competences_certificateur : ""
    
    formation ||--o{ lien_formation_session : ""
    session ||--o{ lien_formation_session : ""
    
```