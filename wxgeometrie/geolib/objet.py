# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)
from __future__ import with_statement

##--------------------------------------#######
#                   Objet                     #
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

import re, math
from types import FunctionType, BuiltinFunctionType, TypeType

import numpy
from matplotlib.pyparsing import ParseFatalException

from sympy import I, pi as PI, Basic, Integer

from ..mathlib.internal_objects import Reel
# � int�grer dans geolib ??
from ..pylib import property2, no_twin, uu, str2, print_error, mathtext_parser, \
                    is_in, WeakList, CustomWeakKeyDictionary, warning
from .routines import nice_display
from .constantes import FORMULE, TEXTE, NOM
from .formules import Formule
from .contexte import contexte
import param


try:
    import wx
    souffler = wx.YieldIfNeeded
except ImportError:
    wx = None
    def souffler():
        pass


class _(object):
    pass
# G contient tous les objets de geolib � la fin de l'initialisation.
G = _()


###########################################################################


# NOTE : les vassaux ne sont pas parfaitement bien geres :
#    Un objet ne doit pas etre a la fois vassal et suzerain d'un autre.
#    Une telle situation provoquerait un plantage lors de la suppression d'un des deux objets (boucle recursive infinie).
#    Ceci ne pose a priori pas de problemes, sauf un peu de gaspillage de memoire :
#    en effet, les objets geometriques intermediaires introduits pour construire un objet ne sont pas systematiquement detruits quand l'objet est supprime.


TYPES_ENTIERS = (long, int, Integer,)
TYPES_REELS = TYPES_ENTIERS + (float, Basic, )
# XXX: Basic n'est pas forc�ment r�el

TYPES_NUMERIQUES = TYPES_REELS + (complex, )


ALPHABET_GREC_MIN = frozenset(( 'alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta',
                      'eta', 'theta', 'iota', 'kappa', 'lambda', 'mu', 'nu',
                      'xi', 'omicron', 'pi', 'rho', 'sigma', 'tau', 'upsilon',
                      'phi', 'chi', 'psi', 'omega' ))

ALPHABET_GREC_CAP = frozenset(('Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon', 'Zeta',
                    'Eta', 'Theta', 'Iota', 'Kappa', 'Lambda', 'Mu', 'Nu',
                    'Xi', 'Omicron', 'Pi', 'Rho', 'Sigma', 'Tau', 'Upsilon',
                    'Phi', 'Chi', 'Psi', 'Omega'))

ALPHABET_GREC = ALPHABET_GREC_MIN.union(ALPHABET_GREC_CAP)

FILL_STYLES = {'-': 'solid', '--' : 'dashed', '-.' : 'dashdot',  ':' : 'dotted'}

RE_NOM_OBJET = re.compile("[A-Z][^A-Z]*")

RE_NOM_DE_POINT="[A-Z]((_[{][0-9]+[}])|(_[0-9]+)|([']+))?"

##PI = math.pi
##if sympy is not None:
##    PI = sympy.pi

def issympy(*expressions):
    return all(isinstance(e, Basic) for e in expressions)



## OUTILS DIVERS
############

class Nom(object):
    u"""Nom d'un objet.

    Affiche le nom de l'objet quand on le met sous forme dAe cha�ne.

    Exemple :
    >>> from wxgeometrie.geolib import Nom, Feuille, Point
    >>> M = Feuille().objets.M = Point(1, 2)
    >>> nom = Nom(M)
    >>> nom
    'M'
    >>> M.nom = 'A'
    >>> nom
    'A'
    """

    __slots__ = "__objet"

    def __init__(self, objet):
        self.__objet = objet

    def __repr__(self):
        return repr(self.__objet.nom)



class Rendu(object):
    u"""Couche d'abstraction entre l'objet et le canvas.

    Son r�le est de rendre l'objet plus ind�pendant du canvas, mais aussi de faciliter le d�bogage,
    en indiquant quel objet a dessin� quoi.
    """
    def __init__(self, parent):
        self.parent = parent

    @property
    def feuille(self):
        return self.parent.__feuille__

    @property
    def canvas(self):
        return self.feuille and self.feuille.canvas

    def ligne(self, *args, **kw):
        artiste = self.canvas.ligne(*args, **kw)
        # Pour le d�bogage, il est pratique de savoir qui a cr�e quoi.
        artiste._cree_par = self.parent
        return artiste

    def polygone(self,  *args, **kw):
        artiste = self.canvas.polygone(*args, **kw)
        artiste._cree_par = self.parent
        return artiste

    def texte(self, *args, **kw):
        artiste = self.canvas.texte(*args, **kw)
        artiste._cree_par = self.parent
        return artiste

    def arc(self, *args, **kw):
        artiste = self.canvas.arc(*args, **kw)
        artiste._cree_par = self.parent
        return artiste

    def point(self, *args, **kw):
        artiste = self.canvas.point(*args, **kw)
        artiste._cree_par = self.parent
        return artiste

    def cercle(self, *args, **kw):
        artiste = self.canvas.cercle(*args, **kw)
        artiste._cree_par = self.parent
        return artiste

    def fleche(self, *args, **kw):
        artiste = self.canvas.fleche(*args, **kw)
        artiste._cree_par = self.parent
        return artiste

    def fleche_courbe(self, *args, **kw):
        artiste = self.canvas.fleche_courbe(*args, **kw)
        artiste._cree_par = self.parent
        return artiste

    def codage(self, *args, **kw):
        artiste = self.canvas.codage(*args, **kw)
        artiste._cree_par = self.parent
        return artiste

    def angle(self, *args, **kw):
        artiste = self.canvas.angle(*args, **kw)
        artiste._cree_par = self.parent
        return artiste

    def codage_angle(self, *args, **kw):
        artiste = self.canvas.codage_angle(*args, **kw)
        artiste._cree_par = self.parent
        return artiste

    def _pixel(self, point = None):
        if point is None:
            point = self.parent
        return self.canvas.coo2pix(*point.coordonnees_approchees)



class Cache(object):
    u"""Un 'dictionnaire' double dont la m�thode get est sensiblement modifi�e.

    Pour chaque entr�e, il y a une valeur en mode exact, et une valeur en
    mode approch�.

    Si le mot-cl� n'existe pas, le dictionnaire est mis � jour � l'aide de la
    fonction et de ses arguments.
    � noter que la fonction n'est *PAS* execut�e si le dictionnaire contient la cl�,
    ce qui n'est pas le cas de ``dict.get(clef, fonction(*args, **kw))`` bien s�r.
    D'o� l'int�r�t du cache.
    """

    __slots__ = '__approche',  '__exact'

    def __init__(self):
        # Cache pour le mode approch�...
        self.__approche = {}
        # ...et cache pour le mode exact.
        self.__exact = {}

    @property
    def __dict(self):
        return self.__exact if contexte['exact'] else self.__approche

    def get(self, clef, methode, *args, **kw):
        dict = self.__dict
        if clef not in dict:
            dict[clef] = methode(*args, **kw)
        return dict[clef]

    def __setitem__(self, key, value):
        self.__dict[key] = value

    def __getitem__(self, key):
        return self.__dict[key]

    def remove(self, key):
        u"Note: ne renvoie *PAS* d'erreur si la cl� est absente."
        # Si une des deux valeurs (exacte ou approch�e) n'est plus valable,
        # l'autre ne l'est *tr�s* probablement plus non plus.
        self.__exact.pop(key, None)
        self.__approche.pop(key, None)

    def clear(self):
        self.__approche.clear()
        self.__exact.clear()


def pi_():
    return PI if contexte['exact'] else math.pi

def I_():
    return I if contexte['exact'] else 1j



class Ref(object):
    u"""Conteneur pour un argument d'un objet.

    Si l'objet est d�j� une instance de Reference, alors l'objet est renvoy� directement
    (afin de ne pas cr�er de conteneur de conteneur !)"""

    __slots__ = '_utilisateurs', '__objet'

    def __new__(cls, objet):
        # si objet est d�j� une instance de Ref, alors objet est renvoy� directement
        # (afin de ne pas cr�er de conteneur de conteneur !)
        if isinstance(objet, cls):
            return objet
        instance = object.__new__(cls)
        instance.__objet = objet
        instance._utilisateurs = WeakList()
        return instance

    def _changer_objet(self, nouvel_objet, premiere_definition = False):
        ancien_objet = self.__objet
        self.__objet = nouvel_objet

        # Tous les objets qui utilisent cette r�f�rence doivent maintenant �tre mis � jour.

        # Le verrou suivant indique si le code suivant est ex�cut� dans
        # un cadre plus g�n�ral de rafraichissement de l'affichage.
        # Exemple :
        # Si A est un Point, alors le code A.coordonnees = 2, 3
        # invoque successivement les actions A.x = 2, et A.y = 3
        # Aucun rafraichissement interm�diaire de l'affichage ne doit avoir lieu apr�s A.x = 2,
        # sous peine d'une nette d�gradation des performances.

        if self._utilisateurs and not premiere_definition:
            # Attention, l'objet n'est pas forc�ment de type Objet (il peut-�tre de type int, str...)
            feuille = self._utilisateurs[0].__feuille__
            if feuille is not None and feuille._verrou_affichage is None:
                feuille._a_rafraichir = []
            for user in self._utilisateurs:
                # 1. Il ne d�pendent plus de l'ancien objet, mais du nouveau
                if isinstance(ancien_objet, Objet):
                    ancien_objet.vassaux.remove(user)
                if isinstance(nouvel_objet, Objet):
                    nouvel_objet.vassaux.append(user)
                # 2. Il faut mettre � jour la liste de leurs anc�tres
                # (auquel cas, il ne s'agit pas vraiment d'une red�finition des arguments)
                user._recenser_les_ancetres()
                # 3. Tous les h�ritiers doivent �galement subir une mise � jour
                heritiers = user._heritiers()
                user._heritiers_a_recalculer(heritiers)
                if feuille is not None:
                    feuille._a_rafraichir.extend(heritiers)
                    feuille._a_rafraichir.append(user)
            if feuille is not None and feuille._verrou_affichage is None:
                a_rafraichir = no_twin(feuille._a_rafraichir)
                for obj in a_rafraichir:
                    obj.figure_perimee()
##                feuille.affichage_perime()


    @property
    def objet(self):
        return self.__objet







class BaseArgument(object):
    u"""Classe m�re des descripteurs 'Argument', 'ArgumentNonModifiable' et 'Arguments'."""

    __compteur__ = 0

    def __init__(self, types, get_method=None, set_method=None, defaut=None):
        self.__contenu__ = CustomWeakKeyDictionary()
        BaseArgument.__compteur__ += 1
        self.__compteur__ = BaseArgument.__compteur__
        self.types = types
        self.get_method = get_method
        self.set_method = set_method
        self.defaut = defaut
        # La classe de rattachement (ie. la classe � laquelle l'argument se rapporte) sera compl�t�e dynamiquement.
        # cf. Objet.__init__()
        self.rattachement = None
        # Le nom est de la forme '_NomDeClasse__NomDArgument', et est compl�t� dynamiquement
        # cf. geolib/__init__.py
        self.nom = None


    def _definir_type(self):
        # Les arguments sont cr��s en m�me temps que les classes ;
        # il se peut donc qu'un type d'argument soit une classe qui n'existe pas encore.
        # On rentre donc le type d'argument sous la forme d'une cha�ne : "Ma_classe",
        # et � la premi�re utilisation de l'argument par une instance,
        # on transforme la cha�ne "Ma_classe" en la classe Ma_classe elle-m�me.
        if isinstance(self.types, str):
            def convert(chaine):
                if hasattr(G, chaine):
                    return getattr(G, chaine)
                else:
                    return __builtins__[chaine]
            self.types = tuple(convert(elt.strip()) for elt in self.types.split(","))
        elif not hasattr(self.types, '__iter__'):
            self.types = (self.types,)

    def _verifier_type(self, objet):
        if isinstance(objet, G.Variable):
            objet = objet.copy()
        if not isinstance(objet, self.types):
            for _type in self.types:
                if hasattr(_type, "_convertir"):
                    try:
                        objet = _type._convertir(objet)
                        break
                    except Exception:
                        if param.verbose:
                            print_error("Conversion impossible : de %s en %s" %(type(objet), _type))
        # Attention : penser � v�rifier ensuite le type m�me si la conversion semble avoir r�ussie !
        # En effet, la m�thode '_convertir()' peut �tre celle d'une sous-classe du type voulu, et donc ne pas convertir exactement l'objet dans le bon type.
        # Par exemple, pour un Vecteur_libre, c'est la m�thode Vecteur_generique._convertir() qui est utilis�e ; on obtient donc un objet de type 'Vecteur_generique', mais pas forc�ment de type 'Vecteur_libre'.
        if not isinstance(objet, self.types):
            raise TypeError, "%s should be of type %s, and not %s." %(objet, self.types, type(objet))
        return objet


    def _definir(self, obj, value):
        self._definir_type()
        if not hasattr(obj, "_valeurs_par_defaut"):
            # indique les arguments qui ont �t� initialis�s avec une valeur par d�faut
            obj._valeurs_par_defaut = []
        if not isinstance(value, Ref):
            raise TypeError, "l'argument doit etre encapsule dans un objet 'Ref' lors d'une premiere definition."
        if value.objet is None and self.defaut is not None:
            # Du fait des d�pendances circulaires, self.defaut est parfois rentr�
            # sous forme de chaine. � la premi�re utilisation, il est converti.
            if isinstance(self.defaut, basestring):
                self.defaut = eval(self.defaut, G)
            if isinstance(self.defaut, (FunctionType, BuiltinFunctionType, TypeType)):
                value._Ref__objet = self.defaut()
            else:
                value._Ref__objet = self.defaut
            obj._valeurs_par_defaut.append(self.nom)
        # Attention : on utilise l'attribut de bas niveau ._Ref__objet,
        # pour �viter que la r�f�rence croit � une red�finition.
        value._changer_objet(self._verifier_type(value.objet), premiere_definition = True)
#        if isinstance(value.__objet__, Objet) and value.__objet__.__feuille__ is None:
#            value.__objet__.__feuille__ = obj.__feuille__
        if not is_in(obj, value._utilisateurs):
            value._utilisateurs.append(obj)
        return value

    def _redefinir(self, obj, value):
        if isinstance(value, Ref):
            raise TypeError, "l'argument ne doit pas etre encapsule dans un objet 'Ref' lors d'une redefinition."
        if self.rattachement is not type(obj):
            raise AttributeError, "on ne peut pas redefinir un argument d'une sous-classe"
        value = self._verifier_type(value)
        # La premi�re �tape, c'est d'�liminer les d�pendances circulaires.
        # Par exemple, u = Variable(3); A = Point("u", "2*u"); u("A.x")
        # A deviendrait alors � la fois h�ritier de u (ie. on a besoin de u pour calculer A), et anc�tre de u (ie. on a besoin de A pour calculer u !)
        if value is obj or is_in(value, obj._heritiers()):
#            self.erreur(u"D�finition circulaire dans %s : l'objet %s se retrouve d�pendre de lui-m�me." %(obj, obj))
            raise RuntimeError, "Definition circulaire dans %s : l'objet %s se retrouve dependre de lui-meme." %(obj, obj)
        # La valeur a �t� fix�e par l'utilisateur, elle n'est donc plus d�finie par d�faut :
        if self.nom in obj._valeurs_par_defaut:
            obj._valeurs_par_defaut.remove(self.nom)
        if isinstance(value, Objet) and value.__feuille__ is None:
            value.__feuille__ = obj.__feuille__
        return value

    def _set(self, obj, value, premiere_definition = False):
        if self.set_method is not None:
            if isinstance(value, Ref):
                value._changer_objet(self.set_method(obj, value.objet), premiere_definition = premiere_definition)
                return value
            else:
                return self.set_method(obj, value)
        return value

    def _get(self, obj, value):
        if self.get_method is not None:
            return self.get_method(obj, value)
        return value




class Argument(BaseArgument):
    u"""Un descripteur pour un argument d'un objet."""

    def __get__(self, obj, type=None):
        if obj is None:
            # c'est la classe (et non une instance) qui appelle l'argument ; on renvoie alors l'objet 'BaseArgument' lui-m�me (et pas son contenu)
            return self
        return self._get(obj, self.__contenu__[obj].objet)
        # ----------------------
        # NOTE : en cas de 'KeyError' ici, c'est probablement que la classe
        # qui poss�de l'argument ne l'initialise pas dans sa m�thode __init__().
        # Il faut donc rajouter dans MaClasse.__init__() une ligne style
        # 'self.__monargument = monargument = Ref(monargument)'.
        # ----------------------


    def __set__(self, obj, value):
        # 1er cas : Red�finition d'un argument (self.__contenu__ contient d�j� une r�f�rence � l'instance.
        if is_in(obj, self.__contenu__):
            value = self._set(obj, value)
            if isinstance(self.__contenu__[obj].objet, G.Variable):
                # Optimisation : par exemple, on effectue A.x = 2 o� A est un Point.
                # Il est bien plus rapide de modifier la valeur de la variable A.x (A.x.val = 2),
                # que de cr�er une nouvelle Variable de valeur 2,
                # et de faire pointer A.x vers cette Variable (c.�-d. de faire A.x = Variable(2)).
                self.__contenu__[obj].objet.val = value
            else:
                self.__contenu__[obj]._changer_objet(self._redefinir(obj, value))
##                self._rafraichir(obj)

        # 2�me cas : D�finition d'un nouvel argument
        else:
            value = self._set(obj, value, premiere_definition = True)
            self.__contenu__[obj] = self._definir(obj, value)



class ArgumentNonModifiable(BaseArgument):
    u"""Un descripteur pour un argument non modifiable d'un objet.

    Note : un argument non modifiable n'est pas encapsul� dans un objet 'Ref'."""

    def __init__(self, types, get_method = None, set_method = None):
        BaseArgument.__init__(self, types, get_method = None, set_method = None)

    def _definir(self, obj, value):
        self._definir_type()
#        if value is None and self.defaut is not None:
#            if isinstance(self.defaut, (types.FunctionType, types.BuiltinFunctionType, types.TypeType)):
#                value = self.defaut()
#            else:
#                value = self.defaut
        value = self._verifier_type(value)
        if not isinstance(value, self.types):
            for _type in self.types:
                if hasattr(type, "_convertir"):
                    try:
                        value = _type._convertir(value)
                        break
                    except Exception:
                        if param.verbose:
                            print_error("Conversion impossible :")
        if not isinstance(value, self.types):
            raise TypeError, "%s should be of type %s, and not %s." %(value, self.types, type(value))
        if isinstance(value, Objet) and value.__feuille__ is None:
            value.__feuille__ = obj.__feuille__
        return value

    def __get__(self, obj, type=None):
        if obj is None:
        # c'est la classe (et non une instance) qui appelle l'argument ; on renvoie alors l'objet 'BaseArgument' lui-m�me (et pas son contenu)
            return self
        return self._get(obj, self.__contenu__[obj])


    def __set__(self, obj, value):
        value = self._set(obj, value, premiere_definition = True)
        # 1er cas : Red�finition d'un argument (self.__contenu__ contient d�j� une r�f�rence � l'instance.
        if is_in(obj, self.__contenu__):
            raise AttributeError, "Argument non modifiable."

        # 2�me cas : D�finition d'un nouvel argument
        else:
           self.__contenu__[obj] = self._definir(obj, value)



class Arguments(BaseArgument): # au pluriel !
    u"""Un descripteur pour une liste d'arguments d'un objet."""


    def __get__(self, obj, type=None):
        if obj is None:
            return self
        value = TupleObjets((elt.objet for elt in self.__contenu__[obj]),
                            objet = obj, arguments = self.__contenu__[obj])
        return self._get(obj, value)


    def __set__(self, obj, value):
        # 1er cas : Red�finition d'un argument (self.__contenu__ contient d�j� une r�f�rence � l'instance.
        if is_in(obj, self.__contenu__):
            objets = tuple(self._redefinir(obj, self._set(obj, elt)) for elt in value)
            if len(objets) != len(self.__contenu__[obj]):
                raise RuntimeError, "Impossible (actuellement) de modifier la taille d'une liste d'arguments."
            for elt, objet in zip(self.__contenu__[obj], objets):
                elt._changer_objet(objet)
##            self._rafraichir(obj)

        # 2�me cas : D�finition d'un nouvel argument
        else:
            self.__contenu__[obj] = tuple(self._definir(obj, self._set(obj, elt, premiere_definition = True)) for elt in value)





class TupleObjets(tuple):
    u"""Un objet tuple personnalis�, destin� � contenir des objets g�om�triques.

    Usage interne."""

#    __slots__ = "_arguments", "_obj"

    def __new__(cls, valeurs, objet, arguments):
        instance = tuple.__new__(cls, valeurs)
        instance._obj = objet
        instance._arguments = arguments
        return instance

    def __setitem__(self, index, value):
        self._arguments[index]._changer_objet(self._arguments.redefinir(self._obj, value))






class DescripteurFeuille(object):
    u"""Descripteur g�rant l'attribut '.__feuille __' de la classe 'Objet'.

    Usage interne."""

    def __init__(self):
        self.__contenu__ = CustomWeakKeyDictionary()

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        return self.__contenu__.get(obj)


    def __set__(self, obj, value):
        self.__contenu__[obj] = value

        for ancetre in obj._ancetres:
            if ancetre.__feuille__ is None:
                ancetre.__feuille__ = value
        label = obj._style.get("label")

        if isinstance(label, Formule):
            label.__feuille__ = value

        if hasattr(obj, "_set_feuille") and value is not None:
            obj._set_feuille()





## LA CLASSE Objet ET SES HERITIERS DIRECTES
##############################

class Objet(object):
    u"""Un objet g�om�trique.

    La classe Objet est la classe m�re de tous les objets g�om�triques.
    Note : elle n'est pas utilisable en l'�tat, mais doit �tre surclass�e.
    """

    __arguments__ = () # cf. geolib/__init__.py
    __feuille__ = DescripteurFeuille()
    __compteur_hierarchie__ = 0
    _prefixe_nom = "objet"
    _utiliser_coordonnees_approchees = False
    _label_temporaire = None

    # Indique si l'objet doit �tre rafraichi lorsque la fen�tre d'affichage change
    # Typiquement, c'est le cas des objets 'infinis' (comme les droites ou les courbes...),
    # et des objets dont la taille ne doit pas d�pendre de la fen�tre :
    # les textes, les codages des segments, des angles et des arcs, la fl�che des vecteurs...
    _affichage_depend_de_la_fenetre = False

    # Certains types d'objets (par exemple, les points), doivent apparaitre sur la feuille
    # m�me s'ils ont �t� g�n�r�s comme valeur par d�faut (par exemple,
    _enregistrer_sur_la_feuille_par_defaut = False

    # Le dictionnaire 'contexte' sert � partager des informations entre tous les objets
    __contexte = contexte
    @property
    def contexte(self):
        return self.__contexte

    # NOTES:
    # Apres l'importation du module, on peut ainsi changer la __feuille__ utilisee par defaut par les objets crees.
    # Pour changer la feuille par defaut, il suffit donc de modifier l'attribut de classe.
    # Si la __feuille__ est nulle (None), les objets ne sont pas enregistres.
    # Cela sert essentiellement a creer des objets temporaires, ou a faire de la geometrie sans figures (sic!)

    _style_defaut = param.defaut_objets

    # Un objet prot�g� ne peut pas �tre supprim�
    protege = False

    # Les labels ont une initialisation minimale
    _initialisation_minimale = False

    def __init__(self, **styles):
        # ---------------------------------------------------------------------
        # PARTIE 1 de l'initialisation :
        # tout ce qui ne doit se faire qu'une seule fois, m�me en cas d'h�ritage multiple.
        # ---------------------------------------------------------------------
        if not hasattr(self, "_style"):
            # CREATION DES ATTRIBUTS 'STANDARDS'
            self.etiquette = None # None pour '�tiquette non d�finie'
            self._pointable = hasattr(self, "_get_coordonnees")
            self._modifiable = hasattr(self, "_set_coordonnees") or hasattr(self, "_set_val") or hasattr(self, "_set_equation")
            self._deplacable = hasattr(self, "_set_coordonnees")
            # Lorque l'objet est enregistr� sur une feuille sur une feuille de travail, celle-ci lui donne un nom.
            self.__nom = ""
            self.nom_latex = "" # Code LaTeX utilis� pour l'affichage du nom

            # Valeurs mises en cache (coordonn�es, etc.)
            self._cache = Cache()


            # gestion des styles par d�faut
            self._creer_style_par_defaut()

            # Parametres par defauts
            # TODO: renommer _representation en _representation
            self._representation = []
            self._trace = []
            self._trace_x = []
            self._trace_y = []
            self._gras = False

            # Indique que la figure devra �tre rafra�chie
            self.__figure_perimee = True

            # Indique que le label devra �tre test�
            # (ceci sert pour �viter les plantages du parser de matplotlib en cas d'expression LaTeX incorrecte)
            self._label_correct = None

            # Interface avec le moteur d'affichage
            self.rendu = Rendu(self)

            # GESTION DES DEPENDANCES
            self.vassaux = WeakList()   # lors de sa cr�ation, l'objet n'a, lui, aucun vassal (aucun objet ne d�pend de lui)
            # La cr�ation d'une WeakList plut�t que d'une liste permet d'�viter les pertes de m�moire.
            # ATTENTION : ne pas utiliser un objet WeakSet.
            # En effet, il se peut qu'un objet apparaisse plusieurs fois comme vassal, si il apparait plusieurs fois comme argument.
            # C'est un comportement normal ; en cas de d�r�f�rencement de l'objet comme vassal, il ne doit �tre d�r�f�renc�
            # qu'une fois si un seul argument est chang� !

            if self._initialisation_minimale:
                return # les labels ont une initialisation minimaliste


            self._ancetres = set()
            self._recenser_les_ancetres()
            for ancetre in self._ancetres:   # l'objet est vassal de chacun des objets dont il depend
                ancetre.vassaux.append(self)
        # ---------------------------------------------------------------------
        # PARTIE 2 de l'initialisation :
        # ce qui suit peut �tre ex�cut� plusieurs fois en cas d'initialisations multiples
        # ---------------------------------------------------------------------
        if styles:
            self.style(**styles)


    def __hash__(self):
        return id(self)

    def _nom_alea(self):
        u"""Retourne un nom disponible sur la feuille, adapt� au type d'objet.

        Ex: M1 pour un point, s1 pour un segment, etc.
        """
        return self.__feuille__.nom_aleatoire(self)



# Fonctions d'initialisation de l'objet :
#########################################


    def  _creer_style_par_defaut(self):
        self._style = {}
        classes = self.__class__.mro()[:-1]
        classes.reverse()
        for classe in classes:
            if issubclass(classe, Objet):
                self._style.update(classe._style_defaut)



    @property
    def _iter_arguments(self):
        """Retourne un iterateur vers les couples (argument, valeur)

        L'ordre des arguments est respect�.
        """
        return iter((arg,  getattr(self, arg)) for arg in self.__arguments__)

    @property
    def _arguments(self):
        return dict((arg,  getattr(self, arg)) for arg in self.__arguments__)


    def _set_feuille(self):
        if hasattr(self,  "_valeurs_par_defaut") and self._valeurs_par_defaut:
            noms_args, args = zip(*self._iter_arguments)
            correspondance = False
            # On tente de d�tecter via le nom  de l'objet le nom que doit prendre chacun de ses arguments.
            # Par exemple, si un rectangle s'appelle ABCD, alors les points qui le constituent
            # doivent prendre pour noms A, B, C et D.
            if all(isinstance(arg, G.Point_generique) for arg in args):
                noms = re.findall(RE_NOM_OBJET, self._nom)
                if len(args) == len(noms):
                    correspondance = True
                    for i in xrange(len(args)):
                        if args[i]._nom != "" and args[i]._nom != noms[i]:
                            correspondance = False
                            break
                    if correspondance:
                        for i in xrange(len(args)):
                            if "_" + self.__class__.__name__ + "__" + noms_args[i] in self._valeurs_par_defaut:
                                self.__feuille__.objets[noms[i]] = args[i]
            # �chec du nommage intelligent : on se rabat sur des noms al�atoires
            if not correspondance:
                for nom_arg in self._valeurs_par_defaut:
                    self.__feuille__.objets[''] = getattr(self, nom_arg)
            self._valeurs_par_defaut = []


# Styles et informations sur l'objet
####################################

    def label(self, label = None, formule = False):
        u"""Affiche le label (ou etiquette) de l'objet.

        La chaine renvoy�e d�pendra de la valeur du style legende:
        - si legende = 0, renvoie ''
        - si legende = 1, renvoie le nom de l'objet
        - si legende = 2, renvoie le label proprement dit de l'objet
        - si legende = 4, renvoie le label interpr�t� comme une formule

        Si le param�tre label est sp�cifi�, le label est modifi�, et le style de l�gende est fix� � 2."""
        if label is not None:
            if formule:
                # on bascule l'affichage en mode formule en m�me temps
                self.style(label = label, legende = FORMULE)
            else:
                # si on change le label, celui-ci s'affiche par d�faut en m�me temps.
                self.style(label = label, legende = TEXTE)
        legende = self.style("legende")
        if legende == NOM:
            label = self.nom_latex
        elif legende == TEXTE:
            txt = self.style("label")
            label = uu(txt)
        elif legende == FORMULE:
            # Retourne le texte avec les expressions �valu�es
            label = unicode(self._style["label"])
        else:
            return ""

        if self._label_correct is None:
            if '$' in label:
                # on teste si l'expression LaTeX convient au parser de matplotlib
                try:
                    mathtext_parser(label)
                    self._label_correct = True
                except Exception:
                    print_error()
                    self._label_correct = False
            else: # le parser ne sera pas utilis� (ce n'est pas une expression LaTeX)
                self._label_correct = True
        if not self._label_correct:
            label = label.replace('$', r'$\$$')

        return label


    @property2
    def label_temporaire(self, *val):
        if val:
            self._label_temporaire = val[0]
            self.figure_perimee()
        return self._label_temporaire


    def style(self, nom_style = None, **kwargs):
        u"""Renvoie le ou les styles demand�s, ou modifie les styles de l'objet.

        * ``nom_style`` est un nom de style, ou une liste de noms de styles:
        La propri�t� correspondante est recherch�e dans self._style.
        Ex: couleur, taille = A.style(('couleur', 'taille'))

        * ``**kw`` sert � modifier des styles.
        Ex: A.style(couleur = 'blue')
        """
        if kwargs:# or defaut:
            #~ if defaut:
                #~ defaut = defaut.copy()
                #~ defaut.update(kwargs)
                #~ kwargs = defaut
            if kwargs.has_key("label") or kwargs.has_key("legende"):
                # il faudra tester le label
                self._label_correct = None
                if isinstance(self._style["label"], Formule):
                    label = self._style["label"]
                    self._style["label"] = ""
                    label.supprimer()
                # si la l�gende passe en mode formule, ou si elle reste en mode formule :
                if kwargs.get("legende", None) == FORMULE or (not kwargs.has_key("legende") and self._style["legende"] == FORMULE):
                    if kwargs.has_key("label"):
                        kwargs["label"] = Formule(self, kwargs["label"])
                    else:
                        self._style["label"] = Formule(self, self._style["label"])
                # sinon, si elle n'est plus en mode formule :
                elif isinstance(self._style["label"], Formule):
                    self._style["label"] = eval(repr(label))

            self._style.update(kwargs)

            self.figure_perimee()
        if nom_style:
            def get_style(nom):
                if nom == 'label' and self._style['legende'] == FORMULE:
                    return eval(repr(self._style['label']))
                return self._style.get(nom)
            return get_style(nom_style) if isinstance(nom_style, basestring) else [get_style(nom) for nom in nom_style]
        return self._style

##    @deprecated('Utiliser directement style desormais.')
##    def modifier(self, **kwargs):
##        u"Change le style et rafraichit l'affichage."
##        self.style(**kwargs)




    def cacher(self):
        self.style(visible = False)
        self.message(self.nom_complet + u" cach\xe9.")

    def voir(self):
        self.style(visible = True)
        self.message(self.nom_complet + u" visible.")

    @property2
    def visible(self, val = None):
        if val is not None:
            assert isinstance(val, bool)
            self.style(visible = val)
        return self.style('visible')

    #~ def fixer(self):
        #~ self.style(fixe = True)

    #~ def liberer(self):
        #~ self.style(fixe = False)

    def renommer(self, nom, **kw):
        u"Permet de renommer l'objet, et �ventuellement de changer en m�me temps son style."
        nom_actuel = self.nom
        if nom_actuel != nom:
            nom = self.__feuille__.objets._objet_renommable(self, nom)
##            objet = self.__feuille__.objets.pop(nom_actuel)
##            # Important: pour que l'objet soit bien consid�r� non r�f�renc�
##            # il faut qu'il n'ait pas de nom (on ne peut pas r�f�rencer 2 fois un objet).
##            objet._nom = ""
            self.__feuille__.objets._dereferencer(self)
            self.__feuille__.objets[nom] = self
        self.style(**kw)
        self.figure_perimee()

# Nom de l'objet
##############################""

    def _nom(self, chaine = None):
        if chaine is None:
            return self.__nom
        else:
            self.__nom = chaine
            self._creer_nom_latex()

    _nom = property(_nom, _nom)

    def nom(self):
        if self.__feuille__:
            return self._nom
        return ""

    nom = property(nom, renommer)

    @property
    def _hierarchie_et_nom(self): # pour classer les objets
        return (self._hierarchie, self.nom)

    def _creer_nom_latex(self):
        u"""Renvoie le nom format� en LaTeX. Ex: M1 -> $M_1$."""
        nom = self.nom_corrige.rstrip('_')
        if not nom: # l'objet n'est pas enregistr� dans une feuille
            self.nom_latex = ""
            return
        nom = re.sub("([A-Za-z']+)_?([0-9]+)", lambda m:"%s_{%s}" %m.groups(), nom)
        for lettre in ALPHABET_GREC:
            if nom.startswith(lettre) and (nom == lettre or not nom[len(lettre)].isalpha()):
                nom = "\\" + nom
                break

        self.nom_latex = "$" + nom + "$"
        # Test de nom_latex :
        try:
            mathtext_parser(self.nom_latex)
        except ParseFatalException:
            warning('"%s" can not be parsed by mathtext.' %self.nom_latex)
            self.nom_latex = self.nom
        except Exception:
            print_error()
            self.nom_latex = self.nom

    @staticmethod
    def latex_police_cursive(nom):
        def _police_cursive(m):
            s = m.group(0)
            return r"\mathscr{" + s + "}" if s[0] != '\\' else s
        return re.sub(r"\\?[A-Za-z]+", _police_cursive,  nom)

    @property
    def nom_corrige(self):
        u"""Renvoie le nom en rempla�ant, le cas �ch�ant, _prime par un guillemet simple (')."""
        return self.nom.replace("_prime", "'")

    @property
    def nom_complet(self):
        return self.__class__.__name__.split("_")[0] + " " + self.nom_corrige

    @property
    def definition(self):
        u"""D�finition en fran�ais correct de l'objet.

        Exemple: 'Perpendiculaire � d passant par M'"""
        return self.nom_complet # � surclasser en g�n�ral


    @classmethod
    def type(cls):
        return cls.__name__.lower()

    @classmethod
    def classe(cls):
        return cls.__name__



    @classmethod
    def titre(cls, article = "un", point_final = True):
        u"""Affichage format� du type de l'objet... (un peu de grammaire!).
        Article peut �tre 'un', 'le', ou 'du', l'accord se faisant automatiquement.
        Le formatage est respect� (essayez 'un', 'UN', 'Un').

        >>> from wxgeometrie.geolib.vecteurs import Vecteur_libre
        >>> u = Vecteur_libre()
        >>> print u.titre()
        un vecteur libre.
        """

        titre = cls.__doc__.split("\n")[0].rstrip(".").lower()
        if point_final: titre += "."

        if not (article.lower() == u"un"):
            titre = " ".join(titre.split()[1:])

        if article.lower() == u"le":
            if titre[0] in "aeiouy":
                titre = u"l'" + titre
            elif cls.genre() == "m":
                titre = u"le " + titre
            else:
                titre = u"la " + titre

        if article.lower() == u"du":
            if titre[0] in "aeiouy":
                titre = u"de l'" + titre
            elif cls.genre() == "m":
                titre = u"du " + titre
            else:
                titre = u"de la " + titre

        if article.istitle():   titre = titre.capitalize()
        if article.isupper():   titre = titre.upper()
        return titre



    def titre_complet(self, article = "un", point_final = False):
        return self.titre(article, point_final) + " " + self.nom_corrige


    @classmethod
    def genre(cls):
        det = cls.__doc__.split()[0]
        if det.lower() == u"un":
            return "m"
        else:
            return "f"


# Gestion des d�pendances
###########################"

    def _recenser_les_ancetres(self):
        u"""Met � jour l'ensemble des anc�tres (de la g�n�ration pr�c�dente), c-�-d. l'ensemble des objets dont d�pend (directement) l'objet.

        L'ensemble est mis en cache dans self._ancetres.
        Pour obtenir tous les anc�tres (recherche r�cursive), utiliser la m�thode '_tous_les_ancetres'.
        """
        self._ancetres.clear()
        for val in self._arguments.values():
            if isinstance(val, (list, tuple)):
                for item in val:
                    if isinstance(item, Objet):
                        self._ancetres.add(item)
            elif isinstance(val, Objet):
                self._ancetres.add(val)
        self._modifier_hierarchie()

    def _tous_les_ancetres(self):
        u"""Retourne tous les objets dont d�pend, de pr�s ou de loin, l'objet."""
        ancetres = self._ancetres.copy()
        for ancetre in self._ancetres:
            ancetres.update(ancetre._tous_les_ancetres())
        return ancetres


##    def _heritiers(self, classer = False):
##        u"Retourne l'ensemble des objets qui d�pendent de cet objet, �ventuellement class�s selon l'attribut '_hierarchie'."
##        heritiers = self.vassaux.values()
##        vassaux = tuple(heritiers)
##        for vassal in vassaux:
##            heritiers += vassal._heritiers()
##        heritiers = no_twin(heritiers)
##        if classer:
##            heritiers.sort(key = lambda x: getattr(x, "_hierarchie"))
##        return heritiers

    def _heritiers(self):
        u"Retourne l'ensemble des objets qui d�pendent de cet objet."
        heritiers = set(self.vassaux)
        for vassal in heritiers.copy():
            heritiers.update(vassal._heritiers())
        return heritiers

##    def _modifier_hierarchie(self, valeur = None):
##        # plus self._hierarchie est faible, plus l'objet est haut plac� dans la hierarchie
##        # au sommet, pour les objets libres ("suzerains"), self._hierarchie = 0
##        if valeur is None:
##            valeur = max(-1, -1, *(objet._hierarchie for objet in self._ancetres)) + 1
##        self._hierarchie = valeur
##        for obj in self.vassaux.values():
##            if obj._hierarchie <= self._hierarchie:
##                obj._modifier_hierarchie(self._hierarchie + 1)

    def _modifier_hierarchie(self, valeur = None):
        # plus self._hierarchie est faible, plus l'objet est haut plac� dans la hierarchie
        Objet.__compteur_hierarchie__ += 1
        if valeur is None:
            valeur = self.__class__.__compteur_hierarchie__
        self._hierarchie = valeur
        # Il peut arriver (tr�s rarement) que self.vassaux soit modifi�
        # en m�me temps. Mieux vaut donc transformer self.vassaux en tuple.
        for obj in tuple(self.vassaux):
            obj._modifier_hierarchie()



# Acces a l'environnement exterieur
###################################

    @property
    def __canvas__(self):
        return self.__feuille__ and self.__feuille__.canvas

    def _pixel(self, point = None):
        if point is None:
            point = self
        return self.__canvas__.coo2pix(*point.coordonnees_approchees)


    def message(self, message):
        if self.__feuille__:
            self.__feuille__.message(message)
        else:
            print message

    def erreur(self, message):
        if self.__feuille__ is not None:
            self.__feuille__.erreur(message)
        else:
            raise RuntimeError, str2(message)

    @property
    def info(self):
        u"""� surclasser, en donnant une information significative pour l'objet.

        Par exemple, pour un point ou un vecteur, ses coordonn�es,
        pour un segment, sa longueur, pour un polygone, son aire...
        """
        return self.nom_complet


# API graphique (affichage et gestion des coordonnees)
######################################################

##    def _trace(self):
##        if self.style("trace"):
##            x, y = self.coordonnees_approchees
##            if self.__trace__:
##                self.__trace__[0]._x.append(x)
##                self.__trace__[0]._y.append(y)
##            else:
##                self.__trace__ = [self.rendu.ligne([x], [y], color = self.style("couleur"), marker = ".", linestyle = "None", markersize = 10)]
##        else:
##            self.__trace__ = []
##        return self.__trace__

    # NB: cette fonction est d�finie pour tous les objets.
    # (Pour les objets invisibles (variables), elle n'a aucun effet).
    def _creer_figure(self):
        pass

    def figure_perimee(self):
        self.__figure_perimee = True
        if self.__feuille__ is not None:
            self.__feuille__.affichage_perime()
        # NB: si, par ex., un objet est d�plac�, son �tiquette aussi.
        # On pourrait raffiner, mais dans le doute on rafraichit
        # toujours les coordonn�es de l'�tiquette avec l'objet.
        if self.etiquette is not None:
            self.etiquette.figure_perimee()


    @property
    def figure(self):
        if self.__figure_perimee and self.__feuille__ is not None:
            with contexte(exact = False):
                visible = self.style("visible")
                if self.existe and (visible or self.__feuille__.afficher_objets_caches):
                    # Remet alpha � 1 par d�faut :
                    # la transparence a peut-�tre �t� modifi�e si l'objet �tait auparavant invisible
                    for representation in self._representation:
                        representation.set_alpha(1)
                    self._creer_figure()
                    # Styles suppl�mentaires (pour le d�bugage essentiellement)
                    extra = self.style("extra")
                    if extra:
                        for representation in self._representation:
                            representation.set(**extra)
                    if not visible:
                        for representation in self._representation:
                            representation.set_alpha(.4*representation.get_alpha())
                    self._creer_trace()
                else:
                    self._representation = []
            self.__figure_perimee = False
        return self._representation


##    def creer_figure(self):
##        u"Construit la repr�sentation graphique de l'objet (mais ne rafraichit pas l'affichage par d�faut)."
##        # si l'objet n'a pas de nom (''), c'est que c'est une construction intermediaire
##        # il ne faut donc pas l'afficher.
##        if self.__feuille__ is not None:
##            #~ nom = self.nom
##            canvas = self.__canvas__
##
##            with contexte(exact = False):
##                if (self.__feuille__.contient_objet(self) or self.__feuille__.contient_objet_temporaire(self)) and canvas:
##                    if self.etiquette is not None:
##                        self.etiquette.creer_figure()
##                    visible = self.style("visible")
##                    if self.existe and (visible or self.__feuille__.afficher_objets_caches):
##                        # Remet alpha � 1 par d�faut :
##                        # la transparence a peut-�tre �t� modifi�e si l'objet �tait auparavant invisible
##                        for representation in self._representation:
##                            representation.set_alpha(1)
##
##                        self._creer_figure()
##                        # Styles suppl�mentaires (pour le d�bugage essentiellement)
##                        extra = self.style("extra")
##                        if extra:
##                            for representation in self._representation:
##                                representation.set(**extra)
##                        if not visible:
##                            for representation in self._representation:
##                                representation.set_alpha(.4*representation.get_alpha())
##                        self._creer_trace()
##
##                    else:
##                        self._representation = []
##                self.__feuille__.affichage_perime()



    def effacer_trace(self):
        self._trace = []
        self._trace_x = []
        self._trace_y = []

    def _creer_trace(self):
        u"M�thode � surclasser."
        pass

    def en_gras(self, valeur = True):
        u"""Met en valeur un objet.

        Typiquement, il s'agit d'un objet s�lectionn�.

        Si l'objet a �t� mis en gras, retourne True.
        S'il a �t� remis en �tat "normal", retourne False.
        Si l'�tat de l'objet n'a pas chang�, retourne None.
        """
        if valeur:
            if not self._gras:
                self._en_gras(valeur)
                self._gras = True
                return True
        else:
            if self._gras:
                self._en_gras(valeur)
                self._gras = False
                return False

    def _en_gras(self, booleen):
        e = self.style("epaisseur")
        t = self.style("taille")
##        if e is not None:
##            e *= param.zoom_ligne
##        if t is not None:
##            t *= param.zoom_ligne
        if booleen:
            for plot in self.figure:
                if hasattr(plot, "set_linewidth") and e is not None:
                    plot.set_linewidth(2*e)
                    if hasattr(plot, "set_markeredgewidth") and e is not None:
                            plot.set_markeredgewidth(2*e)
                            if t is not None:
                                plot.set_markersize(1.15*t)
#            if self.etiquette is not None:
#                self.etiquette._en_gras(True)
        else:
            for plot in self.figure:
                if hasattr(plot, "set_linewidth") and e is not None:
                    plot.set_linewidth(e)
                    if hasattr(plot, "set_markeredgewidth") and e is not None:
                            plot.set_markeredgewidth(e)
                            if t is not None:
                                plot.set_markersize(t)
#            if self.etiquette is not None:
#                self.etiquette._en_gras(False)




    def distance_inf(self, x, y, d):
        u"Teste si la distance (� l'ecran, en pixels) entre l'objet et (x, y) est inf�rieure � d."
        if hasattr(self, "_distance_inf") and self.existe:
            with contexte(exact = False):
                return self._distance_inf(x, y, d)
        else:
            return False




    # Certains objets n'existent pas toujours.
    # Par exemple, l'intersection de 2 droites est parfois vide.
    # Un objet construit a partir du point d'intersection de 2 droites peut donc ne plus exister temporairement.
    # En particulier, il est important de verifier que l'objet existe avant de l'afficher.
    def _existe(self):
        # Les conditions d'existence sont toujours �valu�es de mani�re approch�e pour l'instant
        with contexte(exact = False):
            if all(obj.existe for obj in self._ancetres):
                return self._cache.get('conditions', self._conditions_existence)
            else:
                # /!\ self.conditions_existence() ne doit PAS etre evalue si un ancetre n'existe pas (resultat imprevisible)
                return False

    @property
    def existe(self):
        return self._cache.get('existence', self._existe)



    def _conditions_existence(self):
        u"""Conditions sp�cifiques pour que l'objet existe, � definir pour chaque objet.

        Exemple: la mediatrice de [AB] existe ssi A != B.
        """
        return True


    def _espace_vital(self):
        return None

    @property
    def espace_vital(self):
        if self.existe:   return self._espace_vital()




    # Notes concernant le code pr�c�dent :
    # - Un objet qui "n'existe pas" (au sens g�om�trique) a des coordonn�es fix�es � None.
    # - Un objet libre (c'est-�-dire qui accepte des arguments pour ses m�thodes coordonnees() ou equation())
    #   ne doit pas avoir de conditions d'existence.





# API non graphique
###################

    def __contains__(self, y):
        with contexte(exact = False):
            return self._contains(y)

    def _contains(self):
        raise NotImplementedError


    def supprimer(self):
#        if self.style('protege'):
#            self.cacher()
#            return
        # Le nom doit �tre r�cup�r� AVANT la suppression.
        nom = self.nom_complet
        if self.protege:
            self.erreur(u"%s est prot�g�." %nom)
        else:
            self._supprime()
            if self.__feuille__:
                self.__feuille__.affichage_perime()
            self.message(u"%s supprim�." %nom)


    def _supprime(self):
        for ancetre in self._ancetres:
            # L'objet est supprim� de la liste des vassaux, pour chaque objet dont il d�pend.
            ancetre.vassaux.remove_all(self)
            # NB: ne g�n�re jamais d'erreur, m�me si self n'est pas dans la WeakList
            # (contrairement au ".remove()" d'une liste)
        for heritier in list(self.vassaux):
            try:
                heritier._supprime()
            except KeyError:
                pass # il se peut que l'objet n'existe d�j� plus.
        if self.__feuille__:
            self.__feuille__.objets._dereferencer(self)
##            if self.__canvas__:
##                self.__canvas__.graph.supprimer(self._representation)
##                if self.etiquette is not None:
##                    self.__canvas__.graph.supprimer(self.etiquette._representation)
        if isinstance(self._style["label"], Formule):
            # il faut supprimer proprement la formule.
            self._style["label"].supprimer()


    def redefinir(self, valeur):
        self.__feuille__.redefinir(self, valeur)


    def __repr__(self, styles = True):
        u"M�thode utilis�e pour sauvegarder les objets."
        def formater(objet):
            if isinstance(objet, Objet):
                if self.__feuille__ and self.__feuille__.contient_objet(objet):
                    return objet.nom
                else:
                    return objet.__repr__(styles)
                #if isinstance(objet, Variable): return repr(objet.val())
            if isinstance(objet, (list, tuple)):
                return "[" + ",".join([formater(item) for item in objet]) + "]"
            # Le 'float()' servent � contourner un bug de numpy 1.1.x et numpy 1.2.x (repr de float64) :
            if isinstance(objet, numpy.floating):
                return repr(float(objet))
            return repr(objet)

        if styles:
            return self.classe() + "(" + ",".join(key + "=" + formater(val) for key, val in self._iter_arguments) + ", **" + repr(self.style()) + ")"
        else:
            return self.classe() + "(" + ",".join(key + "=" + formater(val) for key, val in self._iter_arguments) + ")"


    def __str__(self):
        u"M�thode utilis�e pour l'affichage (ne retourne pas les styles)."
        def formater(objet):
            if isinstance(objet, Objet):
                if self.__feuille__ and self.__feuille__.contient_objet(objet):
                    return objet.nom
##                #if isinstance(objet, Variable): return repr(objet.val())
            if isinstance(objet, (list, tuple)):
                return "[" + ", ".join(formater(item) for item in objet) + "]"
            return unicode(objet)

        return uu(self.classe() + "(" + ", ".join(key + " = " + formater(val) for key, val in self._iter_arguments) + ")")


    def _definition(self):
        u"""Utilis� pour afficher la d�finition actuelle de l'objet avant de le red�finir.

        L'affichage est compact (styles, etc. non affich�s).
        """
        def formater(objet):
            if isinstance(objet, Objet):
                if self.__feuille__ and self.__feuille__.contient_objet(objet):
                    return objet.nom
                else:
                    return objet._definition()
##                #if isinstance(objet, Variable): return repr(objet.val())
            if isinstance(objet, (list, tuple)):
                return "[" + ",".join([formater(item) for item in objet]) + "]"
            # Le 'float()' servent � contourner un bug de numpy 1.1.x et numpy 1.2.x (repr de float64) :
            if isinstance(objet, numpy.floating):
                return repr(float(objet))
            return repr(objet)

        return self.classe() + "(" + ", ".join(formater(val) for key, val in self._iter_arguments) + ")"


    def copy(self):
        kwargs = self.style().copy()
        kwargs.pop("noms", None)
##        #~ print "copie de %s :" % self
##        #~ print self.style()
        kwargs.update(self._arguments)
        return self.__class__(**kwargs)


    def copier_style(self, objet):
        u"""Applique le style de 'objet' � l'objet (self).

        Si les objets sont de type diff�rent, seuls certains styles communs entrent en compte."""
        style = self.style()
        for key, value in objet.style().items():
            if style.has_key(key):
                if key in param.styles_a_signification_variable:
                    #print "clef:", key, style["categorie"], objet.style("categorie")
                    if style["categorie"] == objet.style("categorie"):
                        style[key] = value
                elif key not in param.styles_a_ne_pas_copier:
                    style[key] = value

        if objet.etiquette is not None and self.etiquette is not None:
            style_etiquette = objet.etiquette.style().copy()
            for key in param.styles_a_ne_pas_copier:
                style_etiquette.pop(key, None)
            self.etiquette.style(**style_etiquette)

        self.figure_perimee()


#    def _image(self, transformation):
#        raise NotImplementedError




### Routines rapides
###
### Les routines suivantes sont optimis�es pour la vitesse, afin d'�viter de passer par des classes (Vecteur, Segment, ...) lors des calculs internes.
### Elles essaient de concilier ceci avec une grande souplesse d'utilisation, en acceptant des arguments de types tr�s divers.
### Par exemple, un point peut �tre donn� sous la forme d'une instance de la classe Point, d'un tuple, d'une liste, d'un array.
##############################
##
##
##    @staticmethod
##    def _distance(A, B):
##        u"Distance entre les points A et B."
##        pylib.deprecation("A eviter desormais.")
##        xA, yA = A
##        xB,  yB = B
##        return math.hypot(xA - xB, yA - yB)
##
##    @staticmethod
##    def _carre_distance(A, B):
##        u"Carr� de la distance entre les points A et B."
##        pylib.deprecation("A eviter desormais.")
##        xA, yA = A
##        xB, yB = B
##        return (xB-xA)**2+(yB-yA)**2
##
##    @staticmethod
##    def _vec(A, B):
##        u"Coordonn�es du vecteur A>B."
##        pylib.deprecation("A eviter desormais.")
##        xA, yA = A
##        xB, yB = B
##        return xB - xA, yB - yA

##    @staticmethod
##    def _angle_oriente(vec1, vec2): # DESUET ! Utiliser la fonction angle_vectoriel() de pylib maintenant
##        u"Valeur en radian de l'angle d�finit par les vecteurs vec1, et vec2."
##        pylib.deprecation("Utiliser la fonction angle_vectoriel() de pylib maintenant")
##        x1, y1 = vec1; x2, y2 = vec2
##        signe = cmp(x1*y2-x2*y1, 0) # signe du d�terminant
##        if signe is 0:
##            signe = 1 # Peut importe le signe quand les vecteurs sont colineaires (0 = -0 et pi = -pi [2pi])
##        return signe*math.acos(produit_scalaire(vec1, vec2)/(math.hypot(*vec1)*math.hypot(*vec2)))


#    La gestion de l'affichage est compliqu�e...
#    L'id�e est que, quand on modifie un objet (style except�), on passe par 3 m�thodes :
#    _set_val, _set_equation, et _set_coordonnees.
#    Une fois ces m�thodes appel�es, on doit rafraichir l'affichage de toutes les d�pendances, apr�s les avoir recalcul�es.
#    La difficult�, c'est que quand on modifie, par exemple, les coordonn�es d'un point,
#    on modifie aussi les variables x et y (arguments de ce point), et donc,
#    on rafraichit inutilement plusieurs fois l'affichage.
#    Pour �viter cela, on marque simplement les objets � r�afficher, et on rafra�chit l'affichage une seule fois "� la fin".
#    Mais comment d�tecter "la fin" ? La solution retenue est de cr�er un verrou que pose la premi�re m�thode � s'�x�cuter.





    def _heritiers_a_recalculer(self, heritiers):
        u"""Indique que l'objet a �t� modifi�, et que les coordonn�es de tous les objets
        qui en d�pendent doivent �tre recalcul�es."""
        self._cache.clear()
        if self.etiquette is not None:
            self.etiquette._cache.clear()
        for objet in heritiers:
            objet._cache.clear()
            if objet.etiquette is not None:
                objet.etiquette._cache.clear()








#############################################################
#### Types d'objets tr�s g�n�raux


class Objet_avec_coordonnees(Objet):
    u"""Un objet ayant des coordonn�es (ex: points, vecteurs, ...).

    Usage interne : permet aux objets en h�ritant d'offrir un acc�s facile pour l'utilisateur final aux coordonn�es via __call__."""

    _style_defaut = {} # en cas d'h�ritage multiple, cela �vite que le style de Objet efface d'autres styles

    def _get_coordonnees(self):
        raise NotImplementedError

##    def _get_coordonnees_approchees(self):
##        return self._get_coordonnees()

    def __call__(self, *args):
        if args and not self.style("fixe"):
            if len(args) == 1:
                self.coordonnees = args[0]
            elif len(args) == 2:
                self.coordonnees = args
            else:
                raise TypeError, "Trop d'arguments."
        return self.coordonnees

    def __iter__(self): # definit tuple(objet) si l'objet renvoie des coordonnees
        if self.existe:
            return iter(self.coordonnees)
        raise TypeError, str2(u"Conversion impossible, l'objet n'est pas defini.")

##    @property
##    def coo(self):
##        u"""Alias de numpy.array(self.coordonnees)."""
##        pylib.deprecation("A eviter desormais.")
##        coordonnees = self.coordonnees
##        if coordonnees is None:
##            self.message(u"L'objet %s n'est pas d�fini" % self.nom)
##            return None
##        return numpy.array(coordonnees)

    @property
    def info(self):
        return self.nom_complet + u" de coordonn�es ("+ nice_display(self.x) + ", " + nice_display(self.y) + ")"

    @property
    def coordonnees_approchees(self):
        with contexte(exact = False):
            return self.coordonnees


    @property2
    def coordonnees(self, couple = None):
        if couple is None:
            d = ({'exact': False} if self._utiliser_coordonnees_approchees else {})
            with contexte(**d):
                return self._cache.get('xy', self._get_coordonnees) if self.existe else None

        try:
            if self.__feuille__ is not None and self.__feuille__._verrou_affichage is None:
                self.__feuille__._verrou_affichage = self
                self.__feuille__._a_rafraichir = []
            self._set_coordonnees(*couple)
            if self.__feuille__ is not None and self.__feuille__._verrou_affichage is self:
                for obj in no_twin(self.__feuille__._a_rafraichir):
                    obj.figure_perimee()
                self.__feuille__._objet_deplace = self
        finally:
            if self.__feuille__ is not None and self.__feuille__._verrou_affichage is self:
                self.__feuille__._verrou_affichage = None

    xy = coordonnees

    def __getitem__(self, i):
        return self.coordonnees[i]

    def _creer_trace(self):
        if self.style("trace"):
            x, y = self.coordonnees
            if not self._trace:
                ligne = self.rendu.ligne()
                ligne.set_color(self.style("couleur"))
                ligne.set_marker(".")
                ligne.set_linestyle("None")
                ligne.set_markersize(10)
                self._trace = [ligne]
            self._trace_x.append(x)
            self._trace_y.append(y)
            self._trace[0].set_data(self._trace_x, self._trace_y)
        else:
            self._trace = []
            self._trace_x = []
            self._trace_y = []



class Objet_avec_coordonnees_modifiables(Objet_avec_coordonnees):
    u"""Un objet ayant des coordonn�es (ex: points libres, vecteurs libres, textes...).

    Usage interne."""

    _style_defaut = {}

    abscisse = x = __x = Argument("Variable_generique", defaut = 0)
    ordonnee = y = __y = Argument("Variable_generique", defaut = 0)

    def __init__(self, x = None, y = None, **styles):
        self.__x = x = Ref(x)
        self.__y = y = Ref(y)
        Objet_avec_coordonnees.__init__(self, **styles)

    @staticmethod
    def _recuperer_x_y(x, y, kw = None):
        if kw and kw.get("z", False):
            z = kw.pop("z")
            x = z.real
            y = z.imag
        if y is None:
            if isinstance(x, complex): # un nombre complexe comme -1+2j est accept� comme argument
                x = x.real
                y = x.imag
            elif hasattr(x, "__iter__"): # un couple comme (-1,2) est accept� comme argument
                x, y = x
        if kw is None:
            return x, y
        else:
            return x, y, kw


    def _get_coordonnees(self):
        return self.__x.valeur, self.__y.valeur


    def _set_coordonnees(self, x = None, y = None):
        if x is not None:
            x, y = self._recuperer_x_y(x, y)
            self.__x = x
            self.__y = y



    def z(self, valeur = None):
        if valeur is None:
            return self.__x + 1j*self.__y
        self.__x = valeur.real
        self.__y = valeur.imag

    affixe = z = property(z, z)

    def __setitem__(self, i, valeur):
        if i == 0:
            self.__x = valeur
        elif i == 1:
            self.__y = valeur
        else:
            raise IndexError, "L'objet n'a que deux coordonnees."




class Objet_avec_equation(Objet):
    u"""Un objet contenant une �quation (ex: droites, ...).

    Usage interne : permet aux objets en h�ritant d'offrir un acc�s facile pour l'utilisateur final � cette valeur via __call__."""

    _style_defaut = {} # en cas d'h�ritage multiple, cela �vite que le style de Objet efface d'autres styles

    def _get_equation(self):
        raise NotImplementedError

##    def _get_equation_approchee(self):
##        return self._get_equation()

    def __call__(self, equation = None):
        if equation is not None and not self.style("fixe"):
            self.equation = equation
        return self.equation

    def __iter__(self): # definit tuple(objet) si l'objet renvoie une �quation
        if self.existe:
            return iter(self.equation)
        raise TypeError, str2(u"Conversion impossible, l'objet n'est pas defini.")

    @property
    def equation_approchee(self):
        with contexte(exact = False):
            return self.equation


    @property2
    def equation(self, coefficients = None):
        if coefficients is None:
            return self._cache.get('eq', self._get_equation) if self.existe else None

        try:
            if self.__feuille__ is not None and self.__feuille__._verrou_affichage is None:
                self.__feuille__._verrou_affichage = self
                self.__feuille__._a_rafraichir = []
            self._set_equation(*coefficients)
            if self.__feuille__ is not None and self.__feuille__._verrou_affichage is self:
                # Une seule fois � la fin
                for obj in no_twin(self.__feuille__._a_rafraichir):
                    obj.figure_perimee()
                self.__feuille__._objet_deplace = self
        finally:
            if self.__feuille__ is not None and self.__feuille__._verrou_affichage is self:
                self.__feuille__._verrou_affichage = None












class Objet_avec_valeur(Objet):
    u"""Un objet contenant une valeur num�rique (ex: angles, variables, ...).

    Usage interne : permet aux objets en h�ritant d'offrir un acc�s facile pour l'utilisateur final � cette valeur via __call__."""

    _style_defaut = {} # en cas d'h�ritage multiple, cela �vite que le style de Objet efface d'autres styles

    def _get_valeur(self):
        raise NotImplementedError

    def _set_valeur(self):
        raise NotImplementedError

##    def _get_valeur_approchee(self):
##        return self._get_valeur()

    def __call__(self, valeur = None):
        if valeur is not None and not self.style("fixe"):
            self.val = valeur
        return self.val

    @property
    def valeur_approchee(self):
        with contexte(exact = False):
            return self.valeur

    @property2
    def valeur(self, valeur = None):
        if valeur is None:
            return self._cache.get('val', self._get_valeur) if self.existe else None

        try:
            if self.__feuille__ is not None and self.__feuille__._verrou_affichage is None:
                self.__feuille__._verrou_affichage = self
                self.__feuille__._a_rafraichir = []
            self._set_valeur(valeur)
            if self.__feuille__ is not None and self.__feuille__._verrou_affichage is self:
                for obj in no_twin(self.__feuille__._a_rafraichir):
                    obj.figure_perimee()
                self.__feuille__._objet_deplace = self
        finally:
            if self.__feuille__ is not None and self.__feuille__._verrou_affichage is self:
                self.__feuille__._verrou_affichage = None


    val = valeur





class Objet_numerique(Reel, Objet_avec_valeur):
    u"Ensemble de m�thodes propres aux angles, aux variables, et autres objets num�riques."

    _style_defaut = {} # en cas d'h�ritage multiple, cela �vite que le style de Objet efface d'autres styles

    def __init__(self, *args, **kw):
        Objet.__init__(self, *args, **kw)

    def __float__(self):
        return float(self.val)

    def __int__(self):
        return int(self.val)

    ## -- code g�n�r� automatiquement -- (cf. creer_operations.py)

    def __add__(self, y):
        if isinstance(y, Objet_numerique):
            return self.val + y.val
        return self.val + y

    def __radd__(self, y):
        return y + self.val

    def __iadd__(self, y):
        self.val = self.val + (y.val if isinstance(y, Objet_numerique) else y)
        return self

    def __sub__(self, y):
        if isinstance(y, Objet_numerique):
            return self.val - y.val
        return self.val - y

    def __rsub__(self, y):
        return y - self.val

    def __isub__(self, y):
        self.val = self.val - (y.val if isinstance(y, Objet_numerique) else y)
        return self

    def __mul__(self, y):
        if isinstance(y, Objet_numerique):
            return self.val * y.val
        return self.val * y

    def __rmul__(self, y):
        return y * self.val

    def __imul__(self, y):
        self.val = self.val * (y.val if isinstance(y, Objet_numerique) else y)
        return self

    def __div__(self, y):
        if isinstance(y, Objet_numerique):
            return self.val / y.val
        return self.val / y

    def __rdiv__(self, y):
        return y / self.val

    def __idiv__(self, y):
        self.val = self.val / (y.val if isinstance(y, Objet_numerique) else y)
        return self

    def __truediv__(self, y):
        if isinstance(y, Objet_numerique):
            return self.val / y.val
        return self.val / y

    def __rtruediv__(self, y):
        return y / self.val

    def __itruediv__(self, y):
        self.val = self.val / (y.val if isinstance(y, Objet_numerique) else y)
        return self

    def __pow__(self, y):
        if isinstance(y, Objet_numerique):
            return self.val ** y.val
        return self.val ** y

    def __rpow__(self, y):
        return y ** self.val

    def __ipow__(self, y):
        self.val = self.val ** (y.val if isinstance(y, Objet_numerique) else y)
        return self

    def __mod__(self, y):
        if isinstance(y, Objet_numerique):
            return self.val % y.val
        return self.val % y

    def __rmod__(self, y):
        return y % self.val

    def __imod__(self, y):
        self.val = self.val % (y.val if isinstance(y, Objet_numerique) else y)
        return self

    def __floordiv__(self, y):
        if isinstance(y, Objet_numerique):
            return self.val // y.val
        return self.val // y

    def __rfloordiv__(self, y):
        return y // self.val

    def __ifloordiv__(self, y):
        self.val = self.val // (y.val if isinstance(y, Objet_numerique) else y)
        return self

    ## -- fin du code g�n�r� automatiquement --

    def __abs__(self):
        return abs(self.val)

    def __neg__(self):
        return 0 - self

#    def __pos__(self):
#        return 0 + self

    def __eq__(self, y):
        return self.val == y
##        return hasattr(y, "__float__") and abs(float(self) - float(y)) < param.tolerance

#    def __ne__(self, y):
#        return not self == y

    def __nonzero__(self):
        return self != 0

    def __gt__(self, y):
        return self.val > y
##        return hasattr(y, "__float__") and float(self) > float(y)

#    def __ge__(self, y):
#        return self > y or self == y



### TEMPLATE ###

##class MonObjet(ObjetParent1, ObjetParent2):
##
##    __slots__ = ("objet_lie", "__objet_interne")
##    _style_defaut = param.mon_objet
##    __objet1 = objet1 = Argument("Point_generique")
##    __objet2 = objet2 = Argument("Droite, Segment, Demidroite")
##    __objets = objets = Arguments("Point_generique")
##
##
##    def __init__(self, objet1, objet2, *objets, **styles):
##        self.__objet1 = objet1 = Ref(objet1)
##        self.__objet2 = objet2 = Ref(objet2)
##        self.__objets = objets = (Ref(objet) for objet in objets)
##        ObjetParent1.__init__(self, objet1, objet2)
##        ObjetParent2.__init__(self, *objets, **styles)
##        self.objet_lie = AutreObjet(*objets)
##        self.etiquette = MonLabel(self)
