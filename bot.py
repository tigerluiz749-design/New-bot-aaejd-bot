"""
LANCEUR PRINCIPAL DU BOT AAE-JD.
Ce fichier ne contient AUCUNE logique métier — il sert uniquement à :
1. Initialiser la base de données
2. Démarrer le petit serveur web (nécessaire pour le plan gratuit Render)
3. Enregistrer les handlers de chaque module (app/membre, app/finance...)
4. Lancer le bot

Phase actuelle : Module Membre uniquement (les autres modules seront
ajoutés un par un, après tests, comme prévu au cahier des charges).
"""

import os
import logging
import threading
from flask import Flask

from telegram.ext import Application

import config
import database
from app.membre import bot as module_membre

# ============ LOGS ============
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ============ MINI-SERVEUR WEB (plan gratuit Render) ============
web_app = Flask(__name__)


@web_app.route("/")
def accueil():
    return "🤖 Le bot AAE-JD (v2 - architecture modulaire) est actif !"


def lancer_serveur_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)


# ============ LANCEMENT ============

def main():
    if not config.BOT_TOKEN:
        raise RuntimeError("La variable d'environnement BOT_TOKEN n'est pas définie.")

    database.initialiser_base()
    logger.info("Base de données initialisée.")

    app = Application.builder().token(config.BOT_TOKEN).build()

    # ===== Enregistrement des modules (un seul pour l'instant : Membre) =====
    module_membre.enregistrer_handlers(app)
    logger.info("Module Membre enregistré.")

    # D'autres modules viendront ici au fur et à mesure :
    # from app.finance import bot as module_finance
    # module_finance.enregistrer_handlers(app)

    threading.Thread(target=lancer_serveur_web, daemon=True).start()

    logger.info("Bot AAE-JD démarré (architecture modulaire, Phase 1 : Membre)...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
