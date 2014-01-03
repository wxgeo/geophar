# -*- coding: utf-8 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)
from __future__ import with_statement

##--------------------------------------#######
#                 Fenetres                              #
##--------------------------------------#######
#    WxGeometrie
#    Dynamic geometry, graph plotter, and more for french mathematic teachers.
#    Copyright (C) 2005-2013  Nicolas Pourcelot
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
                         QSpinBox, QTextEdit, QDoubleSpinBox,
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

        assert len(self.objets) >= 1

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

        objets = self.objets
        categorie = objets[0].style("categorie")
        sous_categorie = objets[0].style("sous-categorie")
        tous_de_meme_categorie = all(objet.style("categorie") == categorie for objet in objets)
        tous_de_meme_sous_categorie = (tous_de_meme_categorie and
                all(objet.style("sous-categorie") == sous_categorie for objet in objets))

        encadre2 = QVBoxLayout()

        hb = QHBoxLayout()
        if tous_de_meme_categorie:
            styles_possibles = getattr(param, "styles_de_%s" % categorie, [])
            # On ne peut régler les styles simultanément que pour des objets de même catégorie.
            if self.add_combo_box(hb, 'style', u"Style de l'objet : ", styles_possibles):
                encadre2.addLayout(hb)

        self.add_color_selecter(hb, 'couleur', "Couleur de l'objet")

        hb = QHBoxLayout()
        types_de_hachures = getattr(param, "types_de_hachures", [])
        if self.add_combo_box(hb, 'hachures', u"Style des hâchures : ", types_de_hachures):
            encadre2.addLayout(hb)

        if tous_de_meme_categorie:
            hb = QHBoxLayout()
            familles_possibles = getattr(param, "familles_de_%s" % categorie, [])
            if self.add_combo_box(hb, 'famille', 'Police : ', familles_possibles):
                encadre2.addLayout(hb)

        hb = QHBoxLayout()
        if self.add_spin_box(hb, 'epaisseur', u'Épaisseur', .1, 1000, .5, ' px'):
            encadre2.addLayout(hb)

        hb = QHBoxLayout()
        if tous_de_meme_sous_categorie and sous_categorie in ('vecteurs', 'axes'):
            legende = u"Taille de la flêche"
        else:
            legende = u'Taille'
        if self.add_spin_box(hb, 'taille', legende, .1, 1000, .5, ' px'):
            #~ hb.addStretch()
            encadre2.addLayout(hb)

        hb = QHBoxLayout()
        if self.add_spin_box(hb, 'position', u"Position de la flêche", 0, 100, 5, coeff=100):
            #~ hb.addStretch()
            encadre2.addLayout(hb)

        hb = QHBoxLayout()
        if tous_de_meme_sous_categorie and sous_categorie in ('vecteurs', 'axes'):
            legende = u"Angle d'ouverture"
        else:
            legende = u'Angle'
        if self.add_spin_box(hb, 'angle', legende, -180, 180,
                             suffixe=u'°', wrapping=True, special_value='auto'):
            #~ hb.addStretch()
            encadre2.addLayout(hb)

        self.add_checkbox(encadre, 'double_fleche', u"Flêche double")

        if tous_de_meme_categorie:
            hb = QHBoxLayout()
            codages_possibles = getattr(param, "codage_des_%s" % categorie, [])
            # On ne peut régler les codages simultanément que pour des objets de même catégorie.
            if self.add_combo_box(hb, 'codage', 'Codage : ', codages_possibles):
                encadre2.addLayout(hb)

        # --------------------------------------------------------
        # Styles s'appliquant aux textes seulement (fond et cadre)
        # --------------------------------------------------------

        encadre3 = QVBoxLayout()
        if tous_de_meme_categorie and categorie == 'textes':

            #  FOND
            #  ====

            # Réglage de l'opacité du fond
            # ----------------------------
            hb2 = QHBoxLayout()
            widgets = self.add_spin_box(hb2, 'alpha_fond', u'Opacité', 0, 100, 5, '%', coeff=100)

            # Réglage de la couleur du fond
            # -----------------------------
            widgets.extend(self.add_color_selecter(hb2, 'couleur_fond'))

            # Activation/désactivation du fond
            # --------------------------------
            hb1 = QHBoxLayout()
            self.add_checkbox(hb1, 'fond', 'Fond', fils=widgets)
            encadre3.addLayout(hb1)
            encadre3.addLayout(hb2)


            #  CADRE
            #  =====

            # Réglage de l'épaisseur du cadre
            # -------------------------------
            hb2 = QHBoxLayout()
            widgets = self.add_spin_box(hb2, 'epaisseur_cadre', u'Épaisseur', 0, 100, 0.5, ' px')

            # Réglage de la couleur du cadre
            # ------------------------------
            widgets.extend(self.add_color_selecter(hb2, 'couleur_cadre'))

            # Réglage du style du cadre
            # -------------------------
            widgets.extend(self.add_combo_box(hb2, 'style_cadre', 'Style : ', param.styles_de_lignes))

            # Activation/désactivation du cadre
            # ---------------------------------
            hb1 = QHBoxLayout()
            self.add_checkbox(hb1, 'cadre', 'Cadre', fils=widgets)
            encadre3.addLayout(hb1)
            encadre3.addLayout(hb2)

        # ----------------------------------------------------
        # Styles s'appliquant aux axes seulement (graduations)
        # ----------------------------------------------------

        encadre4 = QVBoxLayout()
        if tous_de_meme_sous_categorie and sous_categorie == 'axes':

            """
            Styles spécifiques:
            - `graduations` (bool): afficher ou non les graduations
            - `pas` (int|None):
                * entier `n` (non nul): `n` fois l'écart entre les deux points repères
                  de l'axe.
                * `None` ou `0`: adapte automatiquement la taille
                  de la graduation à la fenêtre (défaut)
            - `pas_num` (int): entier positif `n`:
                * si `n` est nul, n'affiche aucun nombre sur l'axe ;
                * sinon, affiche un nombre toutes les `n` graduations
                  (en partant de l'origine de l'axe).
                  En particulier, si `pas_num=1`, toutes les graduations
                  auront un nombre.
            - `repeter` (bool): répéter ou non la numérotation sur les axes.
            - `hauteur` (int): hauteur d'une graduation (en pixels).
            - `placement_num` (-1|1): position de la numérotation par rapport à l'axe.
            """


            # GRADUATIONS (AXE)
            # =================

            # Répéter ou non les valeurs
            # --------------------------
            hb2 = QHBoxLayout()
            widgets = self.add_checkbox(hb2, 'repeter', u"Afficher régulièrement les valeurs")


            # Espace entre deux valeurs de l'axe
            # ----------------------------------
            hb3 = QHBoxLayout()
            widgets.extend(self.add_spin_box(hb3, 'pas_num', u'Afficher les valeurs toutes les',
                           0, 100, 1, ' graduations'))

            # Activation/désactivation des graduations
            # ----------------------------------------
            hb1 = QHBoxLayout()
            self.add_checkbox(hb1, 'graduations', u"Graduer l'axe", fils=widgets)
            encadre4.addLayout(hb1)
            encadre4.addLayout(hb2)
            encadre4.addLayout(hb3)





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

        self.add_groupbox(encadre, u"Mode d'affichage")
        self.add_groupbox(encadre1, u"Etiquette")
        self.add_groupbox(encadre2, u"Styles")
        self.add_groupbox(encadre3, u"Fond et encadrement")
        self.add_groupbox(encadre4, u"Graduations")
        self.sizer.addLayout(boutons)
        self.setLayout(self.sizer)
        ##self.parent.parent.dim1 = self.sizer.CalcMin().Get()


    def add_groupbox(self, layout, titre):
        # Ne pas afficher une rubrique vide !
        if layout.count():
            box = QGroupBox(titre)
            box.setLayout(layout)
            self.sizer.addWidget(box)
            return [box]
        return []

    def add_checkbox(self, layout, propriete, titre, fils=()):
        objets = [objet for objet in self.objets if objet.style(propriete) is not None]
        if not objets:
            return []
        cb = QCheckBox(titre)
        cb.setTristate(True)
        layout.addWidget(cb)
        layout.addStretch()
        verifies = [objet.style(propriete) is True for objet in objets]
        if not any(verifies):
            etat = Qt.Unchecked
        elif all(verifies):
            etat = Qt.Checked
        else:
            etat = Qt.PartiallyChecked
        cb.setCheckState(etat)
        for widget in fils:
            widget.setVisible(etat != Qt.Unchecked)
        cb.stateChanged.connect(partial(self.checked, propriete=propriete, fils=fils))
        cb.stateChanged.connect(partial(cb.setTristate, False))
        return [cb]


    def add_color_selecter(self, layout, propriete, titre='Couleur'):
        objets = [objet for objet in self.objets if objet.style(propriete) is not None]
        if not objets:
            return []
        couleur = objets[0].style(propriete)
        label = QLabel(titre + ' : ')
        layout.addWidget(label)

        if couleur and all(objet.style(propriete) == couleur for objet in objets):
            # conversion du format matplotlib au format Qt
            r, g, b = colorConverter.to_rgb(couleur)
            couleur = QColor(int(255*r), int(255*g), int(255*b))
        else:
            couleur = None
        selecter = ColorSelecter(self, color=couleur)
        layout.addWidget(selecter)
        layout.addStretch()
        selecter.colorSelected.connect(partial(self.colour_selected, propriete=propriete))
        return [label, selecter]


    def add_spin_box(self, layout, propriete, titre, min_, max_,
                     step=1, suffixe=None, coeff=1, wrapping=False, special_value=None):
        u"""Ajouter un widget QSpinBox.
        """
        assert special_value != ' ' # Réservé au cas où les objets ont des valeurs différentes.
        objets = [objet for objet in self.objets if objet.style(propriete) is not None]
        if not objets:
            return []
        val = objets[0].style(propriete)
        label = QLabel(titre + ' : ')
        layout.addWidget(label)
        if isinstance(step, float):
            widget = QDoubleSpinBox()
            widget.setDecimals(len(str(step).split('.')[1]))
        else:
            widget = QSpinBox()
        widget.setMinimumWidth(30)
        widget.setSingleStep(step)
        widget.setWrapping(wrapping)
        widget.setRange(min_, max_)
        if special_value is not None:
            widget.setSpecialValueText(special_value)
        if suffixe is not None:
            widget.setSuffix(suffixe)
        if all(objet.style(propriete) == val for objet in objets):
            if special_value is not None and val == special_value:
                widget.setValue(min_)
            else:
                widget.setValue(coeff*val)
        else:
            # Lorsque tous les objets sélectionnés n'ont pas la même valeur
            # pour ce paramètre, on affiche ' '.
            widget.setMinimum(min_ - step)
            widget.setSpecialValueText(' ')
            widget.setValue(min_ - step)
        widget.valueChanged.connect(partial(self.spin_changed, propriete=propriete, widget=widget, coeff=coeff))
        layout.addWidget(widget)
        layout.addStretch()
        return [label, widget]


    def add_combo_box(self, layout, propriete, titre, liste):
        objets = [objet for objet in self.objets if objet.style(propriete) is not None]
        if not objets:
            print("pas d'objets... (%s)" % propriete)
            return []

        label = QLabel(titre)
        layout.addWidget(label)

        widget = QComboBox()
        widget.addItems(liste)
        widget.currentIndexChanged.connect(partial(self.item_selected, propriete=propriete, liste=liste))

        val = objets[0].style(propriete)
        if val in liste and all(objet.style(propriete) == val for objet in objets):
            # On sélectionne la valeur actuelle du paramètre.
            widget.setCurrentIndex(liste.index(val))
        layout.addWidget(widget)
        layout.addStretch()
        return [label, widget]


    def EvtMode(self, valeur):
        self.changements["mode"] = valeur

    def EvtEtiquette(self):
        self.changements["label"] = self.etiquette.text()

    def checked(self, state, propriete, fils):
        # Bug avec Qt 4.8.1 - En cochant la case la première fois, on obtient
        # Qt.PartiallyChecked, et non Qt.Checked. Si ensuite, on décoche et on
        # recoche, on obtient bien Qt.Checked.
        self.changements[propriete] = (state != Qt.Unchecked)
        for widget in fils:
            widget.setVisible(state != Qt.Unchecked)


    def colour_selected(self, color, propriete):
        # conversion du format Qt au format matplotlib
        r, g, b, a = color.getRgb()
        self.changements[propriete] = (r/255, g/255, b/255, a/255)

    def spin_changed(self, value, propriete, widget, coeff):
        special_value = widget.specialValueText()
        if value == widget.minimum() and special_value:
            if special_value == ' ':
                # ' ' est affiché initialement lorsque tous les objets sélectionnés
                # n'ont pas la même valeur pour ce paramètre.
                # L'utilisateur peut remettre la valeur à ' ' manuellement
                # s'il ne souhaite plus modifier ce paramètre.
                del self.changements[propriete]
            else:
                self.changements[propriete] = special_value
        else:
            self.changements[propriete] = value/coeff

    def item_selected(self, index, propriete, liste):
        self.changements[propriete] = liste[index]


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
                        if mode is None:
                            # Conserver le mode formule, sinon basculer en mode TEXTE.
                            mode = (FORMULE if objet.mode_affichage == FORMULE else TEXTE)
                        self.canvas.executer(u"%s.label(%s, %s)" %(objet.nom, repr(label), mode))
                        self.radios[mode].setChecked(True)
                        # Le texte a pu changer (ajout automatique des accolades en mode formule)
                        self.etiquette.setText(objet.legende)
                    if changements:
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
            style.addWidget(QLabel(u"<span style='color:red;font-style:italic;'>Attention, ne modifiez ce contenu que si vous savez ce que vous faites.</span>"))
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
