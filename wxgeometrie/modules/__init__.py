# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##########################################
#            Modules
##########################################
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

import os

from ..GUI.menu import MenuBar
from ..GUI.panel import Panel_simple
from ..API.parametres import actualiser_module
import param
from ..pylib import print_error, str2, path2

def importer_module(nom_module, forcer = False):
    u"Retourne le module si l'import a r�ussi, None sinon."
    if param.modules_actifs[nom_module] or forcer:
        if param.verbose:
            print("Import du module '%s'..." %nom_module)
        try:
            wxgeometrie = __import__('wxgeometrie.modules.' + nom_module, level=2)
            module = getattr(wxgeometrie.modules, nom_module)
            if hasattr(module, '_menu_'):
                # Module d�j� import� -> rien � faire.
                return module

            module._nom_ = module.__name__.split('.')[-1]

            menus = [objet for objet in module.__dict__.itervalues() if isinstance(objet, type) and issubclass(objet, MenuBar) and objet.__name__ != "MenuBar"]
            if len(menus) > 1 and param.debug:
                print menus
                raise IndexError, str2(u"Plusieurs classes h�ritent de MenuBar dans le module %s." %nom_module)
            if len(menus) == 0 and param.debug:
                raise IndexError, str2(u"Aucune classe n'h�rite de MenuBar dans le module %s." %nom_module)
            module._menu_ = menus[0]


            panels = [objet for objet in module.__dict__.itervalues() if isinstance(objet, type) and issubclass(objet, Panel_simple) and objet.__name__ not in ("Panel_simple", "Panel_API_graphique")]
            if len(panels) > 1 and param.debug:
                print panels
                raise IndexError, str2(u"Plusieurs classes h�ritent de Panel_simple dans le module %s." %nom_module)
            if len(panels) == 0 and param.debug:
                raise IndexError, str2(u"Aucune classe n'h�rite de Panel_simple dans le module %s." %nom_module)
            panel = module._panel_ = panels[0]
            try:
                param_pth = 'wxgeometrie.modules.%s._param_' %nom_module
                wxgeometrie = __import__(param_pth, level=2)
                panel._param_ = eval(param_pth)
                path = path2(param.emplacements['preferences'] + "/" + nom_module + "/parametres.xml")
                if param.sauver_preferences and param.charger_preferences and os.path.exists(path):
                    try:
                        a_verifier = dict((dicname, getattr(param, dicname)) for dicname in param.a_mettre_a_jour)
                        actualiser_module(panel._param_, path)
                        # certains param�tres peuvent avoir besoin d'une mise � jour
                        # (en cas de changement de version de wxg�om�trie par exemple)
                        # cela concerne en particulier les dictionnaires, qui peuvent gagner de nouvelles cl�s.
                        for dicname in param.a_mettre_a_jour:
                            for key, val in a_verifier[dicname].iteritems():
                                if hasattr(panel._param_, dicname):
                                    # (pour l'instant) param.a_mettre_a_jour s'applique � tout wxg�om�trie,
                                    # mais tous les param�tres ne concernent pas tous les modules.
                                    getattr(panel._param_, dicname).setdefault(key, val)
                    except:
                        print_error(u"\n\nImpossible d'actualiser les pr�f�rences du module '%s'" %nom_module)
            except ImportError:
                panel._param_ = None
                print_error(u"\n\nImpossible d'importer les param�tres du module '%s'" %nom_module)
            except:
                print_error(u"\n\nImpossible d'importer les param�tres du module '%s'" %nom_module)
                panel._param_ = None

        except:
            print_error(u"\nError: Impossible d'importer le module '%s'" %nom_module)
            # On d�sactive les modules non charg�s.
            param.modules_actifs[nom_module] = False
        else:
            return module
