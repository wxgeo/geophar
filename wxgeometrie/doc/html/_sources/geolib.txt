Textes, labels, étiquettes
==========================

Présentation
------------

Chaque objet représentable (en gros, tous les objets sauf ceux de type
``Variable_generique``) possède une étiquette.

.. note:: Une exception notable : les objest de type ``Texte`` gèrent eux
          même leur affichage, sans passer par une étiquette.

Cette étiquette permet d'afficher le nom de l'objet, ou un commentaire associé
à l'objet.
Éventuellement, ce commentaire peut contenir du code LaTeX, pour sa mise
en forme::

    >>> from wxgeometrie import *
    >>> f = Feuille()
    >>> A = f.objets.A = Point(-1, 5)
    >>> A.label(u"bonjour, $\\alpha_i+\\beta_j=\\frac{\\pi}{2}$ !")
    >>> A.label()
    u'bonjour, $\\alpha_i+\\beta_j=\\frac{\\pi}{2}$ !'

Il peut aussi contenir des formules interprétées::

    >>> A.label(u"Mon abscisse est {A.x}, et mon ordonnée est {A.y}.", formule=True)
    >>> A.label()
    u'Mon abscisse est -1, et mon ordonnée est 5.'

Les portions interprétées doivent être entre accolades.


Mode d'affichage, formatage
---------------------------
Il y a 3 modes d'affichages:

    * NOM : le nom de l'objet est affiché près de l'objet (défaut sauf pour les
      objets ``Texte``).
    * TEXTE : le commentaire est affiché près de l'objet (défaut pour les objets
      ``Texte``).
    * FORMULE : le commentaire est affiché près de l'objet, et les sections entre
      accolades sont interprétées.

Il y a également 3 modes de formatage :

    * RIEN: aucun formatage n'est appliqué.
    * MATH: le texte est supposé être une expression mathématique.
      Il est converti autant que possible en code LaTeX (fractions, etc.)
    * CUSTOM: une fonction de formatage personnalisée est appliquée.

.. warning:: Pour l'instant, le mode CUSTOM n'est pas supporté.



Implémentation
--------------

Les textes et les étiquettes possèdent un argument `texte`, qui contient le texte
brut à afficher (après éventuellement interprétation, conversion en LaTeX, ...
suivant les mode d'affichage et de formatage).

Ils possèdent également un style `mode` et un style `formatage`.

Valeurs possibles pour `mode` : NOM, TEXTE, FORMULE.

Valeurs possibles pour `formatage`: RIEN, MATH.

Pour plus de facilité, chaque objet possède une méthode ``.label()``.

Cette méthode permet de modifier simultanément le texte, le mode d'affichage,
et le formatage du texte.

Elle retourne un texte prêt à l'affichage, c'est-à-dire formaté et/ou interprété
le cas échéant.

.. note:: L'utilisation de la méthode ``Objet.label()`` permet d'avoir une
          interface commune aux objets ``Texte`` et aux autres objets.

          Il est fortement conseillé d'utiliser la méthode ``.label()``
          de l'objet, plutôt que l'attribut ``.texte`` du texte ou de l'étiquette
          de l'objet.

.. note:: À l'exception des objets ``Texte``, la méthode ``Objet.label()``
          redirige vers la méthode ``Label_generique.label()`` de l'étiquette.




Enfants, parents, ancetres et heritiers
=======================================

Terminologie
------------

Au sein d'une feuille, les objets géométriques dépendent souvent les uns
des autres.

Par exemple, considérons le code suivant::

    >>> from wxgeometrie import *
    >>> A = Point(1, 5)
    >>> B = Point(8, 2)
    >>> AB = Segment(A, B)
    >>> M = Point(AB)

Le point `M` dépend du segment `AB` : si `AB` est modifiée, les coordonnées
du point seront adaptées afin que le point reste sur le segment.

On dit que le point `M` est un **enfant** du segment `AB`.

    >>> M in AB.enfants
    True

De même, le segment `AB` est **enfant** des points `A` et `B` : si `A` ou `B`
est modifié, la longueur du segment `AB` sera automatiquement modifiée en
conséquent.

Ces relations de dépendance sont primordiales dans un logiciel de géométrie
dynamique : si un objet est modifié, il faut que tous les objets
qui en dépendent soient actualisés (mais seulement eux, pour des raisons
évidentes de performance).

Dans le code précédent, le point `A` n'a qu'un seul enfant, le segment `AB`,
qui a lui-même pour enfant le point `M`.

Comme `M` dépend, quoique indirectement, du point `A`, on dit que `M`
est un **héritier** de `A`.

Le point `A` possède ainsi 2 héritiers : le segment `AB`, et le point `M`.

À l'inverse, les **ancêtres** du point `M` sont le segment `AB` (**parent**,
c'est-à-dire ancêtre direct) et les points `A` et `B` (ancêtres indirects).



Implementation
--------------

Les **parents** sont faciles à récupérer, car tous les objets géométriques
gardent en mémoire leurs arguments de construction.

On génère la liste des parents d'un objet_geometrique via la méthode
``Objet._recenser_les_parents()``.

.. note:: En principe, cette méthode n'a pas à être appelée directement.

Le résultat est mis en cache dans l'attribut ``._parents``::

    >>> AB._parents == set([A, B])
    True

.. note:: le résultat retourné est du type *set* (ensemble).

Si l'on souhaite la liste de *tous* les ancêtres (requête récursive), on utilise
alors la méthode ``Objet._ancetres()``.

    >>> AB._ancetres == set([A, B, A.x, A.y, B.x, B.y])
    True

.. note:: Des variables correspondant aux coordonnées des points `A` et `B` sont
          automatiquement générées lorsque les points sont créés.

..note:: Les **enfants** sont gardés en mémoire sous forme de *weakreferences*.
         Ainsi, si un objet n'est plus utilisé, il est automatiquement
         déréférencé des listes des enfants de chacun de ses parents.
         (Cela évite de maintenir en vie dans la mémoire de Python des objets
         « zombie », qui n'apparaissent plus nul part ailleurs.) [#]_

.. [#] Cela sert notamment pour les objets temporaires ou les intermédiares de
       construction, qui n'apparaissent pas sur la feuille. Les objets de la
       feuille, eux, gèrent proprement leur déréférencement auprès de leurs
       parents lorsqu'ils sont supprimés, via `Objet.supprimer()`.


Cas particulier des formules
----------------------------

La *légende* d'un objet peut contenir une *formule*, c'est à dire une expression
qui fait référence à des objets de la feuille (du moins en général), et qui
sera interprétée au moment de l'affichage de l'étiquette de l'objet [#]_.

.. [#] L'étiquette d'un objet est un objet spécial, qui est uniquement en charge
       de l'affichage de sa légende.

.. note:: Les objets *Texte* peuvent également contenir des formules dans le
          texte à afficher.

Supposons que l'objet `M` ait pour légende::

    u"Le point A a pour coordonnées ({A.x}, {A.y})."

Alors le point M doit dépendre des deux variables générées par la formule, à
savoir `Variable("A.x")` et `Variable("A.y")`.

Par conséquent, ces deux variables doivent être ajoutées aux parents de `M`,
tant que cette formule est associée au point `M` ; et `M` doit être ajouté
à la liste des enfants, pour chacune de ces deux variables.

Si le point `M` change de légende, il faut actualiser la liste des parents de
`M`.
