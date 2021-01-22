# -*- coding: utf-8 -*-
from .repetition import repetition_experiences

# TODO: sortir DialogRepetition de repetition_experiences.py -> __init__.py
# pour que repetition_experiences.py n'importe plus pyQt (risque de ralentir l'import pour ptyx !)

def parse_text(text):
    """Describe drawing.

    Coordinates are expressed as percentages of picture dimensions.
    Return a dict containing 2 lists:
     * one for points: [(text, x, y), ...]
     * one for lines: [(text, xy1, xy2), ...]
    """
    lines = [l for l in text.split("\n") if l.strip()]

    if not lines:
        return {'points': [], 'lines': []}

    if lines[0].startswith("|"):
        legende = lines.pop(0)
        # On réserve de la place pour la légence
        ymax = 90
    else:
        legende = None
        ymax = 100

    if not lines:
        return {'points': [], 'lines': []}

    # Répétition d'expériences aléatoires indépendantes
    #
    # Ex:
    # >> A:  1/3
    # >> &A: 2/3
    #
    # équivaut à:
    #
    # > A_1:   1/3
    # >> A_2:  1/3
    # >> &A_2: 2/3
    # > &A_1:  2/3
    # >> A_2:  1/3
    # >> &A_2: 2/3

    if lines[0].startswith('>>'):
        profondeur = len(lines[0]) - len(lines[0].lstrip('>'))
        evenements = {}
        for line in lines:
            assert line.startswith(profondeur*'>')
            nom, proba = line[profondeur:].split(':')
            evenements[nom.strip()] = proba.strip()
        lines = repetition_experiences(_profondeur=profondeur, _numeroter=True, **evenements).split('\n')

    # La 1re ligne doit correspondre au 1er embranchement, c'est-à-dire à l'univers (Omega en général).
    # À défaut, on met un ligne vide (pas de nom au 1er embranchement donc).
    if lines[0].startswith(">"):
        lines = [""] + lines

    depths = [len(line) - len(line.lstrip(">")) for line in lines]

    nbr_colonnes = 1 + max(depths, default=0)

    # Nbr de lignes pour chaque colonne.
    nbr_lignes = []

    for i in xrange(nbr_colonnes):
        nbr_lignes.append(depths.count(i))

    #intersection, union : \cap \cup

    # Interprétation des lines sous forme de listes de listes
    # >A
    # >>B
    # >>C
    # >D
    # >>E
    # >>>F
    # >>>G
    # >>H
    # >E
    # devient :
    # [{'liste': [{'liste': [{'liste': [], 'texte': u'B'}, {'liste': [], 'texte': u'C'}], 'texte': u'A'}, {'liste': [{'liste': [{'liste': [], 'texte': u'F'}, {'liste': [], 'texte': u'G'}], 'texte': u'E'}, {'liste': [], 'texte': u'H'}], 'texte': u'D'}, {'liste': [], 'texte': u'E'}], 'texte': ''}]

    arbre = []
    ligne_precedente = [-1 for i in xrange(nbr_colonnes)] # numéro de ligne atteint pour chaque colonne
    for line in lines:
        colonne = len(line) - len(line.lstrip(">"))
        branche = arbre
        for i in xrange(colonne): # on se déplace de branche en branche ;)
            branche = branche[ligne_precedente[i]]["liste"]
        branche.append({"texte": line.lstrip(">"), "liste": []})
        ligne_precedente[colonne] += 1
        for i in xrange(colonne + 1, nbr_colonnes):
            ligne_precedente[i] = -1
    print arbre

    # on parcourt l'arbre pour compter le nombre de ramifications

    def compter_ramifications(branche):
        if len(branche["liste"]) > 0:
            return sum(compter_ramifications(tige) for tige in branche["liste"])
        else:
            return 1

    ramifications = sum(compter_ramifications(branche) for branche in arbre)
    if param.debug:
        print("Nombre de ramifications: " + str(ramifications))

    def formater_texte(texte):
        if texte:
            if texte.startswith("&"):
                texte = r"\overline{" + texte[1:] + "}"
            texte = texte.replace("&", r"\overline ")
            # P(\overline A) -> P(\overline{A})
            texte = re.sub("(\\\\overline)[ ]+(%s)" % VAR, lambda m:'%s{%s}' % (m.group(1), m.group(2)), texte)
            texte = "$" + texte + "$" if texte[0] != '$' else texte
            if param.latex:
                texte = "$" + texte + "$" # passage en mode "display" de LaTeX
            texte = texte.replace(" inter ", r"\  \cap \ ").replace(" union ", r"\  \cup \ ").replace("Omega", r"\Omega").replace("omega", r"\Omega")
            if param.latex: # on remplace les fractions. Ex: "1/15" -> "\frac{1}{15}"
                texte = re.sub("[0-9]+/[0-9]+",lambda s:"\\frac{" + s.group().replace("/", "}{") + "}", texte)
        return texte


    def creer_point(x, y, texte):
        texte = formater_texte(texte)
        M = Point(x, y, style = "o", couleur = "w", taille = 0)
        M.label(texte)
        M.etiquette.style(_rayon_=0, niveau=15, alignement_vertical="center",
                          alignement_horizontal="center", fond=True,
                          couleur_fond="w")
        return M


    def creer_segment(point1, point2, texte):
        texte = formater_texte(texte)
        s = Segment(point1, point2)
        s.label(texte)
        style = {'_rayon_': 0, 'niveau': 15}
        placement = self.param('placement_probabilites')
        if placement == 'dessus':
            style.update(alignement_vertical='center', couleur_fond='w',
                         fond=True, alignement_horizontal='center',
                         angle=0)
        elif placement == 'longe':
            style.update(alignement_vertical='auto', fond=False,
                         alignement_horizontal='center', angle='auto')
        elif placement == 'decale':
            style.update(alignement_vertical='auto', fond=False,
                         alignement_horizontal='right', angle=0)
        else:
            print(u"Placement: mode '%s' non reconnu." % placement)
        s.etiquette.style(**style)
        return s

    ramification = [0] # astuce pour avoir un "objet modifiable" (a mutable object)
    def parcourir_branche(branche, n, ramification = ramification):
        txt = branche["texte"].rsplit(":", 1)
        if len(txt) == 2:
            txt_pt, txt_segm = txt
        else:
            txt_pt = txt[0]
            txt_segm = ""
        if len(branche["liste"]) > 0:
            l = []
            for tige in branche["liste"]:
                l.append(parcourir_branche(tige, n + 1))

            M = creer_point(n/(nbr_colonnes - 1), .5*(l[0][0].ordonnee+l[-1][0].ordonnee), txt_pt)
            self.feuille_actuelle.objets.add(M)
            for point, txt_s in l:
                s = creer_segment(M, point, txt_s)
                self.feuille_actuelle.objets.add(s)
            return M, txt_segm
        else:
            if ramifications > 1:
                y = 1 - ramification[0]/(ramifications - 1)
            else:
                y = .5
            M = creer_point(n/(nbr_colonnes - 1), y, txt_pt)
            ramification[0] += 1
            self.feuille_actuelle.objets.add(M)
            return M, txt_segm

    for branche in arbre:
        parcourir_branche(branche, 0)

    if legende is not None:
        decalage = -0.5
        for i in legende:
            if i != "|":
                break
            decalage += .5
        legende = legende.strip("|").split("|")
        for n in xrange(len(legende)):
            t = Texte(legende[n], (n + decalage)/(nbr_colonnes - 1), 1.1)
            self.feuille_actuelle.objets.add(t)

    self.feuille_actuelle.interprete.commande_executee()
