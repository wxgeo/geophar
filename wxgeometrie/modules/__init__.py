# -*- coding: utf-8 -*-

##########################################
#            Modules
##########################################
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

import os, sys
from importlib import import_module

from wxgeometrie.GUI.menu import MenuBar
from wxgeometrie.GUI.panel import Panel_simple, Panel_API_graphique
from wxgeometrie.GUI.exercice import Exercice, ExerciceMenuBar
from wxgeometrie.API.parametres import actualiser_module
from wxgeometrie import param
from wxgeometrie.pylib import print_error, path2


def importer_module(nom_module):
    "Retourne le module si l'import a réussi, None sinon."
    if param.verbose:
        print("Import du module '%s'..." %nom_module)
    try:
        module = import_module('wxgeometrie.modules.%s' % nom_module)

        if hasattr(module, '_menu_'):
            # Module déjà importé -> rien à faire.
            return module

        module._nom_ = module.__name__.split('.')[-1]

        menus = [cls for cls in module.__dict__.values() if isinstance(cls, type)
                 and issubclass(cls, MenuBar) and cls not in (MenuBar, ExerciceMenuBar)]
        if len(menus) > 1 and param.debug:
            ##print menus
            raise IndexError("Plusieurs classes héritent de MenuBar dans le module %s: " %nom_module
                                   + ', '.join(m.__name__ for m in menus))
        if len(menus) == 0 and param.debug:
            raise IndexError("Aucune classe n'hérite de MenuBar dans le module %s." %nom_module)
        module._menu_ = menus[0]


        panels = [cls for cls in module.__dict__.values() if isinstance(cls, type)
                  and issubclass(cls, Panel_simple) and cls not in (Panel_simple, Panel_API_graphique, Exercice)]
        if len(panels) > 1 and param.debug:
            ##print panels
            raise IndexError("Plusieurs classes héritent de Panel_simple dans le module %s: " %nom_module
                                + ', '.join(p.__name__ for p in panels))
        if len(panels) == 0 and param.debug:
            raise IndexError("Aucune classe n'hérite de Panel_simple dans le module %s." %nom_module)
        panel = module._panel_ = panels[0]
        try:
            panel._param_ = import_module('wxgeometrie.modules.%s._param_' %nom_module)
            copie = panel._param_.__dict__.copy()
            copie.pop("__builtins__", {})
            setattr(panel._param_, "_parametres_par_defaut", copie)
            path = path2(param.emplacements['preferences'] + "/" + nom_module + "/parametres.xml")
            if param.sauver_preferences and param.charger_preferences and os.path.exists(path):
                try:
                    a_verifier = dict((dicname, getattr(param, dicname)) for dicname in param.a_mettre_a_jour)
                    actualiser_module(panel._param_, path)
                    # certains paramètres peuvent avoir besoin d'une mise à jour
                    # (en cas de changement de version de wxgéométrie par exemple)
                    # cela concerne en particulier les dictionnaires, qui peuvent gagner de nouvelles clés.
                    for dicname in param.a_mettre_a_jour:
                        for key, val in a_verifier[dicname].items():
                            if hasattr(panel._param_, dicname):
                                # (pour l'instant) param.a_mettre_a_jour s'applique à tout wxgéométrie,
                                # mais tous les paramètres ne concernent pas tous les modules.
                                getattr(panel._param_, dicname).setdefault(key, val)
                except:
                    print_error("\n\nImpossible d'actualiser les préférences du module '%s'" %nom_module)

        except ImportError:
            print_error("\n\nImpossible d'importer les paramètres du module '%s'" %nom_module)
        except:
            print_error("\n\nImpossible d'importer les paramètres du module '%s'" %nom_module)

    except:
        print_error("\nError: Impossible d'importer le module '%s'" %nom_module)
        # On désactive les modules non chargés.
        param.modules_actifs[nom_module] = False
    else:
        return module
