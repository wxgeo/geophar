# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)
from __future__ import with_statement

##--------------------------------------#######
#                  Surfaces                   #
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
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.axes import Axes
from matplotlib.colors import LinearSegmentedColormap
from numpy import max as nmax, min as nmin, meshgrid

from ...GUI.wxlib import BusyCursor
from ...GUI import MenuBar, Panel_API_graphique
from ...pylib import fullrange, eval_safe
from ...pylib.securite import dictionnaire_builtins
from ...mathlib import end_user_functions
from ...mathlib.parsers import traduire_formule


class SurfacesMenuBar(MenuBar):
    def __init__(self, panel):
        MenuBar.__init__(self, panel)

        self.ajouter(u"Fichier", [u"exporter"], [u"presse-papier"], [u"quitter"])
        self.ajouter(u"Affichage", [u"onglet"])#, ["repere"], ["quadrillage"], ["orthonorme"], ["fenetre"], ["zoomer"], ["dezoomer"], ["orthonormaliser"], [u"zoom_auto"])
        self.ajouter(u"Outils", [u"debug"], [u"options"])
        self.ajouter(u"?")



class MyAxes3D(Axes3D):
    def draw(self, renderer):
        # draw the background patch
        self.axesPatch.draw(renderer)
        self._frameon = False

        # add the projection matrix to the renderer
        self.M = self.get_proj()
        renderer.M = self.M
        renderer.vvec = self.vvec
        renderer.eye = self.eye
        renderer.get_axis_position = self.get_axis_position

        # Calculate projection of collections and zorder them
        zlist = [(col.do_3d_projection(renderer), col) \
                for col in self.collections]
        zlist.sort(reverse=True)
        for i, (z, col) in enumerate(zlist):
            col.zorder = getattr(col, '_force_zorder', i)


        # Calculate projection of patches and zorder them
        zlist = [(patch.do_3d_projection(renderer), patch) \
                for patch in self.patches]
        zlist.sort(reverse=True)
        for i, (z, patch) in enumerate(zlist):
            patch.zorder = i

        self.w_xaxis.draw(renderer)
        self.w_yaxis.draw(renderer)
        self.w_zaxis.draw(renderer)
        Axes.draw(self, renderer)



class Surfaces(Panel_API_graphique):

    __titre__ = u"Surfaces" # Donner un titre a chaque module

    def __init__(self, *args, **kw):
        Panel_API_graphique.__init__(self, *args, **kw)

        self.canvas.fixe = True

        #self.couleurs = u"bgrmkcy"
#        self.couleurs = [(0, 1, 0), (.5, .5, 0), (1, 0, 0),
#                         (.5, 0, .5), (0, 0, 1), (0, .5, .5)]
        self.couleurs = [
[0.0, 0.0, 0.5],
#[0.0, 0.0, 0.68939393939393945],
#[0.0, 0.0, 0.87878787878787878],
#[0.0, 0.0, 1.0],
#[0.0, 0.16666666666666663, 1.0],
[0.0, 0.33333333333333326, 1.0],
#[0.0, 0.5, 1.0],
#[0.0, 0.66666666666666652, 1.0],
[0.0, 0.83333333333333326, 1.0],
[0.080645161290322731, 1.0, 0.88709677419354827],
#[0.21505376344086025, 1.0, 0.75268817204301075],
#[0.34946236559139776, 1.0, 0.61827956989247301],
[0.4838709677419355, 1.0, 0.48387096774193528],
#[0.61827956989247301, 1.0, 0.34946236559139776],
#[0.75268817204301053, 1.0, 0.21505376344086025],
[0.88709677419354827, 1.0, 0.080645161290322509],
#[1.0, 0.90123456790123502, 0.0],
[1.0, 0.82, 0.0],
#[1.0, 0.74691358024691423, 0.0],
[1.0, 0.59259259259259256, 0.0],
#[1.0, 0.43827160493827177, 0.0],
[1.0, 0.28395061728395099, 0.0],
#[1.0, 0.12962962962962976, 0.0],
[0.8787878787878789, 0.0, 0.0],
[0.68939393939393945, 0.0, 0.0],
[0.5, 0, 0],
]
        self._Z = None

        self.entrees = wx.BoxSizer(wx.VERTICAL)


        box = wx.StaticBox(self, -1, u"Equation")
        ligne = wx.StaticBoxSizer(box, wx.HORIZONTAL)
        ligne.Add(wx.StaticText(self, -1, "Z = "), 0, wx.ALIGN_CENTRE|wx.ALL,5)
        self.equation = wx.TextCtrl(self, size = (160, -1), style=wx.TE_PROCESS_ENTER)
        self.equation.Bind(wx.EVT_CHAR, self.EvtChar)
        ligne.Add(self.equation, 0, wx.ALIGN_CENTRE|wx.ALL,5)
        self.entrees.Add(ligne, 0, wx.ALL, 5)

        box = wx.StaticBox(self, -1, u"Abscisse")
        liste = wx.StaticBoxSizer(box, wx.VERTICAL)

        ligne = wx.BoxSizer(wx.HORIZONTAL)
        ligne.Add(wx.StaticText(self, -1, "Xmin"), 0, wx.ALIGN_CENTRE|wx.ALL,5)
        self.xmin = wx.TextCtrl(self, value = "-5", size = (160, -1), style=wx.TE_PROCESS_ENTER)
        self.xmin.Bind(wx.EVT_CHAR, self.EvtChar)
        ligne.Add(self.xmin, 0, wx.ALIGN_CENTRE|wx.ALL,5)
        liste.Add(ligne, 0, wx.ALL, 5)

        ligne = wx.BoxSizer(wx.HORIZONTAL)
        ligne.Add(wx.StaticText(self, -1, u"Xmax"), 0, wx.ALIGN_CENTRE|wx.ALL,5)
        self.xmax = wx.TextCtrl(self, value = "5", size = (160, -1), style=wx.TE_PROCESS_ENTER)
        self.xmax.Bind(wx.EVT_CHAR, self.EvtChar)
        ligne.Add(self.xmax, 0, wx.ALIGN_CENTRE|wx.ALL,5)
        liste.Add(ligne, 0, wx.ALL, 5)

        ligne = wx.BoxSizer(wx.HORIZONTAL)
        ligne.Add(wx.StaticText(self, -1, u"Pas"), 0, wx.ALIGN_CENTRE|wx.ALL,5)
        self.pasX = wx.TextCtrl(self, value = "", size = (160, -1), style=wx.TE_PROCESS_ENTER)
        self.pasX.Bind(wx.EVT_CHAR, self.EvtChar)
        ligne.Add(self.pasX, 0, wx.ALIGN_CENTRE|wx.ALL,5)
        liste.Add(ligne, 0, wx.ALL, 5)

        self.entrees.Add(liste, 0, wx.ALL, 5)

        box = wx.StaticBox(self, -1, u"Ordonnée")
        liste = wx.StaticBoxSizer(box, wx.VERTICAL)

        ligne = wx.BoxSizer(wx.HORIZONTAL)
        ligne.Add(wx.StaticText(self, -1, u"Ymin"), 0, wx.ALIGN_CENTRE|wx.ALL,5)
        self.ymin = wx.TextCtrl(self, value = "-5", size = (160, -1), style=wx.TE_PROCESS_ENTER)
        self.ymin.Bind(wx.EVT_CHAR, self.EvtChar)
        ligne.Add(self.ymin, 0, wx.ALIGN_CENTRE|wx.ALL,5)
        liste.Add(ligne, 0, wx.ALL, 5)

        ligne = wx.BoxSizer(wx.HORIZONTAL)
        ligne.Add(wx.StaticText(self, -1, u"Ymax"), 0, wx.ALIGN_CENTRE|wx.ALL,5)
        self.ymax = wx.TextCtrl(self, value = "5", size = (160, -1), style=wx.TE_PROCESS_ENTER)
        self.ymax.Bind(wx.EVT_CHAR, self.EvtChar)
        ligne.Add(self.ymax, 0, wx.ALIGN_CENTRE|wx.ALL,5)
        liste.Add(ligne, 0, wx.ALL, 5)

        ligne = wx.BoxSizer(wx.HORIZONTAL)
        ligne.Add(wx.StaticText(self, -1, u"Pas"), 0, wx.ALIGN_CENTRE|wx.ALL,5)
        self.pasY = wx.TextCtrl(self, value = "", size = (160, -1), style=wx.TE_PROCESS_ENTER)
        self.pasY.Bind(wx.EVT_CHAR, self.EvtChar)
        ligne.Add(self.pasY, 0, wx.ALIGN_CENTRE|wx.ALL,5)
        liste.Add(ligne, 0, wx.ALL, 5)

        self.entrees.Add(liste, 0, wx.ALL, 5)

        box = wx.StaticBox(self, -1, u"Seuils")
        liste = wx.StaticBoxSizer(box, wx.VERTICAL)

        ligne = wx.BoxSizer(wx.HORIZONTAL)
#        ligne.Add(wx.StaticText(self, -1, u"Pas"), 0, wx.ALIGN_CENTRE|wx.ALL,5)
        self.seuils = wx.TextCtrl(self, size = (160, -1), style=wx.TE_PROCESS_ENTER)
        self.seuils.Bind(wx.EVT_CHAR, self.EvtChar)
        ligne.Add(self.seuils, 0, wx.ALIGN_CENTRE|wx.ALL,5)
        liste.Add(ligne, 0, wx.ALL, 5)
#        liste.Add(wx.StaticText(self, -1, u"Exemple : 0.2 (évitez des valeurs trop faibles)."), 0, wx.ALL, 5)

        self.entrees.Add(liste, 0, wx.ALL, 5)


        #self.dessiner = wx.Button(self, wx.ID_REFRESH)
        #self.entrees.Add(self.dessiner, 0, wx.ALL, 5)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.sizer.Add(self.entrees, 0, wx.ALL, 5)
        self.SetSizer(self.sizer)
        self.Fit()
        self.ax3d = MyAxes3D(self.canvas.figure)
        self.plt = self.canvas.figure.axes.append(self.ax3d)
        self.initialisation_terminee = True







    def _sauvegarder(self, fgeo, feuille=None):
        Panel_API_graphique._sauvegarder(self, fgeo, feuille)
        # TODO: implémenter sauvegarde
        return
        fgeo.contenu[u"Courbe"] = [{"Y" : [self.equations[i].GetValue()], u"intervalle" : [self.intervalles[i].GetValue()], u"active" : [str(self.boites[i].GetValue())]} for i in range(self.nombre_courbes)]


    def _ouvrir(self, fgeo):
        Panel_API_graphique._ouvrir(self, fgeo)
        # TODO: implémenter sauvegarde
        return
        if fgeo.contenu.has_key(u"Courbe"):
            for i in range(min(len(fgeo.contenu[u"Courbe"]), self.nombre_courbes)):
                self.equations[i].SetValue(fgeo.contenu[u"Courbe"][i][u"Y"][0])
                self.intervalles[i].SetValue(fgeo.contenu[u"Courbe"][i][u"intervalle"][0])
                self.boites[i].SetValue(fgeo.contenu[u"Courbe"][i][u"active"][0] == u"True")
        self.affiche()



    def EvtChar(self, event):
        code = event.GetKeyCode()

        if code == 13:
            self.affiche()
        else:
            event.Skip()




    def _affiche(self):
#            if not hasattr(self, "initialisation_terminee"):
#                return
        if not self.equation.GetValue().strip():
            return
        xmin = eval_safe(self.xmin.GetValue().strip())
        xmax = eval_safe(self.xmax.GetValue().strip())
        ymin = eval_safe(self.ymin.GetValue().strip())
        ymax = eval_safe(self.ymax.GetValue().strip())

        pasX = self.pasX.GetValue().strip()
        if not pasX:
            pasX = self._param_.resolution*(xmax - xmin)
        else:
            pasX = eval_safe(pasX)
        if pasX < self._param_.resolution_minimale*max(xmax - xmin, ymax - ymin):
            pasX = self._param_.resolution_minimale*max(xmax - xmin, ymax - ymin)
            self.canvas.message(u"Attention, le pas est trop petit !")
        pasY = self.pasY.GetValue().strip()
        if not pasY:
            pasY = self._param_.resolution*(xmax - xmin)
        else:
            pasY = eval_safe(pasY)
        if pasY < self._param_.resolution_minimale*max(xmax - xmin, ymax - ymin):
            pasY = self._param_.resolution_minimale*max(xmax - xmin, ymax - ymin)
            self.canvas.message(u"Attention, le pas est trop petit !")
        with BusyCursor():
            X = fullrange(xmin, xmax, pasX)
            Y = fullrange(ymin, ymax, pasY)
            X, Y = meshgrid(X, Y)
            dico = vars(end_user_functions).copy()
            dico.update({'x': X, 'X': X, 'Y': Y, 'y': Y})
            dico.update(dictionnaire_builtins)
            formule = traduire_formule(self.equation.GetValue(), dico)
            self._Z = Z = eval(formule, dico) + 0*X # conversion des constantes en numpy.ndarray

            seuils_txt = self.seuils.GetValue().strip()
            if seuils_txt:
                # On récupère et on classe les valeurs
                seuils = sorted(float(seuil) for seuil in seuils_txt.split(' '))
                cmap = self._creer_cmap(seuils)
            else:
                cmap = cm.jet

            self.ax3d.clear()
            self.polyc = self.ax3d.plot_surface(X, Y, Z, rstride = 1, cstride = 1, cmap = cmap)
            self.polyc.set_linewidth(self._param_.epaisseur_grillage)
            return
            if seuils_txt:
                # linestyles = 'dotted'
                self.cs = self.ax3d.contour(X, Y, Z, cmap = cmap, levels = seuils, linewidths = 2*self._param_.epaisseur_grillage + 1)
                for collection in self.cs.collections:
                    collection._force_zorder = 100


    def _creer_cmap(self, seuils):
        zmax = nmax(self._Z)
        zmin = nmin(self._Z)
        delta = zmax - zmin
        # On les ramène entre 0 et 1 par transformation affine
        if delta:
            a = 1/delta
            b = -zmin/delta
        seuils = [0] + [a*z + b for z in seuils if zmin < z < zmax] + [1] # NB: < et pas <=
        print seuils
        cdict = {'red': [], 'green': [], 'blue': []}
        def add_col(val, color1, color2):
            cdict['red'].append((val, color1[0], color2[0]))
            cdict['green'].append((val, color1[1], color2[1]))
            cdict['blue'].append((val, color1[2], color2[2]))

        n = len(self.couleurs)
        for i, seuil in enumerate(seuils):
            add_col(seuil, self.couleurs[(i - 1)%n], self.couleurs[i%n])
        return LinearSegmentedColormap('seuils', cdict, 256)





def _colors_from_cmap(cmap, n):
    "Retourne 'n' couleurs régulièrement espacées de cmap."
    cdict = cmap._segmentdata
    vals = fullrange(0, 1, 1/(n - 1))
    l = []
    for val in vals:
        l.append([])
        for c in ('red', 'green', 'blue'):
            gradient = cdict[c]
            for i, triplet in enumerate(gradient):
                if triplet[0] > val:
                    val0, tmp, x0 = gradient[i - 1]
                    val1, x1, tmp = triplet
                    a = (x1 - x0)/(val1 - val0)
                    b = x0 - a*val0
                    x = a*val + b
                    l[-1].append(x)
                    break
            else:
                l[-1].append(gradient[-1][1])
    return l

# code pour générer la liste de couleur de la méthode __init__
# print '\n'.join(repr(i) + ',' for i in _colors_from_cmap(cm.jet,25))
