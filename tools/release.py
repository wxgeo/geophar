#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)
from __future__ import with_statement, print_function

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


import os, sys, time, re, types
from optparse import OptionParser
import scriptlib as s

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
parser.add_option("-q", "--quiet",
                  action="store_true", dest="quiet", default=False,
                  help="don't ask for confirmation")

(options, args) = parser.parse_args()

if len(args) != 1:
    s.cd('..')
    sys.path.append(os.getcwd())
    from wxgeometrie.param import version, NOMPROG2
    nom_prog = NOMPROG2.lower()
    parser.error("fournir un (et un seul) argument (numero de version).\nVersion actuelle: " + version)
version = args[0]

def version_interne(version):
    version = version.replace("alpha", "-3").replace("beta", "-2").replace("rc", "-1").replace(".", " ").replace("_", " ")
    return [int(n) for n in version.split(' ')]

def test_version(version):
    version = version.replace(' ', '_')
    reg='[0-9]+[.][0-9]+(([.][0-9]+([.][0-9]+)?)|(_(beta|alpha|rc)_[0-9]+))?$'
    if re.match(reg, version):
        return version


sys.path.insert(0, os.getcwd())

# Option --dry-run
if options.fake:
    for nom, val in s.__dict__.items():
        if isinstance(val, types.FunctionType):
            setattr(s, nom, eval("lambda s, *args, **kw:print('@%s: ' + s)" %nom))

# Mise à jour de la version et de la date dans param.__init__.py
t=time.localtime()
date = str((t.tm_year, t.tm_mon, t.tm_mday))
contenu = []
with open('version.py', 'r') as f:
    for line in f:
        if line.startswith('date_version = '):
            contenu.append('date_version = ' + date)
        elif line.startswith('version = '):
            version_precedente = line[11:].split('#')[0].strip()[:-1]
            # Changement du numéro de version
            contenu.append('version = ' + repr(version.replace('_', ' ')) + '\n')
        elif line.startswith('git = '):
            contenu.append('git = ' + repr(s.command('git describe')))
        else:
            contenu.append(line)

# Quelques tests sur le numéro de version:
while True:
    modifier = False
    print('\n-------------------')
    print(u"Version précédente: " + version_precedente)
    version = test_version(version)
    if version is None:
        print('Numero de version incorrect: ' + args[0])
        modifier = True
    elif version_interne(version) <= version_interne(version_precedente):
        print('Les numeros de version doivent etre croissants: ' + args[0])
        modifier = True
    else:
        print(u"Nouvelle version: " + version)
        if options.quiet:
            break
        rep = raw_input(u"Est-ce correct ? [y(es)/n(o)/(q)uit]")
        if not rep:
            continue
        if rep in 'yYoO':
            break
        elif rep in 'qQ':
            sys.exit()
        elif rep in 'nN':
            modifier = True
    if modifier:
        version = raw_input(u"Entrez un nouveau numero de version:")

print(u'\nCréation de la version ' + version + '...')

if not options.fake:
    # Mise à jour de param/version.py
    with open('version.py', 'w') as f:
        f.write(''.join(contenu).strip())

# Création du changelog correspondant
date = time.strftime("%d/%m/%Y")
s.command(u'echo "%s version %s\nPubliée le %s\n\n">doc/changelog.txt' %(nom_prog, date, version))
s.command('git log v%s..HEAD --no-merges --pretty="* %%s">>doc/changelog.txt' % version_precedente)

# Commit correspondant
s.command('git add doc/changelog.txt')
s.command('git add version.py')
s.command('git commit -m %s' %repr('Version ' + version))

archive_tar = "wxgeometrie_%s.tar" %version
archive_gz = archive_tar + '.gz'

print(u'\nCréation du paquet...')

# Nettoyage (inutile, sauf plantage précédent)
s.cd('..')
s.rmdir('build_', quiet=True)
s.rm(archive_gz, quiet=True)

# Création d'un répertoire temporaire build_/
s.mkdir('build_')
s.mkdir('build_/wxgeometrie')

# Création du tag de release
tag = 'v' + version
s.command('git tag -am %s %s' %(repr(options.message or 'Version ' + version), tag))

# Récupération des fichiers via git
s.command('git archive %s -o build_/wxgeometrie.tar' %tag)
s.cd('build_')
s.command('tar -xf wxgeometrie.tar --directory wxgeometrie')
s.rm('wxgeometrie.tar')

# Personnalisation du contenu
s.cd('wxgeometrie')
s.rename('README.md', 'README')
s.rm('MANIFEST.in')
s.rm('.gitignore')
s.rename('wxgeometrie/param/personnaliser_.py', 'wxgeometrie/param/personnaliser.py')
s.cd('..')

# Création de l'archive .tar.gz
s.command('tar -cf %s wxgeometrie' %archive_tar)
s.command('gzip %s' %archive_tar)
s.mv(archive_gz, options.output)

print(u'\nPaquet créé dans %s.\n' %os.path.abspath(options.output))

# Nettoyage
s.cd('..')
s.rmdir('build_')
