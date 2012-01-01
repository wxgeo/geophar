MODULES
_______

Ce répertoire contient tous les modules de WxGéométrie.

L'activation d'un module au démarrage de WxGéométrie dépend de sa présence dans param.__init__.py
Pour activer/désactiver des modules, éditez ce fichier avec un éditeur de texte, et modifiez la ligne :
modules = ("geometre", "traceur", "statistiques", "calculatrice", "probabilites", "surfaces")

Un fichier description.py permet d'intégrer le module dans l'installeur pour Windows.
Depuis la version 0.131, un module n'est pas reconnu si ce fichier est absent.

Format du fichier description.py :
----------------------------------
# titre : description sommaire du module
# description : description détaillée
# defaut : par défaut, le module est-il installé ou non ?
# groupe : "Modules" pour tous les modules
defaut peut valoir True, False ou None.
(None signifie que le module est nécessairement installé)

Exemple de fichier 'description.py':

# -*- coding: iso-8859-1 -*-
description = {
"titre":                    u"Calculatrice",
"description":              u"Calculatrice avancée orientée mathématiques destinée au collège/lycée.",
"groupe":                   u"Modules",
"defaut":  True,
}


Pour plus de détails concernant la création de nouveaux modules pour WxGéométrie, voir :
doc/developpeurs/documentation de l'API.pdf
