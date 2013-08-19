# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)


calcul_exact = True    # gerer les fractions et les racines de maniere exacte si possible.
ecriture_scientifique = False # afficher les resultats en ecriture scientifique.
copie_automatique = True # copie automatique de chaque resultat dans le presse-papier
copie_automatique_LaTeX = False
formatage_OOo = True
formatage_LaTeX = True
ecriture_scientifique_decimales = 2
precision_calcul = 60
precision_affichage = 18
forme_affichage_complexe = ("algebrique", "exponentielle")[0]
# Fonction à appliquer à tout résultat avant de le renvoyer :
appliquer_au_resultat = None
# Domaine de résolution des équations ('R' ou 'C')
ensemble = 'R'
