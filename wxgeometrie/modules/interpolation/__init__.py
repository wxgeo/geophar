# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

#    :--------------------------------------------:
#    :                  Interpolation - EN TEST   :
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
#import re
import wx

import os as os
import string as string
import math as math
import fractions as frac
from numpy import poly1d, arange
from scipy.interpolate import KroghInterpolator, PiecewisePolynomial
from pylab import plot, show, grid, ylim, xlim, arrow
import re as re

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


class Traceur(Panel_API_graphique):

    __titre__ = u"Interpolation de degré 1" # Donner un titre a chaque module

    def __init__(self, *args, **kw):
        Panel_API_graphique.__init__(self, *args, **kw)

        self.couleurs = u"bgrmkcy"

        self.nombre_courbes = self._param_.nombre_courbes
        self.boites = []
        self.equations = []
        self.intervalles = []

        self.entrees = wx.BoxSizer(wx.VERTICAL)
        self.entrees.Add(wx.StaticText(self, -1, u" Equations :"), 0, wx.ALL,5)

        ligne = wx.BoxSizer(wx.HORIZONTAL)
        ligne.Add(wx.StaticText(self, -1, "Liste des valeurs en x"), 0, wx.ALIGN_CENTRE|wx.ALL,5)
        ligne.Add(wx.StaticText(self, -1, "Liste des valeurs en y"), 0, wx.ALIGN_CENTRE|wx.ALL,5)
        self.entrees.Add(ligne, 0, wx.ALL, 5)
        ligne.Add(wx.StaticText(self, -1, "Liste des nombres dérivés"), 0, wx.ALIGN_CENTRE|wx.ALL,5)
        self.entrees.Add(ligne, 0, wx.ALL, 5)
        ligne.Add(self.equations[i], 0, wx.ALIGN_CENTRE|wx.ALL,5)
#         for i in range(self.nombre_courbes):
#                 ligne = wx.BoxSizer(wx.HORIZONTAL)
# 
#                 self.boites.append(wx.CheckBox(self, label='f%s:'%(i+1)))
#                 self.boites[-1].SetValue(True) # Par defaut, les cases sont cochees.
#                 self.boites[i].Bind(wx.EVT_CHECKBOX, self.synchronise_et_affiche)
#                 # Bug de WxGtk: on ne peut pas attacher simultanément une fonction
#                 # aux évènements EVT_CHECKBOX et EVT_ENTER_WINDOW
#                 #self.boites[i].Bind(wx.EVT_ENTER_WINDOW, partial(self.MouseOver, i=i))
#                 self.boites[i].Bind(wx.EVT_LEAVE_WINDOW, self.MouseOver)
#                 ligne.Add(self.boites[i], 0, wx.ALIGN_CENTRE|wx.ALL,5)
# 
#                 ligne.Add(wx.StaticText(self, -1, "Y ="), 0, wx.ALIGN_CENTRE|wx.ALL,5)
#                 self.equations.append(wx.TextCtrl(self, size=(120, -1), style=wx.TE_PROCESS_ENTER))
#                 self.equations[i].Bind(wx.EVT_CHAR, partial(self.EvtChar, i=i))
#                 self.equations[i].Bind(wx.EVT_ENTER_WINDOW, partial(self.MouseOver, i=i))
#                 self.equations[i].Bind(wx.EVT_LEAVE_WINDOW, self.MouseOver)
#                 ligne.Add(self.equations[i], 0, wx.ALIGN_CENTRE|wx.ALL,5)
# 
#                 ligne.Add(wx.StaticText(self, -1, "sur"), 0, wx.ALIGN_CENTRE|wx.ALL,5)
#                 self.intervalles.append(wx.TextCtrl(self, size = (100, -1), style = wx.TE_PROCESS_ENTER))
#                 self.intervalles[i].Bind(wx.EVT_CHAR, partial(self.EvtChar, i=i))
#                 self.intervalles[i].Bind(wx.EVT_ENTER_WINDOW, partial(self.MouseOver, i=i))
#                 self.intervalles[i].Bind(wx.EVT_LEAVE_WINDOW, self.MouseOver)
#                 ligne.Add(self.intervalles[i], 0, wx.ALIGN_CENTRE|wx.ALL,5)
# 
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


# fonctions d'interpolation avec contrôle de la dérivée
# pour les tracés de tangente

__doc__ = u"""
Paquet d'interpolation: 
Tracer des courbes sous contraintes de point de passage et nombre dérivé.
Tracés donnés pour Géogebra.
Fonctions de passage à Latex: équations des tangentes.
"""

def bgrid(x, y, xstep = 1, ystep = 1, *args):
    u"""
    trace une grille adaptée avec le pas défini en x et en y
    x = [xmin, xmax], y  = [ymin, ymax]
    faire bgrid([-1,1], [-1,1],1 ,1 , 'k:') 
    """
    xl = arange(x[0], x[1], xstep)
    yl = arange(y[0], y[1], ystep)
    for x1 in xl:
        plot([x1, x1], y, *args)
    for y1 in yl:
        plot(x, [y1, y1], *args)

def droite2eqn(a, b, m, name="d"):
    u"""
    renvoie l'équation réduite de la droite en LaTeX.
    les arguments sont transformés en str avant de devenir des fractions
    La droite passe par (a,b) avec coef dir m.
    """
    m_fr = frac.Fraction(str(m))
    a_fr = frac.Fraction(str(a))
    b_fr = frac.Fraction(str(b))
    ord_orig_fr = -1*m_fr*a_fr+b_fr
    # pour b_fr <0, mettre des parenthèses
    if b_fr<0:
        add_cst1 = "("+frac2tex(b_fr)+")"
    else:
        add_cst1 = frac2tex(b_fr)
    out = name+u":y="+frac2tex(m_fr)+u"\\left( x - "+frac2tex(a_fr) + u"\\right) + "+add_cst1
    out += u"\\text{ qui donne }"
    out += name+":y="+frac2tex(m_fr)+"x"+addsimplif(ord_orig_fr)
    return out

def addsimplif(f):
    u"""
    renvoie le bon signe + ou - suivi de la fraction
    @type f: frac.Fraction

    @return: string
    """
    if (f.numerator<0) and (f.denominator==1):
        return str(f.numerator)
    elif (f.numerator<0):
        return ' - '+frac2tex(-1*f)
    else:
        return ' + '+frac2tex(f)

def frac2tex(f):
    u"""
    sortie latex d'une fraction
    """
    if f.denominator == 1:
        return str(f.numerator)
    else:
        return u'\\frac{'+str(f.numerator)+'}{'+str(f.denominator)+'}'
    

def poly2string(p):
    u"""
    return a string definition of polynome p
    printable in latex or geogebra.
    succesion of +- simplified at end

    @type p: numpy.lib.polynomial.poly1d
    @param p: a polynome

    @return a string definition of p
    """
    s = ''
    c = list(p.coeffs)
    n= p.order
    for i in range(n):
        # attention il manquera le dernier coef
        s+=str(c[i])+'*x^'+str(n-i)+'+'
    s+=str(c[-1])
    return re.sub('\+\-', '-', s)
        
def fct2xml(expr, name="f"):
    phrase = '<expression label ="'+name+'" exp="'+name+'(x) ='+expr+'"/>'
    elem = '<element type="function" label="'+name+'">\
	<lineStyle thickness="2" type="0"/>\
	<show object="true" label="true"/>\
	<objColor r="0" g="0" b="0" alpha="0.0"/>\
	<layer val="0"/>\
	<labelMode val="0"/>\
	<animation step="0.1" speed="1" type="0" playing="false"/>\
	<lineStyle thickness="2" type="0"/>\
</element>'
    return phrase+elem

def droitexml(a, b , m, name="d"):
    u"""
    renvoie l'élément xml ggb d'une droite
    y=m(x-a)+b 
    -mx +y +(ma-b) = 0
    """
    m_fr = frac.Fraction(str(m))
    a_fr = frac.Fraction(str(a))
    b_fr = frac.Fraction(str(b))
    return '<element type="line" label="'+name+'">\
	<lineStyle thickness="2" type="0"/>\
	<show object="true" label="true"/>\
	<objColor r="0" g="0" b="0" alpha="0.0"/>\
	<layer val="0"/>\
	<labelMode val="0"/>\
	<animation step="0.1" speed="1" type="0" playing="false"/>\
	<coords x="'+str(float(-1.0*m_fr))+'" y="'+str(1.0)+'" z="'+str(float(m_fr*a_fr-b_fr))+'"/>\
	<lineStyle thickness="2" type="0"/>\
	<eqnStyle style="explicit"/>\
     </element>'
    #return str(m)+"*(x-"+str(x)+")+"+str(y)

def pointxml(self, x, y, name="A", print_name=False):
    u"""
    renvoie l'élément xml ggb d'un point.
    Par défaut, le nom n'est pas affiché
    """
    return '<element type="point" label="'+name+'">\
	<show object="true" label="'+str(print_name).lower()+'"/>\
	<objColor r="0" g="0" b="255" alpha="0.0"/>\
	<layer val="0"/>\
	<labelMode val="0"/>\
	<animation step="0.1" speed="1.0" type="0" playing="false"/>\
	<coords x="'+str(float(x))+'" y="'+str(float(y))+'" z="1.0"/>\
	<pointSize val="3"/>\
</element>'


def poly2ggb(p, xl, yl, deriv , nom = "sortie", fname ="f" , tangentes = True):
    u"""
    build the geogebra output of a polynom.
    by default, tangents are built.
    
    @type p: numpy.lib.polynomial.poly1d
    @param p: a polynome
    @type nom: string
    @param nom: name of the output file
    @type fname : string
    @param fname: name of the function in ggb. 
    @type tangentes: boolean
    @param tangentes: chose to plot the tangentes or not
    
    @return None
    """
    out_file = open(nom+"1.xml", "w")
    intro = '<?xml version="1.0" encoding="utf-8"?>\
    <geogebra format="3.2">\
    <gui>\
    	<show algebraView="true" spreadsheetView="false" auxiliaryObjects="false" algebraInput="true" cmdList="true"/>\
    	<splitDivider loc="650" locVertical="400" loc2="250" locVertical2="300" horizontal="true"/>\
    	<font  size="12"/>\
    </gui>\
    <euclidianView>\
    	<size  width="633" height="513"/>\
    	<coordSystem xZero="215.0" yZero="315.0" scale="50.0" yscale="50.0"/>\
    	<evSettings axes="true" grid="false" gridIsBold="false" pointCapturing="3" pointStyle="0" rightAngleStyle="1" checkboxSize="13" gridType="0"/>\
    	<bgColor r="255" g="255" b="255"/>\
    	<axesColor r="0" g="0" b="0"/>\
    	<gridColor r="192" g="192" b="192"/>\
    	<lineStyle axes="1" grid="10"/>\
    	<axis id="0" show="true" label="" unitLabel="" tickStyle="1" showNumbers="true"/>\
    	<axis id="1" show="true" label="" unitLabel="" tickStyle="1" showNumbers="true"/>\
    </euclidianView>\
    <kernel>\
    	<continuous val="false"/>\
    	<decimals val="2"/>\
    	<angleUnit val="degree"/>\
    	<algebraStyle val="0"/>\
    	<coordStyle val="0"/>\
    </kernel>\
    <construction title="" author="" date="">'
    out_file.write(intro)
    expr = poly2string(p)
    out_file.write(fct2xml(expr, name=fname))
    if tangentes:
        for i in range(len(xl)):
            d_name = "d_"+str(i+1)
            expr = droitexml(xl[i], yl[i], deriv[i], d_name)
            out_file.write(expr)
            point = pointxml(xl[i], yl[i], name="A_"+str(i+1))
            out_file.write(point)
    out_file.write("</construction></geogebra>")
    out_file.close()
    
    cmd = "xmllint --format "+nom+"1.xml> geogebra.xml"
    os.system(cmd)
    os.system("rm "+nom+"1.xml")
    os.system("zip -r "+nom+".ggb geogebra.xml")
    os.system("rm geogebra.xml")


class interpol1():
    u"""
    Classe d'interpolation. Elle contient la liste des x, y et nombre dérivé ain\
    si que la fonction d'interpolation.
    @param self.interpol: La fonction d'interpolation
    @type self.interpol: numpy.lib.polynomial
    @param self.tangentes: liste des droites tangentes
    @type self.tangentes: list of numpy.lib.polynomial
    """
    
    def __init__(self, xl = [], yl = [], derivl = []):
        self.xl = xl
        self.yl = yl
        self.derivl = [frac.Fraction(x) for x in derivl]
        self.tangentes = []
        self.interpol = self.poly_inter(xl, yl, derivl)
        for i in range(len(xl)):
            self.tangentes.append(poly1d([derivl[i], -1*derivl[i]*xl[i]+yl[i]]))


    def __call__(self, t):
        u"""
        calcule l'image de t par la fonction d'interpolation.
        @type t: float or array of float etc..
        """
        return self.interpol(t)


    def poly_inter(self, xl, yl, derivl):
        u"""
        create the interpolation function: passing through points of (xl, yl)
        and with derivate in derivl at xl abscisses.
        
        @type xl: list
        @param xl: abscisses list
        @type yl: list
        @param yl: ord list
        @type derivl: list
        @param derivl: value of the derivate at each point
        
        @return : numpy.lib.polynomial
        """
        # two lists of polynoms: the Lagrange interpolation ones
        # and the local construction ones before product
        inter = []
        local = []
        for x in xl:
            i = xl.index(x)
            yi, di = yl[i], derivl[i]
            xl.remove(x)
            # poly1d True: for definition by roots
            # squared for transparency up to derivation
            p = poly1d(xl, True)**2
            p_der = p.deriv()
            inter.append(p)
            li = p_der(float(x))/p(float(x))
            gi = di - yi * li
            # compute the local fun. coef made to match the interpolation
            local.append(poly1d([gi, yi - gi * x]))
            # reverse xl to its initial value
            xl.insert(i, x)
        f = [local[i] * inter[i] / inter[i](float(xl[i]))  for i in range(len(xl))]
        return sum(f)


    def list_tangentes(self):
        u"""
        renvoie la liste des équations réduites des tangentes au format tex

        @return: string
        """
        out = u''
        for i in range(len(self.xl)):
            out += "$"+droite2eqn(self.xl[i], self.yl[i], self.derivl[i], name="d_"+str(i+1))+"$\\\\"
            out += '\n'
        return out

    def plot_all(self, color='b', xstep = 0.5, ystep = 0.5, plain_tan=False):
        u"""
        Trace la fonction ainsi que les tangentes (droites ou flèches).
        @param color: couleur des tangentes
        @type color: char
        @param xstep: le pas de la grille en x
        @type xstep: float
        @param ystep: le pas de la grille en y
        @type ystep: float
        @param plain_tan: détermine si on trace des droites (True) ou des \ 
        flèches (False) pour les tangentes.
        @type plain_tan: boolean
        @return: None
        """
        num_points = 200
        delta_x = self.xl[-1] - self.xl[0]
        my = min(self.yl)
        My = max(self.yl)
        delta_y = My - my
        x_bound = [ self.xl[0]-0.3*delta_x,  self.xl[-1]+0.3*delta_x]
        y_bound = [my-0.1*delta_y, My+0.1*delta_y]
        t = arange(self.xl[0]-0.3*delta_x, self.xl[-1]+0.3*delta_x, 1.6*delta_x/num_points)
        #courbe
        plot(t, self.interpol(t), color)
        #points de passage
        for i in range(len(self.xl)):
            plot(self.xl[i], self.yl[i], 'go')
        #tangentes
        if plain_tan: # droites completes
            for d in self.tangentes:
                plot(t, d(t),'k')
        else:
        #juste des fleches - A AMELIORER
            arrow_params = {'head_width': 0.1, 'head_starts_at_zero':True, 'shape': 'full'}
            for i in range(len(self.xl)):
                arrow(self.xl[i], self.yl[i], xstep*self.derivl[i].denominator*1.1,\
                          ystep*self.derivl[i].numerator*1.1, **arrow_params)
                arrow(self.xl[i], self.yl[i], -xstep*self.derivl[i].denominator*1.1,\
                          -ystep*self.derivl[i].numerator*1.1, **arrow_params)
        #grille
        bgrid([ math.floor(x_bound[0]/ xstep) * xstep, x_bound[1]], [math.floor(y_bound[0]/ystep)*ystep, y_bound[1]],\
                    xstep, ystep, 'k:')
        xlim(tuple(x_bound))
        ylim(tuple(y_bound))
        show()
       
       
class interpol1Krogh(interpol1):
    u"""
    utilise l'interpolation de scipy pour construire la fonction
    c'est la classe scipy.interpolate.KroghInterpolator
    même résultat que la classe de base.
    """
    def poly_inter(self, xl, yl, derivl):
        # doubler les x dans la liste
        xl_cum = reduce((lambda x,y:x+y), [[i,i] for i in xl])
        yl_cum = reduce((lambda x,y:x+y), [[yl[i], derivl[i]] for i in range(len(yl))])
        return KroghInterpolator(xl_cum, yl_cum)


class interpol1Piecewise(interpol1):
    u"""
    utilise l'interpolation par morceau de scipy pour construire la fonction
    c'est la classe scipy.interpolate.PiecewisePolynomial
    """
    def poly_inter(self, xl, yl, derivl):
        yl_cum = [[yl[i], derivl[i]] for i in range(len(yl))]
        return PiecewisePolynomial(xl, yl_cum)


# Example
# from binterpolation import *
# #%figure 2
# x=[0,2,4]
# y=[-2,3,1]
# d=[frac.Fraction(2,3),frac.Fraction(1,2), -2]
# p = poly_inter(x,y,d)
# name="interpol2"
# f=open(name+".tex","w")
# for i in range(len(x)):
#     f.write(droite2eqn(x[i],y[i],d[i], name="d_"+str(i)))
#     f.write('\n')
# f.close()
# poly2ggb(p, x, y, d, nom=name, fname="f", tangentes = True)

#   import os as os
#   from binterpolation import *
#   x=[0,2,4]
#   y=[-2,3,1]
#   d=[frac.Fraction(2,3),frac.Fraction(1,2), -2]
#   p = interpol1(x,y,d)
#   print(p.list_tangentes())
#   name="interpol2"
#   f=open(name+".tex","w")
#   f.write(p.list_tangentes())
#   f.close()
#   poly2ggb(p.interpol, p.xl, p.yl, p.derivl, nom=name, fname="f", tangentes = True)

# import fractions as frac
# import math as math
# from binterpolation import *
# x=[0,2,4]
# y=[-2,3,1]
# d=[frac.Fraction(2,3),frac.Fraction(1,2), -2]
# p1 = interpol1(x,y,d)
# p2 = interpol1Piecewise(x,y,d)

# x=[-3,0,2,4,5]
# y=[-2, frac.Fraction(-3,2),1,frac.Fraction(-5,2), 3]
# d=[frac.Fraction(2,3),frac.Fraction(-2,5), frac.Fraction(1,2), -1, -2]
# p1 = interpol1(x,y,d)
# p2 = interpol1Piecewise(x,y,d)
# p1.plot_all()
