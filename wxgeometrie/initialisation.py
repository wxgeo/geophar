# -*- coding: utf-8 -*-

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

import time
t0 = time.time()
import sys, os, itertools, traceback, imp, subprocess
from os.path import dirname, realpath, normpath

# Emplacement du module python nommé wxgeometrie
EMPLACEMENT = dirname(dirname(realpath(sys._getframe().f_code.co_filename)))

if getattr(sys, '_launch_geophar', False):
    from .arguments import lire_arguments, traiter_arguments

    options, arguments = lire_arguments()


    # Le splash screen doit être affiché le plus tôt possible.
    # Par contre, il ne doit pas être affiché si le fichier est importé simplement
    # comme module.
    if not (options.script or options.lister_modules):
        try:
            from .GUI.app import app, splash

            splash_screen = splash(normpath(EMPLACEMENT + '/wxgeometrie/images/logo6-1.png'))
            # .showMessage() doit être appelé pour que le splash screen apparaisse.
            # cf. https://bugreports.qt-project.org/browse/QTBUG-24910
            splash_screen.showMessage('Chargement en cours...')
            print("Démarrage GUI...")
        except ImportError:
            # Il manque très probablement PyQt4, un message d'erreur sera affiché
            # un peu plus loin lors de la vérification des modules.
            splash_screen = None

    parametres_additionnels, arguments, options = traiter_arguments(options, arguments)

    from . import param
    # Attention, les paramètres importés explicitement ici dans l'espace des noms
    # du module `initialisation` ne pourront pas être modifié en ligne de commande :
    # en effet, pour modifier les paramètres via la ligne de commande,
    # on met à jour l'espace des noms du module param.
    # En particulier, il ne faut *PAS* écrire ``from .param import debug``,
    # car alors, ``$ geophar -b`` ne prendrait pas en compte le ``-b``
    # lors de l'initialisation.
    from .param import dependances, NOMPROG, NOMPROG2, LOGO, plateforme, GUIlib
    from .pylib.fonctions import path2, uu

    # Résolution de l'écran en dpi (remarque : 1 inch = 2.54 cm)
    param.dpi_ecran = (app.desktop().physicalDpiX() + app.desktop().physicalDpiY())/2
    # Remarque:
    # Sous Linux, on peut facilement calculer la résolution
    # via la commande suivante, qui donne le nombre de pixels et la taille physique (en mm) du moniteur:
    # xrandr | grep -w connected
    # Le résultat est exact, contrairement à la résolution fournie par Qt
    # qui est très approximative.


    param.EMPLACEMENT = EMPLACEMENT
    # Un identifiant unique pour chaque instance de wxgeometrie lancée.
    # Doit permettre notamment de gérer les accès simultannés aux ressources
    # (sauvegardes automatiques).
    # Chaque session est sauvée automatiquement sous le nom :
    # 'config/session/session-%s.geos' % ID
    # Les ID successifs sont strictement incrémentaux, ce qui fait qu'en cas de crash
    # il est facile de retrouver le dernier fichier de session (pour le recharger),
    # c'est celui qui a l'ID le plus élevé.
    param.ID = ID = repr(t0).replace('.','-')

    if not options.script:
        app.nom(NOMPROG)
        if param.style_Qt:
            app.setStyle(param.style_Qt)
        app.icone("%/wxgeometrie/images/icone.ico")

    #def my_excepthook(exc_type, exc_obj, exc_tb):
    #    u"""Affiche l'erreur sans interrompre le programme.
    #    C'est un alias de sys.excepthook, mais qui est plus souple avec les encodages.
    #    """
    #    tb = traceback.extract_tb(exc_tb)
    #    print 'Traceback (most recent call last !)'
    #    for fichier, ligne, fonction, code in tb:
    #        print '    File "' + uu(fichier) +'", line ' + unicode(ligne) + ', in ' + uu(fonction)
    #        if code is not None:
    #            print '        ' + uu(code)
    #    print uu(exc_type.__name__) + ": " + uu(exc_obj)


    #sys.excepthook = my_excepthook

    class SortieTemporaire(list):
        def write(self, chaine):
            self.append(uu(chaine).encode(param.encodage))


    class SortiesMultiples(object):
        softspace = 0
        def __init__(self, obligatoires = (), facultatives = ()):
            self.obligatoires = list(obligatoires)
            self.facultatives = list(facultatives)
            self.total = 0

        def write(self, chaine):
            uni = uu(chaine)
            chaine = uni.encode(param.encodage)
    #        default_out = (sys.__stdout__ if not param.py2exe else sys.py2exe_stderr)
            # Sous Windows, l'encodage se fait en cp1252, sauf dans console où cp850 est utilisé !
    #        default_out.write(chaine if plateforme != 'Windows' else uni.encode('cp850'))
            # Sous Windows, l'encodage se fait en cp1252, sauf dans console où cp850 est utilisé !
            sys.__stdout__.write(chaine if plateforme != 'Windows' else uni.encode('cp850'))

            self.total += len(chaine)
            if self.total - len(chaine) < param.taille_max_log <= self.total:
                chaine = "Sortie saturée !".encode(param.encodage)
            for sortie in self.obligatoires:
                sortie.write(chaine)
            if param.debug:
                for sortie in self.facultatives:
                    sortie.write(chaine)

        def flush(self):
            for sortie in itertools.chain(self.obligatoires, self.facultatives):
                if hasattr(sortie, 'flush'):
                    sortie.flush()

        def __del__(self):
            self.close()

        def close(self):
            for sortie in self.obligatoires:
                if hasattr(sortie, 'close'):
                    sortie.close()
            for sortie in self.facultatives:
                if hasattr(sortie, 'close'):
                    sortie.close()


    # S'assurer que les dossiers log/, session/, etc. existent:
    for emplacement in param.emplacements.values():
        emplacement = path2(emplacement)
        try:
            if not os.path.isdir(emplacement):
                os.makedirs(emplacement)
                print('Création du répertoire : ' + emplacement)
        except IOError:
            print("Impossible de créer le répertoire %s !" %emplacement)
            print('%s: %s' % sys.exc_info()[:2])
        except Exception:
            print('Erreur inattendue lors de la création du répertoire %s.' %emplacement)
            print('%s: %s' % sys.exc_info()[:2])


    # PARTIE CRITIQUE (redirection des messages d'erreur)
    # Attention avant de modifier, c'est très difficile à déboguer ensuite (et pour cause !)
    # Réduire la taille de cette partie au minimum possible.

    try:
        sorties = sys.stdout = sys.stderr = SortiesMultiples()
        # Tester sys.stdout/stderr (les plantages de sys.stderr sont très pénibles à tracer !)
        sorties.write('')
    except:
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        raise

    log_filename = path2(param.emplacements['log'] + "/messages.log")
    if param.enregistrer_messages and isinstance(sys.stdout, SortiesMultiples):
        try:
            sys.stdout.facultatives.append(SortieTemporaire())
            fichier_log = open(log_filename, 'w')
            fichier_log.write(NOMPROG.encode(param.encodage) + " version " + param.version + '\n')
            fichier_log.write(time.strftime("%d/%m/%Y - %H:%M:%S") + '\n')
            sys.stdout.obligatoires.append(fichier_log)
        except IOError:
            fichier_log = None
            param.enregistrer_messages = param.historique_log = False
            print(traceback.format_exc(sys.exc_info()))
            print('Warning: This exception was not raised.')
    else:
        fichier_log = None

    # FIN DE PARTIE CRITIQUE


    # On enclôt tout dans un try/except.
    # En effet, le sys.stderr personnalisé se comporte mal en cas d'erreur non interceptée
    # (il semble qu'une partie de l'espace des noms ne soit déjà plus accessible au moment où l'erreur
    # est traitée...??)
    try:
        # à faire avant d'importer API
        if param.verbose:
            print('Arguments de la ligne de commande :', parametres_additionnels, arguments)
            if options.script:
                print("--- Mode script activé. ---")

        if param.frozen:
            print(sys.path)
            sys.path.extend(('library.zip\\matplotlib', 'library.zip\\' + GUIlib))

        if param.charger_psyco is not False:
            try:
                import psyco
                if param.charger_psyco is True:
                    psyco.full()
                else:
                    psyco.profile()
            except ImportError:
                pass



        def initialiser():
            from .API.parametres import actualiser_module
            from .pylib import print_error
            from .geolib import contexte
            # Récupération d'un crash éventuel
            path_lock = path2(param.emplacements['session'] + "/lock")
            crash = os.path.isfile(path_lock)

            try:
                open(path_lock, 'w').close()
                param.ecriture_possible = True
            except IOError:
                print("Warning: impossible de créer le fichier '%s'." %path_lock)
                param.ecriture_possible = False

            # On sauvegarde la valeur des paramètres par défaut.
            copie = param.__dict__.copy()
            copie.pop("__builtins__", None)
            setattr(param, "_parametres_par_defaut", copie)

            # Mise à jour des paramètres en fonction des préférences de l'utilisateur.
            # (NB: à faire avant d'importer modules.py, qui lui-même utilise param.modules_actifs)
            path = path2(param.emplacements['preferences'] + "/parametres.xml")
            try:
                if os.path.exists(path) and param.charger_preferences:
                    if param.verbose:
                        print("Chargement des préférences...")
                    # On charge les préférences de l'utilisateur depuis parametres.xml.
                    a_verifier = dict((dicname, getattr(param, dicname)) for dicname in param.a_mettre_a_jour)
                    actualiser_module(param, path)
                    # Certains paramètres peuvent avoir besoin d'une mise à jour
                    # (en cas de changement de version du programme par exemple).
                    # Cela concerne en particulier les dictionnaires, qui peuvent gagner de nouvelles clés.
                    for dicname in param.a_mettre_a_jour:
                        for key, val in a_verifier[dicname].items():
                            getattr(param, dicname).setdefault(key, val)
                    # Mise à jour du contexte de geolib:
                    for parametre in ('decimales', 'unite_angle', 'tolerance'):
                        contexte[parametre] = getattr(param,  parametre)
            except:
                sys.excepthook(*sys.exc_info())

            param.__dict__.update(parametres_additionnels)

            if options.script:
                from .GUI.mode_script import mode_script
                msg = mode_script(options.input, options.output)
                if msg:
                    print(msg)

            else:
                # param._restart est mis à True si l'application doit être redémarrée.
                param._restart = False

                from .GUI.fenetre_principale import FenetrePrincipale
                if param.debug:
                    print("Temps d'initialisation: %f s" % (time.time() - t0))
                frame = FenetrePrincipale(app, fichier_log = fichier_log)
                if not param._restart:
                    # Tous les modules ont pu être chargés (pas d'erreur fatale).
                    splash_screen.finish(frame)
                    if isinstance(sys.stdout, SortiesMultiples):
                        if param.debug:
                            for msg in sys.stdout.facultatives[0]:
                                frame.fenetre_sortie.write(msg)
                        sys.stdout.facultatives[0] = frame.fenetre_sortie
                    if arguments:
                        try:
                            for arg in arguments:
                                frame.onglets.ouvrir(arg) # ouvre le fichier passé en paramètre
                        except:
                            print_error() # affiche l'erreur interceptée, à titre informatif
                            print(arg)
                    elif options.restaurer or ((param.auto_restaurer_session or crash)
                                                and not options.nouveau):
                        # On recharge la session précédente.
                        # (options.restaurer est utilisé quand on redémarre l'application)
                        try:
                            if crash:
                                print(NOMPROG + " n'a pas été fermé correctement.\n"
                                      "Tentative de restauration de la session en cours...")
                            # En général, ne pas activer automatiquement tous les modules
                            # de la session précédente, mais seulement ceux demandés.
                            frame.gestion.charger_session(activer_modules=crash)
                        except:
                            print("Warning: La session n'a pas pu être restaurée.")
                            print_error()
                    frame.show()
                    if param.debug:
                        print('Temps de démarrage: %f s' % (time.time() - t0))
                    app.boucle()
                else:
                    # Une erreur fatale s'est produite lors du chargement d'un ou plusieurs modules.
                    # L'application va être redémarrée sans les modules problématiques.
                    # On ferme proprement le module de gestion des paramètres avant de quitter
                    # (pour mémoriser en particulier les noms des modules à désactiver).
                    frame.gestion.fermer()
                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__
                sorties.close()
            try:
                os.remove(path_lock)
            except OSError:
                print("Warning: impossible de supprimer %s." % repr(path_lock))
            if param._restart:
                args = [sys.executable, sys.argv[0], '--restaurer']
                # Nota: execv() a une syntaxe étrange : le nom de la commande lancée
                # (ie. sys.executable) doit réapparaître au début de la liste des arguments.
                print("\n=======================")
                print("Redémarrage en cours...")
                print(' '.join(args))
                print("=======================\n")
                os.execv(sys.executable, args)

    except Exception: # do *NOT* catch SystemExit ! ("wxgeometrie -h" use it)
        #~ if param.freezed:
            #~ details = u"Détails de l'erreur :\n"
            #~ # 25 lignes maxi dans la fenetre
            #~ l = uu(traceback.format_exc(sys.exc_info())).split('\n')[-25:]
            #~ details += '\n'.join(l) + '\n\n'
            #~ if param.enregistrer_messages:
                #~ details += u"Pour plus de détails, voir \n'%s'." %log_filename
            #~ else:
                #~ details += u"Par ailleurs, impossible de générer le fichier\n'%s'." %log_filename
            #~ msgbox(u"Erreur fatale lors de l'initialisation.", details)
        sys.excepthook(*sys.exc_info())
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        sorties.close()
        sys.exit("Erreur fatale lors de l'initialisation.")
