"""
Configuration centrale du bot AAE-JD.
Toutes les valeurs par défaut ici peuvent être surchargées depuis Telegram
via le module Paramètres (à venir), sans jamais toucher au code.
"""

import os

# ============ IDENTITÉ ============
NOM_ASSOCIATION = "AAE-JD"
NOM_COMPLET = "ASSOCIATION DES ANCIENS ÉLÈVES ET JEUNES DYNAMIQUES"
SLOGAN = "Ensemble, nous sommes plus forts"

# ============ SÉCURITÉ ============
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]

# ============ BASE DE DONNÉES ============
DB_PATH = os.path.join(os.path.dirname(__file__), "database", "aae_jd.db")

# ============ RÉGLEMENT (valeurs par défaut, modifiables depuis Telegram) ============
MONTANTS_DEFAUT = {
    "nouvelle_inscription": 2000,
    "reinscription": 1000,
    "membre_honneur": 5000,
    "pot_commun_reunion": 500,
    "pot_famille_min": 500,
    "aide_maladie": 50000,
    "aide_mariage": 100000,
    "aide_accouchement": 50000,
    "aide_deces_membre": 150000,
    "aide_deces_parent": 50000,
}

# ============ LANGUES ============
LANGUES_DISPONIBLES = ["fr", "en"]
LANGUE_DEFAUT = "fr"
