# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)
from __future__ import with_statement

##--------------------------------------#######
#                Probabilités                 #
##--------------------------------------#######
#    WxGeometrie
#    Dynamic geometry, graph plotter, and more for french mathematic teachers.
#    Copyright (C) 2005-2010  Nicolas Pourcelot
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import re
import wx
from ...GUI import MenuBar, Panel_API_graphique
from ...GUI.proprietes_objets import Proprietes

from ...geolib import Segment, Texte, Point, TEXTE
from ... import param


class ProbaMenuBar(MenuBar):
    def __init__(self, panel):
        MenuBar.__init__(self, panel)

        self.ajouter(u"Fichier", [u"nouveau"], [u"ouvrir"], [u"ouvrir ici"], [u"enregistrer"], [u"enregistrer_sous"], [u"exporter"], [u"exporter&sauver"], None, [u"mise en page"], [u"imprimer"], [u"presse-papier"], None, [u"proprietes"], None, self.panel.doc_ouverts, None, ["fermer"], ["quitter"])
        self.ajouter(u"Editer", ["annuler"], ["refaire"], ["modifier"], ["supprimer"])
        self.ajouter(u"creer")
        self.ajouter(u"Affichage", ["onglet"], None, ["repere"], ["quadrillage"], ["orthonorme"], None, ["zoom_texte"], ["zoom_ligne"], ["zoom_general"], None, ["fenetre"], ["zoomer"], ["dezoomer"], ["orthonormaliser"], [u"zoom_auto"])
        self.ajouter(u"Autres actions", [u"detecter"])
        self.ajouter(u"Outils", [u"Style des sommets", u"Modifier le style des sommets de l'arbre.", None, self.panel.proprietes_sommets], [u"Style des arêtes", u"Modifier le style des arêtes de l'arbre.", None, self.panel.proprietes_aretes], [u"Style de la légende", u"Modifier le style des titres de chaque niveau.", None, self.panel.proprietes_titres], None, [u"options"])
##        self.ajouter(u"Avancé", [u"historique"], [u"securise"], [u"ligne_commande"], [u"debug"])
        self.ajouter(u"avance1")
        self.ajouter(u"?")




class Probabilites(Panel_API_graphique):

    __titre__ = u"Arbre de probabilités" # Donner un titre a chaque module

    def __init__(self, *args, **kw):
        Panel_API_graphique.__init__(self, *args, **kw)

        self.couleurs = u"bgrmkcy"

        self.entrees = wx.BoxSizer(wx.VERTICAL)

        self.entrees.Add(wx.StaticText(self, -1, u" Instructions :"), 0, wx.ALL,5)

        self.instructions = wx.TextCtrl(self, size = (200, 300), style = wx.TE_MULTILINE)
        self.instructions.SetValue("""||Tirage 1|Tirage 2|Tirage 3
omega
>A:0,7
>>B:0,2
>>C:0,8
>&A:0,3
>>E:0,1
>>>F
>>>G
>>>H
>>&E:0,9""")
        self.entrees.Add(self.instructions, 0, wx.ALL,5)
        self.appliquer = wx.Button(self, label = u"Générer l'arbre")
        self.appliquer.Bind(wx.EVT_BUTTON, self.Appliquer)
        self.entrees.Add(self.appliquer, 0, wx.ALL,5)

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.sizer.Add(self.entrees, 0, wx.ALL, 5)
        self.finaliser(contenu = self.sizer)


    def _sauvegarder(self, fgeo, feuille = None):
        Panel_API_graphique._sauvegarder(self, fgeo, feuille)
        fgeo.contenu[u"Instructions"] = [self.instructions.GetValue()]


    def _ouvrir(self, fgeo):
        Panel_API_graphique._ouvrir(self, fgeo)
        if fgeo.contenu.has_key(u"Instructions"):
            self.instructions.SetValue(fgeo.contenu[u"Instructions"][0])


    def Appliquer(self, event):
        with self.canvas.geler_affichage(actualiser=True, sablier=True):
            self.creer_feuille()
            instructions = [instruction for instruction in self.instructions.GetValue().split("\n") if instruction]
            nbr_colonnes = 0
            if instructions[0].startswith("|"):
                legende = instructions[0]
                instructions = instructions[1:]
                self.canvas.fenetre = -.1, 1.1, -.1, 1.2
            else:
                legende = None
                self.canvas.fenetre = -.1, 1.1, -.1, 1.1

            for instruction in instructions:
                if instruction.startswith(">"):
                    nbr_colonnes = max(nbr_colonnes, len(instruction) - len(instruction.lstrip(">")))
            if instructions[0].startswith(">"):
                instructions = [""] + instructions
            nbr_colonnes += 1
            nbr_lignes = []
            for i in xrange(nbr_colonnes):
                nbr_lignes.append(len([instruction for instruction in instructions if instruction.startswith(i*">") and not instruction.startswith((i+1)*">")]))

            #intersection, union : \cap \cup

            # Interprétation des instructions sous forme de listes de listes
            # >A
            # >>B
            # >>C
            # >D
            # >>E
            # >>>F
            # >>>G
            # >>H
            # >E
            # devient :
            # [{'liste': [{'liste': [{'liste': [], 'texte': u'B'}, {'liste': [], 'texte': u'C'}], 'texte': u'A'}, {'liste': [{'liste': [{'liste': [], 'texte': u'F'}, {'liste': [], 'texte': u'G'}], 'texte': u'E'}, {'liste': [], 'texte': u'H'}], 'texte': u'D'}, {'liste': [], 'texte': u'E'}], 'texte': ''}]

            arbre = []
            ligne_precedente = [-1 for i in xrange(nbr_colonnes)] # numéro de ligne atteint pour chaque colonne
            for instruction in instructions:
                colonne = len(instruction) - len(instruction.lstrip(">"))
                branche = arbre
                for i in xrange(colonne): # on se déplace de branche en branche ;)
                    branche = branche[ligne_precedente[i]]["liste"]
                branche.append({"texte": instruction.lstrip(">"), "liste": []})
                ligne_precedente[colonne] += 1
                for i in xrange(colonne + 1, nbr_colonnes):
                    ligne_precedente[i] = -1
            print arbre

            # on parcourt l'arbre pour compter le nombre de ramifications

            def compter_ramifications(branche):
                if len(branche["liste"]) > 0:
                    return sum(compter_ramifications(tige) for tige in branche["liste"])
                else:
                    return 1

            ramifications = sum(compter_ramifications(branche) for branche in arbre)
            print ramifications

            def formater_texte(texte):
                if texte:
                    if param.latex:
                        if texte.startswith("&"):
                            texte = r"\overline{" + texte[1:] + "}"
                        texte = texte.replace("&{", r"\overline{")
                        texte = texte.replace("&", r"\bar ")
                    else:
                        if texte.startswith("&"):
                            texte = r"\bar{" + texte[1:] + "}"
                        texte = texte.replace("&", r"\bar ")
                    texte = "$" + texte + "$" if texte[0] != '$' else texte
                    if param.latex:
                        texte = "$" + texte + "$" # passage en mode "display" de LaTeX
                    texte = texte.replace(" inter ", r"\  \cap \ ").replace(" union ", r"\  \cup \ ").replace("Omega", r"\Omega").replace("omega", r"\Omega")
                    if param.latex: # on remplace les fractions. Ex: "1/15" -> "\frac{1}{15}"
                        texte = re.sub("[0-9]+/[0-9]+",lambda s:"\\frac{" + s.group().replace("/", "}{") + "}", texte)
                return texte


            def creer_point(x, y, texte):
                texte = formater_texte(texte)
                M = Point(x, y, legende = TEXTE, label = texte, style = "o", couleur = "w", taille = 0)
                M.etiquette.style(_rayon_ = 0, niveau = 15, alignement_vertical = "center", alignement_horizontal = "center", fond = "w")
                return M


            def creer_segment(point1, point2, texte):
                texte = formater_texte(texte)
                s = Segment(point1, point2, legende = TEXTE, label = texte)
                s.etiquette.style(_rayon_ = 0, niveau = 15, alignement_vertical = "center", alignement_horizontal = "center", fond = "w")
                return s

            ramification = [0] # astuce pour avoir un "objet modifiable" (a mutable object)
            def parcourir_branche(branche, n, ramification = ramification):
                txt = branche["texte"].rsplit(":", 1)
                if len(txt) == 2:
                    txt_pt, txt_segm = txt
                else:
                    txt_pt = txt[0]
                    txt_segm = ""
                if len(branche["liste"]) > 0:
                    l = []
                    for tige in branche["liste"]:
                        l.append(parcourir_branche(tige, n + 1))

                    M = creer_point(n/(nbr_colonnes - 1), .5*(l[0][0].ordonnee+l[-1][0].ordonnee), txt_pt)
                    self.feuille_actuelle.objets.add(M)
                    for point, txt_s in l:
                        s = creer_segment(M, point, txt_s)
                        self.feuille_actuelle.objets.add(s)
                    return M, txt_segm
                else:
                    M = creer_point(n/(nbr_colonnes - 1), 1 - ramification[0]/(ramifications - 1), txt_pt)
                    ramification[0] += 1
                    self.feuille_actuelle.objets.add(M)
                    return M, txt_segm

            for branche in arbre:
                parcourir_branche(branche, 0)

            if legende is not None:
                decalage = -0.5
                for i in legende:
                    if i != "|":
                        break
                    decalage += .5
                legende = legende.strip("|").split("|")
                for n in xrange(len(legende)):
                    t = Texte(legende[n], (n + decalage)/(nbr_colonnes - 1), 1.1)
                    self.feuille_actuelle.objets.add(t)

            self.feuille_actuelle.interprete.commande_executee()

    def info_proprietes(self, titre):
        dlg = wx.MessageDialog(self, u"Créez l'arbre au préalable.", titre, wx.OK)
        dlg.ShowModal()
        dlg.Destroy()


    def proprietes_sommets(self, event = None):
        objets = self.feuille_actuelle.objets.lister(type = Point)
        if not objets:
            self.info_proprietes(u'Aucun sommet.')
            return
        win = Proprietes(self, objets)
        win.Show(True)



    def proprietes_aretes(self, event = None):
        objets = self.feuille_actuelle.objets.lister(type = Segment)
        if not objets:
            self.info_proprietes(u'Aucune arête.')
            return
        win = Proprietes(self, objets)
        win.Show(True)


    def proprietes_titres(self, event = None):
        objets = self.feuille_actuelle.objets.lister(type = Texte)
        if not objets:
            self.info_proprietes(u'Aucun titre.')
            return
        win = Proprietes(self, objets)
        win.Show(True)


    def _affiche(self):
        pass

    def assistant(self, event = None, liste = None):
        """Crée un arbre en supposant les évènements de la liste tous indépendants entre eux.

        Exemple:
        self.assistant(liste = ["A:0.4", "B:0.7"])

        On peut spécifier explicitement les évènements contraires:
        self.assistant(liste = [("G_1:0.4", "P_1:0.6"), ("G_2:0.5", "P_2:0.5")])"""


        lignes = [""]
        niveau = 0
        for couple in liste:
            if isinstance(couple, str):
                evt1 = couple
                evt2 = None
            else:
                evt1, evt2 = couple

            niveau += 1

            for i in xrange(len(lignes) - 1, -1, -1):
                if evt2 is None:
                    if ":" in evt1:
                        evt, proba = evt1.rsplit(":", 1)
                    else:
                        evt = evt1
                        proba = ""
                    try:
                        proba = str(1-float(proba))
                    except ValueError:
                        proba = "1-" + proba
                    evt2 = "&" + evt + ":" + proba

                lignes.insert(i, niveau*">" + evt2)
                lignes.insert(i, niveau*">" + evt1)

        print "test", "\n".join(lignes)
        self.instructions.SetValue("\n".join(lignes))



    def bernouilli(self, event = None, n = 3, evt1 = "", evt2 = None):
        self.assistant(liste = n*[(evt1, evt2)])
