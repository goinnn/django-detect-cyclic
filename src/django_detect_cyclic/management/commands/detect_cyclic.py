
import sys

try:
    import gv
except ImportError:
    sys.path.append('/usr/lib/pyshared/python2.6')
    import gv

from pygraph.algorithms.searching import breadth_first_search
from pygraph.classes.digraph import digraph
from pygraph.readwrite.dot import write

from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        gr = digraph()
        gr.add_nodes(["Portugal", "Spain", "France", "Germany", "Belgium", "Netherlands", "Italy"])
        gr.add_edge(("Portugal", "Spain"))
        gr.add_edge(("Spain", "Portugal"))
        gr.add_edge(("Spain", "France"))
        gr.add_edge(("France", "Belgium"))
        gr.add_edge(("France", "Germany"))
        gr.add_edge(("France", "Italy"))
        gr.add_edge(("Belgium", "Netherlands"))
        gr.add_edge(("Germany", "Belgium"))
        gr.add_edge(("Germany", "Netherlands"))
        dot = write(gr)
        gvv = gv.readstring(dot)
        gv.layout(gvv, 'dot')
        gv.render(gvv, 'svg', 'europe3.svg')
