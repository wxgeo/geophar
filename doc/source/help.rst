
.. image:: images/logo.png
    :alt: WxGeometrie

=

Dynamic geometry, graph plotter, and more for french mathematic teachers.
*Copyright (C) 2005-2011 Nicolas Pourcelot*

**http://wxgeo.free.fr**

Sommaire
--------

1.
`Licence`_
:::::::

2.
`Installation`_
::::::::::::

3.
`Premiers pas`_
::::::::::::

    1.  `Le module de geometrie dynamique`_
    2.  `Le traceur de courbes`_
    3.  `La calculatrice`_
    4.  `Le module de statistiques`_
    5.  `Le generateur d'arbres de probabilites`_


4.
`Utilisation avancee`_
:

    1.  ` Le fichier param.py`_
    2.  `Debogage`_
    3.  `La ligne de commande `_


5.
`Comment contribuer ?`_
::::::::::::::::::::

6.
`Remerciements`_
:::::::::::::



-


I. LICENCE
----------

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 2 of the License, or (at your option) any later
version.
This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
details.
You should have received a copy of the GNU General Public License along with
this program; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA 02110-1301

Ce programme est un logiciel libre; vous pouvez le redistribuer et/ou le
modifier selon les termes de la GNU General Public Licence telle qu'elle a
ete publiee par la Free Software Foundation; soit la version 2 de la licence,
ou (au choix) toute version ulterieure.
Ce programme est distribue dans l'espoir qu'il puisse etre utile, mais sans
aucune garantie, pas meme la garantie implicite qu'il puisse etre adapte a un
usage donne. Pour plus de precisions, lisez la GNU General Public License.
Vous avez recu en principe une copie de la GNU General Public License en meme
temps que ce programme. Si ce n'est pas le cas, ecrivez a l'adresse suivante
: Free Software Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA
02110-1301



II. INSTALLATION
----------------

Pour fonctionner, ce programme necessite la configuration logicielle suivante
:


-   Windows 98 ou superieur, ou une distribution Linux assez recente.
-   Le logiciel Python, version 2.4 ou superieure.
(Logiciel libre, disponible gratuitement sur *http://www.python.org *)
Sous Linux, une version recente est en principe deja presente.
-   La librairie graphique WxPython, version 2.6 (des problemes
    subsistent avec la version 2.8 sous Windows).
(Logiciel libre, disponible gratuitement sur *http://www.wxpython.org*)
Sous Linux, une version est en principe deja presente, mais elle n'est pas
toujours assez recente.
-   La librairie mathematique numpy
(Logiciel libre, disponible gratuitement sur *http://sourceforge.net/project/
showfiles.php?group_id=1369&package_id=175103*)
-   La librairie mathematique Matplotlib, version 0.91.2 ou superieure
(Logiciel libre, disponible gratuitement sur
*http://www.sourceforge.net/projects/matplotlib*)

*

Remarque* : ces logiciels doivent etre installes dans l'ordre mentionne.

Sous Windows, un redemarrage du systeme est conseille apres ces
installations.

Apres avoir telecharge la derniere version de WxGeometrie
(*http://www.sourceforge.net/projects/wxgeometrie*), dezippez l'archive dans
un repertoire sur lequel vous avez les permissions necessaires.
Vous pouvez lancer le programme en double-cliquant sur le fichier
*wxgeometrie.pyw* .

*Sous Windows :*
Il existe desormais un programme d'installation de WxGeometrie.
Ce programme necessite un acces a internet, car il telecharge les dernieres
versions de Python, et des autres librairies necessaires (afin de ne pas
alourdir inutilement le programme d'installation en incluant systematiquement
tout).

Pour **desinstaller** WxGeometrie, il suffit de supprimer le repertoire
d'installation du programme. En effet, pour l'instant, WxGeometrie n'ecrit
rien dans la base de registre.

Il existe egalement une version sans installation, qui ne necessite pas la
presence de Python.
Cette derniere version est surtout livree a des fins de demonstration (ou
pour etre utilisee sur une clef USB, style Framakey) ; elle est  probablement
moins stable (si quelqu'un veut reprendre et ameliorer le projet ?).




III. PREMIERS PAS
-----------------

Certaines options de WxGeometrie ne sont pas encore fonctionnelles.
Il ne s'agit pas de bugs en general, mais, simplement, du fait que ces
options ne sont pas encore completement ecrites. Ainsi, un certain nombre de
boutons et d'entrees du menu ne provoquent aucune action dans les versions
actuelles. Ceci correspond a des fonctionnalites qui seront implementees dans
les prochaines versions.

WxGeometrie est composee de plusieurs modules ; les 5 principaux sont :


-   Un module de geometrie dynamique.
-   Un traceur de courbes.
-   Une calculatrice formelle.
-   Un module graphique de statistiques.
-   Un generateur d'arbres de probabilites.

Les autres modules presents sont fournis a titre purement experimental, et ne
sont donc pas documentes ici.

*Note :*
Toutes les fonctionnalites du module de geometrie dynamique sont utilisables
dans le traceur de courbes ; elles sont aussi (en partie) utilisables dans le
module de statistiques.


1. Le module de geometrie dynamique
~~~~~~~~~~~~~~


**Pilotage avec la souris**
Vous pouvez pour l'instant faire les actions suivantes :


-   creer une nouvelle feuille
-   creer differents types de points, de droites, de cercles, des
    vecteurs, des intersections...
-   modifier les proprietes de ces differents objets (changer leur
    couleur, les masquer...)
-   regler la fenetre d'affichage
-   orthonormaliser le repere
-   annuler une ou plusieurs actions
-   exporter et sauvegarder la figure

Utilisation de la souris pour piloter le logiciel :


-   Laissez enfonce le bouton droit de la souris pour deplacer la figure.
-   La molette de la souris permet de zoomer sur la figure.
-   En laissant enfoncee la touche [Ctrl], la molette de la souris permet
    d'ajuster la taille des textes de la figure.
-   Laissez enfoncee la touche [Ctrl], et le bouton gauche de la souris,
    pour selectionner une zone et zoomer dessus.
-   Vous pouvez deplacer les points libres de la figure avec la souris.
-   Placez-vous sur un point, ou un texte, et appuyez sur la touche
    [Entree], pour le renommer.
-   Placez-vous sur un objet, et faites un clic droit pour editer ses
    proprietes
-   Placez-vous sur un objet, et faites [Suppr] pour le supprimer, ou
    [Maj] + [Suppr] pour le masquer .
-   Si vous creez un point libre en laissant la touche [Maj] enfoncee, le
    point se placera sur le quadrillage.
-   Vous pouvez deplacer le nom d'un point autour de celui-ci en cliquant
    dessus, la touche [Alt] etant enfoncee.

*Note:*
Sous Ubuntu, la touche [Alt] est deja utilisee pour deplacer la fenetre. Il
est conseille de modifier ce comportement : dans Systeme>Preference>Fenetres,
choisir "Super" comme "touche de mouvement".

**Creation d'objets via le menu *Creer***
Pour la creation des objets geometriques, il existe une abondante aide
contextuelle dans chaque fenetre de creation d'objet.
Cliquez sur le point d'interrogation en haut de la fenetre, puis sur un
champ, pour obtenir une aide detaillee.
En cliquant avec le bouton du milieu de la souris dans un champ, vous ferez
egalement apparaitre diverses propositions.

Vous pouvez utiliser les notations suivantes : [A B] pour le segment [AB], (A
B) pour la droite (AB), (A>B) pour le vecteur A->B, ||A>B|| pour sa norme.
*Remarquez l'espace entre les lettres "A" et "B" dans les deux premiers cas.*


**Choisir le mode d'affichage de l'etiquette d'un objet**
Vous remarquerez que chaque objet possede quatre modes d'affichage : nom,
texte, formule, ou aucun.
.. image:: images/ptes_objets.png
    :alt: "Fenetre de propriete"


Que signifient ces 4 modes ?


-   Mode ? Nom ? : le nom de l'objet est affiche.
Un nom d'objet doit commencer par une lettre (non accentuee), suivie de
lettres (non accentuees) et de chiffres.
Il est forcement unique.
Certains noms sont reserves (*e, pi, x, y, t, i, ...* )
-   Mode ? Texte ? : un texte est affiche a la place du nom.
Ce mode permet d'associer n'importe quel type de texte a un objet.
La syntaxe LATEX est egalement partiellement supportee, dans ce cas, le texte
doit etre entre $.
*Exemple :*
"$\alpha_{n}$"
-   Mode ? Formule ? : le texte affiche est interprete comme une formule.
On peut aussi melanger du texte interprete et non interprete, en mettant les
blocs a interpreter entre { }.
*Exemple :*
"Le point A a pour abscisse {A.x} et pour ordonnee {A.y}."
-   Mode ? Aucun ? : rien n'est affiche.




**La ligne de commande**
Elle permet de creer rapidement des objet geometriques. (Personnellement, je
l'utilise frequemment).
Elle fonctionne dans le module geometrie, dans le module traceur, et dans le
module statistiques.

*Utilisation :*
Voici quelques exemples qui parleront mieux qu'un long discours...

*Exemples*


1.  "A=Point(1,2)" ou "A=(1,2)"
Creation d'un point A de coordonnees (1 ; 2).

2.  "u=Vecteur(1,2)" ou "u=(1,2)"
Creation d'un vecteur u de coordonnees (1 ; 2).

3.  "AB=Segment(A,B)" ou "AB=[A B]"
Creation du segment [AB].
*Attention a l'espace entre les lettres dans le deuxieme cas.*
4.  "d=Droite(A,B)" ou "d=(A B)"
Creation de la droite (AB).
*Attention a l'espace entre les lettres dans le deuxieme cas.*
5.  "u=Vecteur(A,B)" ou "u=A>B"
Creation du vecteur A->B.
6.  "M=C+2*(A>B)"
Creation du point M verifiant C->M = 2 A->B.
*Les parentheses sont obligatoires.*
7.  "fenetre=(-10,10,-5,5)"
Changement de la fenetre d'affichage (xmin, xmax, ymin, ymax).
*Si l'affichage est en mode orthonorme, la fenetre sera elargie pour
respecter cette contrainte.*



2. Le traceur de courbes
~~~~~~~~~~~~~~~~~~~~~~~~

Vous pouvez pour l'instant faire les actions suivantes :


-   regler la fenetre d'affichage
-   orthonormaliser le repere
-   utiliser des objets geometriques
-   representer des suites


Le traceur de courbes supporte les fonctions definies par morceau, continues
ou non.

*Exemples* :
1) Soit la fonction *f*, definie sur R-{0} par *f*(*x*)=1/*x*
Remplissez les champs de la maniere suivante :
 .. image:: images/inverse.png
    :alt: [V] Y1= [ 1/x ] sur [ R-{0} ]


*Notes* : vous remplissez le premier champ avec 1/x (la fonction), le
deuxieme avec l'intervalle de definition, c'est-a-dire R-{0}.
.. image:: images/inverse_graphe.png
    :alt: Graphe de la fonction inverse.


2) Soit la fonction  *f*, definie sur [-2;0[ par *f*(*x*) = -1, et sur
    [0;1[ U ]2;3] par *f*(*x*) = *x*
Remplissez les champs de la maniere suivante :
.. image:: images/morceaux.png
    :alt: [V] Y2= [ -1|x ] sur [ [-2;0[|[0;1[U]2;3] ]


*Notes* : Vous remplissez le premier champ avec la fonction.
Comme elle est definie par morceaux, on utilise le symbole "|" comme
separateur: ce qui donne -1|x.
Vous remplissez le 2eme champ avec l'intervalle de definition.
Comme elle est definie par morceaux, on utilise le symbole "|" comme
separateur: ce qui donne [-2;0[|[0;1[U]2;3].
.. image:: images/morceaux_graphe.png
    :alt: Graphe d'une fonction affine par morceaux.



3. La calculatrice
~~~~~~~~~~~~~~~~~~

Son fonctionnement sera assez familier pour quiconque a deja utilise une
calculatrice scientifique.
Elle permet de travailler sur des nombres reels ou complexes, et de faire du
calcul formel de niveau lycee.


En particulier, on peut developper, factoriser, deriver, integrer, et
resoudre des (in)equations ou des systemes lineaires :


-   developpe((x-3)(x+sin(x)-4))
-   factorise(x*exp(x)+exp(x))
-   derive(x^2+x+1)
-   integre(x^2+x+1)
-   resous(x*exp(x)+exp(x)=0)
-   resous(x+3>2-x ou (x-4<=3x+7 et x>0))
-   resous(x+3-y=2-x et x-4y=3x+7y-1)





*Nota 1* : Pour obtenir le resultat d'un calcul sous forme decimale (calcul
approche), appuyez sur MAJ+ENTR?E au lieu de ENTR?E.
*Nota 2* : On peut faire apparaitre la liste des fonctions par un clic-droit
dans la zone de saisie, en laissant enoncee la touche CTRL.

Depuis la version 0.120, elle utilise la librairie de calcul formel sympy
*((C) 2006-2011 SymPy Development Team)*.

Des variables peuvent etre utilisees pour memoriser des valeurs, ou definir
des fonctions.

*Exemples*:


-   a = 25+7/4
-   f(x)=2x+17
-   g=f'
Ici, la fonction g est definie comme la derivee de la fonction f.





Notez que certaines variables sont protegees (i, e ou E, pi, ...).

4. Le module statistiques
~~~~~~~~~~~~~~~~~~~~~~~~~

Ce module sert essentiellement a tracer des diagrammes, qui n'existent pas
toujours sur tableur, ou qui y sont incorrectement definis.
A l'origine, ma motivation etait essentiellement de pouvoir tracer des
histogrammes, qu'OpenOffice.org? ou Excel? confondent avec les diagrammes en
barre.
Il fait aussi la difference entre diagrammes en barres et en batons
(contrairement a ce qu'on peut lire souvent, la difference essentielle n'est
pas esthetique).

Voici une presentation des principaux types de graphiques :

***Diagrammes en barres :**
*Utilises en particulier pour des series a caractere qualitatif.
*Exemple :* la repartition des voyelles dans l'alphabet.

On selectionne le mode :
.. image:: images/diag_barres0.png


On ajoute les valeurs et les effectifs (ou frequences) qui leur
correspondent.
La syntaxe est la suivante : ? effectif * valeur ? (valeur doit etre entre
guillemets, pour des valeurs non numeriques).
.. image:: images/diag_barres1.png

Il ne reste plus qu'a completer la legende :
.. image:: images/diag_barres2.png


Et a appuyer sur [Entree] dans un des champs.
Le resultat est le suivant :
.. image:: images/diag_barres.png


*
**Diagrammes en batons :**
*Utilises pour des series a caractere quantitatif discret.
*Exemple :* la repartition des pointures de chaussures chez les femmes
fran?aises adultes (2005).

On selectionne le mode :
.. image:: images/diag_baton_0.png


On ajoute les valeurs et les effectifs (ou frequences) qui leur
correspondent, et on complete la legende :
.. image:: images/diag_baton_1.png


On presse la touche [Entree] dans un des champs.
Le resultat est le suivant :

.. image:: images/diag_baton_2.png

*

**Histogrammes :**
*Utilises pour des series a caractere quantitatif continu.
On va reprendre l'exemple precedent, en regroupant les pointures par classe.

On selectionne le mode :
.. image:: images/histo_0.png


On complete la rubrique ? Regroupement par classes ?.
.. image:: images/histo_1.png


Pour les histogrammes, il n'y a pas d'ordonnee, mais il faut preciser la
nature de l'unite d'aire.
.. image:: images/histo_2.png


Et on appuye sur [Entree].
.. image:: images/histo_3.png



*
**Pour aller plus loin :
***

-   A la place des valeurs numeriques, on peut tout a fait inserer des
    formules.
*Exemple : *
.. image:: images/stats_avance.png

-   La generation de listes est egalement possible. La syntaxe est celle
    de Python (cf. *list comprehensions* dans la documentation de Python).
Essayez par exemple de rentrer cette formule : [(rand(),i) for i in
range(4)].
-   Dans Outils, trois sous-menus permettent respectivement de creer des
    experiences.
En particulier, a titre d'exemple, il est possible de simuler des** lancers
de des**, et des **sondages simples**.

N'hesitez pas a editer le fichier *experience.py* dans
*modules/statistiques*/, et a y ajouter de nouvelles fonctions.
Vous pourrez ensuite realiser vos propres experiences, depuis le menu ?
Experience ?.
.. image:: images/stats_experience.png

Entrez votre formule dans le champ ? Experience ? (ici, un lancer de de), et
le nombre d'experiences.
Eventuellement, entrez aussi les valeurs possibles . Pour un lancer de de par
exemple, cela permet d'afficher en legende 1, 2, 3, 4, 5 et 6,
quand bien meme il n'y aurait aucun ? 4 ? par exemple.

*Notes :*
- Pour simuler des lancers de des, mieux vaut utiliser le menu specialement
dedie (quelques optimisations y ont ete faites).
- La case ? lancer une animation ? n'a pas d'effet pour l'instant.



******

4. Le generateur d'arbres de probabilites
~

.. image:: images/arbre.png

Les arbres de probabilite sont codes de la maniere suivante :


-   La premiere ligne (optionnelle) correspond a la legende.

*Exemple :*
||Premier tirage|Deuxieme tirage

*(Note : l'ajout de barres verticales supplementaires (AltGr+6) decale la
legende vers la droite.)*
-   Les lignes suivantes correspondent a l'arbre proprement dit.


    -   Le nombre de > correspond au niveau dans l'arbre.
    -   La syntaxe est la suivante :
? Nom de l'evenement ? : ? Probabilite de l'evenement ?


*Exemple :*
omega
> A:1/4
>> B:1/5
>> J:2/5
>> V:...
> &A :3/4
>> B:...
>> J:...
>> V:...
Le **symbole &** indique qu'il s'agit de l'evenement contraire : &A est ainsi
l'evenement ?A barre?.
*(Note : la syntaxe LaTeX est egalement acceptee).*


IV. UTILISATION AVANC?E
-


1. Le fichier param.py
~~~~~~~~~~~~~~~~~~~~~~

Un grand nombre de parametres peuvent etre modifies dans le fichier
*param.py* avec un simple editeur de textes.
*Exemple: *
Remplacez "affiche_axes = True" par "affiche_axes = False" pour que les axes
ne soient plus affiches par defaut.

Note : il peut etre parfois necessaire d'effacer le dossier */preferences*
(qui contient les parametres de la session precedente) pour que les
changements soient pris en compte.
2. Debogage
~~~~~~

Dans le menu Avance>Deboguer, selectionner ? Deboguer ? pour faire apparaitre
une fenetre contenant entre autres tous les rapports d'erreurs. Par ailleurs,
le repertoire */log* contient les fichiers .log generes lors de la derniere
execution (actions effectuees, messages d'erreurs, etc.)
3. La ligne de commande
~~~~~~~~~~~~~~~~~~~~~~~

*Introduction:*
La ligne de commande sert essentiellement a debuguer le programme.
(Ou a realiser certaines operations internes, etc...)
La ligne de commande permet d'executer des instructions Python.

Precede du symbole **&**, le resultat de la commande sera affiche dans la
console. (*NB* : assurez-vous au prelable que l'option ? Deboguer ? soit
cochee, dans le menu Avance>Deboguer).


Les raccourcis suivants sont disponibles :

-   *!p.* pour *panel.*
-   *!c.* pour *canvas.*
-   *!f.* pour *feuille.*
-   *!o.* pour *objets.*
-   *!g.* pour *moteur_graphique.*


Leur maniement necessite evidemment de bien connaitre l'API de WxGeometrie,
et donc de faire un tour dans le code source.

*Exemples :*
1) "print 'hello world !'"
Ceci va afficher 'hello wold !' sur la console.
*NB :* ? & 'hello world !' ? produirait le meme resultat.
2) "print objets.A"
Affiche, s'il existe, l'objet A dans la console.
*NB :* Cette commande s'abrege de meme en ? & !o.A ?.
3) "panel.exporter('test.png')"
Exporte la figure courante en un fichier *test.png*.
*NB :* Forme abregee : ? !p.exporter('test.png') ?.
4) "feuille.fenetre = (-5,2,-7,3)"
Change la fenetre d'affichage en (-5, 2, -7, 3).
*NB :* Forme abregee : ? !f.fenetre = (-5,2,-7,3) ?.


V. COMMENT CONTRIBUER ?
-----------------------

**Vous pouvez par exemple :**


-   m'envoyer un mail a l'adresse suivante :
    `wxgeo@users.sourceforge.net`_, en me donnant vos impressions generales.
-   corriger les eventuelles fautes d'orthographe.
-   me signaler des bugs existants, et non repertories sur le tracker
    *http://wxgeo.free.fr/tracker* .
-   me proposer des corrections de bug :)
-   ajouter des fonctions mathematiques a la calculatrice
-   implementer la gestion des coniques
-   commencer de geometrie dynamique dans l'espace
-   completer cette documentation ou creer un tutoriel (je manque de
    temps pour tout faire !)



Je suis egalement ouvert a toute autre contribution, et je suis pret a
travailler en equipe... :-)


**Je recherche en particulier (liste non exhaustive) :**


1.  des personnes pour m'aider a maintenir et a ameliorer :


    -   le fonctionnement sous Linux :
tests, creation de scripts bash d'installation, de paquetages .deb ou .rpm,
guides utilisateurs, etc..., chose que je n'ai pas le temps de faire aussi
bien que je le souhaiterais.
    -   le fonctionnement sous MacOs X :
theoriquement, ?a devrait tourner assez facilement,  mais je n'ai jamais eu
la possibilite de le tester.


2.  des personnes interessees par la construction de nouveaux modules
    pour WxGeometrie.
Je pense en particulier a des professeurs de mathematiques, de sciences-
physiques, de technologie... qui auraient un peu d'experience en
programmation objet (mais pas necessairement en python : python en lui-meme
s'apprend en une semaine).
Une premiere experience fructueuse a deja commencee, en collaboration avec
Christophe Vrignaud.

3.  des personnes pour me faire remonter des rapports de bugs, ou des
    suggestions. A quelques exceptions pres, les seuls echos que j'ai pu
    avoir, ce sont les statistiques de sourceforge. Je sais que le projet
    manque encore de maturite, mais au fil des versions, il y a desormais un
    peu de matiere. Toutes les critiques sufisamment precises sont bonnes a
    prendre. ;-)

*

Note :*  une documentation specifique pour developpeurs se trouve dans le
repertoire *doc/developpeurs/*.




VI. REMERCIEMENTS
-----------------


Sans pretention d'exhaustivite, je voudrais remercier :

-   Boris Mauricette, pour avoir contribue au module de Statistiques
    (trace des quartiles).
-   Christophe Bal pour ses commentaires, et pour avoir propose la
    syntaxe du module de Probabilites.
-   Les developpeurs de sympy, avec qui j'ai toujours eu des echanges
    cordiaux et constructifs, y compris de code.
Remerciements plus particuliers a Chris Smith, Vinzent Steinberg et Aaron
Meurer.
-   Christophe Vrignaud, qui a developpe et maintenu quelques temps le
    module Scicalc pour Wxgeometrie.
-   Stephane Clement a mis a disposition de Wxgeometrie le wiki de
    l'academie d'Aix-Marseille.
-   Tous ceux qui ont pris le temps de faire quelques commentaires sur ce
    programme, et m'ont encourage a continuer (en particulier dans les
    premiers temps : mon frere Thomas, Enzo, Rhydwen Volsik, Robert
    Setif...).
-   Fran?ois Lermigeaux, pour les coups de pub occasionnels.
-   Georges Khaznadar, pour ses nombreux conseils concernant Debian.
-   Tous ceux qui ont pris le temps de faire des rapports de bugs et des
    retours.



Merci enfin a Sophie pour sa patience !


.. _Licence: #licence
.. _Installation: #installation
.. _Premiers pas: #pas
.. _trie dynamique: #geometrie
.. _Le traceur de courbes: #courbe
.. _La calculatrice: #calc
.. _Le module de statistiques: #stats
.. _s: #probas
.. _e: #avance
.. _ Le fichier param.py: #param
.. _bogage: #debogage
.. _La ligne de commande : #ligne
.. _Comment contribuer ?: #contrib
.. _Remerciements: #merci
.. _wxgeo@users.sourceforge.net: mailto:wxgeo@users.sourceforge.net
