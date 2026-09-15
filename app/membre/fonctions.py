"""
MODULE MEMBRE — Logique métier.
Aucune ligne de code ici ne parle à Telegram : uniquement des fonctions
Python qui lisent/écrivent dans la base de données. Le fichier bot.py
du même dossier s'occupe de la partie Telegram et appelle ces fonctions.
"""

from datetime import datetime
import config


def generer_prochain_id(conn):
    """Génère le prochain identifiant AAE (AAE001, AAE002, ...)."""
    cur = conn.execute("SELECT COUNT(*) as total FROM members")
    total = cur.fetchone()["total"]
    return f"AAE{total + 1:03d}"


def creer_membre(conn, telegram_id, prenom, nom="", username="", langue="fr"):
    """Inscrit un nouveau membre et lui attribue un identifiant AAE."""
    id_aae = generer_prochain_id(conn)
    est_admin = 1 if telegram_id in config.ADMIN_IDS else 0
    conn.execute(
        """INSERT INTO members
           (id_aae, telegram_id, telegram_username, prenom, nom, langue,
            statut, est_admin, date_inscription)
           VALUES (?, ?, ?, ?, ?, ?, 'actif', ?, ?)""",
        (
            id_aae, telegram_id, username, prenom, nom, langue, est_admin,
            datetime.now().strftime("%d/%m/%Y"),
        ),
    )
    conn.commit()
    return id_aae


def get_membre_par_telegram_id(conn, telegram_id):
    cur = conn.execute("SELECT * FROM members WHERE telegram_id = ?", (telegram_id,))
    return cur.fetchone()


def get_membre_par_id_aae(conn, id_aae):
    cur = conn.execute("SELECT * FROM members WHERE id_aae = ?", (id_aae.upper(),))
    return cur.fetchone()


def get_ou_creer_membre(conn, telegram_id, prenom, nom="", username="", langue="fr"):
    """Récupère un membre existant, ou l'inscrit s'il n'existe pas encore.
    Retourne (membre, est_nouveau)."""
    membre = get_membre_par_telegram_id(conn, telegram_id)
    if membre:
        return membre, False
    creer_membre(conn, telegram_id, prenom, nom, username, langue)
    return get_membre_par_telegram_id(conn, telegram_id), True


def rechercher_membres(conn, terme):
    """Recherche par identifiant AAE, prénom ou nom (insensible à la casse)."""
    terme_like = f"%{terme.lower()}%"
    cur = conn.execute(
        """SELECT * FROM members
           WHERE LOWER(id_aae) LIKE ? OR LOWER(prenom) LIKE ? OR LOWER(nom) LIKE ?
           ORDER BY id_aae""",
        (terme_like, terme_like, terme_like),
    )
    return cur.fetchall()


def lister_membres(conn, actifs_seulement=False):
    if actifs_seulement:
        cur = conn.execute("SELECT * FROM members WHERE statut = 'actif' ORDER BY id_aae")
    else:
        cur = conn.execute("SELECT * FROM members ORDER BY id_aae")
    return cur.fetchall()


def modifier_membre(conn, id_aae, **champs):
    """Modifie un ou plusieurs champs d'un membre. Ex: modifier_membre(conn, 'AAE001', prenom='Roger')"""
    if not champs:
        return False
    colonnes = ", ".join(f"{cle} = ?" for cle in champs)
    valeurs = list(champs.values()) + [id_aae.upper()]
    conn.execute(f"UPDATE members SET {colonnes} WHERE id_aae = ?", valeurs)
    conn.commit()
    return conn.total_changes > 0


def changer_langue(conn, telegram_id, langue):
    conn.execute("UPDATE members SET langue = ? WHERE telegram_id = ?", (langue, telegram_id))
    conn.commit()


def desactiver_membre(conn, id_aae):
    conn.execute(
        "UPDATE members SET statut = 'inactif', date_desactivation = ? WHERE id_aae = ?",
        (datetime.now().strftime("%d/%m/%Y"), id_aae.upper()),
    )
    conn.commit()


def reactiver_membre(conn, id_aae):
    conn.execute(
        "UPDATE members SET statut = 'actif', date_desactivation = NULL WHERE id_aae = ?",
        (id_aae.upper(),),
    )
    conn.commit()


def supprimer_membre(conn, id_aae):
    """Suppression DÉFINITIVE. À utiliser avec précaution (erreur d'inscription, etc.)."""
    conn.execute("DELETE FROM members WHERE id_aae = ?", (id_aae.upper(),))
    conn.commit()


def est_admin(telegram_id):
    """Vérifie le statut admin via la configuration (ADMIN_IDS)."""
    return telegram_id in config.ADMIN_IDS


def nom_complet(membre):
    """Retourne 'Prénom Nom' proprement (sans espace en trop si pas de nom)."""
    if membre["nom"]:
        return f"{membre['prenom']} {membre['nom']}"
    return membre["prenom"]
