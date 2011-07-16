# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)
from __future__ import with_statement

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


import os, math
import wx, wx.lib.dialogs, wx.lib.newevent
from .. import param
from ..pylib import uu


class PseudoEvent(object):
    u"Cette classe est destinée à maintenir en vie un évènement périmé."

    _methodes = ("AltDown", "ControlDown", "ShiftDown", "GetPositionTuple",
                "RightIsDown", "RightIsUp", "LeftIsDown", "LeftIsUp", "GetWheelRotation")

    def __init__(self, event):
        self._dict = {}
        for methode in self._methodes:
            if hasattr(event, methode):
                self._dict[methode] = getattr(event, methode)()

    def __getattr__(self, name):
        try:
            return lambda:self._dict[name]
        except KeyError:
            print(u"La méthode " + name + " n'est actuellement pas définie pour les pseudo-évènements.")
            raise

    def Skip(self):
        pass


TransmitEvent, EVT_TRANSMIT = wx.lib.newevent.NewEvent()
#AutoSaveEvent, EVT_AUTOSAVE = wx.lib.newevent.NewEvent()

class BusyCursor(object):
    compteur = 0

    def __enter__(self):
        self.__class__.compteur += 1

    def __exit__(self, type, value, traceback):
        self.__class__.compteur -= 1
        if self.compteur == 0:
            wx.EndBusyCursor()

class BusyCursor(object):
    def __enter__(self):
        wx.BeginBusyCursor()

    def __exit__(self, type, value, traceback):
        wx.EndBusyCursor()
        if wx.Platform == '__WXMSW__':
            # Le curseur disparaît sinon sous Windows !!
            wx.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))


if wx.Platform == '__WXGTK__':
    # Bug de wx.Miniframe lorsque Compiz est activé sous Linux.
    class MyMiniFrame(wx.Frame):
        def __init__(self, parent, titre):
            wx.Frame.__init__(self, parent, -1, titre, style= wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT | wx.FRAME_NO_TASKBAR)
else:
    class MyMiniFrame(wx.MiniFrame):
        def __init__(self, parent, titre):
            wx.MiniFrame.__init__(self, parent, -1, titre, style=wx.DEFAULT_FRAME_STYLE)

# La version de WxPython doit supporter l'unicode.
assert (wx.PlatformInfo[2] == "unicode"), "La version de WxPython utilisee doit imperativement supporter l'unicode !"


def png(nom):
    u"""Charge l'image <nom>.png depuis le repertoire 'images/'.

    L'image doit être au format png, et son nom doit indiqué sans l'extension '.png'."""
    return wx.Image(os.path.normpath(os.path.join(uu(param.EMPLACEMENT), 'images', nom + ".png")), wx.BITMAP_TYPE_PNG).ConvertToBitmap()


def screen_dpi(diagonale,  ratio = (16, 10), pixels = None):
    u"""diagonale : longueur (en inches) de la diagonale de l'écran.
    ratio : (4, 3) ou (16, 10)
    pixels : 1024x768 par exemple (la soit-disant "résolution" de l'écran)
    """
    if pixels is None:
        pixels = wx.ScreenDC().GetSizeTuple()
    l, h = pixels
    x, y = ratio
    d = math.hypot(x, y)
    k = diagonale/d
    x *= k
    y *= k
    return (l/x, h/y)


class MyFont(wx.Font):
    u"""Créé une nouvelle police, héritant par défaut ses attributs de 'widget'."""
    def __init__(self, widget, size=None, family=None, style=None, weight=None, underline=None):
        font = widget.GetFont()
        if size is None:
            size = font.GetPointSize()
        if family is None:
            family = font.GetFamily()
        if style is None:
            style = font.GetStyle()
        if weight is None:
            weight = font.GetWeight()
        if underline is None:
            underline = font.GetUnderlined()
        wx.Font.__init__(self, size, family, style, weight, underline)
