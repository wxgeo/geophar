# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------#######
#                 Contact                     #
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

import thread, sys
import wx
from wxlib import TransmitEvent, EVT_TRANSMIT

from .. import param
from ..pylib import path2
from ..pylib.bugs_report import rapporter

class Contact(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, u"Contacter l'auteur", style = wx.FRAME_FLOAT_ON_PARENT|wx.CLIP_CHILDREN|wx.CLOSE_BOX|wx.CAPTION)
        self.SetBackgroundColour(wx.WHITE)

        self.parent = parent

        panel = wx.Panel(self, -1)
        italic = wx.Font(panel.GetFont().GetPointSize(), panel.GetFont().GetFamily(), wx.ITALIC, wx.NORMAL)
#        bold_italic = wx.Font(panel.GetFont().GetPointSize(), panel.GetFont().GetFamily(), wx.ITALIC, wx.BOLD)
        panel.SetBackgroundColour(wx.WHITE)

        panelSizer = wx.BoxSizer(wx.VERTICAL)

        avant_propos = wx.StaticText(panel, -1, u"""Afin d'améliorer le fonctionnement de WxGéométrie,
vous êtes invités à signaler tout problème rencontré.""")
        panelSizer.Add(avant_propos, 0, wx.ALL, 5)
        avant_propos.SetFont(italic)
        panelSizer.Add((5, 5))


        rapport = wx.StaticBoxSizer(wx.StaticBox(panel, -1, u"Rapport d'incident"), wx.VERTICAL)
        #rapport.Add(wx.StaticText(panel, -1, u"Résumé :"), 0, wx.ALL, 5)
        self.titre = titre = wx.TextCtrl(panel, -1, u"Résumé", size = (300, -1))
        titre.SelectAll()
        rapport.Add(titre, 0, wx.ALL, 5)

        sizer= wx.BoxSizer(wx.HORIZONTAL)
        self.modules = modules = wx.Choice(panel, choices = [self.parent.onglet(md).__titre__ for md in param.modules if hasattr(self.parent.onglet(md), "__titre__")])
        sizer.Add(wx.StaticText(panel, -1, u"Module concerné :"), 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        modules.SetSelection(self.parent.GetSelection())
        sizer.Add(modules, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        rapport.Add(sizer, 0, wx.ALL, 0)

        rapport.Add(wx.StaticText(panel, -1, u"Description du problème :"), 0, wx.ALL, 5)
        self.commentaire = commentaire = wx.TextCtrl(panel, size = (300,100), style = wx.TE_MULTILINE)
        rapport.Add(commentaire, 0, wx.ALL, 5)

        panelSizer.Add(rapport, 0, wx.ALL|wx.EXPAND, 5)

        sizer = wx.StaticBoxSizer(wx.StaticBox(panel, -1, u"Vos coordonnées (facultatif)"), wx.HORIZONTAL)
        sizer.Add(wx.StaticText(panel, -1, u"Nom :"), 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        self.nom = nom = wx.TextCtrl(panel, size = (100, -1))
        sizer.Add(nom, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(wx.StaticText(panel, -1, u" E-mail :"), 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        self.mail = mail = wx.TextCtrl(panel, size = (100, -1))
        sizer.Add(mail, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)

        panelSizer.Add(sizer, 0, wx.ALL|wx.EXPAND, 5)

        options = wx.StaticBoxSizer(wx.StaticBox(panel, -1, u"Options"), wx.VERTICAL)
        self.histo = histo = wx.CheckBox(panel, -1, "Inclure l'historique du module courant.")
        histo.SetValue(True)
        options.Add(histo, 0, wx.ALL, 5)

        self.msg = msg = wx.CheckBox(panel, -1, "Inclure l'historique des commandes.")
        msg.SetValue(True)
        options.Add(msg, 0, wx.ALL, 5)

        panelSizer.Add(options, 0, wx.ALL|wx.EXPAND, 5)


        btnOK = wx.Button(panel, wx.ID_OK, u"Envoyer")
        btnOK.SetToolTipString(u"Envoyer les informations.")
        btnCancel = wx.Button(panel, wx.ID_CANCEL, u"Annuler")
        btnCancel.SetToolTipString(u"Quitter sans rien envoyer.")

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(btnOK, 0, wx.RIGHT, 40)
        sizer.Add(btnCancel, 0, wx.LEFT, 40)
        panelSizer.Add(sizer, 0, wx.ALL | wx.ALIGN_CENTRE, 15)

        panel.SetAutoLayout(True)
        panel.SetSizer(panelSizer)
        panelSizer.Fit(panel)

        topSizer = wx.BoxSizer(wx.HORIZONTAL)
        topSizer.Add(panel, 0, wx.ALL, 10)

        self.SetAutoLayout(True)
        self.SetSizer(topSizer)
        topSizer.Fit(self)

        self.Centre()

        self.Bind(EVT_TRANSMIT, self.onTransmit)
        btnOK.Bind(wx.EVT_BUTTON, self.rapporter)
        btnCancel.Bind(wx.EVT_BUTTON, self.annuler)


    def annuler(self, event):
        self.Close()


    def rapporter(self, event):
        titre = self.titre.GetValue()
        commentaire = self.commentaire.GetValue()
        nom = self.nom.GetValue()
        mail = self.mail.GetValue()
        module = self.parent.onglet(self.modules.GetSelection())
        if self.histo.GetValue() and hasattr(module, "log"):
            histo = module.log.contenu()
        else:
            histo = ""
        if self.msg.GetValue():
            sys.stdout.flush()
            filename = path2(param.emplacements['log'] + u"/messages.log")
            try:
                file = open(filename, 'r')
                msg = file.read()
            finally:
                file.close()
        else:
            msg = ""
        def f():
            result = rapporter(titre = titre, auteur = nom, email = mail, description = commentaire, historique = histo, log = msg)
            wx.PostEvent(self, TransmitEvent(success = result))
        self.Hide()
        thread.start_new_thread(f, ())



    def onTransmit(self, event):
        if event.success:
            dlg = wx.MessageDialog(self, u"Le message a été envoyé avec succès. Merci !",
                                   u"Message envoyé",
                                   wx.OK | wx.ICON_INFORMATION
                                   )
        else:
            dlg = wx.MessageDialog(self, u"Impossible d'envoyer le message !",
                               u"Connexion impossible.",
                               wx.OK | wx.ICON_INFORMATION
                               #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                               )
        dlg.ShowModal()
        dlg.Destroy()
        if event.success:
            self.Close()
        else:
            self.Show()
