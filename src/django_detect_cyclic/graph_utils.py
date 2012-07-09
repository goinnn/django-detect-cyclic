# -*- coding: utf-8 -*-
# Copyright (c) 2012 by Pablo Martín <goinnn@gmail.com>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.


import logging
import sys
try:
    import gv
except ImportError:
    sys.path.append('/usr/lib/pyshared/python2.6')
    import gv

from copy import deepcopy

from pygraph.algorithms.cycles import find_cycle
from pygraph.classes.digraph import digraph
from pygraph.readwrite.dot import write

CYCLE_COLOR_SEED = "f8c85c"
CYCLE_LABEL = 'Cycle'
log = logging.getLogger('django_detect_cyclic.graph_utils.py')


def create_graph_test(*args, **kwargs):
    gr = digraph()
    gr.add_nodes(["Portugal", "Spain", "France", "Germany", "Belgium", "Netherlands", "Italy"])
    gr.add_node_attribute("Spain", ("style", "filled"))
    gr.add_node_attribute("Spain", ("fillcolor", "red"))
    gr.add_node_attribute("Spain", ("color", "blue"))
    gr.add_node_attribute("Spain", ("fontcolor", "yellow"))
    gr.add_edge(("Portugal", "Spain"))
    gr.add_edge(("Spain", "France"))
    gr.add_edge(("France", "Portugal"))
    gr.add_edge(("France", "Belgium"))
    gr.add_edge(("France", "Germany"))
    gr.add_edge(("Germany", "France"))
    gr.add_edge(("France", "Italy"))
    gr.add_edge(("Italy", "Belgium"))
    gr.add_edge(("Belgium", "France"))
    gr.add_edge(("Belgium", "Netherlands"))
    gr.add_edge(("Germany", "Belgium"))
    gr.add_edge(("Germany", "Netherlands"))
    return gr


def treatment_final_graph(gr, remove_isolated_nodes=False, remove_sink_nodes=False,
                          remove_source_nodes=False, only_cyclic=False, verbosity=False):
    if only_cyclic:
        for edge, properties in gr.edge_properties.items():
            if not CYCLE_LABEL in properties['label']:
                if verbosity:
                    log.info("Remove the edge %s-->%s" % edge)
                gr.del_edge(edge)
    if remove_source_nodes:
        for node, incidence in gr.node_incidence.items():
            if not incidence:
                if verbosity:
                    log.info("Remove the node %s" % node)
                gr.del_node(node)
    if remove_sink_nodes:
        for node, neighbor in gr.node_neighbors.items():
            if not neighbor:
                if verbosity:
                    log.info("Remove the node %s" % node)
                gr.del_node(node)
    if remove_isolated_nodes:
        for node, incidence in gr.node_incidence.items():
            neighbor = gr.node_neighbors.get(node, None)
            if not incidence and not neighbor:
                if verbosity:
                    log.info("Remove the node %s" % node)
                gr.del_node(node)
    return gr


def find_all_cycle(gr, gr_copy=None, number_cycle=1):
    gr_copy = gr_copy or deepcopy(gr)
    cycle = find_cycle(gr_copy)
    if cycle:
        mark_cycle(gr, cycle, number_cycle, gr_copy)
        find_all_cycle(gr, gr_copy, number_cycle=number_cycle + 1)


def mark_cycle(gr, cycle, number_cycle, gr_copy):
    i = 0
    while i < len(cycle):
        item = cycle[i]
        try:
            next_item = cycle[i + 1]
        except IndexError:
            next_item = cycle[0]
        weight = gr.edge_weight((item, next_item))
        gr.set_edge_label((item, next_item), "%s %s (%s)" % (CYCLE_LABEL, number_cycle, weight))
        cycle_color = '#%s' % hex((number_cycle * int('369369', 16) + int(CYCLE_COLOR_SEED, 16)) % int('ffffff', 16))
        gr.add_edge_attribute((item, next_item), ("color", cycle_color))
        gr_copy.del_edge((item, next_item))
        i += 1


def print_graph(gr, name):
    dot = write(gr)
    gvv = gv.readstring(dot)
    gv.layout(gvv, 'dot')
    format = name.split('.')[-1]
    gv.render(gvv, format, name)
