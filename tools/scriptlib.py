# -*- coding: utf-8 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)
from __future__ import with_statement

######################################
#
#    Scriptlib
#
######################################
#
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
#
######################################

import sys, shutil, os, glob, subprocess

_path_7zip = r"C:\Program Files\7-Zip\7z.exe"

def norm(path):
    return os.path.realpath(os.path.normpath(os.path.expanduser(path)))

def cp(src, dst, **kw):
    src_found = False
    for pth in glob.glob(norm(src)):
        if os.path.isfile(pth):
            shutil.copy(pth, norm(dst))
            src_found = True
        elif os.path.isdir(pth):
            shutil.copytree(pth, norm(dst))
            src_found = True
    if not src_found and not kw.get('quiet', False):
        print('Warning: %s not found.' % repr(src))


def mv(src, dst):
    for pth in glob.glob(norm(src)):
        shutil.move(pth, norm(dst))

def rm(*paths, **kw):
    quiet = kw.get('quiet', False)
    recursive = kw.get('recursive', False)
    if recursive:
        cwd = os.getcwdu()
        listcwd = os.listdir('.')
    for path in paths:
        pths = glob.glob(norm(path))
        if not (pths or quiet or recursive):
            print "Warning: %s not found, couldn't be removed." %path
        for pth in pths:
            if os.path.isfile(pth):
                os.remove(pth)
        if recursive:
            for pth in listcwd:
                if os.path.isdir(pth):
                    cd(pth)
                    rm(*paths, **kw)
                    cd(cwd)

def rename(src, dst):
    os.rename(norm(src), norm(dst))

def rmdir(*paths, **kw):
    quiet = kw.get('quiet', False)
    for path in paths:
        pths = glob.glob(norm(path))
        if not (pths or quiet):
            print "Warning: %s not found, couldn't be removed." %path
        for pth in pths:
            if os.path.isdir(pth):
                shutil.rmtree(norm(pth))

def mkdir(path):
    os.mkdir(norm(path))

def cd(path):
    return os.chdir(norm(path))

def command(string, quiet=False):
    out = subprocess.Popen(string, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout
    output = out.read()
    sys.stdout.write(output)
    out.close()
    if not quiet:
        print "Commande '%s' executee." %string
    return output

def zip7(string):
    command('"%s" %s' %(_path_7zip, string))

def compil(script):
    command(sys.executable + ' -O ' + script + ' py2exe')

def append(srcs, dst):
    with open(dst, 'wb') as dest:
        for src in srcs:
            with open(src, 'rb') as source:
                dest.write(source.read())

def pause(string = "\n-- pause --\n"):
    raw_input(string)

def ls(path = '.'):
    if '*' in path:
        return glob.glob(path)
    return os.listdir(norm(path))
