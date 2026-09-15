"""
Gestion de la base de données SQLite.
Ce fichier ne contient QUE la connexion et la création des tables.
Chaque module (app/membre, app/finance...) gère ses propres requêtes
dans son fichier Fonctions.py.
"""

import sqlite3
import os
import config


def get_connexion():
    """Ouvre une connexion à la base, avec accès aux colonnes par nom."""
    os.makedirs(os.path.dirname(config.DB_PATH), exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialiser_base():
    """Crée toutes les tables si elles n'existent pas encore."""
    conn = get_connexion()

    # ===== TABLE MEMBRES (Module Membre) =====
    conn.execute("""
        CREATE TABLE IF NOT EXISTS members (
            id_aae TEXT PRIMARY KEY,
            telegram_id INTEGER UNIQUE NOT NULL,
            telegram_username TEXT,
            prenom TEXT NOT NULL,
            nom TEXT DEFAULT '',
            langue TEXT DEFAULT 'fr',
            statut TEXT DEFAULT 'actif',
            est_admin INTEGER DEFAULT 0,
            est_presidente INTEGER DEFAULT 0,
            date_inscription TEXT NOT NULL,
            date_desactivation TEXT
        )
    """)

    # ===== TABLE PARAMÈTRES GÉNÉRAUX (Module Paramètres, utilisée dès maintenant) =====
    conn.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            cle TEXT PRIMARY KEY,
            valeur TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()
