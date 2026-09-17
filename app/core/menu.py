"""
MODULE CORE — Menu fixe partagé.
Ce fichier construit le menu qui reste toujours affiché en bas de l'écran
Telegram, DIFFÉRENT selon que la personne est admin (bureau) ou membre
simple. Chaque nouveau module (Finance, Réunions, Jeux...) viendra
ajouter ses propres boutons ici au fur et à mesure de sa construction,
sans jamais toucher aux modules déjà en place.
"""

from telegram import ReplyKeyboardMarkup
from locales import t


def construire_menu(est_admin: bool, langue: str = "fr"):
    """
    Construit le clavier fixe adapté au statut (admin/membre) et à la langue.

    Phase actuelle : Module Membre uniquement.
    À enrichir plus tard avec les boutons Finance, Réunions, Jeux, etc.
    """
    if est_admin:
        boutons = [
            [t(langue, "menu_mon_espace"), t(langue, "menu_langue")],
            [t(langue, "menu_membres"), t(langue, "menu_rechercher")],
        ]
    else:
        boutons = [
            [t(langue, "menu_mon_espace"), t(langue, "menu_langue")],
        ]
    return ReplyKeyboardMarkup(boutons, resize_keyboard=True)
