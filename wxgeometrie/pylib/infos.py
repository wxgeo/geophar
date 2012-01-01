# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)


##--------------------------------------#######
#                 infos pylib                 #
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

# version unicode

import sys
import wx
import matplotlib
import os
import platform
import locale


class dossier(object):
    def __init__(self, titre):
        self.__titre__ = titre

    def contenu(self):
        l = []
        l.append("+ " + self.__titre__ + ":")
        if hasattr(self, "version"):
            l.append("     Version: " + self.version)
        for key in self.__dict__:
            if key not in ("__titre__", "version"):
                l.append("     %s:  %s" %(key.capitalize(), getattr(self, key)))
        return "\n".join(l) + "\n\n"



def informations_configuration():
    dossier_os = dossier("Systeme")
    dossier_os.repertoire = os.getcwd()
    dossier_os.processeur = os.environ.get("PROCESSOR_IDENTIFIER", "?")
    dossier_os.version = platform.platform().replace("-", " ")
    if dossier_os.version.startswith("Windows"):
        dossier_os.distribution = "%s.%s build %s (%s) - %s" %sys.getwindowsversion()
    elif dossier_os.version.startswith("Linux"):
        try:
            f = open("/etc/lsb-release")
            s = f.read()
            f.close()
            dossier_os.distribution = " ".join(elt.split("=")[1] for elt in s.split("\n") if "=" in elt)
        except IOError:
            dossier_os.distribution = "?"
        except Exception:
            dossier_os.distribution = "#ERREUR#"
#    os.version = sys.platform
#    try:
#        __major__, __minor__, __build__, platform, __text__ = sys.getwindowsversion()
#        if platform is 0:
#            platform = "win32s"
#        elif platform is 1:
#            platform = "Windows 9x/ME"
#        elif platform is 2:
#            platform = "Windows NT/2000/XP"
#        else:
#            platform = "Unknown"
#        os.version += "  %s version %s.%s %s build %s" %(platform, __major__, __minor__, __text__, __build__)
#    except AttributeError:
#        pass
    dossier_local = dossier("Localisation")
    dossier_local.langue = locale.getdefaultlocale()[0]
    dossier_local.encodage = locale.getpreferredencoding()

    dossier_python = dossier("Python")
    dossier_python.encodage = sys.getdefaultencoding() + " / Noms de fichiers: " + sys.getfilesystemencoding()
    dossier_python.version = sys.version
    dossier_python.executable = sys.executable

    # Pas tres utile :
#    dossier_python.api = sys.api_version
#    dossier_python.recursions = sys.getrecursionlimit()



    dossier_wxpython = dossier("WxPython")
    dossier_wxpython.portage = "  ".join(wx.PlatformInfo[1:])
    dossier_wxpython.version = wx.VERSION_STRING

    # Le code suivant provoque un Memory Leak de WxPython :
#    __p__ = wx.PlatformInformation()
#    dossier_wxpython.architecture = __p__.GetArchName() + "  " + __p__.GetEndiannessName()
#    dossier_wxpython.os = "%s  %s.%s" %(__p__.GetOperatingSystemFamilyName(), __p__.GetOSMajorVersion(), __p__.GetOSMinorVersion())

    dossier_matplotlib = dossier("Matplolib")
    dossier_matplotlib.version = matplotlib.__version__
    dossier_matplotlib.tex = matplotlib.rcParams["text.usetex"]
    if hasattr(matplotlib, "numerix"): # matplotlib <= 0.92
        dossier_matplotlib.numerix = matplotlib.rcParams["numerix"]
        dossier_matplotlib.numerix += " (" + matplotlib.numerix.version + ")"
    else: # matplotlib 0.98+
        dossier_matplotlib.numerix = "numpy"
        dossier_matplotlib.numerix += " (" + matplotlib.numpy.__version__ + ")"

    dossier_sympy = dossier("Sympy")
    try:
        import sympy
        dossier_sympy.version = sympy.__version__
    except:
        dossier_sympy.version = "?"

    dossier_psyco = dossier("Psyco")
    try:
        import psyco
        dossier_psyco.version = ".".join(str(elt) for elt in psyco.version_info)
        try:
            import param
            if param.charger_psyco is False:
                dossier_psyco.utilisation = "unused"
            elif param.charger_psyco is None:
                dossier_psyco.utilisation = "profile"
            elif param.charger_psyco is True:
                dossier_psyco.utilisation = "full"
            else:
                dossier_psyco.utilisation = "inconnue"
        except ImportError:
            dossier_psyco.utilisation = "?"
    except ImportError:
        dossier_psyco.version = "Psyco non trouve."
    except Exception:
        dossier_psyco.version = "#ERREUR#"

    dossier_wxgeometrie = dossier("Wxgeometrie")
    try:
        import param
        dossier_wxgeometrie.version = param.version
    except Exception:
        dossier_wxgeometrie.version = "?"


    return (dossier_os.contenu() + dossier_local.contenu() + dossier_python.contenu()
                                + dossier_wxpython.contenu() + dossier_matplotlib.contenu()
                                + dossier_sympy.contenu() + dossier_psyco.contenu()
                                + dossier_wxgeometrie.contenu())
