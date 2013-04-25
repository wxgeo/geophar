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


from .qtlib import ColorSelecter
from .app import white_palette, app
from .. import param
from ..pylib import print_error, debug, advanced_split, OrderedDict
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
        encadre = QHBoxLayout()

        if not self.islabel:
            proprietes = {'fixe': u'Objet fixe', 'visible': u'Objet visible', 'trace': u'Laisser une trace'}
            for propriete, titre in proprietes.items():
                self.add_checkbox(encadre, propriete, titre)
            encadre.addStretch()


        encadre1 = QVBoxLayout()
        if not self.islabel:
            ligne = QHBoxLayout()
            if len(self.objets) == 1:
                self.etiquette = etiquette = QLineEdit()
                etiquette.setText(self.objets[0].legende)
                etiquette.setMinimumWidth(200)
                etiquette.editingFinished.connect(self.EvtEtiquette)
                ligne.addWidget(etiquette)
            if [objet for objet in self.objets if objet.etiquette is not None]:
                editer = QPushButton(u"Style")
                editer.clicked.connect(self.EvtLabelStyle)
                ligne.addWidget(editer)
            encadre1.addLayout(ligne)

            objets = [objet for objet in self.objets if objet.mode_affichage is not None]
            if objets:
                mode = objets[0].mode_affichage
                legende = QHBoxLayout()
                self.radios = OrderedDict((
                        (NOM, QRadioButton("Nom")),
                        (TEXTE, QRadioButton(u"Texte")),
                        (FORMULE, QRadioButton(u"Formule")),
                        (RIEN, QRadioButton(u"Aucun")),
                              ))
                if all(objet.mode_affichage == mode for objet in objets):
                    self.radios[mode].setChecked(True)

                for mode, radio in self.radios.iteritems():
                    radio.toggled.connect(partial(self.EvtMode, mode))
                    legende.addWidget(radio)

                legende.addStretch()
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
                self.style.setCurrentIndex(self.liste_styles.index(style)) # on sélectionne le style actuel
            choix.addWidget(self.style)
            choix.addStretch()
            encadre2.addLayout(choix)


        objets = [objet for objet in self.objets if objet.style("hachures") is not None]
        if objets:
            choix = QHBoxLayout()
            choix.addWidget(QLabel(u"Style des hâchures : "))

            self.types_de_hachures = getattr(param, "types_de_hachures", [])
            self.hachures = QComboBox()
            self.hachures.addItems(self.types_de_hachures)
            self.hachures.currentIndexChanged.connect(self.EvtHachures)

            hachures = objets[0].style("hachures")
            if hachures in self.types_de_hachures and all(objet.style("hachures") == hachures for objet in objets):
                self.hachures.setCurrentIndex(self.types_de_hachures.index(hachures)) # on sélectionne les hachures actuelles
            choix.addWidget(self.hachures)
            choix.addStretch()
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
                self.famille.setCurrentIndex(self.liste_familles.index(famille)) # on sélectionne la famille actuelle

            choix.addWidget(self.famille)
            choix.addStretch()
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
            choix.addStretch()
            encadre2.addLayout(choix)


        objets = [objet for objet in self.objets if objet.style("epaisseur") is not None]
        if objets:
            epaiss = objets[0].style("epaisseur")
            epaisseur = QHBoxLayout()
            epaisseur.addWidget(QLabel(u"Epaisseur (en 10e de pixels) : "))
            self.epaisseur = QSpinBox()
            self.epaisseur.setMinimumWidth(30)
            self.epaisseur.setRange(1, 10000)
            if all(objet.style("epaisseur") == epaiss for objet in objets):
                self.epaisseur.setValue(10*epaiss)
            else:
                self.epaisseur.setSpecialValueText(' ')
                print(u'FIXME: cas non géré.')
            self.epaisseur.valueChanged.connect(self.EvtEpaisseur)
            epaisseur.addWidget(self.epaisseur)
            epaisseur.addStretch()
            encadre2.addLayout(epaisseur)


        objets = [objet for objet in self.objets if objet.style("taille") is not None]
        if objets:
            tail = objets[0].style("taille")
            taille = QHBoxLayout()
            taille.addWidget(QLabel(u"Taille (en 10e de pixels) : "))
            self.taille = QSpinBox()
            self.taille.setMinimumWidth(30)
            self.taille.setRange(1,10000)
            if all(objet.style("taille") == tail for objet in objets):
                self.taille.setValue(10*tail)
            else:
                self.taille.setSpecialValueText(' ')
                print(u'FIXME: cas non géré.')
            self.taille.valueChanged.connect(self.EvtTaille)
            taille.addWidget(self.taille)
            taille.addStretch()
            encadre2.addLayout(taille)


        objets = [objet for objet in self.objets if objet.style("position") is not None]
        if objets:
            pos = objets[0].style("position")
            position = QHBoxLayout()
            position.addWidget(QLabel(u"Position de la flêche : "))
            self.position = QSpinBox()
            self.position.setMinimumWidth(30)
            self.position.setRange(0, 100)
            if all(objet.style("position") == pos for objet in objets):
                self.position.setValue(100*pos)
            else:
                self.position.setSpecialValueText(' ')
                print(u'FIXME: cas non géré.')
            self.position.valueChanged.connect(self.EvtPosition)
            position.addWidget(self.position)
            position.addStretch()
            encadre2.addLayout(position)



        objets = [objet for objet in self.objets if objet.style("angle") is not None]
        if objets:
            ang = objets[0].style("angle")
            angle = QHBoxLayout()
            angle.addWidget(QLabel(u"Angle (en degré) : "))
            self.angle = QSpinBox()
            self.angle.setMinimumWidth(30)
            self.angle.setRange(-180, 180)
            self.angle.setSpecialValueText('auto')
            self.angle.setSuffix(u'°');
            self.angle.setWrapping(True)
            if all(objet.style("angle") == ang for objet in objets):
                self.angle.setValue(ang if ang != 'auto' else -180)
            else:
                self.angle.setSpecialValueText(' ')
                print(u'FIXME: cas non géré.')
            self.angle.valueChanged.connect(self.EvtAngle)
            angle.addWidget(self.angle)
            angle.addStretch()
            encadre2.addLayout(angle)

        self.add_checkbox(encadre, 'double_fleche', u"Flêche double")

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
                self.codage.setCurrentIndex(self.liste_codages.index(codage)) # on sélectionne le codage actuel
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
            encadre1_box.setLayout(encadre1)
            self.sizer.addWidget(encadre1_box)
        if encadre2.count():
            encadre2_box = QGroupBox(u"Styles")
            encadre2_box.setLayout(encadre2)
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
            cb.stateChanged.connect(partial(self.checked, propriete=propriete))
            cb.stateChanged.connect(partial(cb.setTristate, False))


    def EvtMode(self, valeur):
        self.changements["mode"] = valeur

    def checked(self, state, propriete):
        # Bug avec Qt 4.8.1 - En cochant la case la première fois, on obtient
        # Qt.PartiallyChecked, et non Qt.Checked. Si ensuite, on décoche et on
        # recoche, on obtient bien Qt.Checked.
        self.changements[propriete] = (state != Qt.Unchecked)

    def EvtEtiquette(self):
        self.changements["label"] = self.etiquette.text()

    def OnSelectColour(self, color):
        # conversion du format Qt au format matplotlib
        r, g, b, a = color.getRgb()
        self.changements["couleur"] = (r/255, g/255, b/255, a/255)

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
                    mode = changements.pop('mode', None)
                    label = changements.pop('label', None)
                    for key in changements.copy():
                        if objet.style(key) is None: # le style n'a pas de sens pour l'objet
                            changements.pop(key)
                    if mode is not None or label is not None:
                        self.canvas.executer(u"%s.label(%s, %s)" %(objet.nom, repr(label), mode))
                        if mode is None:
                            mode = objet.etiquette.style("mode")
                            self.changements["mode"] = mode
                            self.radios[mode].setChecked(True)

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
        # quand une fenêtre de sélection de couleur a été affichée,
        # la fenêtre principale passe au second plan à la fermeture de la fenêtre de propriétés ?!?
        # (ce qui est très désagréable dès qu'un dossier est ouvert dans l'explorateur, par exemple !)
        # -> à supprimer avec Qt ?
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
        angle = self.angle.value()
        self.changements["angle"] = (angle if angle != -180 else 'auto')

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
                return u"Valeur non définie."
            elif hasattr(valeur, '__iter__'):
                return " ; ".join(self.formater(elt) for elt in valeur)
            return nice_display(valeur)
        else:
            return u"L'objet n'est pas défini."

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
                debug(u"Erreur lors de la lecture de la propriété '%s' de l'objet %s." %(propriete, self.objet.nom))
                print_error()

        self.ajouter(infos, "equation_formatee", u"Equation cartésienne")


        if self.textes:
            infos_box = QGroupBox(u"Informations")
            infos_box.setLayout(infos)
            self.sizer.addWidget(infos_box)
            actualiser = QPushButton(u"Actualiser")
            actualiser.clicked.connect(self.EvtActualiser)
            self.sizer.addStretch()
            self.sizer.addWidget(actualiser)
        else:
            self.sizer.addWidget(QLabel(str(len(self.objets)) + u" objets sélectionnés."))

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
        self.addTab(self.avance, u"Avancé")






class Proprietes(QDialog):
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
        self.fenetre_principale = self.parent.window()
        self.panel = app.fenetre_principale.onglets.onglet_actuel
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
        QDialog.__init__(self, parent)
        self.setWindowTitle(u"Propriétés " + titre)
        self.setPalette(white_palette)
        ##self.SetExtraStyle(wx.WS_EX_BLOCK_EVENTS )
        main = QVBoxLayout()
        self.setLayout(main)
        self.onglets = OngletsProprietes(self)
        main.addWidget(self.onglets)
        ##self.SetSize(wx.Size(*(max(dimensions) + 50 for dimensions in zip(self.dim1, self.dim2, self.dim3))))
