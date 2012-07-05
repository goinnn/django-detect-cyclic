
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

from django.core.management.base import BaseCommand

CYCLE_COLOR = "#f8c85c"


class Command(BaseCommand):

    def create_graph(self):
        gr = digraph()
        gr.add_nodes(["Portugal", "Spain", "France", "Germany", "Belgium", "Netherlands", "Italy"])
        gr.add_edge(("Portugal", "Spain"))
        gr.add_edge(("Spain", "France"))
        gr.add_edge(("France", "Portugal"))
        gr.add_edge(("France", "Belgium"))
        gr.add_edge(("France", "Germany"))
        gr.add_edge(("Germany", "France"))
        gr.add_edge(("France", "Italy"))
        gr.add_edge(("Belgium", "Netherlands"))
        gr.add_edge(("Germany", "Belgium"))
        gr.add_edge(("Germany", "Netherlands"))
        return gr

    def find_all_cycle(self, gr, gr_copy=None, number_cycle=1):
        gr_copy = gr_copy or deepcopy(gr)
        cycle = find_cycle(gr_copy)
        if cycle:
            self.print_cycle(gr, cycle, number_cycle, gr_copy)
            self.find_all_cycle(gr, gr_copy, number_cycle=number_cycle + 1)

    def print_cycle(self, gr, cycle, number_cycle, gr_copy):
        i = 0
        while i < len(cycle):
            item = cycle[i]
            try:
                next_item = cycle[i + 1]
            except IndexError:
                next_item = cycle[0]
            gr.set_edge_label((item, next_item), "Cycle %s" % number_cycle)
            gr.add_edge_attribute((item, next_item), ("color", "#f8c85c"))
            gr_copy.del_edge((item, next_item))
            i += 1

    def handle(self, *args, **options):
        gr = self.create_graph()
        self.find_all_cycle(gr)
        dot = write(gr)
        gvv = gv.readstring(dot)
        gv.layout(gvv, 'dot')
        gv.render(gvv, 'svg', 'europe3.svg')
