# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)
from __future__ import with_statement

##--------------------------------------#######
#                 Fenetres                              #
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

from PyQt4.QtGui import QWidget, QTabWidget

import wx
from  wx.lib.colourselect import EVT_COLOURSELECT, ColourSelect
from matplotlib.colors import colorConverter as colorConverter


from .wxlib import MyMiniFrame
from .. import param
from ..pylib import print_error, debug, advanced_split
from ..geolib.constantes import NOM, FORMULE, TEXTE, RIEN
from ..geolib.routines import nice_display

class ProprietesAffichage(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.parent = parent
        self.panel = self.parent.parent.panel
        self.canvas = self.panel.canvas
        self.islabel = self.parent.parent.islabel
        self.objets = parent.objets
        self.sizer = QVBoxLayout()

        self.changements = {} # ce dictionnaire contiendra tous les styles modifiés
        encadre = wx.StaticBoxSizer(QGroupBox(self, -1, u"Mode d'affichage"), wx.HORIZONTAL)

        if not self.islabel:
            objets = [objet for objet in self.objets if objet.style("fixe") is not None]
            if objets:
                cb1 = QCheckBox(self, -1, u"Objet fixe", style = wx.CHK_3STATE)
                cb1.Bind(wx.EVT_CHECKBOX, self.EvtFixe)
                encadre.Add(cb1)
                fixe = [objet.style("fixe") is True for objet in objets]
                if not any(fixe):
                    etat = wx.CHK_UNCHECKED
                elif all(fixe):
                    etat = wx.CHK_CHECKED
                else:
                    etat = wx.CHK_UNDETERMINED
                cb1.Set3StateValue(etat)



            objets = [objet for objet in self.objets if objet.style("visible") is not None]
            if objets:
                cb2 = QCheckBox(self, -1, u"Objet visible", style = wx.CHK_3STATE)
                cb2.Bind(wx.EVT_CHECKBOX, self.EvtVisible)
                encadre.Add(cb2)
                visible = [objet.style("visible") is True for objet in objets]
                if not any(visible):
                    etat = wx.CHK_UNCHECKED
                elif all(visible):
                    etat = wx.CHK_CHECKED
                else:
                    etat = wx.CHK_UNDETERMINED
                cb2.Set3StateValue(etat)


            objets = [objet for objet in self.objets if objet.style("trace") is not None]
            if objets:
                cb3 = QCheckBox(self, -1, u"Laisser une trace", style = wx.CHK_3STATE)
                cb3.Bind(wx.EVT_CHECKBOX, self.EvtTrace)
                encadre.Add(cb3)
                trace = [objet.style("trace") is True for objet in objets]
                if not any(trace):
                    etat = wx.CHK_UNCHECKED
                elif all(trace):
                    etat = wx.CHK_CHECKED
                else:
                    etat = wx.CHK_UNDETERMINED
                cb3.Set3StateValue(etat)


        encadre1 = wx.StaticBoxSizer(QGroupBox(self, -1, u"Etiquette"), wx.VERTICAL)
        if not self.islabel:
            ligne = QHBoxLayout()
            if len(self.objets) == 1:
                etiquette = wx.TextCtrl(self, value = self.objets[0].style("label"), size=wx.Size(200, -1))
                self.Bind(wx.EVT_TEXT, self.EvtEtiquette, etiquette)
                ligne.Add(etiquette)
            if [objet for objet in self.objets if objet.etiquette is not None]:
                editer = QPushButton(self, label = u"Style")
                editer.Bind(wx.EVT_BUTTON, self.EvtLabelStyle)
                ligne.Add(editer)
            encadre1.Add(ligne)

            objets = [objet for objet in self.objets if objet.style("legende") is not None]
            if objets:
                leg = objets[0].style("legende")
                legende = QHBoxLayout()
                self.radio_nom = wx.RadioButton(self, -1, "Nom", style = wx.RB_GROUP)
                self.radio_nom.SetValue(0)
                self.radio_etiquette = wx.RadioButton(self, -1, u"Texte")
                self.radio_etiquette.SetValue(0)
                self.radio_formule = wx.RadioButton(self, -1, u"Formule")
                self.radio_formule.SetValue(0)
                self.radio_aucun = wx.RadioButton(self, -1, u"Aucun")
                self.radio_aucun.SetValue(0)
                if all(objet.style("legende") == leg for objet in objets):
                    if leg == NOM:
                        self.radio_nom.SetValue(1)
                    elif leg == TEXTE:
                        self.radio_etiquette.SetValue(1)
                    elif leg == FORMULE:
                        self.radio_formule.SetValue(1)
                    elif leg == RIEN:
                        self.radio_aucun.SetValue(1)

                self.Bind(wx.EVT_RADIOBUTTON, self.EvtLegende, self.radio_nom)
                self.Bind(wx.EVT_RADIOBUTTON, self.EvtLegende, self.radio_etiquette)
                self.Bind(wx.EVT_RADIOBUTTON, self.EvtLegende, self.radio_formule)
                self.Bind(wx.EVT_RADIOBUTTON, self.EvtLegende, self.radio_aucun)
                legende.Add(self.radio_nom)
                legende.Add(self.radio_etiquette)
                legende.Add(self.radio_formule)
                legende.Add(self.radio_aucun)
                encadre1.Add(QLabel(self, u"Afficher : "), 0, wx.ALL,5)
                encadre1.Add(legende)




        encadre2 = wx.StaticBoxSizer(QGroupBox(self, -1, u"Styles"), wx.VERTICAL)


        objets = [objet for objet in self.objets if objet.style("style") is not None]
        # on ne peut regler les styles simultanement que pour des objets de meme categorie
        categorie = objets and objets[0].style("categorie") or None


        if objets and categorie and all(objet.style("categorie") == categorie for objet in objets):
            choix = QHBoxLayout()
            choix.Add(QLabel(self, u"Style de l'objet : "), 0, wx.ALL,5)

            #categorie = objets[0].style("categorie") or "lignes"
            self.liste_styles = getattr(param, "styles_de_" + categorie, [])
            self.style = QComboBox(self, -1, (100, 50), choices = self.liste_styles)
            self.Bind(wx.EVT_CHOICE, self.EvtStyle, self.style)

            style = objets[0].style("style")
            if style in self.liste_styles and all(objet.style("style") == style for objet in objets):
                self.style.setSelection(self.liste_styles.index(style)) # on sélectionne le style actuel
            choix.Add(self.style)
            encadre2.Add(choix)


        objets = [objet for objet in self.objets if objet.style("hachures") is not None]
        if objets:
            choix = QHBoxLayout()
            choix.Add(QLabel(self, u"Style des hâchures : "), 0, wx.ALL,5)

            self.types_de_hachures = getattr(param, "types_de_hachures", [])
            self.hachures = QComboBox(self, -1, (100, 50), choices = self.types_de_hachures)
            self.Bind(wx.EVT_CHOICE, self.EvtHachures, self.hachures)

            hachures = objets[0].style("hachures")
            if hachures in self.types_de_hachures and all(objet.style("hachures") == hachures for objet in objets):
                self.hachures.setSelection(self.types_de_hachures.index(hachures)) # on sélectionne les hachures actuelles
            choix.Add(self.hachures)
            encadre2.Add(choix)


        objets = [objet for objet in self.objets if objet.style("famille") is not None]
        categorie = objets and objets[0].style("categorie") or None

        if objets and categorie and all(objet.style("categorie") == categorie for objet in objets):
            choix = QHBoxLayout()
            choix.Add(QLabel(self, "Police : "), 0, wx.ALL,5)

            #categorie = self.objet.style("categorie") or "lignes"
            self.liste_familles = getattr(param, "familles_de_" + categorie, [])
            self.famille = QComboBox(self, -1, (100, 50), choices = self.liste_familles)
            self.Bind(wx.EVT_CHOICE, self.EvtFamille, self.famille)

            famille = objets[0].style("famille")
            if famille in self.liste_familles and all(objet.style("famille") == famille for objet in objets):
                self.famille.setSelection(self.liste_familles.index(famille)) # on sélectionne la famille actuelle

            choix.Add(self.famille)
            encadre2.Add(choix)


        objets = [objet for objet in self.objets if objet.style("couleur") is not None]
        if objets:
            couleur = objets[0].style("couleur")
            choix = QHBoxLayout()
            choix.Add(QLabel(self, u"Couleur de l'objet : "), 0, wx.ALL,5)
            if all(objet.style("couleur") == couleur for objet in objets):
                couleur = colorConverter.to_rgb(couleur)
                couleur = tuple(int(255*i) for i in couleur) # conversion du format matplotlib au format wx
            else:
                couleur = self.GetBackgroundColour()
            b = ColourSelect(self, -1, colour = couleur)
            b.Bind(EVT_COLOURSELECT, self.OnSelectColour)
            choix.Add(b)
            encadre2.Add(choix)


        objets = [objet for objet in self.objets if objet.style("epaisseur") is not None]
        if objets:
            epaiss = objets[0].style("epaisseur")
            epaisseur = QHBoxLayout()
            epaisseur.Add(QLabel(self, u"Epaisseur (en 10e de pixels) : "), 0, wx.ALL,5)
            self.epaisseur = QSpinBox(self, -1, "", (30, 50))
            self.epaisseur.SetRange(1,10000)
            if all(objet.style("epaisseur") == epaiss for objet in objets):
                self.epaisseur.SetValue(10*epaiss)
            else:
                self.epaisseur.SetValueString("")
            self.Bind(wx.EVT_TEXT, self.EvtEpaisseur, self.epaisseur)
            epaisseur.Add(self.epaisseur)
            encadre2.Add(epaisseur)


        objets = [objet for objet in self.objets if objet.style("taille") is not None]
        if objets:
            tail = objets[0].style("taille")
            taille = QHBoxLayout()
            taille.Add(QLabel(self, u"Taille (en 10e de pixels) : "), 0, wx.ALL,5)
            self.taille = QSpinBox(self, -1, "", (30, 50))
            self.taille.SetRange(1,10000)
            if all(objet.style("taille") == tail for objet in objets):
                self.taille.SetValue(10*tail)
            else:
                self.taille.SetValueString("")
            self.Bind(wx.EVT_TEXT, self.EvtTaille, self.taille)
            taille.Add(self.taille)
            encadre2.Add(taille)


        objets = [objet for objet in self.objets if objet.style("position") is not None]
        if objets:
            pos = objets[0].style("position")
            position = QHBoxLayout()
            position.Add(QLabel(self, u"Position de la flêche : "), 0, wx.ALL,5)
            self.position = QSpinBox(self, -1, "", (30, 50))
            self.position.SetRange(0, 100)
            if all(objet.style("position") == pos for objet in objets):
                self.position.SetValue(100*pos)
            else:
                self.position.SetValueString("")
            self.Bind(wx.EVT_TEXT, self.EvtPosition, self.position)
            position.Add(self.position)
            encadre2.Add(position)



        objets = [objet for objet in self.objets if objet.style("angle") is not None]
        if objets:
            ang = objets[0].style("angle")
            angle = QHBoxLayout()
            angle.Add(QLabel(self, u"Angle (en degré) : "), 0, wx.ALL,5)
            self.angle = QSpinBox(self, -1, "", (30, 50))
            self.angle.SetRange(0, 360)
            if all(objet.style("angle") == ang for objet in objets):
                self.angle.SetValue(ang)
            else:
                self.angle.SetValueString("")
            self.Bind(wx.EVT_TEXT, self.EvtAngle, self.angle)
            angle.Add(self.angle)
            encadre2.Add(angle)


        objets = [objet for objet in self.objets if objet.style("double_fleche") is not None]
        if objets:
            cb4 = QCheckBox(self, -1, u"Flêche double", style = wx.CHK_3STATE)
            cb4.Bind(wx.EVT_CHECKBOX, self.EvtFlecheDouble)
            encadre.Add(cb4)
            double = [objet.style("double_fleche") is True for objet in objets]
            if not any(double):
                etat = wx.CHK_UNCHECKED
            elif all(double):
                etat = wx.CHK_CHECKED
            else:
                etat = wx.CHK_UNDETERMINED
            cb4.Set3StateValue(etat)


        objets = [objet for objet in self.objets if objet.style("codage") is not None]
        # on ne peut regler les codages simultanement que pour des objets de meme categorie
        categorie = objets and objets[0].style("categorie") or None


        if objets and categorie and all(objet.style("categorie") == categorie for objet in objets):
            choix = QHBoxLayout()
            choix.Add(QLabel(self, "Codage : "), 0, wx.ALL,5)

            #categorie = objets[0].style("categorie") or "lignes"
            self.liste_codages = getattr(param, "codage_des_" + categorie, [])
            self.codage = QComboBox(self, -1, (100, 50), choices = self.liste_codages)
            self.Bind(wx.EVT_CHOICE, self.EvtCodage, self.codage)

            codage = objets[0].style("codage")
            if codage in self.liste_codages and all(objet.style("codage") == codage for objet in objets):
                self.codage.setSelection(self.liste_codages.index(codage)) # on sélectionne le codage actuel
            choix.Add(self.codage)
            encadre2.Add(choix)




        boutons = QHBoxLayout()
        ok = QPushButton(self, wx.ID_OK)
        ok.Bind(wx.EVT_BUTTON, self.EvtOk)
        boutons.Add(ok)

        appliquer = QPushButton(self, label = u"Appliquer")
        appliquer.Bind(wx.EVT_BUTTON, self.EvtAppliquer)
        boutons.Add(appliquer)

        if not self.islabel:
            supprimer = QPushButton(self, label = u"Supprimer")
            supprimer.Bind(wx.EVT_BUTTON, self.EvtSupprimer)
            boutons.Add(supprimer)

        annuler = QPushButton(self, label = u"Annuler")
        annuler.Bind(wx.EVT_BUTTON, self.EvtAnnuler)
        boutons.Add(annuler)

        if encadre.GetChildren(): # ne pas afficher un cadre vide !
            self.sizer.addWidget(encadre)
        else:
            encadre.GetStaticBox().Destroy()
        if encadre1.GetChildren():
            self.sizer.addWidget(encadre1)
        else:
            encadre1.GetStaticBox().Destroy()
        if encadre2.GetChildren():
            self.sizer.addWidget(encadre2)
        else:
            encadre2.GetStaticBox().Destroy()
        self.sizer.addWidget(boutons)
        self.SetSizerAndFit(self.sizer)
        self.parent.parent.dim1 = self.sizer.CalcMin().Get()

    def EvtLegende(self, event):
        radio = event.GetEventObject()
        if radio is self.radio_nom:
            self.changements["legende"] = NOM
        elif radio is self.radio_etiquette:
            self.changements["legende"] = TEXTE
        elif radio is self.radio_formule:
            self.changements["legende"] = FORMULE
        else:
            self.changements["legende"] = RIEN

    def EvtFixe(self, event):
        self.changements["fixe"] = event.IsChecked()

    def EvtVisible(self, event):
        self.changements["visible"] = event.IsChecked()

    def EvtFlecheDouble(self, event):
        self.changements["double_fleche"] = event.IsChecked()

    def EvtTrace(self, event):
        self.changements["trace"] = event.IsChecked()

    def EvtEtiquette(self, event):
        self.changements["label"] = event.GetString()

    def OnSelectColour(self, event):
        couleur = tuple(i/255 for i in event.GetValue().Get()) # conversion du format wx au format matplotlib
        self.changements["couleur"] = couleur

    def EvtStyle(self, event):
        self.changements["style"] = self.liste_styles[event.GetSelection()]

    def EvtHachures(self, event):
        self.changements["hachures"] = self.types_de_hachures[event.GetSelection()]

    def EvtCodage(self, event):
        self.changements["codage"] = self.liste_codages[event.GetSelection()]

    def EvtFamille(self, event):
        self.changements["famille"] = self.liste_familles[event.GetSelection()]

    def EvtOk(self, event):
        self.EvtAppliquer(event)
        self.EvtAnnuler(event)

    def EvtAppliquer(self, event):
        with self.canvas.geler_affichage(actualiser=True, sablier=True):
            try:
                for objet in self.objets:
                    changements = self.changements.copy()
                    for key in changements.copy():
                        if objet.style(key) is None: # le style n'a pas de sens pour l'objet
                            changements.pop(key)
                    if self.islabel:
                        self.canvas.executer(u"%s.etiquette.style(**%s)" %(objet.parent.nom, changements))
                    else:
                        self.canvas.executer(u"%s.style(**%s)" %(objet.nom, changements))
            except:
                print_error()


    def EvtSupprimer(self, event):
        with self.canvas.geler_affichage(actualiser=True, sablier=True):
            for objet in self.objets:
                self.canvas.executer(u"del %s" %objet.nom)
        self.EvtAnnuler(event)

    def EvtAnnuler(self, event):
        # Ce qui suit corrige un genre de bug bizarre de wx: quand une fenêtre de sélection de couleur a été affichée, la fenêtre principale passe au second plan à la fermeture de la fenêtre de propriétés ?!? (ce qui est très désagréable dès qu'un dossier est ouvert dans l'explorateur, par exemple !)
        self.parent.parent.fenetre_principale.Raise()
        self.parent.parent.close() # fermeture de la frame

    def EvtLabelStyle(self, event):
        win = Proprietes(self.parent, [objet.etiquette for objet in self.objets if objet.etiquette is not None], True)
        win.show()


    def EvtEpaisseur(self, event):
        self.changements["epaisseur"] = self.epaisseur.GetValue()/10

    def EvtTaille(self, event):
        self.changements["taille"] = self.taille.GetValue()/10

    def EvtAngle(self, event):
        self.changements["angle"] = self.angle.GetValue()

    def EvtPosition(self, event):
        self.changements["position"] = self.position.GetValue()/100




class UpdatableTextCtrl(wx.TextCtrl):
    def __init__(self, parent, attribut, editable = False):
        wx.TextCtrl.__init__(self, parent, value = "", size=wx.Size(300, -1))
        self.parent = parent
        self.attribut = attribut
        self.SetEditable(editable)
        self.actualiser()


    def formater(self, valeur):
        if self.parent.objet.existe:
            if isinstance(valeur, (str, unicode)):
                return  valeur
            elif valeur is None:
                return u"Valeur non définie."
            elif hasattr(valeur, '__iter__'):
                return " ; ".join(self.formater(elt) for elt in valeur)
            return nice_display(valeur)
        else:
            return u"L'objet n'est pas défini."

    def actualiser(self):
        self.SetValue(self.formater(getattr(self.parent.objet, self.attribut)))


class ProprietesInfos(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.parent = parent
        self.objets = parent.objets
        self.sizer = QVBoxLayout()
        self.infos = wx.StaticBoxSizer(QGroupBox(self, -1, u"Informations"), wx.VERTICAL)
        if len(self.objets) == 1:
            self.objet = self.objets[0]
        else:
            self.objet = None # cela n'a pas vraiment de sens d'afficher une longueur pour 3 segments differents par exemple...

        self.textes = []
        proprietes = ("aire", "centre", "coordonnees", "rayon", "longueur", "perimetre", "norme", "sens")

        for propriete in proprietes:
            try:
                self.ajouter(propriete)
            except:
                debug(u"Erreur lors de la lecture de la propriété '%s' de l'objet %s." %(propriete, self.objet.nom))
                print_error()

        self.ajouter("equation_formatee", u"Equation cartésienne")


        if self.textes:
            self.sizer.addWidget(self.infos)
            actualiser = QPushButton(self, label = u"Actualiser")
            actualiser.Bind(wx.EVT_BUTTON, self.EvtActualiser)
            self.sizer.addWidget(actualiser, 0, wx.ALL, 15)
        else:
            self.sizer.addWidget(QLabel(self, str(len(self.objets)) + u" objets sélectionnés."), 0, wx.ALL, 15)
            self.infos.GetStaticBox().Destroy()
            del self.infos

        self.SetSizerAndFit(self.sizer)
        self.parent.parent.dim2 = self.sizer.CalcMin().Get()



    def ajouter(self, propriete, nom = None):
        if nom is None:
            nom = propriete.replace("_", " ").strip().capitalize()
        nom += " : "
        if hasattr(self.objet, propriete):
            self.infos.Add(QLabel(self, nom))
            txt = UpdatableTextCtrl(self, propriete)
            self.infos.Add(txt)
            self.textes.append(txt)

    def EvtActualiser(self, event = None):
        for txt in self.textes:
            txt.actualiser()





class ProprietesAvance(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.parent = parent
        self.objets = parent.objets
        self.panel = self.parent.parent.panel
        self.canvas = self.parent.parent.canvas
        self.islabel = self.parent.parent.islabel

        self.sizer = QVBoxLayout()
        if len(self.objets) is 1:
            self.objet = self.objets[0]
            box = wx.StaticBoxSizer(QGroupBox(self, -1, u"Style de l'objet"), wx.VERTICAL)
            box.Add(QLabel(self, label = u"Attention, ne modifiez ce contenu que si vous savez ce que vous faites."))
            self.avance = wx.TextCtrl(self, size=wx.Size(350, 200), style = wx.TE_MULTILINE)
            self.actualiser()
            box.Add(self.avance)
            self.sizer.addWidget(box)
            ok = QPushButton(self, id = wx.ID_OK)
            appliquer = QPushButton(self, label = u"Appliquer")
            actualiser = QPushButton(self, label = u"Actualiser")
            ok.Bind(wx.EVT_BUTTON, self.EvtOk)
            appliquer.Bind(wx.EVT_BUTTON, self.EvtAppliquer)
            actualiser.Bind(wx.EVT_BUTTON, self.actualiser)
            boutons = QHBoxLayout()
            boutons.Add(ok)
            boutons.Add(appliquer)
            boutons.Add(actualiser)
            self.sizer.addWidget(boutons)

        self.SetSizerAndFit(self.sizer)
        self.parent.parent.dim3 = self.sizer.CalcMin().Get()

    def EvtOk(self, event):
        self.EvtAppliquer(event)
        self.parent.parent.fenetre_principale.Raise()
        self.parent.parent.close() # fermeture de la frame


    def EvtAppliquer(self, event):
        txt = self.avance.GetValue().split('\n')
        dico = "{"
        for ligne in txt:
            key, value = ligne.split(":", 1)
            key = "'" + key.strip() + "':"
            dico += key + value + ","
        dico += "}"
        if self.islabel:
            self.canvas.executer(u"%s.etiquette.style(**%s)" %(self.objet.parent.nom, dico))
        else:
            self.canvas.executer(u"%s.style(**%s)" %(self.objet.nom, dico))

    def actualiser(self, event = None):
        items = (txt.split(':', 1) for txt in advanced_split(str(self.objet.style())[1:-1], ","))
        self.avance.SetValue('\n'.join(sorted(key.strip()[1:-1] + ':' + value for key, value in items)))



class OngletsProprietes(QTabWidget):
    def __init__(self, parent):
        self.parent = parent
        self.objets = parent.objets
        QTabWidget.__init__(self, parent)
        self.affichage = ProprietesAffichage(self)
        self.addTab(self.affichage, u"Affichage")
        self.infos = ProprietesInfos(self)
        self.addTab(self.infos, u"Informations")
        self.avance = ProprietesAvance(self)
        self.addTab(self.avance, u"Avancé")











class Proprietes(MyMiniFrame):
    def __init__(self, parent, objets, islabel = False):
        u"Le paramètre 'label' indique si l'objet à éditer est un label"
        print "OBJETS:"
        print objets
        print unicode(objets[0])
        print repr(objets[0])
        print objets[0].__class__
        print isinstance(objets[0], str)
        objets[0].titre_complet("du", False)
        self.parent = parent
        self.islabel = islabel
        self.fenetre_principale = self
        while hasattr(self.fenetre_principale, "parent"): # detection de la fenetre principale de WxGeometrie.
            self.fenetre_principale = self.fenetre_principale.parent
        self.panel = self.fenetre_principale.onglets.onglet_actuel
        self.canvas = self.panel.canvas

        self.objets = objets
        if self.islabel:
            titre = u"du label"
        else:
            if len(objets) == 0:
                self.close()
            if len(objets) == 1:
                titre = objets[0].titre_complet("du", False)
            else:
                titre = u"des objets"
#        wx.MiniFrame.__init__(self, parent, -1, u"Propriétés " + titre, style=wx.DEFAULT_FRAME_STYLE | wx.TINY_CAPTION_HORIZ)
        MyMiniFrame.__init__(self, parent, u"Propriétés " + titre)
        self.SetExtraStyle(wx.WS_EX_BLOCK_EVENTS )
        self.onglets = OngletsProprietes(self)
        self.SetSize(wx.Size(*(max(dimensions) + 50 for dimensions in zip(self.dim1, self.dim2, self.dim3))))
