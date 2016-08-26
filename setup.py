#!/usr/bin/env python

from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals
from distutils.core import setup
from wxgeometrie.param import version

long_description = u"""\
Geophar provides various tools for math teachers :
 * dynamic geometry
 * various plots (function curves, histograms, probability trees...)
 * symbolic calculus (with extensive LaTeX support)
 * tools to generate LaTeX code (functions variations and sign tables).

It follows french conventions concerning graphics, as taught in french schools.

Note that Geophar is only avalaible in french currently.
"""

setup(name=u'Geophar',
    version=version,
    description='Dynamic geometry, plots and symbolic calculus for teachers.',
    long_description=long_description,
    keywords=['math', 'CAS', 'geometry', 'french', 'latex', 'plot'],
    author='Nicolas Pourcelot',
    author_email='nicolas.pourcelot@gmail.com',
    url='http://wxgeo.free.fr/',
    license='GPLv2 or next',
    packages=['wxgeometrie'],
    package_data = { 'wxgeometrie' : ['wxgeometrie/images/*.png'] },
    )
