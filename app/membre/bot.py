"""
MODULE MEMBRE — Partie Telegram.
Ce fichier gère uniquement les commandes/boutons Telegram. Toute la
logique (inscription, recherche, modification...) est dans fonctions.py.
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters

import database
from locales import t, fr as locale_fr, en as locale_en
from app.membre import fonctions as f
from app.core.menu import construire_menu


# ============ COMMANDES POUR TOUS LES MEMBRES ============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inscrit automatiquement un nouveau membre, ou accueille un membre existant."""
    user = update.effective_user
    conn = database.get_connexion()
    membre, est_nouveau = f.get_ou_creer_membre(
        conn, user.id, user.first_name or "Membre", user.last_name or "",
        user.username or "",
    )
    conn.close()

    if est_nouveau:
        message = t(membre["langue"], "bienvenue_nouveau",
                    prenom=membre["prenom"], id_aae=membre["id_aae"])
    else:
        message = t(membre["langue"], "bienvenue_retour", prenom=membre["prenom"])

    clavier = construire_menu(f.est_admin(user.id), membre["langue"])
    await update.message.reply_text(message, reply_markup=clavier)


async def profil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Affiche la fiche du membre qui fait la demande (jamais celle d'un autre)."""
    user = update.effective_user
    conn = database.get_connexion()
    membre, _ = f.get_ou_creer_membre(conn, user.id, user.first_name or "Membre")
    conn.close()

    lg = membre["langue"]
    statut_texte = t(lg, "statut_actif") if membre["statut"] == "actif" else t(lg, "statut_inactif")

    message = (
        f"{t(lg, 'profil_titre')}\n\n"
        f"🆔 {t(lg, 'profil_id')} : {membre['id_aae']}\n"
        f"👤 {t(lg, 'profil_nom')} : {f.nom_complet(membre)}\n"
        f"📊 {t(lg, 'profil_statut')} : {statut_texte}\n"
        f"🌐 {t(lg, 'profil_langue')} : {membre['langue'].upper()}\n"
        f"📅 {t(lg, 'profil_inscription')} : {membre['date_inscription']}"
    )
    await update.message.reply_text(message)


async def langue_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Affiche les boutons de choix de langue."""
    user = update.effective_user
    conn = database.get_connexion()
    membre, _ = f.get_ou_creer_membre(conn, user.id, user.first_name or "Membre")
    conn.close()

    clavier = InlineKeyboardMarkup([[
        InlineKeyboardButton("🇫🇷 Français", callback_data="membre_langue:fr"),
        InlineKeyboardButton("🇬🇧 English", callback_data="membre_langue:en"),
    ]])
    await update.message.reply_text(t(membre["langue"], "langue_choix"), reply_markup=clavier)


async def clic_langue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    nouvelle_langue = query.data.replace("membre_langue:", "", 1)
    user = query.from_user

    conn = database.get_connexion()
    f.changer_langue(conn, user.id, nouvelle_langue)
    conn.close()

    await query.answer(t(nouvelle_langue, "langue_changee"))
    await query.edit_message_text(t(nouvelle_langue, "langue_changee"))
    await context.bot.send_message(
        chat_id=user.id,
        text=t(nouvelle_langue, "menu_accueil"),
        reply_markup=construire_menu(f.est_admin(user.id), nouvelle_langue),
    )


# ============ COMMANDES ADMIN ============

async def membres(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Liste tous les membres (admin uniquement)."""
    user = update.effective_user
    if not f.est_admin(user.id):
        conn = database.get_connexion()
        m, _ = f.get_ou_creer_membre(conn, user.id, user.first_name or "Membre")
        conn.close()
        await update.message.reply_text(t(m["langue"], "reserve_bureau"))
        return

    conn = database.get_connexion()
    tous = f.lister_membres(conn)
    conn.close()

    if not tous:
        await update.message.reply_text("Aucun membre enregistré pour l'instant.")
        return

    message = "👥 LISTE DES MEMBRES\n\n"
    for m in tous:
        statut_emoji = "✅" if m["statut"] == "actif" else "🔴"
        message += f"{statut_emoji} {m['id_aae']} — {f.nom_complet(m)}\n"
    await update.message.reply_text(message)


async def rechercher_membre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Usage : /rechercher_membre <terme>"""
    user = update.effective_user
    conn = database.get_connexion()
    if not f.est_admin(user.id):
        m, _ = f.get_ou_creer_membre(conn, user.id, user.first_name or "Membre")
        conn.close()
        await update.message.reply_text(t(m["langue"], "reserve_bureau"))
        return

    if not context.args:
        conn.close()
        await update.message.reply_text("Usage : /rechercher_membre <nom ou identifiant AAE>")
        return

    resultats = f.rechercher_membres(conn, " ".join(context.args))
    conn.close()

    if not resultats:
        await update.message.reply_text("❌ Aucun résultat.")
        return

    message = "🔍 RÉSULTATS\n\n"
    for m in resultats:
        statut_emoji = "✅" if m["statut"] == "actif" else "🔴"
        message += f"{statut_emoji} {m['id_aae']} — {f.nom_complet(m)} (Telegram: {m['telegram_id']})\n"
    await update.message.reply_text(message)


async def modifier_membre_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Usage : /modifier_membre <id_aae> <champ> <valeur>
    Champs modifiables : prenom, nom"""
    user = update.effective_user
    conn = database.get_connexion()
    if not f.est_admin(user.id):
        m, _ = f.get_ou_creer_membre(conn, user.id, user.first_name or "Membre")
        conn.close()
        await update.message.reply_text(t(m["langue"], "reserve_bureau"))
        return

    args = context.args
    if len(args) < 3:
        conn.close()
        await update.message.reply_text(
            "Usage : /modifier_membre <id_aae> <champ> <valeur>\n"
            "Champs possibles : prenom, nom\n"
            "Exemple : /modifier_membre AAE001 prenom Roger"
        )
        return

    id_aae, champ, valeur = args[0], args[1], " ".join(args[2:])
    if champ not in ("prenom", "nom"):
        conn.close()
        await update.message.reply_text("❌ Champ non modifiable. Utilise : prenom ou nom.")
        return

    membre = f.get_membre_par_id_aae(conn, id_aae)
    if not membre:
        conn.close()
        await update.message.reply_text(t("fr", "membre_introuvable"))
        return

    f.modifier_membre(conn, id_aae, **{champ: valeur})
    conn.close()
    await update.message.reply_text(f"✅ {id_aae} mis à jour : {champ} = {valeur}")


async def desactiver_membre_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Usage : /desactiver_membre <id_aae>"""
    user = update.effective_user
    conn = database.get_connexion()
    if not f.est_admin(user.id):
        m, _ = f.get_ou_creer_membre(conn, user.id, user.first_name or "Membre")
        conn.close()
        await update.message.reply_text(t(m["langue"], "reserve_bureau"))
        return

    if not context.args:
        conn.close()
        await update.message.reply_text("Usage : /desactiver_membre <id_aae>")
        return

    membre = f.get_membre_par_id_aae(conn, context.args[0])
    if not membre:
        conn.close()
        await update.message.reply_text(t("fr", "membre_introuvable"))
        return

    f.desactiver_membre(conn, context.args[0])
    conn.close()
    await update.message.reply_text(t("fr", "membre_desactive", nom=f.nom_complet(membre)))


async def reactiver_membre_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Usage : /reactiver_membre <id_aae>"""
    user = update.effective_user
    conn = database.get_connexion()
    if not f.est_admin(user.id):
        m, _ = f.get_ou_creer_membre(conn, user.id, user.first_name or "Membre")
        conn.close()
        await update.message.reply_text(t(m["langue"], "reserve_bureau"))
        return

    if not context.args:
        conn.close()
        await update.message.reply_text("Usage : /reactiver_membre <id_aae>")
        return

    membre = f.get_membre_par_id_aae(conn, context.args[0])
    if not membre:
        conn.close()
        await update.message.reply_text(t("fr", "membre_introuvable"))
        return

    f.reactiver_membre(conn, context.args[0])
    conn.close()
    await update.message.reply_text(t("fr", "membre_reactive", nom=f.nom_complet(membre)))


async def supprimer_membre_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Usage : /supprimer_membre <id_aae> — suppression DÉFINITIVE."""
    user = update.effective_user
    conn = database.get_connexion()
    if not f.est_admin(user.id):
        m, _ = f.get_ou_creer_membre(conn, user.id, user.first_name or "Membre")
        conn.close()
        await update.message.reply_text(t(m["langue"], "reserve_bureau"))
        return

    if not context.args:
        conn.close()
        await update.message.reply_text("Usage : /supprimer_membre <id_aae>")
        return

    membre = f.get_membre_par_id_aae(conn, context.args[0])
    if not membre:
        conn.close()
        await update.message.reply_text(t("fr", "membre_introuvable"))
        return

    nom = f.nom_complet(membre)
    f.supprimer_membre(conn, context.args[0])
    conn.close()
    await update.message.reply_text(t("fr", "membre_supprime", nom=nom))


async def clic_menu_fixe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Réagit aux clics sur le menu fixe, reconnaît le bouton peu importe la langue."""
    texte = update.message.text

    if texte in (locale_fr.TEXTES["menu_mon_espace"], locale_en.TEXTES["menu_mon_espace"]):
        await profil(update, context)
    elif texte in (locale_fr.TEXTES["menu_langue"], locale_en.TEXTES["menu_langue"]):
        await langue_cmd(update, context)
    elif texte in (locale_fr.TEXTES["menu_membres"], locale_en.TEXTES["menu_membres"]):
        await membres(update, context)
    elif texte in (locale_fr.TEXTES["menu_rechercher"], locale_en.TEXTES["menu_rechercher"]):
        await update.message.reply_text("Usage : /rechercher_membre <nom ou identifiant>")


# ============ ENREGISTREMENT DES HANDLERS ============

def enregistrer_handlers(app):
    """Appelé une seule fois par bot.py (racine) au démarrage."""
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("profil", profil))
    app.add_handler(CommandHandler("langue", langue_cmd))
    app.add_handler(CallbackQueryHandler(clic_langue, pattern=r"^membre_langue:"))

    app.add_handler(CommandHandler("membres", membres))
    app.add_handler(CommandHandler("rechercher_membre", rechercher_membre))
    app.add_handler(CommandHandler("modifier_membre", modifier_membre_cmd))
    app.add_handler(CommandHandler("desactiver_membre", desactiver_membre_cmd))
    app.add_handler(CommandHandler("reactiver_membre", reactiver_membre_cmd))
    app.add_handler(CommandHandler("supprimer_membre", supprimer_membre_cmd))

    textes_menu = []
    for cle in ("menu_mon_espace", "menu_langue", "menu_membres", "menu_rechercher"):
        textes_menu.append(locale_fr.TEXTES[cle])
        textes_menu.append(locale_en.TEXTES[cle])
    app.add_handler(MessageHandler(filters.Text(textes_menu), clic_menu_fixe))
