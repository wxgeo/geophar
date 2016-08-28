#!/usr/bin/env python3
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


import os, sys, time, re, types
from os.path import isfile
from optparse import OptionParser
from urllib.request import urlopen
from . import scriptlib as s

_module_path = os.path.split(os.path.realpath(sys._getframe().f_code.co_filename))[0]

s.cd(_module_path + '/../wxgeometrie')

parser = OptionParser(prog='release.py', usage="usage: %prog [options] release_number")
parser.add_option("-o", "--output", dest="output", default='..',
                  help="store output archive as FILE", metavar="FILE")
parser.add_option("-m", "--message", dest="message",
                  help="set release message to MSG (default: 'Version VERSION')", metavar="MSG")
parser.add_option("-n", "--dry-run",
                  action="store_true", dest="fake", default=False,
                  help="simulate only")
parser.add_option("-a", "--archive-only",
                  action="store_true", dest="archive_only", default=False,
                  help="Create an archive but DON'T make a release tag in git.\n"
                       "This is useful to make release candidates or test release process.")
parser.add_option("-p", "--publish",
                  action="store_true", dest="publish", default=False,
                  help=("publish on sourceforge (source package only)\n"
                        "and change current version number online."))
parser.add_option("-b", "--publish-only",
                  action="store_true", dest="publish_only", default=False,
                  help="Publish last (already existing) release.")
parser.add_option("-q", "--quiet",
                  action="store_true", dest="quiet", default=False,
                  help="don't ask for confirmation")

(options, args) = parser.parse_args()

def publish(filename, version):
    """Publie le fichier sur sourceforge, et met à jour le fichier distant
    contenant le numéro de la dernière version.
    """
    SOURCEFORGE_CONFIG = 'tools/.sourceforge'
    if isfile(SOURCEFORGE_CONFIG):
        with open(SOURCEFORGE_CONFIG) as _file:
            key = _file.read(1000)
    else:
        key = input('API-key:')
    print('\nMise en ligne de la version %s (%s)' % (version, filename))
    remote_dir = '/home/frs/project/geophar/Geophar/version_%s' % version
    s.command('ssh wxgeo,geophar@shell.sourceforge.net create')
    s.command('cat %s | ssh wxgeo@shell.sourceforge.net "mkdir -p %s;cat > %s/%s"'
                % (filename, remote_dir, remote_dir, filename))
    # http://sourceforge.net/p/forge/community-docs/Using%20the%20Release%20API/
    s.command(('curl -H "Accept: application/json" '
               '-X PUT -d "default=linux&default=bsd&default=solaris&default=others"'
               '-d "api_key=%s" '
               'https://sourceforge.net/projects/geophar/files/Geophar/version_%s/%s')
               % (key, version, filename))
    urlopen('http://wxgeo.free.fr/wordpress/update_geophar_version.php?version=%s' % version)

def version_interne(version):
    version = version.replace("alpha", "-3").replace("beta", "-2").replace("rc", "-1").replace(".", " ").replace("_", " ")
    return [int(n) for n in version.split(' ')]

def test_version(version):
    version = version.replace(' ', '_')
    reg='[0-9]+[.][0-9]+(([.][0-9]+([.][0-9]+)?)|(_(beta|alpha|rc)_[0-9]+))?$'
    if re.match(reg, version):
        return version

s.cd('..')
sys.path.insert(0, os.getcwd())
from wxgeometrie.param import version as version_precedente, NOMPROG2, NOMPROG
nom_prog = NOMPROG2.lower()

if options.publish_only:
    filename = '%s_%s.tar.gz' % (nom_prog, version_precedente)
    publish(filename, version_precedente)
    print('\nTerminé.')
    sys.exit()


s.cd('wxgeometrie')

sys.path.insert(0, os.getcwd())

# Option --dry-run
if options.fake:
    for nom, val in s.__dict__.items():
        if isinstance(val, types.FunctionType) and nom not in ('version_interne', 'test_version'):
            setattr(s, nom, eval("lambda s, *args, **kw:print('@%s: ' + s)" %nom))

# Récupération des infos de version puis mise en cache.
# Celles-ci serviront à mettre à jour version.py.
t=time.localtime()
date = str((t.tm_year, t.tm_mon, t.tm_mday))
contenu = []
with open('version.py', 'r') as f:
    for line in f:
        if line.startswith('date_version = '):
            contenu.append('date_version = %s\n' % date)
        elif line.startswith('version = '):
            #~ version_precedente = line[11:].split('#')[0].strip()[:-1]
            # Le nouveau numéro de version sera complété plus tard.
            contenu.append('version = %s\n')
        elif line.startswith('git = '):
            contenu.append('git = ' + repr(s.command('git describe').strip()))
        else:
            contenu.append(line)


if options.archive_only:
    last_commit_hash = s.command('git rev-parse --short HEAD').strip()
    date = time.strftime('%d.%m.%Y-%H.%M.%S')
    version = '%s-git-%s-%s' % (version_precedente, last_commit_hash, date)
else:
    if len(args) != 1:
        parser.error("fournir un (et un seul) argument (numero de version).\nVersion actuelle: " + version_precedente)
    version = args[0]
    # Quelques tests sur le numéro de version:
    while True:
        modifier = False
        print('\n-------------------')
        print("Version précédente: " + version_precedente)
        version = test_version(version)
        if version is None:
            print('Numero de version incorrect: ' + args[0])
            modifier = True
        elif version_interne(version) <= version_interne(version_precedente):
            print('Les numeros de version doivent etre croissants: ' + args[0])
            modifier = True
        else:
            print("Nouvelle version: " + version)
            if options.quiet:
                break
            rep = input("Est-ce correct ? [y(es)/n(o)/(q)uit]")
            if not rep:
                continue
            if rep in 'yYoO':
                break
            elif rep in 'qQ':
                sys.exit()
            elif rep in 'nN':
                modifier = True
        if modifier:
            version = input("Entrez un nouveau numero de version:")

print('\nCréation de la version ' + version + '...')

if not (options.fake or options.archive_only):
    # Mise à jour de version.py
    with open('version.py', 'w') as f:
        f.write(''.join(contenu).strip() % repr(version))

    # Création du changelog correspondant
    date = time.strftime("%d/%m/%Y")
    s.command('echo "%s version %s\nPubliée le %s\n\n">doc/changelog.txt'
                            % (NOMPROG, version, date))

    tags = s.command('git tag', quiet=True).strip().split('\n')

    # On inverse la liste et on supprime les 'v' devant chaque tag.
    tags = [tag[1:] for tag in reversed(tags)]
    # On récupère la version majeure précédente
    for tag in tags:
        if tag.count('.') == 1 and not version.startswith(tag):
            break

    s.command('git log v%s..HEAD --no-merges --pretty="* %%s">>doc/changelog.txt' % tag)

    # Commit correspondant
    s.command('git add doc/changelog.txt')
    s.command('git add version.py')
    s.command('git commit -m %s' % repr('Version ' + version))

archive_tar = "%s_%s.tar" % (nom_prog, version)
archive_gz = archive_tar + '.gz'

print('\nCréation du paquet...')

# Nettoyage (inutile, sauf plantage précédent)
s.cd('..')
s.rmdir('build_', quiet=True)
s.rm(archive_gz, quiet=True)

# Création d'un répertoire temporaire build_/
s.mkdir('build_')
s.mkdir('build_/%s' % nom_prog)

if options.archive_only:
    s.command('git archive HEAD -o build_/%s.tar' % nom_prog)
else:
    # Création du tag de release
    tag = 'v' + version
    s.command('git tag -am %s %s' %(repr(options.message or 'Version ' + version), tag))

    # Récupération des fichiers via git
    s.command('git archive %s -o build_/%s.tar' % (tag, nom_prog))

# Personnalisation du contenu
s.cd('build_')
s.command('tar -xf %s.tar --directory %s' % (nom_prog, nom_prog))
s.rm('%s.tar' % nom_prog)
s.cd(nom_prog)
s.rename('README.md', 'README')
s.rm('MANIFEST.in')
s.rm('.gitignore')
s.rename('wxgeometrie/param/personnaliser_.py', 'wxgeometrie/param/personnaliser.py')
s.cd('..')

# Création de l'archive .tar.gz
s.command('tar -cf %s %s' % (archive_tar, nom_prog))
s.command('gzip %s' % archive_tar)
s.mv(archive_gz, options.output)

print('\nPaquet créé dans %s.\n' % os.path.abspath(options.output))

# Publie sur sourceforge et met à jour le fichier de version...
if options.publish:
    publish(archive_gz, version)

# Nettoyage
s.cd('..')
s.rmdir('build_')
