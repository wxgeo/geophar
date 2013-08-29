# -*- coding: utf-8 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

resolution = .025
resolution_minimale = .002 # une valeur trop faible peut faire planter l'ordinateur (à adapter selon la puissance de la machine) !
mode = ("plot_surface", "plot_wireframe", "contour3D", "contourf3D")[0] # cf axes3d.py de matplotlib
epaisseur_grillage = .5
