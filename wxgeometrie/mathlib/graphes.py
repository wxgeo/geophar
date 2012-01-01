# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------#######
#                Graphes                  #
##--------------------------------------#######
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

# Lexicon
# http://www.apprendre-en-ligne.net/graphes/lexique/index.html
# http://en.wikipedia.org/wiki/Glossary_of_graph_theory

import collections, copy

from sympy import oo, Matrix
from ..pylib import OrderedDict, advanced_split

class GraphError(StandardError):
    pass

# http://www.chansonsdewallonie.be/PAGES/COULEURS/CouleursTeintes.htm
# http://www.w3.org/TR/css3-color/#svg-color (less usefull)

colors_dict = OrderedDict((
           ('bleu', (0, 0, 255)), ('rouge', (255, 0, 0)), ('vert', (0, 128, 0)),
           ('orange', (255, 69, 0)), ('violet', (148, 0, 211)), ('jaune', (255, 255, 0)),
           ('marron', (210, 105, 30)), ('rose', (255, 20, 147)), ('turquoise', (64, 224, 208)),
           ('indigo', (75, 0, 130)), ('magenta', (255, 0, 255)), ('ocre', (184, 134, 11)),
            ('olive', (184, 134, 11)), ('pomme', (127, 255, 0)), ('gris', (128, 128, 128)),
            ('noir', (0, 0, 0))
            ))

def colors():
    for color in colors_dict:
        yield color
    num = 0
    while True:
        yield 'color %s' %num
        num += 1



class Graph(dict):
    u"""A graph representation.

    Graph are stored as a dictionary:
    >>> from mathlib.graphes import Graph
    >>> g = Graph({'A': {'B':[1],'C':[2],'D':[3]}, 'B': {'A':[4],'C':[2]}, 'C':{}, 'D':{}}, oriented=True)

    For convenience, they may be entered as a string:
    >>> h = Graph("A>(B:1,C:2,D:3), B>(A:4,C:2), C, D", oriented=True)
    >>> g == h
    True

    If the graph is not oriented (default), the graph must be symetric:
    >>> k = Graph("A>(B:1,C:2,D:3), B>(A:4,C:2), C>(A:2,B:2), D>(A:3)")
    >>> k.symetric
    True
    """  #XXX: doctest fails !!!
#    teintes = ('bleu', 'rouge', 'vert', 'jaune', 'orange', 'violet',
#                        'marron', 'rose', 'turquoise', 'cyan', 'magenta', 'ocre',
#                        'marine', 'indigo', 'pourpre')

    def __init__(self, dictionary = (), oriented = False):
        # Ex: {"A": {"B":[1], "C":[2, 5]}, "B": {}, "C": {"A": [2], "C": [1]}}
        if isinstance(dictionary, basestring):
            dictionary = self._convert_input(dictionary)
        elif not isinstance(dictionary, dict):
            dictionary = dict.fromkeys(dictionary, {})
        for key, val in dictionary.items():
            if not isinstance(val, dict):
                dictionary[key] = dict.fromkeys(val, [1])
            elif isinstance(val, collections.defaultdict):
                dictionary[key] = dict(val)
            for node in dictionary[key]:
                if node not in dictionary:
                    raise GraphError("Edge contain a unknown node: %s." %repr(node))
        self.oriented = oriented
        dict.__init__(self, dictionary)
        if not oriented and not self.symetric:
            raise GraphError("Unoriented graph must be symetric.")


    @staticmethod
    def _convert_input(chaine):
        # Support nicer input format : "A>(B:1,C:2,D:3), B>(A:4, ...) ..."
        # -> {"A":{"B":1,"C":2,"D":3},"B":{"A":4, ...} ...}
        dic = {}
        nodes = advanced_split(chaine, ',')
        for node_stuff in nodes:
            if '>' in node_stuff:
                node, edges = node_stuff.split('>', 1)
            else:
                node, edges = node_stuff, '()'
            node = node.strip()
            edges = edges.strip()[1:-1]
            dic[node] = {}
            for edge in edges.split(','):
                if edge:
                    if ':' in edge:
                        node2, distance = edge.split(':', 1)
                    else:
                        node2, distance = edge, '1'
                    node2 = node2.strip()
                    if not dic[node].has_key(node2):
                        dic[node][node2] = []
                    dic[node][node2].append(float(distance) if '.' in distance else int(distance))
                    #TODO: support exact calculus
        return dic





    @property
    def order(self):
        return len(self)

##    @property
##    def ordered_nodes(self):
##        return sorted(self)

    nodes = property(dict.keys)

    @property
    def matrix(self):
        n = self.order
        nodes = sorted(self)
        def f(i, j):
            # In an unoriented graph, loops are counted twice.
            k = (1 if self.oriented or i != j else 2)
            return k*len(self[nodes[i]].get(nodes[j], ()))
        return Matrix(n, n, f)

    def degree(self, node):
        if self.oriented:
            return sum(len(edges) for node2, edges in self[node].items() if node2)
        else:
            # In an unoriented graph, loops are counted twice.
            return sum(len(edges) for node2, edges in self[node].items() if node2 != node) \
                    + 2*len(self[node].get(node, ()))


    @property
    def degrees(self):
        return dict((node, self.degree(node)) for node in self.nodes)

    @property
    def to_dict(self):
        return copy.deepcopy(dict(self))

    def adjacents(self, node1, node2):
        return self[node1].has_key(node2) or self[node2].has_key(node1)

    @property
    def connected(self):
        def adjacent(node, new_nodes):
            return any(self.adjacents(node, new) for new in new_nodes)
        remaining_nodes = set(self)
        new_nodes = [remaining_nodes.pop()]
        while new_nodes:
            new_nodes = [node for node in remaining_nodes if adjacent(node, new_nodes)]
            remaining_nodes.difference_update(new_nodes)
        return not remaining_nodes


    @property
    def symetric(self):
        M = self.matrix
        return M.transpose() == M

    @property
    def eulerian(self):
        odds = sum(self.degree(node)%2 for node in self.nodes)
        return odds in (0, 2)

    def _nodes_sorted_by_degree(self, *first_nodes):
        return list(first_nodes) \
            + sorted(set(self).difference(first_nodes), key = self.degree, reverse = True)


    def eulerian_trail(self, walk=None):
        if walk is None:
            #TODO: return an (arbitrary) eulerian trail if any, else None
            raise NotImplementedError
#            return trail

        # Convert input string to a list of nodes.
        for sep in ('-', ',', ';'):
            if sep in walk:
                walk_lst = walk.split(sep)
                break
        else:
            if ' ' in walk:
                walk_lst = walk.split()
            else:
                walk_lst = list(walk)
#            if not walk_lst:
#                raise SyntaxError, repr(walk) + " format is incorrect. Nodes should be separated by '-'."

        graph = self.to_dict
        previous = None # previous node

        def remove_edge(A, B):
            "Remove edge from graph"
            endpoints = graph.get(A, {})
            edges = endpoints.get(B, [])
            if edges:
                edges.pop()
            else:
                return False
            if not edges:
                endpoints.pop(B)
            if not endpoints:
                graph.pop(A)
            return True

        # We remove edges one by one from graph.
        for node in walk_lst:
            node = node.strip()
            if previous is not None:
                if not remove_edge(previous, node):
                    print("%s-%s edge does not exist, or was already used !"
                            %(previous, node))
                    return False
                    # Edge did not exist, or was already removed.
                if not self.oriented:
                    if not remove_edge(node, previous):
                        return False
            previous = node

        if graph:
            print("Following edges were never used:")
            for node in graph:
                for endpoint in graph[node]:
                    print ('%s-%s' %(node, endpoint))
        return not graph



    def coloring(self, *first_nodes):
        u"""Graph colorization using Welsh & Powell algorithm.

        By default, nodes are sorted according to their degrees, but you can also
        choose manually the first nodes to be visited.
        """
        coloring = []
        uncolored = self._nodes_sorted_by_degree(*first_nodes)
        while uncolored:
            coloring.append([])
            for node in uncolored:
                if not any(self.adjacents(node, s) for s in coloring[-1]):
                    coloring[-1].append(node)
            assert coloring[-1]
            uncolored = [s for s in uncolored if s not in coloring[-1]]
        return coloring


    def latex_WelshPowell(self, *first_nodes):
        ordered_nodes = self._nodes_sorted_by_degree(*first_nodes)
        dico = {}
        for nodes, color in zip(self.coloring(*ordered_nodes), colors()):
            for node in nodes:
                dico[node] = color
        # Génération du code LaTeX
        nodes_line =  r'Sommets '
        degrees_line =   r'Degr\'es'
        colors_line = r'Couleurs'
        for node in ordered_nodes:
            nodes_line += ' & $%s$ ' %node
            degrees_line += ' & $%s$ ' %self.degree(node)
            colors_line += ' & %s ' %dico[node]
        code = r'\begin{tabular}{|l||*{%s}{c|}}' % len(dico)
        code += '\n\\hline\n'
        code += nodes_line + '\\\\\n\\hline\n'
        code += degrees_line + '\\\\\n\\hline\n'
        code += colors_line + '\\\\\n\\hline\n'
        code += '\\end{tabular}\n'
        return code

    def shortest_path(self, start, end):
        u"Implementation of Dijkstra-Moore algorithm."
        # current node
        current = start
        # Nodes which have been already visited, but still not archived:
        visited = {start: [0, [start]]}
        # format: {node: [distance from start, [previous node, alternative previous node, ...]]}

        # Nodes which will not change anymore:
        archived = {}

        while current != end and visited:
            archived[current] = visited.pop(current)
            # We select the node having the smallest distance
            for neighbor in self[current]:
                if neighbor not in archived:
                    distance = visited.get(neighbor, [oo])[0]
                    new_distance = archived[current][0] + min(self[current][neighbor])
                    if new_distance < distance:
                        visited[neighbor] = [new_distance, [current]]
                    elif new_distance == distance:
                        visited[neighbor][1].append(current)
            current = min(visited.items(), key = lambda x:x[1][0])[0]
        if visited.has_key(current):
            archived[current] = visited.pop(current)
            in_progress = set([(current,)])
            final_paths = set()
            while in_progress:
                for path in set(in_progress):
#                    print path, in_progress, final_paths
                    in_progress.remove(path)
                    node1 = path[0]
                    for previous in archived[node1][1]:
                        if previous == start:
                            final_paths.add((previous,) + path)
                        else:
                            in_progress.add((previous,) + path)
            return archived[current][0], final_paths
        else:
            return oo, []


    def latex_Dijkstra(self, start, end):
        nodes = sorted(self)
        code = u"On applique l'algorithme de Moore-Dijkstra~:\n\n"
        code += r'\begin{tabular}{|*{%s}{c|}}\hline' %len(self)
        code += '\n' + '&'.join(('$%s$' %node) for node in nodes) + r'\\\hline\hline' + '\n'
        # current node
        current = start
        # Nodes which have been already visited, but still not archived:
        visited = {start: [0, [start]]}
        # format: {node: [distance from start, [previous node, alternative previous node, ...]]}

        # Nodes which will not change anymore:
        archived = {}

        while current != end and visited:
            def str2(val):
                # 2.0 -> "2" ; 2.3 -> "2,3"
                return str(20.).rstrip('0').rstrip('.').replace('.', ',')

            def format(node):
                def _format(node):
                    previous_nodes = ','.join(str(prev) for prev in visited[node][1])
                    return str2(visited[node][0]) + ' $(%s)$' %previous_nodes
                if node == current:
                    return r'\textbf{%s}' %_format(node)
                elif node in archived:
                    return ''
                elif node in visited:
                    return _format(node)
                else:
                    return r'$+\infty$'
            code += '&'.join(format(node) for node in nodes) + r'\\\hline' + '\n'
            archived[current] = visited.pop(current)
            # We select the node having the smallest distance
            for neighbor in self[current]:
                if neighbor not in archived:
                    distance = visited.get(neighbor, [oo])[0]
                    new_distance = archived[current][0] + min(self[current][neighbor])
                    if new_distance < distance:
                        visited[neighbor] = [new_distance, [current]]
                    elif new_distance == distance:
                        visited[neighbor][1].append(current)
            current = min(visited.items(), key = lambda x:x[1][0])[0]
        code += '&'.join(format(node) for node in nodes) + r'\\\hline' + '\n'
        code += '\\end{tabular}\n'
        if visited.has_key(current):
            archived[current] = visited.pop(current)
            in_progress = set([(current,)])
            final_paths = set()
            while in_progress:
                for path in set(in_progress):
#                    print path, in_progress, final_paths
                    in_progress.remove(path)
                    node1 = path[0]
                    for previous in archived[node1][1]:
                        if previous == start:
                            final_paths.add((previous,) + path)
                        else:
                            in_progress.add((previous,) + path)
        distance = archived[current][0]
        paths = ', '.join('$' + '-'.join(path) + '$' for path in final_paths)
        plur1 = ('x' if len(final_paths) > 1 else '')
        plur2 = ('s' if len(final_paths) > 1 else '')
        code += u"""
La distance minimale entre le sommet $%(start)s$ et le sommet $%(end)s$ est de $%(distance)s$.
Cela correspond au%(plur1)s chemin%(plur2)s %(paths)s.
""" %locals()
        return code
