# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

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
#
######################################

from functools import partial
import wx, wx.lib.newevent

from ..param.options import Section, Parametre

OptionsModifiedEvent, EVT_OPTIONS_MODIFIED = wx.lib.newevent.NewEvent()

class FenetreOptions(wx.Frame):
    def __init__(self, parent, options):
        wx.Frame.__init__(self, parent, -1, options.titre, style = wx.DEFAULT_FRAME_STYLE|wx.FRAME_FLOAT_ON_PARENT)
        self.parent = parent
        self.onglets = wx.Notebook(self, -1, style=wx.NB_TOP)
        dimensions_onglets = []
        self.widgets = {}
        for theme in options:
            panel = wx.Panel(self.onglets)
            sizer = wx.BoxSizer(wx.VERTICAL)
            self.onglets.AddPage(panel, theme.titre)
            for elt in theme:
                if isinstance(elt, Section):
                    box = wx.StaticBox(panel, -1, elt.titre)
                    bsizer = wx.StaticBoxSizer(box, wx.VERTICAL)
                    bsizer.AddSpacer(3)
                    for parametre in elt:
                        if isinstance(parametre, Parametre):
                            psizer = self.ajouter_parametre(parametre, panel, sizer)
                            bsizer.Add(psizer, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2)
                        elif isinstance(parametre, basestring):
                            bsizer.Add(wx.StaticText(panel, -1, parametre), 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
                        else:
                            raise NotImplementedError, repr(type(elt))
                    bsizer.AddSpacer(3)
                    sizer.Add(bsizer, 0, wx.ALL, 8)
                elif isinstance(elt, Parametre):
                    psizer = self.ajouter_parametre(elt, panel, sizer)
                    sizer.Add(psizer, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
                elif isinstance(elt, basestring):
                    sizer.Add(wx.StaticText(panel, -1, elt), 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
                else:
                    raise NotImplementedError, repr(type(elt))

            boutons = wx.BoxSizer(wx.HORIZONTAL)
            ok = wx.Button(panel, wx.ID_OK)
            ok.Bind(wx.EVT_BUTTON, self.EvtOk)
            boutons.Add(ok, 0, wx.ALL, 5)

            defaut = wx.Button(panel, label = u"Défaut")
            defaut.Bind(wx.EVT_BUTTON, self.EvtDefaut)
            boutons.Add(defaut, 0, wx.ALL, 5)

            annuler = wx.Button(panel, wx.ID_CANCEL)
            annuler.Bind(wx.EVT_BUTTON, self.EvtAnnuler)
            boutons.Add(annuler, 0, wx.ALL, 5)
            sizer.Add(boutons, 0, wx.ALL, 5)
            panel.SetSizer(sizer)
            dimensions_onglets.append(sizer.CalcMin().Get())

        w, h = (max(dimensions) for dimensions in zip(*dimensions_onglets))
        self.SetSize(wx.Size(w + 10, h + 50))
        self.CenterOnParent()



    def ajouter_parametre(self, parametre, panel, sizer):
        psizer = wx.BoxSizer(wx.HORIZONTAL)
        if parametre.type is not bool:
            psizer.Add(wx.StaticText(panel, -1, parametre.texte + ' :'), 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)

        if parametre.type is bool:
            widget = wx.CheckBox(panel, label=parametre.texte)
        elif parametre.type is file:
            widget = wx.TextCtrl(panel, -1, '', size=(200,-1))
        elif parametre.type is str:
            widget = wx.TextCtrl(panel, -1, '')
        elif isinstance(parametre.type, tuple):
            min_, max_ = parametre.type
            widget = wx.SpinCtrl(panel, min = min_, max = max_)
        elif isinstance(parametre.type, list):
##            widget = wx.Choice(panel, -1, choices = parametre.type)
            widget = wx.ComboBox(panel, choices = parametre.type,  style = wx.CB_READONLY)
        else:
            print parametre.type
            raise NotImplementedError
        self.widgets[parametre.nom] = widget
        widget.parametre = parametre
##        if insinstance(parametre.type, list):
##            widget.SetSelection(parametre.type.index(parametre.valeur))
##        else:
##            widget.SetValue(parametre.valeur)
        widget.SetValue(parametre.valeur)
        psizer.Add(widget, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        if parametre.type is file:
            parcourir = wx.Button(panel, -1, u'Parcourir')
            self.Bind(wx.EVT_BUTTON, partial(self.EvtParcourir, widget = widget), parcourir)
            psizer.Add(parcourir, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        return psizer


    def EvtOk(self, evt = None):
        modifs = set()
        for widget in self.widgets.itervalues():
            new_val = widget.GetValue()
            if new_val != widget.parametre.valeur:
                widget.parametre.valeur = new_val
                modifs.add(widget.parametre.prefixe)
        wx.PostEvent(self.parent, OptionsModifiedEvent(options = modifs))
        self.Close()

    def EvtDefaut(self, evt = None):
        for widget in self.widgets.itervalues():
            widget.SetValue(widget.parametre.defaut)

    def EvtAnnuler(self, evt = None):
        self.Close()

    def EvtParcourir(self, evt = None, widget = None):
        dlg = wx.DirDialog(self, u"Choisissez un répertoire :", style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            widget.SetValue(dlg.GetPath())
