# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)


##--------------------------------------#######
#                 Aide                        #
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


import  wx.html as html
import wx

from .. import param
from .wxlib import png
from ..pylib.infos import informations_configuration



class Help(wx.Frame):
    def __init__(self, parent, path):
        wx.Frame.__init__(self, parent, -1, size=wx.Size(700,610))

        self.path = path

        self.SetBackgroundColour(wx.Colour(255, 225, 153))
        self.html = html.HtmlWindow(self, -1, style=wx.NO_FULL_REPAINT_ON_RESIZE)
        self.html.SetRelatedFrame(self, u" %s ")
        #self.html.SetRelatedStatusBar(0)

        self.printer = html.HtmlEasyPrinting()

        self.box = wx.BoxSizer(wx.VERTICAL)

        subbox = wx.BoxSizer(wx.HORIZONTAL)

        icones = [(u"maison",u"Page d'accueil.", self.OnHome), (u"gauche", u"Page precedente.", self.OnBack), (u"droite", u"Page suivante.", self.OnForward), (u"print", u"Imprimer la page.", self.OnPrint)]

        for i in range(len(icones)):
            icone = icones[i]
            bmp = png(icone[0])
            bouton = wx.BitmapButton(self, -1, bmp, style=wx.NO_BORDER)
            bouton.SetBackgroundColour(self.GetBackgroundColour())
            subbox.Add(bouton, 0, wx.ALL,5)
            bouton.SetToolTipString(icone[1])
            bouton.Bind(wx.EVT_BUTTON, icone[2])



        self.box.Add(subbox, 0)
        self.box.Add(self.html, 1, wx.GROW)
        self.SetSizer(self.box)
        self.SetAutoLayout(True)

        self.OnHome(None)


    def OnHome(self, event):
        self.html.LoadPage(self.path)



    def OnBack(self, event):
        self.html.HistoryBack()


    def OnForward(self, event):
        self.html.HistoryForward()


    def OnPrint(self, event):
        self.printer.GetPrintData().SetPaperId(wx.PAPER_LETTER)
        self.printer.PrintFile(self.html.GetOpenedPage())


class Informations(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, u"Configuration systeme")
        self.SetBackgroundColour(wx.WHITE)

        panel = wx.Panel(self, -1)
        panel.SetBackgroundColour(wx.WHITE)

        panelSizer = wx.BoxSizer(wx.VERTICAL)

        italic = wx.Font(panel.GetFont().GetPointSize(),
                          panel.GetFont().GetFamily(),
                          wx.ITALIC, wx.NORMAL)

        #logo = wx.StaticBitmap(panel, -1, wx.Image(name = "images"+os.sep+"logo2.png").ConvertToBitmap())

        #panelSizer.Add(logo, 0, wx.ALIGN_CENTRE)

        textes = informations_configuration().split(u"\n")

        for texte in textes:
            t = wx.StaticText(panel, -1, texte)
            if texte.startswith("+ "):
                t.SetFont(italic)
            panelSizer.Add(t, 0, wx.ALIGN_LEFT)


        btnOK = wx.Button(panel, wx.ID_OK, u"OK")
        btnCopier = wx.Button(panel, -1, u"Copier")
        btnCopier.Bind(wx.EVT_BUTTON, self.copier)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(btnOK, 0, wx.RIGHT, 40)
        sizer.Add(btnCopier, 0, wx.LEFT, 40)
        panelSizer.Add(sizer, 0, wx.ALL | wx.ALIGN_CENTRE, 5)

        panel.SetAutoLayout(True)
        panel.SetSizer(panelSizer)
        panelSizer.Fit(panel)

        topSizer = wx.BoxSizer(wx.HORIZONTAL)
        topSizer.Add(panel, 0, wx.ALL, 10)

        self.SetAutoLayout(True)
        self.SetSizer(topSizer)
        topSizer.Fit(self)

        self.Centre()


    def copier(self, event):
        self.clipBoard=wx.TheClipboard
        if self.clipBoard.Open():
            self.clipBoard.AddData(wx.TextDataObject(informations_configuration()))
        self.clipBoard.Close()



class About(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, u"A propos de WxGéométrie")
        self.SetBackgroundColour(wx.WHITE)

        panel = wx.Panel(self, -1)
        panel.SetBackgroundColour(wx.WHITE)

        panelSizer = wx.BoxSizer(wx.VERTICAL)

        italic = wx.Font(panel.GetFont().GetPointSize(),
                          panel.GetFont().GetFamily(),
                          wx.ITALIC, wx.NORMAL)

        bold = wx.Font(panel.GetFont().GetPointSize(),
                          panel.GetFont().GetFamily(),
                          wx.NORMAL, wx.BOLD)

        logo = wx.StaticBitmap(panel, -1, png(u"logo2"))

        panelSizer.Add(logo, 0, wx.ALIGN_CENTRE)

        date = "/".join(str(n) for n in reversed(param.date_version))
        textes = [[u"WxGéométrie version %s" % param.version, bold]]
        textes.append([u"Version publiée le " + date + "."])
        textes.append([])
        textes.append([u"De la géométrie dynamique, un traceur de courbes, et bien plus..."])
        textes.append([u"WxGéométrie est un logiciel libre, vous pouvez l'utiliser et le modifier comme vous le souhaitez."])
        textes.append([u"Copyright 2005-" + unicode(param.date_version[0]) +" Nicolas Pourcelot (wxgeo@users.sourceforge.net)", italic])
        textes.append([])
        textes.append([u"WxGéométrie inclut désormais SymPy : Python library for symbolic mathematics."])
        textes.append([u"Copyright 2006-" + unicode(param.date_version[0]) + " The Sympy Team - http://www.sympy.org.", italic])
        textes.append([])
        textes.append([u"À Sophie."])
        textes.append([u"'Le rêve est bien réel. Effleurant votre main, je peux toucher le ciel!'  Alain Ayroles", italic])
        textes.append([u"Tous mes remerciements à la communauté du logiciel libre."])
        textes.append([])

        for texte in textes:
            l = len(texte)
            if l:
                txt = wx.StaticText(panel, -1, texte[0])
                if l > 1:  txt.SetFont(texte[1])
                panelSizer.Add(txt, 0, wx.ALIGN_LEFT)
            else:
                panelSizer.Add((5, 5)) # Spacer.


        btnOK = wx.Button(panel, wx.ID_OK, u"OK")

        panelSizer.Add(btnOK, 0, wx.ALL | wx.ALIGN_CENTRE, 5)

        panel.SetAutoLayout(True)
        panel.SetSizer(panelSizer)
        panelSizer.Fit(panel)

        topSizer = wx.BoxSizer(wx.HORIZONTAL)
        topSizer.Add(panel, 0, wx.ALL, 10)

        self.SetAutoLayout(True)
        self.SetSizer(topSizer)
        topSizer.Fit(self)

        self.Centre()
