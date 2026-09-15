"""
Point d'entrée du système de traduction.
Usage : from locales import t
        t("fr", "bienvenue_retour", prenom="Roger")
"""

from locales import fr, en

_TEXTES = {"fr": fr.TEXTES, "en": en.TEXTES}


def t(langue, cle, **kwargs):
    """Retourne le texte traduit pour une langue donnée ('fr' ou 'en')."""
    textes_langue = _TEXTES.get(langue, _TEXTES["fr"])
    texte = textes_langue.get(cle) or _TEXTES["fr"].get(cle, cle)
    return texte.format(**kwargs) if kwargs else texte
