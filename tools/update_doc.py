#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------##
#              WxGeometrie               #
#          Mise à jour de la doc         #
##--------------------------------------##
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

HOST = 'ftpperso.free.fr'
REMOTE_PATH = '/doc/html'

from os import listdir
from os.path import join, split, realpath, isdir, isfile
import sys
import subprocess
from ftplib import FTP, error_perm

_module_path = split(realpath(sys._getframe().f_code.co_filename))[0]

LOCAL_PATH = realpath(join(_module_path + '/../wxgeometrie/doc/html'))

command = ('cd ' + _module_path + '/../doc;make clean;make html;'
                + 'rm -rf ../wxgeometrie/doc/html/*;'
                + 'cp -rf ../build/html/* ../wxgeometrie/doc/html;'
          )
subprocess.call(command, shell=True)


# -------------------------
# Mise en ligne automatique
# -------------------------

class MyFTP(FTP):
    u"""FTP avec une interface de plus haut niveau."""

    def is_rdir(self, name):
        u"Indique s'il s'agit ou non d'un répertoire distant."
        try:
            self.cwd(name)
            self.cwd('..')
            return True
        except error_perm:
            return False

    def remove_r(self, rpath):
        u"Efface un fichier ou un répertoire, même non vide."
        if self.is_rdir(rpath):
            for pth in self.nlst(rpath)[2:]:
                self.remove_r(pth)
            print('* %s : %s ' % (rpath, self.rmd(rpath)))
        else:
            print('* %s : %s ' % (rpath, self.delete(rpath)))


    def copy_r(self, lpath, rdest):
        u"""Copie récursivement un répertoire local à l'emplacement distant indiqué.

        L'emplacement distant est créé lors de la copie, et ne doit pas exister
        au préalable (contrairement au `cp -r` de UNIX).
        """
        if isdir(lpath):
            print("\033[32m%s\033[0m" % self.mkd(rdest))
            for pth in listdir(lpath):
                self.copy_r(join(lpath, pth), join(rdest, pth))
        else:
            with open(lpath) as _file:
                print('* %s : %s '
                       % (rdest, self.storbinary('STOR ' + rdest, _file)))


    def miroir(self, lpath, rdest):
        u"""Crée un clône du répertoire local à l'emplacement distant.

        Si l'emplacement distant existe déjà, il est supprimé au préalable."""
        if self.is_rdir(rdest):
            self.remove_r(rdest)
        self.copy_r(lpath, rdest)

FTPCONFIG = join(_module_path, '.ftpconfig')

if isfile(FTPCONFIG):
    with open(FTPCONFIG) as _file:
        LOGIN, PASSWORD = _file.read(1000).split()
else:
    LOGIN = raw_input('login:')
    PASSWORD = raw_input('password:')

ftp = MyFTP(HOST)

while LOGIN or PASSWORD:
    try:
        ftp.login(LOGIN, PASSWORD)
        ftp.set_pasv(True)
        break
    except error_perm:
        print('\n*** Login incorrect. ***\n')
        LOGIN = raw_input('login:')
        PASSWORD = raw_input('password:')

ftp.miroir(LOCAL_PATH, REMOTE_PATH)
ftp.quit()
print(u'\n\033[32mLa doc a été mise à jour avec succès !\033[0m\n')
