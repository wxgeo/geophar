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

from functools import partial

from PyQt4.QtCore import Qt
from PyQt4.QtGui import (QDialog, QPushButton, QWidget, QLabel, QGroupBox,
                         QHBoxLayout, QVBoxLayout, QTabWidget, QColor,
                         QLineEdit, QComboBox, QCheckBox, QRadioButton,
                         QSpinBox, QTextEdit,
                         )
from matplotlib.colors import colorConverter as colorConverter


from .wxlib import ColorSelecter
from .app import white_palette
import param
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

        self.changements = {} # ce dictionnaire contiendra tous les styles modifi�s
        encadre = QHBoxLayout()

        if not self.islabel:
            proprietes = {'fixe': u'Objet fixe', 'visible': u'Objet visible', 'trace': u'Laisser une trace'}
            for propriete, titre in proprietes.items():
                self.add_checkbox(encadre, propriete, titre)


        encadre1 = QVBoxLayout()
        if not self.islabel:
            ligne = QHBoxLayout()
            if len(self.objets) == 1:
                self.etiquette = etiquette = QLineEdit()
                etiquette.setText(self.objets[0].style("label"))
                etiquette.setMinimumWidth(200)
                etiquette.editingFinished.connect(self.EvtEtiquette)
                ligne.addWidget(etiquette)
            if [objet for objet in self.objets if objet.etiquette is not None]:
                editer = QPushButton(u"Style")
                editer.clicked.connect(self.EvtLabelStyle)
                ligne.addWidget(editer)
            encadre1.addLayout(ligne)

            objets = [objet for objet in self.objets if objet.style("legende") is not None]
            if objets:
                leg = objets[0].style("legende")
                legende = QHBoxLayout()
                self.radio_nom = QRadioButton("Nom")
                ##self.radio_nom.SetValue(0)
                self.radio_etiquette = QRadioButton(u"Texte")
                ##self.radio_etiquette.SetValue(0)
                self.radio_formule = QRadioButton(u"Formule")
                ##self.radio_formule.SetValue(0)
                self.radio_aucun = QRadioButton(u"Aucun")
                ##self.radio_aucun.SetValue(0)
                if all(objet.style("legende") == leg for objet in objets):
                    if leg == NOM:
                        self.radio_nom.setChecked(True)
                    elif leg == TEXTE:
                        self.radio_etiquette.setChecked(True)
                    elif leg == FORMULE:
                        self.radio_formule.setChecked(True)
                    elif leg == RIEN:
                        self.radio_aucun.setChecked(True)

                self.radio_nom.toggled.connect(partial(self.EvtLegende, NOM))
                self.radio_etiquette.toggled.connect(partial(self.EvtLegende, TEXTE))
                self.radio_formule.toggled.connect(partial(self.EvtLegende, FORMULE))
                self.radio_aucun.toggled.connect(partial(self.EvtLegende, RIEN))
                legende.addWidget(self.radio_nom)
                legende.addWidget(self.radio_etiquette)
                legende.addWidget(self.radio_formule)
                legende.addWidget(self.radio_aucun)
                encadre1.addWidget(QLabel(u"Afficher : "))
                encadre1.addLayout(legende)



        encadre2 = QVBoxLayout()

        objets = [objet for objet in self.objets if objet.style("style") is not None]
        # on ne peut regler les styles simultanement que pour des objets de meme categorie
        categorie = objets and objets[0].style("categorie") or None

        if objets and categorie and all(objet.style("categorie") == categorie for objet in objets):
            choix = QHBoxLayout()
            choix.addWidget(QLabel(u"Style de l'objet : "))

            #categorie = objets[0].style("categorie") or "lignes"
            self.liste_styles = getattr(param, "styles_de_" + categorie, [])
            self.style = QComboBox()
            self.style.addItems(self.liste_styles)
            self.style.currentIndexChanged.connect(self.EvtStyle)

            style = objets[0].style("style")
            if style in self.liste_styles and all(objet.style("style") == style for objet in objets):
                self.style.setCurrentIndex(self.liste_styles.index(style)) # on s�lectionne le style actuel
            choix.addWidget(self.style)
            encadre2.addLayout(choix)


        objets = [objet for objet in self.objets if objet.style("hachures") is not None]
        if objets:
            choix = QHBoxLayout()
            choix.addWidget(QLabel(u"Style des h�chures : "))

            self.types_de_hachures = getattr(param, "types_de_hachures", [])
            self.hachures = QComboBox()
            self.hachures.addItems(self.types_de_hachures)
            self.hachure.currentIndexChanged.connect(self.EvtHachures)

            hachures = objets[0].style("hachures")
            if hachures in self.types_de_hachures and all(objet.style("hachures") == hachures for objet in objets):
                self.hachures.setCurrentIndex(self.types_de_hachures.index(hachures)) # on s�lectionne les hachures actuelles
            choix.addWidget(self.hachures)
            encadre2.addLayout(choix)


        objets = [objet for objet in self.objets if objet.style("famille") is not None]
        categorie = objets and objets[0].style("categorie") or None

        if objets and categorie and all(objet.style("categorie") == categorie for objet in objets):
            choix = QHBoxLayout()
            choix.addWidget(QLabel("Police : "))

            #categorie = self.objet.style("categorie") or "lignes"
            self.liste_familles = getattr(param, "familles_de_" + categorie, [])
            self.famille = QComboBox()
            self.famille.addItems(self.liste_familles)
            self.famille.currentIndexChanged.connect(self.EvtFamille)

            famille = objets[0].style("famille")
            if famille in self.liste_familles and all(objet.style("famille") == famille for objet in objets):
                self.famille.setCurrentIndex(self.liste_familles.index(famille)) # on s�lectionne la famille actuelle

            choix.addWidget(self.famille)
            encadre2.addLayout(choix)


        objets = [objet for objet in self.objets if objet.style("couleur") is not None]
        if objets:
            couleur = objets[0].style("couleur")
            choix = QHBoxLayout()
            choix.addWidget(QLabel(u"Couleur de l'objet : "))
            if all(objet.style("couleur") == couleur for objet in objets):
                # conversion du format matplotlib au format Qt
                r, g, b = colorConverter.to_rgb(couleur)
                couleur = QColor(int(255*r), int(255*g), int(255*b))
            else:
                couleur = None
            b = ColorSelecter(self, color=couleur)
            b.colorSelected.connect(self.OnSelectColour)
            choix.addWidget(b)
            encadre2.addLayout(choix)


        objets = [objet for objet in self.objets if objet.style("epaisseur") is not None]
        if objets:
            epaiss = objets[0].style("epaisseur")
            epaisseur = QHBoxLayout()
            epaisseur.addWidget(QLabel(u"Epaisseur (en 10e de pixels) : "))
            self.epaisseur = QSpinBox()
            self.epaisseur.setMinimumSize(30, 50)
            self.epaisseur.setRange(1,10000)
            if all(objet.style("epaisseur") == epaiss for objet in objets):
                self.epaisseur.setValue(10*epaiss)
            else:
                self.epaisseur.setSpecialValueText(' ')
                print(u'FIXME: cas non g�r�.')
            self.epaisseur.valueChanged.connect(self.EvtEpaisseur)
            epaisseur.addWidget(self.epaisseur)
            encadre2.addLayout(epaisseur)


        objets = [objet for objet in self.objets if objet.style("taille") is not None]
        if objets:
            tail = objets[0].style("taille")
            taille = QHBoxLayout()
            taille.addWidget(QLabel(u"Taille (en 10e de pixels) : "))
            self.taille = QSpinBox()
            self.taille.setMinimumSize(30, 50)
            self.taille.setRange(1,10000)
            if all(objet.style("taille") == tail for objet in objets):
                self.taille.setValue(10*tail)
            else:
                self.taille.setSpecialValueText(' ')
                print(u'FIXME: cas non g�r�.')
            self.taille.valueChanged.connect(self.EvtTaille)
            taille.addWidget(self.taille)
            encadre2.addLayout(taille)


        objets = [objet for objet in self.objets if objet.style("position") is not None]
        if objets:
            pos = objets[0].style("position")
            position = QHBoxLayout()
            position.addWidget(QLabel(u"Position de la fl�che : "))
            self.position = QSpinBox()
            self.position.setMinimumSize(30, 50)
            self.position.setRange(0, 100)
            if all(objet.style("position") == pos for objet in objets):
                self.position.setValue(100*pos)
            else:
                self.position.setSpecialValueText(' ')
                print(u'FIXME: cas non g�r�.')
            self.position.valueChanged.connect(self.EvtPosition)
            position.addWidget(self.position)
            encadre2.addLayout(position)



        objets = [objet for objet in self.objets if objet.style("angle") is not None]
        if objets:
            ang = objets[0].style("angle")
            angle = QHBoxLayout()
            angle.addWidget(QLabel(u"Angle (en degr�) : "))
            self.angle = QSpinBox()
            self.angle.setMinimumSize(30, 50)
            self.angle.setRange(0, 360)
            if all(objet.style("angle") == ang for objet in objets):
                self.angle.setValue(ang)
            else:
                self.angle.setSpecialValueText(' ')
                print(u'FIXME: cas non g�r�.')
            self.angle.valueChanged.connect(self.EvtAngle)
            angle.addWidget(self.angle)
            encadre2.addLayout(angle)

        self.add_checkbox(encadre, 'double_fleche', u"Fl�che double")

        objets = [objet for objet in self.objets if objet.style("codage") is not None]
        # on ne peut regler les codages simultanement que pour des objets de meme categorie
        categorie = objets and objets[0].style("categorie") or None


        if objets and categorie and all(objet.style("categorie") == categorie for objet in objets):
            choix = QHBoxLayout()
            choix.addWidget(QLabel("Codage : "))

            #categorie = objets[0].style("categorie") or "lignes"
            self.liste_codages = getattr(param, "codage_des_" + categorie, [])
            self.codage = QComboBox()
            self.codage.addItems(self.liste_codages)
            self.codage.currentIndexChanged.connect(self.EvtCodage)

            codage = objets[0].style("codage")
            if codage in self.liste_codages and all(objet.style("codage") == codage for objet in objets):
                self.codage.setCurrentIndex(self.liste_codages.index(codage)) # on s�lectionne le codage actuel
            choix.addWidget(self.codage)
            encadre2.addLayout(choix)


        boutons = QHBoxLayout()
        ok = QPushButton('OK')
        ok.clicked.connect(self.EvtOk)
        boutons.addWidget(ok)

        appliquer = QPushButton(u"Appliquer")
        appliquer.clicked.connect(self.EvtAppliquer)
        boutons.addWidget(appliquer)

        if not self.islabel:
            supprimer = QPushButton(u"Supprimer")
            supprimer.clicked.connect(self.EvtSupprimer)
            boutons.addWidget(supprimer)

        annuler = QPushButton(u"Annuler")
        annuler.clicked.connect(self.EvtAnnuler)
        boutons.addWidget(annuler)

        if encadre.count(): # ne pas afficher une rubrique vide !
            encadre_box = QGroupBox(u"Mode d'affichage")
            encadre_box.setLayout(encadre)
            self.sizer.addWidget(encadre_box)
        if encadre1.count():
            encadre1_box = QGroupBox(u"Etiquette")
            encadre_box.setLayout(encadre1)
            self.sizer.addWidget(encadre1_box)
        if encadre2.count():
            encadre2_box = QGroupBox(u"Styles")
            encadre_box.setLayout(encadre2)
            self.sizer.addWidget(encadre2_box)
        self.sizer.addLayout(boutons)
        self.setLayout(self.sizer)
        ##self.parent.parent.dim1 = self.sizer.CalcMin().Get()


    def add_checkbox(self, layout, propriete, titre):
        objets = [objet for objet in self.objets if objet.style(propriete) is not None]
        if objets:
            cb = QCheckBox(titre)
            cb.setTristate(True)
            layout.addWidget(cb)
            verifies = [objet.style(propriete) is True for objet in objets]
            if not any(verifies):
                etat = Qt.Unchecked
            elif all(verifies):
                etat = Qt.Checked
            else:
                etat = Qt.PartiallyChecked
            cb.setCheckState(etat)
            cb.stateChanged.connect(partial(self.checked, propriete))
            cb.stateChanged.connect(partial(cb.setTristate, False))


    def EvtLegende(self, valeur):
        self.changements["legende"] = valeur

    def checked(self, propriete, state):
        self.changements[propriete] = (state == Qt.Checked)

    def EvtEtiquette(self):
        self.changements["label"] = self.etiquette.toPlainText()

    def OnSelectColour(self, color):
        # conversion du format Qt au format matplotlib
        self.changements["couleur"] = color.getRgb()

    def EvtStyle(self, index):
        self.changements["style"] = self.liste_styles[index]

    def EvtHachures(self, index):
        self.changements["hachures"] = self.types_de_hachures[index]

    def EvtCodage(self, index):
        self.changements["codage"] = self.liste_codages[index]

    def EvtFamille(self, index):
        self.changements["famille"] = self.liste_familles[index]

    def EvtOk(self):
        self.EvtAppliquer()
        self.EvtAnnuler()

    def EvtAppliquer(self):
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


    def EvtSupprimer(self):
        with self.canvas.geler_affichage(actualiser=True, sablier=True):
            for objet in self.objets:
                self.canvas.executer(u"del %s" %objet.nom)
        self.EvtAnnuler()

    def EvtAnnuler(self):
        # Ce qui suit corrige un genre de bug bizarre de wx:
        # quand une fen�tre de s�lection de couleur a �t� affich�e,
        # la fen�tre principale passe au second plan � la fermeture de la fen�tre de propri�t�s ?!?
        # (ce qui est tr�s d�sagr�able d�s qu'un dossier est ouvert dans l'explorateur, par exemple !)
        # -> � supprimer avec Qt ?
        self.parent.parent.fenetre_principale.raise_()
        self.parent.parent.close() # fermeture de la frame

    def EvtLabelStyle(self):
        win = Proprietes(self.parent, [objet.etiquette for objet in self.objets
                                       if objet.etiquette is not None], True)
        win.show()


    def EvtEpaisseur(self):
        self.changements["epaisseur"] = self.epaisseur.value()/10

    def EvtTaille(self):
        self.changements["taille"] = self.taille.value()/10

    def EvtAngle(self):
        self.changements["angle"] = self.angle.value()

    def EvtPosition(self):
        self.changements["position"] = self.position.value()/100




class UpdatableLineEdit(QLineEdit):
    def __init__(self, parent, attribut, editable=False):
        QLineEdit.__init__(self, parent)
        self.setMinimumWidth(300)
        self.parent = parent
        self.attribut = attribut
        self.setReadOnly(not editable)
        self.actualiser()


    def formater(self, valeur):
        if self.parent.objet.existe:
            if isinstance(valeur, (str, unicode)):
                return  valeur
            elif valeur is None:
                return u"Valeur non d�finie."
            elif hasattr(valeur, '__iter__'):
                return " ; ".join(self.formater(elt) for elt in valeur)
            return nice_display(valeur)
        else:
            return u"L'objet n'est pas d�fini."

    def actualiser(self):
        self.setText(self.formater(getattr(self.parent.objet, self.attribut)))


class ProprietesInfos(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.parent = parent
        self.objets = parent.objets
        self.sizer = QVBoxLayout()
        self.infos = infos = QVBoxLayout()
        if len(self.objets) == 1:
            self.objet = self.objets[0]
        else:
            self.objet = None # cela n'a pas vraiment de sens d'afficher une longueur pour 3 segments differents par exemple...

        self.textes = []
        proprietes = ("aire", "centre", "coordonnees", "rayon", "longueur", "perimetre", "norme", "sens")

        for propriete in proprietes:
            try:
                self.ajouter(infos, propriete)
            except:
                debug(u"Erreur lors de la lecture de la propri�t� '%s' de l'objet %s." %(propriete, self.objet.nom))
                print_error()

        self.ajouter(infos, "equation_formatee", u"Equation cart�sienne")


        if self.textes:
            infos_box = QGroupBox(u"Informations")
            infos_box.setLayout(infos)
            self.sizer.addWidget(infos_box)
            actualiser = QPushButton(u"Actualiser")
            actualiser.clicked.connect(self.EvtActualiser)
            self.sizer.addWidget(actualiser)
        else:
            self.sizer.addWidget(QLabel(str(len(self.objets)) + u" objets s�lectionn�s."))

        self.setLayout(self.sizer)
        ##self.parent.parent.dim2 = self.sizer.CalcMin().Get()



    def ajouter(self, layout, propriete, nom=None):
        if nom is None:
            nom = propriete.replace("_", " ").strip().capitalize()
        nom += " : "
        if hasattr(self.objet, propriete):
            layout.addWidget(QLabel(nom))
            txt = UpdatableLineEdit(self, propriete)
            self.infos.addWidget(txt)
            self.textes.append(txt)

    def EvtActualiser(self):
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

            style = QVBoxLayout()
            style_box = QGroupBox(u"Style de l'objet")
            style_box.setLayout(style)
            style.addWidget(QLabel(u"Attention, ne modifiez ce contenu que si vous savez ce que vous faites."))
            self.avance = QTextEdit()
            self.avance.setMinimumSize(350, 200)
            self.actualiser()
            style.addWidget(self.avance)
            self.sizer.addWidget(style_box)

            ok = QPushButton('OK')
            appliquer = QPushButton(u"Appliquer")
            actualiser = QPushButton(u"Actualiser")
            ok.clicked.connect(self.EvtOk)
            appliquer.clicked.connect(self.EvtAppliquer)
            actualiser.clicked.connect(self.actualiser)
            boutons = QHBoxLayout()
            boutons.addWidget(ok)
            boutons.addWidget(appliquer)
            boutons.addWidget(actualiser)
            self.sizer.addLayout(boutons)

        self.setLayout(self.sizer)
        ##self.parent.parent.dim3 = self.sizer.CalcMin().Get()

    def EvtOk(self):
        self.EvtAppliquer()
        self.parent.parent.fenetre_principale.raise_()
        self.parent.parent.close() # fermeture de la frame


    def EvtAppliquer(self):
        txt = self.avance.toPlainText().split('\n')
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
        self.avance.setPlainText('\n'.join(sorted(key.strip()[1:-1] + ':' + value for key, value in items)))



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
        self.addTab(self.avance, u"Avanc�")






class Proprietes(QDialog):
    def __init__(self, parent, objets, islabel = False):
        u"Le param�tre 'label' indique si l'objet � �diter est un label"
        print "OBJETS:"
        print objets
        print unicode(objets[0])
        print repr(objets[0])
        print objets[0].__class__
        print isinstance(objets[0], str)
        objets[0].titre_complet("du", False)
        self.parent = parent
        self.islabel = islabel
        self.fenetre_principale = self.parent.window()
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
#        wx.MiniFrame.__init__(self, parent, -1, u"Propri�t�s " + titre, style=wx.DEFAULT_FRAME_STYLE | wx.TINY_CAPTION_HORIZ)
        QDialog.__init__(self, parent)
        self.setWindowTitle(u"Propri�t�s " + titre)
        self.setPalette(white_palette)
        ##self.SetExtraStyle(wx.WS_EX_BLOCK_EVENTS )
        main = QVBoxLayout()
        self.setLayout(main)
        self.onglets = OngletsProprietes(self)
        main.addWidget(self.onglets)
        ##self.SetSize(wx.Size(*(max(dimensions) + 50 for dimensions in zip(self.dim1, self.dim2, self.dim3))))
