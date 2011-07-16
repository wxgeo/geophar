# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

#    :--------------------------------------------:
#    :                  Traceur                   :
#    :--------------------------------------------:
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

from functools import partial
import re
import wx

from ...GUI import MenuBar, Panel_API_graphique
from ...geolib import Courbe, Fonction
from . import suites


class TraceurMenuBar(MenuBar):
    def __init__(self, panel):
        MenuBar.__init__(self, panel)

        self.ajouter(u"Fichier", [u"nouveau"], [u"ouvrir"], [u"ouvrir ici"], [u"enregistrer"], [u"enregistrer_sous"], [u"exporter"], [u"exporter&sauver"], None, [u"mise en page"], [u"imprimer"], [u"presse-papier"], None, [u"proprietes"], None, self.panel.doc_ouverts, None, ["fermer"], ["quitter"])
        self.ajouter(u"Editer", ["annuler"], ["refaire"], ["modifier"], ["supprimer"])
        self.ajouter(u"creer")
        self.ajouter("affichage")
        self.ajouter("autres")
        self.ajouter(u"Outils",
        #[u"Tableau de valeurs", u"Tableaux de valeurs des fonctions.", u"Ctrl+T", self.panel.tableau],
        [u"Représenter une suite", u"Représenter une suite numérique.", None, self.panel.suite],
        None, [u"options"])
        self.ajouter(u"avance1")
        self.ajouter(u"?")




class Traceur(Panel_API_graphique):

    __titre__ = u"Traceur de courbes" # Donner un titre a chaque module

    def __init__(self, *args, **kw):
        Panel_API_graphique.__init__(self, *args, **kw)

        self.couleurs = u"bgrmkcy"

        self.nombre_courbes = self._param_.nombre_courbes
        self.boites = []
        self.equations = []
        self.intervalles = []

        self.entrees = wx.BoxSizer(wx.VERTICAL)
        self.entrees.Add(wx.StaticText(self, -1, u" Equations :"), 0, wx.ALL,5)

        for i in range(self.nombre_courbes):
                ligne = wx.BoxSizer(wx.HORIZONTAL)

                self.boites.append(wx.CheckBox(self, label='f%s:'%(i+1)))
                self.boites[-1].SetValue(True) # Par defaut, les cases sont cochees.
                self.boites[i].Bind(wx.EVT_CHECKBOX, self.synchronise_et_affiche)
                # Bug de WxGtk: on ne peut pas attacher simultanément une fonction
                # aux évènements EVT_CHECKBOX et EVT_ENTER_WINDOW
                #self.boites[i].Bind(wx.EVT_ENTER_WINDOW, partial(self.MouseOver, i=i))
                self.boites[i].Bind(wx.EVT_LEAVE_WINDOW, self.MouseOver)
                ligne.Add(self.boites[i], 0, wx.ALIGN_CENTRE|wx.ALL,5)

                ligne.Add(wx.StaticText(self, -1, "Y ="), 0, wx.ALIGN_CENTRE|wx.ALL,5)
                self.equations.append(wx.TextCtrl(self, size=(120, -1), style=wx.TE_PROCESS_ENTER))
                self.equations[i].Bind(wx.EVT_CHAR, partial(self.EvtChar, i=i))
                self.equations[i].Bind(wx.EVT_ENTER_WINDOW, partial(self.MouseOver, i=i))
                self.equations[i].Bind(wx.EVT_LEAVE_WINDOW, self.MouseOver)
                ligne.Add(self.equations[i], 0, wx.ALIGN_CENTRE|wx.ALL,5)

                ligne.Add(wx.StaticText(self, -1, "sur"), 0, wx.ALIGN_CENTRE|wx.ALL,5)
                self.intervalles.append(wx.TextCtrl(self, size = (100, -1), style = wx.TE_PROCESS_ENTER))
                self.intervalles[i].Bind(wx.EVT_CHAR, partial(self.EvtChar, i=i))
                self.intervalles[i].Bind(wx.EVT_ENTER_WINDOW, partial(self.MouseOver, i=i))
                self.intervalles[i].Bind(wx.EVT_LEAVE_WINDOW, self.MouseOver)
                ligne.Add(self.intervalles[i], 0, wx.ALIGN_CENTRE|wx.ALL,5)

                self.entrees.Add(ligne, 0, wx.ALL, 5)

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW, 0)
        self.sizer.Add(self.entrees, 0, wx.ALL|wx.GROW, 5)
        self.finaliser(contenu = self.sizer)
        self._changement_feuille()


    def activer(self):
        # Actions à effectuer lorsque l'onglet devient actif
        self.equations[0].SetFocus()

    def _changement_feuille(self):
        u"""Après tout changement de feuille."""
        if hasattr(self, 'nombre_courbes'): # initialisation terminée
            self._synchroniser_champs()
            self.feuille_actuelle.lier(self._synchroniser_champs)


    def _synchroniser_champs(self):
        u"""On synchronise le contenu des champs de texte avec les courbes.

        Lors de l'ouverture d'un fichier, ou d'un changement de feuille,
        ou lorsqu'une commande est exécutée dans la feuille."""
        print "Synchronisation des champs..."
        for i in xrange(self.nombre_courbes):
            nom_courbe = 'Cf' + str(i + 1)
            if self.feuille_actuelle.objets.has_key(nom_courbe):
                objet = self.feuille_actuelle.objets[nom_courbe]
                self.boites[i].SetValue(objet.style('visible'))
                expression = objet.fonction.expression
                if expression.strip():
                    self.equations[i].SetValue(expression)
                    self.boites[i].Enable()
                else:
                    self.boites[i].Disable()
                ensemble = objet.fonction.ensemble
                ensemble = re.sub(r"(?<=[][])\+(?=[][])", 'U', ensemble)
                extremites_cachees = (str(e) for e in objet.fonction.style('extremites_cachees'))
                parties = ensemble.split('|')

                j = 0
                for partie, extremites in zip(parties, extremites_cachees):
                    def f(m):
                        a, b, c, d = m.groups()
                        return (a if b not in extremites else ' ') + b + ';' \
                                + c + (d if c not in extremites else ' ')
                    parties[j] = re.sub(r"([][])([^][;]+);([^][;]+)([][])", f, partie)
                    j += 1

                self.intervalles[i].SetValue('|'.join(parties))
            else:
                self.boites[i].Disable()
                self.equations[i].SetValue('')
                self.intervalles[i].SetValue('')

    def _synchroniser_courbes(self):
        u"""Opération inverse : on synchronise les courbes avec le contenu des champs de texte.

        Après un changement dans les champs de textes/cases à cocher."""
        objets = self.feuille_actuelle.objets
        for i in xrange(self.nombre_courbes):
            nom_courbe = 'Cf' + str(i + 1)
            nom_fonction = 'f' + str(i + 1)
            expr = self.equations[i].GetValue()
            ensemble = self.intervalles[i].GetValue()
            visible = self.boites[i].GetValue()
            if not expr.strip():
                visible = False
#                self.boites[i].Disable()
            if self.feuille_actuelle.objets.has_key(nom_fonction):
                objets[nom_fonction].modifier_expression_et_ensemble(expression = expr, ensemble = ensemble)
            else:
                objets[nom_fonction] = Fonction(expr, ensemble, 'x')
            if self.feuille_actuelle.objets.has_key(nom_courbe):
                objets[nom_courbe].style(visible = visible)
            else:
                f = objets[nom_fonction]
                objets[nom_courbe] = Courbe(f, protege = True, visible = visible, couleur = self.couleurs[i%len(self.couleurs)])

##            self.canvas.regenerer_liste = True

##    def _sauvegarder(self, fgeo):
##        Panel_API_graphique._sauvegarder(self, fgeo)
##        fgeo.contenu[u"Courbe"] = [{"Y" : [self.equations[i].GetValue()], u"intervalle" : [self.intervalles[i].GetValue()], u"active" : [str(self.boites[i].GetValue())]} for i in range(self.nombre_courbes)]


##    def _ouvrir(self, fgeo):
##        Panel_API_graphique._ouvrir(self, fgeo)
##        if fgeo.contenu.has_key(u"Courbe"):
##            for i in range(min(len(fgeo.contenu[u"Courbe"]), self.nombre_courbes)):
##                self.equations[i].SetValue(fgeo.contenu[u"Courbe"][i][u"Y"][0])
##                self.intervalles[i].SetValue(fgeo.contenu[u"Courbe"][i][u"intervalle"][0])
##                self.boites[i].SetValue(fgeo.contenu[u"Courbe"][i][u"active"][0] == u"True")
##        self.affiche()

    def _ouvrir(self, fgeo):
        Panel_API_graphique._ouvrir(self, fgeo)
        # On synchronise le contenu des champs de texte avec les courbes *à la fin*.
        self._synchroniser_champs()

    def EvtChar(self, event=None, i=None):
        assert (i is not None)
        code = (event.GetKeyCode() if event is not None else wx.WXK_RETURN)

        if code in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            self.boites[i].SetValue(event is None or not event.ShiftDown())
            self.synchronise_et_affiche()
        elif code == wx.WXK_ESCAPE:
            self.boites[i].SetValue(False)
            self.synchronise_et_affiche()
        else:
            event.Skip()

    def MouseOver(self, event=None, i=None):
        if i is None:
            self.canvas.select = None
        else:
            nom_courbe = 'Cf' + str(i + 1)
            self.canvas.select = self.feuille_actuelle.objets.get(nom_courbe, None)
        self.canvas.selection_en_gras()
        event.Skip()

    def synchronise_et_affiche(self, event = None):
        self._synchroniser_courbes()
        self.action_effectuee(u'Courbes modifiées.')
        self.affiche()
        #event.Skip()

#    def tableau(self, event = None):
#        self.parent.a_venir()
#        return
#        table = tableau.TableauValeurs(self)
#        table.Show(True)
        #table.SetSize(wx.Size(200,250))
        #table.SetDimensions(-1, -1, -1, 300)


    def suite(self, event = None):
        suite = suites.CreerSuite(self)
        suite.Show(True)
