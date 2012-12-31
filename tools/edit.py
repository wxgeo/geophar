#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------##
#              WxGeometrie               #
#    Small facility for editing file     #
#        after Python bug repport        #
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


import re
import sys
import subprocess

# ----- User config -----
DEFAULT_EDITOR = 'geany'
# XXX: move this outside the script
# ------------------------

SUPPORTED_EDITORS = ('geany', 'gedit', 'nano', 'vim', 'emacs', 'kate')

def edit(file_and_line, editor=DEFAULT_EDITOR):
    u"Edit specified file at specified line, with editor."

    file_and_line = file_and_line.strip()
    try:
        m = re.search('File "?([^"]+[.]py)"?, line ([0-9]+)', file_and_line)
        if m is None:
            # Format pyflakes
            m = re.search('([^"]+[.]py):([0-9]+)', file_and_line)
        file_name = m.group(1)
        line = m.group(2)
    except AttributeError:
        print("Incorrect format (see help) : %s" % repr(file_and_line))
        return
    if editor not in SUPPORTED_EDITORS:
        print('"%s" is currently not supported.' % editor)
        print('Supported editors : ' + ','.join(SUPPORTED_EDITORS))
        return
    if editor in ('geany', 'kate'):
        command = '%s -l %s %s' % (editor, line, repr(file_name))
    else:
        command = '%s +%s %s' % (editor, line, repr(file_name))
    subprocess.call(command, shell=True)



def usage():
    u"Affiche l'aide."
    print u"""\n    === Usage ===\n
    - Éditer le fichier '~/wxgeometrie/filename.py' à la ligne 257 :
        $ ./tools/edit.py 'File "~/wxgeometrie/filename.py", line 257'
        """
    exit()


if __name__ == "__main__":
    args = sys.argv[1:]
    kw = {}
    if not args or args[0] in ('-h', '--help'):
        usage()
    else:
        edit(' '.join(args))
