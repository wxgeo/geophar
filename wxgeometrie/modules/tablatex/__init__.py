#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------#######
#                Calculatrice                 #
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

import wx

from ...GUI.ligne_commande import LigneCommande
from ...GUI import MenuBar, Panel_simple
from ... import param
from ...pylib import warning
from ...pylib.erreurs import message
from .tabsign import tabsign
from .tabval import tabval
from .tabvar import tabvar






class TabLaTeXMenuBar(MenuBar):
    def __init__(self, panel):
        MenuBar.__init__(self, panel)
        self.ajouter(u"Fichier", ["quitter"])
        self.ajouter(u"Affichage", ["onglet"])
        self.ajouter(u"Outils",
                        [u"Mémoriser le résultat", u"Copie le code LaTeX généré dans le presse-papier, afin de pouvoir l'utiliser ailleurs.", "Ctrl+M", self.panel.vers_presse_papier],
                        None,
                        [u"options"])
        self.ajouter(u"avance2")
        self.ajouter("?")




class TabLaTeX(Panel_simple):
    __titre__ = u"Tableaux LaTeX" # Donner un titre a chaque module

    def __init__(self, *args, **kw):
        Panel_simple.__init__(self, *args, **kw)

        self.sizer = wx.BoxSizer(wx.VERTICAL)

##        self.entrees = wx.BoxSizer(wx.HORIZONTAL)
##        self.entree = wx.TextCtrl(self, size = (500, -1), style=wx.TE_PROCESS_ENTER)
##        self.entrees.Add(self.entree, 1, wx.ALL|wx.GROW, 5)
##        self.valider = wx.Button(self, wx.ID_OK)
##        self.entrees.Add(self.valider, 0, wx.ALL, 5)
##
##        self.sizer.Add(self.entrees, 0, wx.ALL, 5)
        self.entree = LigneCommande(self, longueur = 500, action = self.generer_code)
        self.sizer.Add(self.entree, 0, wx.ALL, 5)


        self.sizer_type = wx.BoxSizer(wx.HORIZONTAL)
        self.type_tableau = wx.Choice(self, choices = (u"Tableau de variations", u"Tableau de signes", u"Tableau de valeurs"))
        self.type_tableau.SetSelection(self._param_.mode)
        self.sizer_type.Add(wx.StaticText(self, label = u"Type de tableau à générer :"), 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        self.sizer_type.Add(self.type_tableau, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)

        self.utiliser_cellspace =  wx.CheckBox(self, label = u"Utiliser le paquetage cellspace.")
        self.utiliser_cellspace.SetValue(self._param_.utiliser_cellspace)
        self.utiliser_cellspace.SetToolTipString(u"Le paquetage cellspace évite que certains objets (comme les fractions) touchent les bordures du tableaux.")
        self.sizer_type.AddSpacer((10,0))
        self.sizer_type.Add(self.utiliser_cellspace, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)

        self.derivee =  wx.CheckBox(self, label = u"Dérivée.")
        self.derivee.SetValue(self._param_.derivee)
        self.derivee.SetToolTipString(u"Afficher une ligne indiquant le signe de la dérivée.")
        self.sizer_type.AddSpacer((10,0))
        self.sizer_type.Add(self.derivee, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)

        self.limites =  wx.CheckBox(self, label = u"Limites.")
        self.limites.SetValue(self._param_.limites)
        self.limites.SetToolTipString(u"Afficher les limites dans le tableau de variations.")
        self.sizer_type.AddSpacer((10,0))
        self.sizer_type.Add(self.limites, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)

        self.sizer.Add(self.sizer_type, 0, wx.ALL, 5)

        box = wx.StaticBox(self, -1, u"Code LaTeX permettant de de générer le tableau")
        self.bsizer = wx.StaticBoxSizer(box, wx.VERTICAL)

        #~ self.sizer_code = wx.BoxSizer(wx.HORIZONTAL)
        #~ self.sizer_code.Add(wx.StaticText(self, label = u"Code LaTeX permettant de de générer le tableau."), 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        #~ self.copier_code = wx.Button(self, label = u"Copier dans le presse-papier")
        #~ self.sizer_code.Add(self.copier_code, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)


        #~ self.bsizer.Add(self.sizer_code, 0, wx.ALL, 5)

        self.code_tableau = wx.TextCtrl(self, size = (700, 200), style = wx.TE_MULTILINE | wx.TE_RICH)
        self.bsizer.Add(self.code_tableau, 0, wx.ALL, 5)

        self.copier_code = wx.Button(self, label = u"Copier dans le presse-papier")
        self.bsizer.Add(self.copier_code, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)

        self.bsizer.Add(wx.StaticText(self, label = u"Pensez à rajouter dans l'entête de votre fichier LaTeX la ligne suivante :"), 0, wx.TOP|wx.LEFT, 5)

        self.sizer_entete = wx.BoxSizer(wx.HORIZONTAL)
        self.code_entete = wx.TextCtrl(self, size = (200, -1), value = u"\\usepackage{tabvar}", style = wx.TE_READONLY)
        self.sizer_entete.Add(self.code_entete, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        self.copier_entete = wx.Button(self, label = u"Copier cette ligne")
        self.sizer_entete.Add(self.copier_entete, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)

        self.bsizer.Add(self.sizer_entete, 0, wx.ALL, 5)

        self.sizer.Add(self.bsizer, 0, wx.ALL, 5)


        self.cb = wx.CheckBox(self, label = u"Copier automatiquement le code LaTeX dans le presse-papier.")
        self.cb.SetValue(self._param_.copie_automatique)
        self.sizer.Add(self.cb, 0, wx.ALL, 5)

        self.SetSizer(self.sizer)
        self.Fit()


##        self.entree.Bind(wx.EVT_KEY_UP, self.EvtChar)
##        self.valider.Bind(wx.EVT_BUTTON, self.generer_code)

        self.type_tableau.Bind(wx.EVT_CHOICE, self.EvtChoix)
        self.EvtChoix()

        def copier_code(event = None):
            self.vers_presse_papier(texte = self.code_tableau.GetValue())
        self.copier_code.Bind(wx.EVT_BUTTON, copier_code)

        def copier_entete(event = None):
            self.vers_presse_papier(texte = self.code_entete.GetValue())
        self.copier_entete.Bind(wx.EVT_BUTTON, copier_entete)

        def regler_mode_copie(event = None):
            self._param_.copie_automatique = self.cb.GetValue()
        self.cb.Bind(wx.EVT_CHECKBOX, regler_mode_copie)

        def regler_cellspace(event = None):
            self._param_.utiliser_cellspace = self.utiliser_cellspace.GetValue()
            if self._param_.utiliser_cellspace:
                self.code_entete.SetValue(u"\\usepackage{cellspace}")
            else:
                self.code_entete.SetValue(u"")
        self.utiliser_cellspace.Bind(wx.EVT_CHECKBOX, regler_cellspace)

        def regler_derivee(event = None):
            self._param_.derivee = self.derivee.GetValue()
        self.derivee.Bind(wx.EVT_CHECKBOX, regler_derivee)

        def regler_limites(event = None):
            self._param_.limites = self.limites.GetValue()
        self.limites.Bind(wx.EVT_CHECKBOX, regler_limites)

    def activer(self):
        # Actions à effectuer lorsque l'onglet devient actif
        self.entree.SetFocus()

    def vers_presse_papier(self, event = None, texte = ""):
        Panel_simple.vers_presse_papier(texte)


    def generer_code(self, commande, **kw):
        self.modifie = True
        try:
            if self._param_.mode == 0:
                code_latex = tabvar(commande, derivee=self._param_.derivee, limites=self._param_.limites)
            elif self._param_.mode == 1:
                code_latex = tabsign(commande, cellspace=self._param_.utiliser_cellspace)
            elif self._param_.mode == 2:
                code_latex = tabval(commande)
            else:
                warning("Type de tableau non reconnu.")

            self.code_tableau.SetValue(code_latex)
            if self._param_.copie_automatique:
                self.vers_presse_papier(texte = code_latex)
            self.entree.SetFocus()
            self.message(u"Le code LaTeX a bien été généré.")
        except BaseException, erreur:
            self.message(u"Impossible de générer le code LaTeX. " + message(erreur))
            self.entree.SetFocus()
            if param.debug:
                raise






    def EvtChoix(self, event = None):
        self._param_.mode = self.type_tableau.GetSelection()
        if self._param_.mode == 0:
            self.code_entete.SetValue(u"\\usepackage{tabvar}")
            self.entree.SetToolTipString(tabvar.__doc__)
            self.utiliser_cellspace.Disable()
            self.derivee.Enable()
            self.limites.Enable()
        elif self._param_.mode == 1:
            self.utiliser_cellspace.Enable()
            self.derivee.Disable()
            self.limites.Disable()
            self.entree.SetToolTipString(tabsign.__doc__)
            if self._param_.utiliser_cellspace:
                self.code_entete.SetValue(u"\\usepackage{cellspace}")
            else:
                self.code_entete.SetValue(u"")
        elif self._param_.mode == 2:
            self.utiliser_cellspace.Disable()
            self.derivee.Disable()
            self.limites.Disable()
            self.entree.SetToolTipString(tabval.__doc__)
            self.code_entete.SetValue(u"")
