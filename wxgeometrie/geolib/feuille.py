# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)
from __future__ import with_statement

##--------------------------------------#######
#                  Feuille                    #
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


# Ce module contient essentiellement la classe Feuille. C'est la classe qui va accueillir tous les objets geometriques.
# Elle fait l'intermediaire entre les objets et le Panel ou s'affichent les objets.

from keyword import kwlist
from random import choice
from string import letters
from math import pi as PI, e as E
from types import MethodType, GeneratorType, TypeType
from operator import attrgetter
import re
import time

from sympy import Symbol, Wild, sympify, oo

from ..pylib import uu, is_in, str3, property2, print_error, rstrip_, CompressedList
from ..mathlib.intervalles import Union, Intervalle
from ..mathlib.parsers import VAR, NBR_SIGNE, traduire_formule, \
                        _convertir_separateur_decimal

from .objet import Objet, contexte, souffler, G
from .angles import Secteur_angulaire
from .lignes import Segment
from .fonctions import Fonction
from .points import Point
from .cercles import Arc_generique
from .courbes import Courbe
from .textes import Texte
##from .labels import Label_generique
from .vecteurs import Vecteur_libre
from .variables import Variable, XMinVar, XMaxVar, YMinVar, YMaxVar, Dpx, Dpy
from .constantes import NOM, RIEN#, FORMULE,

from .pseudo_canvas import _pseudocanvas
from .. import param
from .. import mathlib
from ..pylib.securite import keywords_interdits_presents, keywords_interdits

PatternType = type(re.compile(''))


def is_equation(chaine):
    u"""Teste si une chaîne correspond bien à une équation."""
    if chaine.count('=') != 1:
        return False
    left, right = chaine.split('=')
    left = left.strip()
    if left.count('(') != left.count(')') or right.count('(') != right.count(')'):
        return False
    if not left or left[-1] in '-+':
        # Affectation. Ex: "=Point()"
        # Opérateurs `+=` et `-=`.
        return False
    if re.match('(%s|[.])+$' % VAR, left):
        # Affectation. Ex: `A = Point()`, `A.x = 3`,...
        # Deux exceptions cependant: `x =` et `y =` correspondent bien à des débuts d'équation.
        return left in ('x', 'y')
    return True

#assert geo.Objet is Objet

def parse_equation(chaine):
    u"""Associe à une équation l'objet géométrique correspondant.

    Vérifie que la chaîne est une équation, et retourne une chaîne
    correspondant à l'objet géométrique correspondant le cas échéant.
    Sinon, retourne l'objet initial.
    """
    #XXX: ébauche d'un parser d'équations
    # La première étape est de vérifier qu'il s'agit bien d'une équation,
    # et pas par exemple d'une affectation (par exemple, `A=Point()`)
    if not is_equation(chaine):
        return chaine

    left, right = chaine.split('=')
    chaine = left + '-(' + right + ')'
    chaine = traduire_formule(chaine, fonctions=mathlib.universal_functions.__dict__.keys())
    try:
        expr = sympify(chaine).expand()
    except Exception:
        print('Sympify: ' + chaine)
        raise
    x = Symbol('x')
    y = Symbol('y')
    a = Wild('a',exclude=[x, y])
    b = Wild('b',exclude=[x, y])
    c = Wild('c',exclude=[x, y])
    d = Wild('d',exclude=[x, y])
    e = Wild('e',exclude=[y])
    f = Wild('f',exclude=[y])
    droite = a*x + b*y + c
    # cercle: a((x - b)^2 + (y - c)^2 - d) = 0
    cercle = a*x**2 + a*y**2 - 2*a*b*x - 2*a*c*y + a*b**2 + a*c**2 - a*d
    m = expr.match(droite)
    if m:
        return "_ = Droite_equation(%s, %s, %s)" %(m[a], m[b], m[c])
    m = expr.match(cercle)
    if m and m[d].is_positive:
        b = m[b]
        c = m[c]
        d = m[d]
        return "_ = Cercle_equation(%s, %s, %s)" %(-2*b, -2*c, b**2 + c**2 - d)
    fonction = f*y - e
    m = expr.match(fonction)
    if m:
        return "_ = Courbe(Fonction(%s))" % repr(str(m[e]/m[f]))
    return chaine





class MethodesObjets(object):
    def __init__(self, nom_de_la_methode, *objets):
        self.methode = nom_de_la_methode
        self.objets = objets

    def __call__(self, *args, **kw):
        for objet in self.objets:
            getattr(objet, self.methode)(*args, **kw)



class Liste_objets(object):
    def __init__(self, feuille, classe):
        self.__dict__['feuille'] = feuille
        self.__dict__['classe'] = classe

    def __iter__(self):
        classe = self.classe
        return (obj for obj in self.feuille.liste_objets() if isinstance(obj, classe))

    def __setattr__(self, nom, valeur):
        for obj in self:
            setattr(obj, nom, valeur)

    def __delattr__(self, nom):
        for obj in self:
            delattr(obj, nom)

    def __getattr__(self, nom):
        if hasattr(self.classe, nom) and isinstance(getattr(self.classe, nom), MethodType):
            return MethodesObjets(nom, *self)
        return [getattr(obj, nom) for obj in self]


    def __str__(self):
        return self.classe.__name__.split("_")[0] + 's: ' + ', '.join(obj.nom for obj in self)

    __unicode__ = __repr__ = __str__


class ModeTolerant(object):
    u'''Mode d'exécution tolérant aux erreurs.
    Cela sert essentiellement à charger un fichier d'une ancienne version de WxGéométrie.'''
    def __init__(self, feuille, mode = True):
        self.feuille = feuille
        self.mode = mode

    def __enter__(self):
        object.__setattr__(self.feuille.objets, '_Dictionnaire_objets__renommer_au_besoin', self.mode)

    def __exit__(self, type, value, traceback):
        object.__setattr__(self.feuille.objets, '_Dictionnaire_objets__renommer_au_besoin', False)
        self.feuille.objets._Dictionnaire_objets__tmp_dict.clear()


class Dictionnaire_objets(dict):
    u"""Cette classe est un conteneur pour les objets de la feuille, qui sont tous ses attributs,
    sauf ceux précédés de __ (attributs reserves pour tous les objets de la classe).
    Elle contient aussi tous les objets geometriques.
    Certaines methodes standard (comme __setattr__) sont aussi interceptées ou redefinies.

    Attributs spéciaux:
    `_` fait référence au dernier objet enregistré dans la feuille.

    `_noms_restreints` est un dictionnaire contenant une liste de noms ou de patterns
    qui ne peuvent être associés qu'à certains types d'objets.
    `_noms_interdits` est une liste de noms correspondant à des objets en lecture
    seule.
    `_suppression_impossible` est une liste de noms d'objets qui ne peuvent pas
    être supprimés.

    Nota: lorsqu'une clef du dictionnaire est supprimée, la méthode `.supprimer()` de
    l'objet est appelée ; les objets qui n'ont pas de méthode `.supprimer()` sont donc
    de fait protégés (c'est le cas de `pi`, `e`, ...), sans qu'il soit nécessaire de
    les inscrire dans `_noms_interdits`.
    """

    __slots__ = ('feuille', '__timestamp', '__renommer_au_besoin', '__tmp_dict',
                 '_noms_restreints', '_noms_interdits', '_suppression_impossible')

    _noms_restreints = {re.compile('f[0-9]+(_prime)*$'): Fonction, 'xmin': XMinVar,
                      'xmax': XMaxVar, 'ymin': YMinVar, 'ymax': YMaxVar, 'dpx': Dpx,
                      'dpy': Dpy, re.compile('Cf[0-9]+$'): Courbe}

    # `kwlist`: noms réservés en python (if, then, else, for, etc.)
    _noms_interdits = kwlist + ['vue', 't', 'x', 'y', 'z']

    _suppression_impossible = ['xmin', 'xmax', 'ymin', 'ymax', 'dpx', 'dpy']

    def __init__(self, feuille):
        object.__setattr__(self, 'feuille', feuille)
        object.__setattr__(self, '_Dictionnaire_objets__timestamp', 0)
        object.__setattr__(self, '_Dictionnaire_objets__renommer_au_besoin', False)
        object.__setattr__(self, '_Dictionnaire_objets__tmp_dict', {})
        self['xmin'] = XMinVar()
        self['xmax'] = XMaxVar()
        self['ymin'] = YMinVar()
        self['ymax'] = YMaxVar()
        self['dpx'] = Dpx()
        self['dpy'] = Dpy()
        self.clear()


    def clear(self):
        u"""Réinitialise le dictionnaire des objets.

        Ne pas utiliser directement, mais utiliser plutôt `Feuille.effacer()`
        qui rafraichit correctement l'affichage."""
        _tmp = {}
        for nom in self._suppression_impossible:
            if dict.__contains__(self, nom):
                _tmp[nom] = dict.__getitem__(self, nom)
        dict.clear(self)
        dict.update(self, **_tmp)
        # On ajoute au dictionnaire courant les objets géométriques, et uniquement eux
        # (pas toutes les classes de geolib !)
        self.update((key, val) for key, val in G.__dict__.iteritems() \
                    if isinstance(val, type) and issubclass(val, Objet))
        # Les noms de classe peuvent aussi être tapés en minuscules (c'est plus rapide à taper)
        self.update((key.lower(), val) for key, val in G.__dict__.iteritems() \
                    if isinstance(val, type) and issubclass(val, Objet))

        # On ajoute au dictionnaire les fonctions mathématiques courantes
        self.update((key, val) for key, val in mathlib.universal_functions.__dict__.iteritems() \
                    if key[0] != "_" and key != "division")

        self.update(pi = PI, e = E, oo = oo, \
                    Intervalle = Intervalle, Union = Union, \
                    x = Symbol("x"), y = Symbol("y"), z = Symbol("z"), \
                    t = Symbol("t"))

        self.update(pause = self.feuille.pause, erreur = self.feuille.erreur,
                    effacer = self.feuille.effacer,
                    coder = self.feuille.coder, effacer_codage = self.feuille.effacer_codage,
                    nettoyer = self.feuille.nettoyer,
                    )
        dict.__setitem__(self, 'None', None)
        dict.__setitem__(self, 'True', True)
        dict.__setitem__(self, 'False', False)
        # NB: 'True = True' et 'False = False' : non compatible Py3k

        types = {'points': 'Point_generique', 'droites': 'Droite_generique', 'polygones': 'Polygone_generique',
                 'segments': 'Segment', 'cercles': 'Cercle_generique', 'arcs': 'Arc_generique',
                 'textes': 'Texte_generique', 'vecteurs': 'Vecteur_generique', 'variables': 'Variable'}
        d = {}
        for typ in types:
            d[typ] = Liste_objets(self.feuille, getattr(G, types[typ]))
        self.update(d)


    def add(self, valeur):
        u"""Ajoute l'objet `valeur` à la feuille.

        Un nom lui est automatiquement attribué."""
        self["_"] = valeur


    def _dereferencer(self, objet):
        u"Commande de bas niveau. Ne pas utiliser directement !"
        if objet._nom:
            self.pop(objet._nom)
            # Important: pour que l'objet soit bien considéré non référencé
            # il faut qu'il n'ait pas de nom (on ne peut pas référencer 2 fois un objet).
            objet._nom = ""


    def __setitem__(self, nom, valeur):
        u"""Crée un objet de la feuille nommé `nom`, et ayant pour valeur `valeur`.

        Remarque: les syntaxes `objets['a'] = 3` et `objets.a = 3` sont équivalentes.

        NB: Les objets d'une feuille (contrairement aux objets Python par exemple)
        ne peuvent pas être redéfinis librement...
        En général, quand on essaie d'attribuer un nom qui existe déjà,
        ce n'est pas volontaire. Pour éviter les erreurs, on impose de
        détruire explicitement l'objet avant que le nom puisse être redonné.

        Certains noms sont également réservés, et ne peuvent pas être
        attribués ainsi. Si l'on veut outrepasser la protection, il faut
        utiliser la méthode `.update()` pour les attribuer (à bon escient !).
        """

        # Paramètres du repère -> géré directement par la feuille
        if nom in self.feuille._parametres_repere:
            return setattr(self.feuille, nom, valeur)
            # Ne pas oublier le 'return' !

        nom = self.__convertir_nom(nom) or '_'

        # Pour certains types d'objets (points libres, textes, variables...),
        # le nom peut être déja attribué.
        # Par exemple, A=Point(1,2) est valide même si A existe déjà.
        # L'objet A ne sera pas écrasé, mais actualisé.
        # Dans cet exemple, les coordonnées de A sont actualisées en (1,2)
        # (Autrement dit, A=(1,2) devient un alias de A(1,2) ou A.coordonnees = 1,2).
        # Bien sûr, il faut en particulier que la valeur soit un objet de meme type.
        # (A = Variable(3) n'est pas valide si A est un point !)

        if self.has_key(nom):
            try:
                # Pour que les variables puissent être interprétées, il faut que la feuille soit donnée
                if isinstance(valeur, Objet) and valeur.feuille is None:
                    valeur.feuille = self.feuille
                self[nom]._update(valeur)
                #self.__refresh_needed(nom)
                return # on quitte, car le nom doit toujours référer à l'objet initial !
            except Exception:
                print_error()
                if self.__renommer_au_besoin:
                    new = self.feuille.nom_aleatoire(valeur, prefixe=nom)
                    print("Warning: '%s' renommé en '%s'." %(nom, new))
                    nom = self.__tmp_dict[nom] = new
                else:
                    self.erreur(u"Ce nom est d\xe9ja utilis\xe9 : " + nom, NameError)


        if not isinstance(valeur, Objet):
            # Permet de construire des points à la volée : '=((i,sqrt(i)) for i in (3,4,5,6))'
            if isinstance(valeur, GeneratorType) and nom == "_":
                for item in valeur:
                    self.__setitem__('', item)
                return

            # 'A = Point' est un alias de 'A = Point()'
            elif isinstance(valeur, TypeType) and issubclass(valeur, Objet):
                valeur = valeur()

            # Par convénience, certains types sont automatiquement convertis :
            # - Variable
            elif isinstance(valeur, (int, long, float, str, unicode)): # u=3 cree une variable
                valeur = Variable(valeur)

            # - Point
            elif isinstance(valeur, complex):
                valeur = Point(valeur.real, valeur.imag)

            elif hasattr(valeur, "__iter__"):
                valeur = tuple(valeur)
                # - Texte
                if len(valeur) in (1, 3) and isinstance(tuple(valeur)[0], basestring):
                    # t=["Bonjour!"] cree un texte
                    # t=('Bonjour!', 2, 3) également
                    valeur = Texte(*valeur)
                elif len(valeur) == 2:
                    # - Vecteur_libre
                    if nom.islower():
                        # u=(1,2) crée un vecteur
                        valeur = Vecteur_libre(*valeur)
                    # - Point
                    else:
                        # A=(1,2) cree un point.
                        valeur = Point(*valeur)

        if not isinstance(valeur, Objet):
            self.erreur("type d'objet incorrect :(%s,%s)"%(nom, valeur), TypeError)

        self.__verifier_syntaxe_nom(valeur, nom)

        if valeur._nom:
            # L'objet est déjà référencé sur la feuille ssi il a un nom.
            # On en fait alors une copie : ainsi, A = B est remplacé par A = B.copy()
            valeur = valeur.copy()


        # On enregistre le nom (éventuellement provisoire) car la méthode '_set_feuille' de l'objet en a besoin.
        valeur._nom = nom
        valeur.feuille = self.feuille

        if nom == "_":
            # Attention, la feuille doit être déjà definie !
            nom = valeur._nom_alea()
            # Pour les objets nommés automatiquement, le nom n'est pas affiché par défaut.
            if valeur.mode_affichage == NOM:
                valeur.label(mode = RIEN)

        # les objets commencant par "_" ne sont pas affichés par défaut (pure convention) :
        if nom[0] == "_":
            valeur.style(visible = False)

##        if is_in(valeur, self.itervalues()):
##            # si l'objet est deja reference sur la feuille, on en fait une copie.
##            valeur = valeur.copy() # ainsi, A = B est remplace par A = B.copy()

        dict.__setitem__(self, nom, valeur)
##        dict.__setattr__(self,  "__derniere_valeur__", weakref.ref(valeur))
        valeur._nom = nom
        valeur._timestamp = self.__timestamp
        object.__setattr__(self, "_Dictionnaire_objets__timestamp", self.__timestamp + 1)
##        valeur.creer_figure(True)
        self.feuille._actualiser_liste_objets = True
        self.feuille.affichage_perime()



    def __getitem(self, nom):
        u"""Usage interne: code commun aux méthodes `.__getitem__()` et `.get()`."""
        # renommage temporaire :
        nom = self.__tmp_dict.get(nom, nom)
        # (utilisé en cas de chargement d'un fichier ancien lors d'un conflit de nom).
        if nom in self.feuille._parametres_repere:
            return getattr(self.feuille, nom)
        elif nom == "objets":
            return self()
        elif nom == "noms":
            return self.noms
        elif nom == "_":
            return self.__derniere_valeur()
        return dict.__getitem__(self, self.__convertir_nom(nom))


    def __getitem__(self, nom):
        try:
            return self.__getitem(nom)
        except KeyError:
            if nom == 'bogu5_123_aTTri8ute' and contexte['afficher_messages']:
                # PyShell détecté, désactivation des messages d'erreur...
                contexte['afficher_messages'] = False
            else:
                assert 'erreur' in self
                self.erreur(u"Objet introuvable sur la feuille : " + nom, KeyError)

    def get(self, nom, defaut=None):
        try:
            return self.__getitem(nom)
        except:
            return defaut


    def __contains__(self, nom):
        return dict.__contains__(self, self.__convertir_nom(nom))


    def __delitem__(self, nom):
        if nom in self.feuille._parametres_repere:
            return delattr(self.feuille, nom)
            # ne pas oublier le 'return'
        elif nom == "_":
            self.__derniere_valeur().supprimer()
        else:
            try:
                self[nom].supprimer()
            except KeyError:
                if param.debug:
                    print_error()
        self.feuille._actualiser_liste_objets = True
        self.feuille.affichage_perime()


    __setattr__ = __setitem__
    __delattr__ = __delitem__
    __getattr__ = __getitem__


    def lister(self, objets_caches=True, etiquettes=False, **kw):
        u"""Retourne la liste des objets géométriques.

        Le paramètre `objets_caches` indique s'il faut inclure les objets cachés.

        Le paramètre `etiquettes` indique s'il faut inclure les étiquettes
        des objets retournés.

        kw:
        * `type` : types à inclure
        * `sauf` : types à exclure

        note:: Utiliser plutôt `Feuille.liste_objets()`, qui bénéficie d'une mise
               en cache des résultats.
        """
        sauf = kw.get("sauf", ())
        type = kw.get("type", Objet)
        objets = []
        for objet in self.values():
            if isinstance(objet, type) and not isinstance(objet, sauf) \
                and (objets_caches or objet._style['visible']):
                    objets.append(objet)
                    if etiquettes and objet.etiquette is not None:
                        objets.append(objet.etiquette)
        return objets

        ##if kw:
            ##sauf = kw.get("sauf", ())
            ##type = kw.get("type", Objet)
            ##objets = [obj for obj in self.values() if isinstance(obj, type) \
                    ##and not isinstance(obj, sauf) and (objets_caches or obj.style("visible"))]
        ##elif objets_caches:
            ##objets = [obj for obj in self.values() if isinstance(obj, Objet)]
        ##else:
            ##objets = [obj for obj in self.values() if isinstance(obj, Objet) and obj.style("visible")]


    def supprimer(self, *objets):
        u"""Supprime plusieurs objets dans le bon ordre.

        Supprime successivement plusieurs objets après les avoir classé
        hiérarchiquement. Cela évite d'avoir des erreurs avec certains
        objets déjà supprimés avec les précédents du fait des dépendances.

        Par exemple, `del feuille.objets.A, feuille.objets.B` renvoie une
        erreur si l'objet `B` dépend de l'objet `A`, car l'objet `B`
        n'existe déjà plus au moment où on cherche à le supprimer.

        Nota: La suppression d'un objet qui n'est pas sur la feuille
        provoque bien toujours une erreur, par contre."""
        for obj in sorted(objets, key=attrgetter("_hierarchie"), reverse=True):
            obj.supprimer()

    @property
    def noms(self):
        u"""Retourne les noms de tous les objets géométriques."""
        return set(nom for nom, obj in self.items() if isinstance(obj, Objet))


    @staticmethod
    def __convertir_nom(nom):
        u'''Convertit les noms contenant des `, ', ou " en noms python corrects.'''
        return nom.replace('`', '_prime').replace('"', '_prime_prime').replace("'", "_prime")


    def __match(self, pattern, nom):
        if isinstance(pattern, PatternType):
            return re.match(pattern, nom)
        else:
            return nom == pattern

    def __verifier_syntaxe_nom(self, objet, nom, **kw):
        u"Vérifie que le nom est correct (ie. bien formé) et le modifie le cas échéant."

        def err(msg):
            if kw.get('skip_err'):
                return
            if self.__renommer_au_besoin:
                new = self.feuille.nom_aleatoire(objet)
                print(u"Warning: '%s' renommé en '%s'." %(nom, new))
                return new
            else:
                self.erreur(msg, NameError)

        if nom == '':
            return '_'
        nom = self.__convertir_nom(nom)

        if nom in self.__class__.__dict__.keys() \
                          or any(self.__match(pattern, nom) for pattern in self._noms_interdits):
            return err(u"Nom r\xe9serv\xe9 : " + nom) # Pas d'accent dans le code ici a cause de Pyshell !
        # Les noms contenant '__' sont des noms réservés pour un usage futur éventuel (convention).
        if "__" in nom:
            return err(u'Un nom ne peut pas contenir "__".')
        if not re.match("""[A-Za-z_][A-Za-z0-9_'"`]*$""", nom):
            return err(u"'%s' n'est pas un nom d'objet valide." %nom)

        # Certains noms sont réservés à des usages spécifiques.
        # Par ex., les noms f1, f2... sont réservés aux fonctions (cf. module Traceur).
        for pattern, types in self._noms_restreints.iteritems():
            if self.__match(pattern, nom):
                if isinstance(objet, types):
                    break
                return err(u"Le nom %s est r\xe9serv\xe9 à certains types d'objets." %nom)

        # Gestion des ' (qui servent pour les dérivées)
        if nom.endswith('_prime'):
            if isinstance(objet, Fonction):
                return err(u'Nom interdit : %s est r\xe9serv\xe9 pour la d\xe9riv\xe9e.' %nom)
            else:
                base = rstrip_(nom, '_prime')
                if isinstance(self.get(base, None), Fonction):
                    return err(u'Nom interdit : %s d\xe9signe d\xe9j\xe0 la d\xe9riv\xe9e de %s.' %(nom, base))
        elif isinstance(objet, Fonction):
            # Si la fonction doit s'appeller f, on vérifie que f', f'', f''', etc. ne correspondent pas déjà à des objets.
            for existant in self:
                if existant.startswith(nom) and rstrip_(existant, '_prime') == nom:
                    return err(u'Ambiguit\xe9 : un objet %s existe d\xe9j\xe0.' %existant)

        return nom


    def _objet_renommable(self, objet, nom):
        u"Vérifie que le nom peut-être attribué (c-à-d. qu'il est bien formé, et non utilisé)."
        nom = self.__verifier_syntaxe_nom(objet, nom)
        if self.has_key(nom):
            self.erreur(u"Ce nom est déjà utilisé.", NameError)
        return nom


    def __str__(self):
        return "Gestionnaire d'objets de la feuille '" + self.feuille.nom \
                    + "': " + str(self.noms)

    def __repr__(self):
        return "Gestionnaire d'objets de la feuille '" + self.feuille.nom \
                    + "': " + repr(self.noms)

    def __derniere_valeur(self):
        u"Dernier objet créé."
        return max(self.feuille.liste_objets(True), key = lambda obj:obj._timestamp)






class Interprete_feuille(object):
    u"""Exécute des commandes dans la feuille.

    Reformule également les commandes avant de les exécuter."""

    def __init__(self, feuille):
        self.feuille = feuille

    def executer(self, commande, parser=True, signature=None):
        u"""Exécute la commande dans la feuille.

        Si parser=False, les facilités de syntaxe (abréviations, etc.)
        sont désactivées pour plus de rapidité.

        Si signature != None, elle est utilisée pour la gestion de l'historique."""
        if parser:
            commande = self.parser(commande)

        if param.debug:
            self.feuille.save_log("REQUETE FEUILLE: " + commande)

        # À mettre en toute fin, pour des raisons de sécurité.
        if keywords_interdits_presents(commande):
            self.erreur("Mots-clefs interdits : " + ", ".join(sorted(keywords_interdits)))
        try:
            code = compile(commande, '<string>', 'eval')
            val = eval(code, self.feuille.objets)
            if isinstance(val, Variable):
                if val._type == "simple":
                    retour = unicode(val.val)
                else:
                    retour = '"' + val.contenu + '" : ' + unicode(val.val)
            elif isinstance(val, (list, tuple, set)):
                # Améliore la lisibilité de l'affichage pour une liste d'objets
                # en affichant le nom des objets au lieu des objets eux-mêmes
                # (pour ceux qui ont un nom).
                if isinstance(val, list):
                    retour = '['
                elif isinstance(val, set):
                    retour = 'set(['
                else:
                    retour = '('
                for elt in val:
                    if isinstance(elt, Objet):
                        nom = elt.nom
                        retour += (nom if nom else str(elt))
                    else:
                        retour += repr(elt)
                    retour += ', '
                retour = retour.rstrip(', ')
                if isinstance(val, list):
                    retour += ']'
                elif isinstance(val, set):
                    retour += '])'
                else:
                    retour += ')'
            else:
                retour = unicode(val)
        except SyntaxError:
            exec(commande + '\n', self.feuille.objets)
            # Le + '\n' final contourne un bug de Python 2.5 avec with_statement
            retour = u'Commande exécutée.'
        finally:
            self.commande_executee(signature = signature)
        return retour

    def commande_executee(self, signature = None):
        u"""Méthode appelée automatiquement après avoir exécuté une commande dans la feuille.
        Si l'on n'a pas utilisé la méthode executer(), il faut alors l'appeler manuellement."""
        self.feuille.historique.archiver(signature = signature)
        # TODO: A déplacer dans la console graphique d'exécution ?
        # Redétection des objets à proximité du pointeur
        self.feuille.canvas.redetecter = True
        if self.feuille.classeur is not None and self.feuille.classeur.parent is not None:
            self.feuille.classeur.parent.rafraichir_titre()
        for action in self.feuille._actions:
            action()


    @staticmethod
    def parser(commande):
        u"""Convertit la commande en code Python.

        >>> from wxgeometrie.geolib.feuille import Interprete_feuille
        >>> Interprete_feuille.parser("[A B]")
        'Segment(A, B)'
        >>> Interprete_feuille.parser("(A B)")
        'Droite(A, B)'
        """

        commande = commande.strip()

        while '  ' in commande:
            commande = commande.replace('  ', ' ')

        if commande.startswith("="):
            commande = "_" + commande

        if commande == "del":
            commande += " _"

        # Gestion des '
        # NB: attention, \' a déjà un sens en LaTeX
        commande = commande.replace("'", "_prime").replace("\\_prime", "\\'")


        # Exception à la conversion décimale :
        # (1,2) est compris comme (1 ; 2) et non (1.2), qui est très peu probable.
        def _virg(m):
            return m.group().replace(',', ', ')
        commande = re.sub(r'[(]%s,%s[)]' % (NBR_SIGNE, NBR_SIGNE), _virg, commande)
        # Conversion décimale : 1,2 -> 1.2
        commande = _convertir_separateur_decimal(commande)

        # (A B) -> Droite(A, B)
        def _dte(m):
            return "Droite(%s, %s)" % m.groups()
        commande = re.sub(r"\([ ]?(%s)[ ](%s)[ ]?\)" % (VAR, VAR), _dte, commande)

        # [A B] -> Segment(A, B)
        def _seg(m):
            return "Segment(%s, %s)" % m.groups()
        commande = re.sub(r"\[[ ]?(%s)[ ](%s)[ ]?\]" % (VAR, VAR), _seg, commande)

        # ||u|| -> u.norme
        def _normu(m):
            return "%s.norme" % m.groups()
        commande = re.sub(r"\|\|[ ]?(%s)[ ]?\|\|" % VAR, _normu, commande)

        # ||A>B|| -> (A>B).norme
        def _normAB(m):
            return "(%s>%s).norme" % m.groups()
        commande = re.sub(r"\|\|[ ]?(%s)>(%s)[ ]?\|\|" % (VAR, VAR), _normAB, commande)

        # 1,2 ou 1;2 ou 1 2 ou (1,2) ou (1;2) ou (1 2) *uniquement* -> Point(1,2)
        m = re.match("(\()?(?P<x>%s)[ ]?[;, ][ ]?(?P<y>%s)(?(1)\))$" % (NBR_SIGNE, NBR_SIGNE), commande)
        if m:
            commande = "Point(%(x)s,%(y)s)" % m.groupdict()

        # `Bonjour !` -> Texte("Bonjour !")
        # NB: attention, \` a déjà un sens en LaTeX
        def _txt(m):
            return "Texte(\"%s\")" % m.groups()[0]
        commande = re.sub(r"(?<!\\)`(([^`]|\\`)*[^`\\]|)`", _txt, commande)

        # Détection des équations
        if '=' in commande:
            commande = parse_equation(commande)

        return commande





class Historique_feuille(object):
    u"""Historique de la feuille.

    Permet d'enregistrer l'état de la feuille à un instant donné,
    et de le restaurer ensuite."""

    def __init__(self, feuille):
        self.feuille = feuille
        # taille maximale
        self.n = param.nbr_annulations
        self.etats = CompressedList()
        self.archiver()
        # pour comparer rapidement
        self.last_hash = None
        # à placer après self.archiver() !
        self.feuille.vierge = True


    def archiver(self, signature = None):
        sauvegarde = self.feuille.sauvegarder()
        # On évite de stocker deux fois de suite la même chose dans l'historique.
        if self.etats and hash(sauvegarde) == self.last_hash and sauvegarde == self.etats[-1]:
            return

        # Avec la molette de la souris, on effectue une succession rapide de zooms.
        # Pour éviter que ça ne remplisse l'historique, on archive alors l'état actuel
        # à la place du précedent. Ceci s'effectue grâce à la signature.
        # De manière générale, si signature != None, lorsque deux demandes d'archivages
        # successives parviennent avec la même signature, la seconde écrase la première.
        if signature is not None and self._derniere_signature == signature:
            self.etats[-1] = sauvegarde
        else:
            self.etats.append(sauvegarde)
        self.etats_annules = CompressedList()
        if len(self.etats) > self.n:
            self.etats.pop(0) # plus rapide que "self.etats = self.etats[-self.n:]"
        self._derniere_signature = signature
        self.last_hash = hash(signature)
        self.feuille.vierge = False
        self.feuille.modifiee = True

    def annuler(self):
        if len(self.etats) > 1:
            etat_actuel = self.etats.pop()
            self.etats_annules.append(etat_actuel)
            if len(self.etats_annules) > self.n:
                self.etats_annules.pop(0) # plus rapide que "self.etats_annules = self.etats_annules[-self.n:]"
            self.restaurer(self.etats[-1])
            self.feuille.message(u"Action annulée.")
            self.feuille.modifiee = True
        else:
            self.feuille.message(u"Impossible d'annuler.")


    def refaire(self):
        if self.etats_annules:
            etat = self.etats_annules.pop()
            self.etats.append(etat)
            if len(self.etats) > self.n:
                self.etats.pop(0) # plus rapide que "self.etats = self.etats[-self.n:]"
            self.restaurer(etat)
            self.feuille.message(u"Action restaurée.")
            self.feuille.modifiee = True
        else:
            self.feuille.message(u"Impossible de restaurer.")


    def restaurer(self, txt):
        self.feuille.effacer()
        self.feuille.charger(txt, archiver = False)










class Feuille(object):
    u"""Feuille de travail.

    L'objet 'log' doit être une liste destinée à contenir tous les messages.
    """
    # Pour limiter les erreurs, on indique le(s) type(s) autorisé
    # pour chaque paramètre.
    _parametres_repere = {"quadrillages": tuple,
                        "afficher_quadrillage": bool,
                        "afficher_axes": bool,
                        "afficher_fleches": bool,
                        "repere": tuple,
                        "gradu": tuple,
                        "utiliser_repere": bool,
                        "liste_axes": tuple,
                        "orthonorme": bool,
                        "fenetre": tuple,
                        "zoom_texte": (int, float),
                        "zoom_ligne": (int, float),
                        "afficher_objets_caches": bool,
                        }

    def __hash__(self):
        return id(self)

    def __init__(self, classeur = None, titre = "", log = None, parametres = None, canvas = None):
        self.log = log
        self.classeur = classeur
        self.__canvas = canvas
##        self._fenetre =  self.param("fenetre")

        # Gestion des paramètres graphiques (repère essentiellement)
        self.__dict_repere = {}
        if parametres is None:
            parametres = {}
        for nom in self._parametres_repere:
            self.__dict_repere[nom] = parametres.get(nom, self.parametres_par_defaut(nom))

        self.macros = {}
        self._cache_listes_objets = {}
        self._actualiser_liste_objets = True
##        self._mettre_a_jour_figures = True
        self._affichage_a_actualiser = True
        self._repere_modifie = True
        self._objets_temporaires = []
        self.__point_temporaire__ = None
        # Permet une optimsation de l'affichage en cas d'objet déplacé
        self._objet_deplace = None
        # On met ._stop à True pour stopper toutes les animations en cours.
        self._stop = False
##        self._afficher_objets_caches = False
##        # Indique que l'arrière-plan doit être redessiné
##        self._repere_modifie = True

        # Parametres permettant de gerer l'enregistrement:
        self.sauvegarde = {
                    "_modifie": True,            # modifications depuis dernière sauvegarde
                    "repertoire": None,         # répertoire de sauvegarde
                    "nom": None,          # nom de sauvegarde
                    "export": None,        # nom complet utilisé pour l'export
                    }
        # (À créer *avant* l'historique de la feuille)

        self.objets = Dictionnaire_objets(self)
        self.historique = Historique_feuille(self)
        self.interprete = Interprete_feuille(self)


        # Informations sur le document
        self._infos = {
            "titre": titre,
            "auteur": param.utilisateur,
            "creation": time.strftime("%d/%m/%Y - %H:%M:%S",time.localtime()),
            "modification": time.strftime("%d/%m/%Y - %H:%M:%S",time.localtime()),
            "version": "",
            "resume": "",
            "notes": "",
            }

        # Actions à effectuer après qu'une commande ait été exécutée.
        self._actions = []


#        Objet.__feuille__ = self # les objets sont crees dans cette feuille par defaut

# ---------------------------------------
#    Gestion des paramètres du repère
# ---------------------------------------

    def lier(self, action):
        if not is_in(action, self._actions):
            self._actions.append(action)

    def affichage_perime(self):
        u"""Indique que l'affichage doit être actualisé.

        Très rapide (inutile d'optimiser les appels), car aucune actualisation
        n'a lieu, mais la feuille est juste marquée comme étant à actualiser."""
        # NB: Utiliser une méthode au lieu d'un attribut permet de générer
        # une erreur en cas de faute de frappe.
        self._affichage_a_actualiser = True

    @property2
    def modifiee(self, val = None):
        if val is None:
            return self.sauvegarde['_modifie']
        self.sauvegarde['_modifie'] = val
        if val and self.classeur is not None:
            self.classeur.modifie = True

    def infos(self, _key_ = None, **kw):
        if kw:
            self._infos.update(kw)
            self.modifiee = True
        elif _key_ is None:
            return self._infos.copy()
        else:
            return self._infos[_key_]

    def _rafraichir_figures(self, tous_les_objets = False):
        u"""Recrée les figures des objets sensibles à la fenêtre d'affichage.

        Si tous_les_objets = True, les figure des objets non sensibles sont
        aussi récréées.
        Par ailleurs, le rafraichissement n'a pas lieu immédiatement, mais
        les figures sont simplement marquées comme périmées, et seront
        rafraichies à la prochaine utilisation.

        En principe, cette méthode n'a pas à être appelée directement.
        """
        for objet in self.liste_objets():
            # Il faut recalculer la position de toutes les étiquettes
            # quand la fenêtre d'affichage change.
            if objet._affichage_depend_de_la_fenetre:
                objet.figure_perimee()
            elif objet.etiquette:
                # Même si tous les objets n'ont pas besoin d'être rafraichis,
                # leurs étiquettes doivent l'être
                objet.etiquette.figure_perimee()


    def _gerer_parametres_repere(self, item = None, **kw):
        if kw:
            self.__dict_repere.update(kw)
            self._repere_modifie = True
            if 'fenetre' in kw or 'orthonorme' in kw:
                self.fenetre_modifiee()
##                self._mettre_a_jour_figures = True
            if 'afficher_objets_caches' in kw:
                for objet in self.liste_objets(True):
                    if not objet.style('visible'):
                        objet.figure_perimee()
                self._actualiser_liste_objets = True
            self.affichage_perime()
        if item is not None:
            return self.__dict_repere[item]

##    @property2
##    def afficher_objets_caches(self, valeur = None):
##        if valeur is not None:
##            self._afficher_objets_caches = valeur
##            for objet in self.liste_objets(True):
##                if not objet.style('visible'):
##                    objet.creer_figure()
##            self._actualiser_liste_objets = True
##        return self._afficher_objets_caches


    def __getattr__(self, nom):
        # Les parametres du repere
        if nom in self._parametres_repere:
            return self._gerer_parametres_repere(nom)
        return object.__getattribute__(self, nom)


    def __setattr__(self, nom, valeur):
        if nom in self._parametres_repere:
            # TODO: améliorer la détection des valeurs incorrectes
            assert isinstance(valeur, self._parametres_repere[nom])
            # tests personnalisés pour certains paramètres
            nom_test = '_test_valeur_' + nom
            if hasattr(self, nom_test):
                valeur = getattr(self, nom_test)(valeur)
            self._gerer_parametres_repere(**{nom: valeur})
        else:
            object.__setattr__(self, nom, valeur)

    def __delattr__(self, nom):
        if nom in self._parametres_repere:
            self._gerer_parametres_repere(**{nom: self.parametres_par_defaut(nom)})
        else:
            object.__delattr__(self, nom)

    def _test_valeur_fenetre(self, valeur):
        xmin, xmax, ymin, ymax = valeur
        xmin = xmin if xmin is not None else self.fenetre[0]
        xmax = xmax if xmax is not None else self.fenetre[1]
        ymin = ymin if ymin is not None else self.fenetre[2]
        ymax = ymax if ymax is not None else self.fenetre[3]
        epsilon = 100*contexte['tolerance']
        if abs(xmax - xmin) < epsilon:
            self.erreur(u"Le réglage de la fenêtre est incorrect (xmin et xmax sont trop proches).\n"
                        u"(Les paramètres doivent être dans cet ordre: xmin, xmax, ymin, ymax.)", ValueError)
        elif abs(ymax - ymin) < epsilon:
            self.erreur(u"Le réglage de la fenêtre est incorrect (ymin et ymax sont trop proches).\n"
                        u"(Les paramètres doivent être dans cet ordre: xmin, xmax, ymin, ymax.)", ValueError)
        # Les 'float()' servent à contourner un bug de numpy 1.1.x et numpy 1.2.x (repr de float64)
        return float(min(xmin, xmax)), float(max(xmin, xmax)), float(min(ymin, ymax)), float(max(ymin, ymax))

    @property2
    def xmin(self, value = None):
        if value is None:
            return self.fenetre[0]
        self.fenetre = value, None, None, None

    @property2
    def xmax(self, value = None):
        if value is None:
            return self.fenetre[1]
        self.fenetre = None, value, None, None

    @property2
    def ymin(self, value = None):
        if value is None:
            return self.fenetre[2]
        self.fenetre = None, None, value, None

    @property2
    def ymax(self, value = None):
        if value is None:
            return self.fenetre[3]
        self.fenetre = None, None, None, value


    def fenetre_modifiee(self):
        self.objets.xmin.perime()
        self.objets.xmax.perime()
        self.objets.ymin.perime()
        self.objets.ymax.perime()
        self.objets.dpx.perime()
        self.objets.dpy.perime()
        # XXX: il ne devrait pas y avoir besoin d'appeler la méthode suivante :
        self._rafraichir_figures()


#########################################################################################


    def liste_objets(self, objets_caches=None, tri=False, etiquettes=False):
        u"""Liste des objets, triés éventuellement selon le style 'niveau'.

        NB: un système de mise en cache est utilisé si possible, contrairement à .objets.lister().
        """
        if self._actualiser_liste_objets:
            for key in self._cache_listes_objets:
                self._cache_listes_objets[key] = None
        if objets_caches is None:
            objets_caches = self.afficher_objets_caches
        # 4 caches, correspondants aux 4 situations possibles :
        # objets_caches = True, trier = True ;
        # objets_caches = True, trier = False ; etc.
        clef = 'c' if objets_caches else ''
        if tri:
            clef += 't'
        if etiquettes:
            clef += 'e'
        objets = self._cache_listes_objets.get(clef)
        if objets is None:
            liste = self.objets.lister(objets_caches=objets_caches, etiquettes=etiquettes)
            if tri:
                # Exceptionnellement, on utilise '._style' au lieu de '.style'
                # car le gain de temps est significatif.
                liste.sort(key=(lambda x:x._style["niveau"]), reverse=True)
            objets = self._cache_listes_objets[clef] = liste
        return objets




#########################################################################################

    @property2
    def canvas(self, val = None):
        if val is None:
            if self.__canvas is not None:
                return self.__canvas
            elif getattr(getattr(self.classeur, 'parent', None), 'canvas', None) is not None:
                return self.classeur.parent.canvas
            return _pseudocanvas

        self.__canvas = val

    # TODO: à réécrire
    # les paramètres par défaut de geolib doivent être contenus dans geolib lui-même.
    def parametres_par_defaut(self, nom):
        if getattr(self.classeur, "parent", None) is not None:
            return self.classeur.parent.param(nom)
        else:
            return getattr(param, nom)

    @property
    def parametres(self):
        return self.__dict_repere.copy()

    @property
    def nom(self):
        u"Destiné à être affiché."
        nom = self.infos("titre")
        if self.sauvegarde["nom"]:
           nom += ' - ' + self.sauvegarde["nom"]
        return nom or "Feuille"


    @property
    def nom_complet(self):
        u"Destiné à être affiché en haut de la fenêtre."
        nom = self.modifiee and "* " or ""
        liste = self.sauvegarde["nom"], self.infos("titre")
        nom += " - ".join(s for s in liste if s)
        return nom



    def objet(self, nom):    # retourne l'objet associe au nom "nom"
        return self.objets[nom]



#######################################################################################

# Methodes se rapportant a la feuille elle-meme

    ##def sauvegarder(self):
        ##u"Renvoie l'ensemble des commandes python qui permettra de recréer la figure avec tous ses objets."
##
        ##objets = self.liste_objets(True)
        ### on doit enregistrer les objets dans le bon ordre (suivant la _hierarchie) :
        ##objets.sort(key = attrgetter("_hierarchie_et_nom"))
##
        ##texte = '\n'.join(nom + ' = ' + repr(getattr(self, nom))
                         ##for nom in self._parametres_repere
                         ##) + '\n'
##
        ##a_rajouter_a_la_fin = ""
##
        ##for objet in objets:
            ##if not objet._enregistrer_sur_la_feuille:
                ##continue
            ##elif isinstance(objet, Texte) and objet.style("legende") == FORMULE:
                ### on fait un cas particulier pour les objets Texte, car ils peuvent contenir une formule
                ### qui dépend d'autres objets. Leur style n'est alors appliqué qu'après.
                ##texte += objet.nom + " = " + objet.__repr__(False) + "\n"
                ##a_rajouter_a_la_fin += objet.nom + ".style(**" + repr(objet.style()) + ")\n"
            ##else:
                ##texte += objet.nom + " = " + repr(objet) + "\n"
##
        ### Les étiquettes peuvent contenir des formules qui dépendent d'autres objets.
        ##for objet in objets:
            ##if objet.etiquette is not None:
                ##texte += objet.nom + ".etiquette.style(**" + repr(objet.etiquette.style()) + ")\n"
##
        ##return texte + a_rajouter_a_la_fin


    def sauvegarder(self):
        u"""Renvoie l'ensemble des commandes python qui permettra de recréer
        la figure avec tous ses objets.

        La figure pourra ensuite être restaurée à l'aide la commande `charger()`.

        :rtype: string
        """

        # On sauvegarde les paramètres de la feuille.
        texte = '\n'.join(nom + ' = ' + repr(getattr(self, nom))
                         for nom in self._parametres_repere
                         ) + '\n\n'

        # Enfin, on sauvegarde les objets de la feuille.
        # On doit enregistrer les objets dans le bon ordre (suivant la _hierarchie).
        objets = sorted(self.liste_objets(objets_caches=True, etiquettes=True),
                                key=attrgetter("_hierarchie_et_nom"))
        return texte + ''.join(obj.sauvegarder() for obj in objets
                                            if obj._enregistrer_sur_la_feuille)

    def effacer(self):
        self.objets.clear()
        self.affichage_perime()


    def charger(self, commandes, rafraichir = True, archiver = True,
                                 mode_tolerant = False):
        u"""Exécute un ensemble de commandes dans la feuille.

        Usage:
        f = Feuille()
        ...
        commandes = f.sauvegarder()
        f.effacer()
        f.charger(commandes)
        """
        with self.canvas.geler_affichage(actualiser=rafraichir, sablier=rafraichir):
            with ModeTolerant(self, mode_tolerant):
                try:
                    exec(commandes, self.objets)
                except:
                    print "Liste des commandes:"
                    print "--------------------"
                    print commandes
                    print "--------------------"
                    try:
                        print_error()
                    except:
                        print u"Affichage de l'erreur impossible !"
                    self.erreur(u"Chargement incomplet de la feuille.")
                finally:
                    for action in self._actions:
                        action()
                    if archiver:
                        self.historique.archiver()


    def executer(self, commande, parser = True):
        return self.interprete.executer(commande, parser = parser)


    def redefinir(self, objet, valeur):
        nom = objet.nom
        # on récupère la liste des arguments, et on la formate...
        args = valeur.strip()[valeur.find("("):-1] + ",)"
        # ...de manière à obtenir un objet 'tuple' en l'évaluant.
        args = eval(args, self.objets) # utiliser evalsafe à la place ?
        heritiers = objet._heritiers()
        heritiers.add(objet)
        for arg in args:
            if isinstance(arg, Objet):
                for heritier in heritiers:
                    if arg is heritier:
                        self.erreur(u"Définition circulaire dans %s : \
                                   l'objet %s se retrouve dépendre de lui-même."
                                   %(valeur, nom))
                        #raise RuntimeError, "Definition circulaire dans %s : l'objet %s se retrouve dependre de lui-meme." %(valeur, nom)
        actuel = self.sauvegarder()
        # Utiliser '.copier_style()' et non '.style()' car le type de l'objet
        # a pu changer, auquel cas il ne faut copier que les styles qui ont
        # du sens pour le nouveau type d'objet.
        valeur += "\n%s.copier_style(%s)" % (nom, repr(objet))
        old = "\n" + objet.sauvegarder()
        assert old in actuel
        nouveau = actuel.replace(old, "\n%s=%s\n" % (nom, valeur))
        if param.debug:
            print(nouveau)
        try:
            self.historique.restaurer(nouveau)
        except Exception:
            print_error()
            self.historique.restaurer(actuel)
            self.erreur(u"Erreur lors de la redéfinition de %s." %nom)



    def inventaire(self):
        if param.debug:
            for obj in self.liste_objets(True):
                print "- " + obj.nom + " : " + repr(obj) + " (" + obj.type() + ")"
        liste = [uu(obj.nom_complet) + u" (" + uu(obj.titre(point_final = False))
                + (not obj.style("visible") and u" invisible)" or u")") for obj in self.liste_objets(True)]
        liste.sort()
        return liste

    def nettoyer(self):
        u"""Supprime les objets cachés inutiles.

        Un objet caché est inutile si aucun objet visible ne dépend de lui."""
        objets = sorted((obj for obj in self.liste_objets(True) if not obj.visible),
                            key = attrgetter("_hierarchie"), reverse = True)
        for obj in objets:
            if obj.nom not in self.objets._suppression_impossible:
                if not any(self.contient_objet(heritier) for heritier in obj._heritiers()):
                    obj.supprimer()

    def effacer_codage(self):
        u"Efface tous les codages sur les segments, angles et arcs de cercles."
        for obj in self.liste_objets(True):
            if obj.style("codage") is not None:
                obj.style(codage = "")
##                obj.figure_perimee()
##        self.affichage_perime()

    def coder(self):
        u"Codage automatique de la figure (longueurs égales, angles égaux, et angles droits)."
        def test(groupe, liste, i):
            if len(groupe) is 1:
                groupe[0]["objet"].style(codage = "")
##                groupe[0]["objet"].creer_figure()
                return False
            else:
                try:
                    for elt in groupe:
                        elt["objet"].style(codage = liste[i])
##                        elt["objet"].creer_figure()
                    return True
                except IndexError:
                    self.message(u"Le nombre de codages disponibles est insuffisant.")
                    print_error(u"Le nombre de codages disponibles est insuffisant.")

        objets = self.objets.lister(False, type = (Segment, Arc_generique))
        lignes = [{"longueur": obj._longueur(), "objet": obj} for obj in objets]
        if lignes:
            lignes.sort() # attention, le classement d'un dictionnaire se fait selon l'ordre alphabétique des clefs
            groupe = [lignes[0]]
            i = 1
            for ligne in lignes[1:]:
                if abs(groupe[-1]["longueur"] - ligne["longueur"]) < contexte['tolerance']:
                    groupe.append(ligne)
                else:
                    resultat = test(groupe, param.codage_des_lignes, i)
                    if resultat is None:
                        break
                    if resultat:
                        i += 1
                    groupe = [ligne]
            test(groupe, param.codage_des_lignes, i)


        objets = self.objets.lister(False, type = Secteur_angulaire)
        angles = [{"angle": obj.val, "objet": obj} for obj in objets]
        if angles:
            angles.sort() # attention, le classement d'un dictionnaire se fait selon l'ordre alphabétique des clefs
            groupe = [angles[0]]
            i = 2
            for angle in angles[1:]:
                if abs(groupe[-1]["angle"] - angle["angle"]) < contexte['tolerance']:
                    groupe.append(angle)
                else:
#                    print abs(abs(groupe[-1]["angle"]) - pi/2)
                    if abs(abs(groupe[-1]["angle"]) - PI/2) < contexte['tolerance']:
                        for elt in groupe:
                            elt["objet"].style(codage = "^")
##                            elt["objet"].creer_figure()
                    else:
                        resultat = test(groupe, param.codage_des_angles, i)
                        if resultat is None:
                            break
                        if resultat:
                            i += 1
                    groupe = [angle]
            if abs(abs(groupe[-1]["angle"]) - PI/2) < contexte['tolerance']:
                for elt in groupe:
                    elt["objet"].style(codage = "^")
##                    elt["objet"].creer_figure()
            else:
                test(groupe, param.codage_des_angles, i)

        self.affichage_perime()


    def objet_temporaire(self, objet = False):
        if objet is not False:
            if self._objets_temporaires:
#                obj = self._objets_temporaires[0]
                self.affichage_perime()
            if objet is None:
                self._objets_temporaires = []
            else:
                objet.feuille = self
                self._objets_temporaires = [objet]
        return self._objets_temporaires


    def contient_objet(self, objet):
        """contient_objet(self, objet) -> bool

        Teste rapidement si l'objet est répertorié dans la feuille.
        (Ne cherche pas parmi les objets temporaires.)"""

        return is_in(objet, self.objets.values())


    def contient_objet_temporaire(self, objet):
        """contient_objet_temporaire(self, objet) -> bool

        Teste rapidement si l'objet est répertorié comme objet temporaire dans la feuille."""

        for obj in self._objets_temporaires:
            if obj is objet:
                return True
        return False


    def point_temporaire(self):
        if self.__point_temporaire__ is None:
            self.__point_temporaire__ = Point()
            self.__point_temporaire__.feuille = self
        return self.__point_temporaire__

    def start(self):
        u"Autorise le lancement d'animations."
        self._stop = False

    def stop(self):
        u"Arrête toutes les animations en cours."
        self._stop = True

    def animer(self, nom, debut = 0, fin = 1, pas = 0.02, periode = 0.03):
        u"Anime la variable nommée 'nom'."
        self.objets[nom].varier(debut, fin, pas, periode)

#######################################################################################

    def message(self, messg): # A REECRIRE
        if contexte['afficher_messages'] and param.verbose:
            messg = 'Feuille "%s" - %s' %(self.nom, messg)
            self.canvas.message(messg)
            print(messg)
            if self.log is not None:
                self.log.append(messg)


    def erreur(self, message, erreur = None):
        self.message(u"Erreur : " + uu(message))
        if erreur is None:
            erreur = RuntimeError
        raise erreur, str3(message)


    def save_log(self, log):
        # Impérativement utiliser 'is not None' car le log peut être vide.
        if self.log is not None:
            self.log.append(log)


#######################################################################################

# Gestion de l'affichage

#    cf. API/affichage.py


    def lister_figures(self):
        u"""Renvoie deux listes de figures (artistes matplotlib).

        La seconde est celle des figures qui vont bouger avec l'objet deplacé ;
        et la première, des autres qui vont rester immobiles.

        S'il n'y a pas d'objet en cours de déplacement, la deuxième liste est vide.
        """
        objet_deplace = self._objet_deplace
        ##if isinstance(objet_deplace, Label_generique):
            ##objet_deplace = objet_deplace.parent
            # TODO: pouvoir rafraichir uniquement l'étiquette ?
##        # Rafraichit les figures s'il y a besoin:
##        if self._mettre_a_jour_figures:
##            self._rafraichir_figures()
##            self._mettre_a_jour_figures = False
        # On liste tous les objets qui vont bouger avec 'objet_deplace':
        if objet_deplace is None:
            heritiers = []
        else:
            heritiers = objet_deplace._heritiers()
            heritiers.add(objet_deplace)
        # objets non susceptibles d'être modifiés (sauf changement de fenêtre, etc.)
        liste1 = []
        # objets susceptibles d'être modifiés
        liste2 = []
        for objet in self.liste_objets(etiquettes=True):
            liste = liste2 if is_in(objet, heritiers) else liste1
            liste.extend(objet.figure)
            liste.extend(objet._trace)
        for objet in self._objets_temporaires:
            liste2.extend(objet.figure)
            liste2.extend(objet._trace)
            if objet.etiquette:
                liste2.extend(objet.etiquette.figure)
                liste2.extend(objet.etiquette._trace)
        return liste1, liste2






    def effacer_traces(self):
        u"Efface toutes les traces (sans enlever le mode trace des objets)."
        for objet in self.liste_objets():
            objet.effacer_trace()
        self.affichage_perime()

    def objets_en_gras(self, *objets):
        u"""Met en gras les objets indiqués, et remet les autres objets en état "normal" le cas échéant."""

        changements = False
        for objet in self.liste_objets(True):
            if is_in(objet, objets):
                val = objet.en_gras(True)
            else:
                val = objet.en_gras(False)
            if val is not None:
                changements = True

        if changements:
            self.affichage_perime()
#########################################################################################





#########################################################################################

# Gestion du zoom et des coordonnees, reglage de la fenetre d'affichage.

#    cf. API/affichage.py




#########################################################################################

# Diverses fonctionnalites de la feuille, utilisees par les objets.
# C'est un peu la boite a outils :-)




    def nom_aleatoire(self, objet, prefixe=None):
        u"""Génère un nom d'objet non encore utilisé.

        Si possible, le nom sera de la forme 'prefixe' + chiffres.
        Sinon, un préfixe aléatoire est généré."""
        prefixe = (prefixe if prefixe else objet._prefixe_nom)
        existants = self.objets.noms
        for i in xrange(1000):
            n = len(prefixe)
            numeros = [int(s[n:]) for s in existants if re.match(prefixe + "[0-9]+$", s)]
            nom = prefixe + (str(max(numeros) + 1) if numeros else '1')
            nom = self.objets._Dictionnaire_objets__verifier_syntaxe_nom(objet, nom, skip_err=True)
            if nom is not None:
                return nom
            prefixe = ''.join(choice(letters) for i in xrange(8))
        raise RuntimeError, "Impossible de trouver un nom convenable apres 1000 essais !"



    def pause(self):
        souffler()
        if self._stop:
            raise RuntimeError, "Interruption de la macro."
