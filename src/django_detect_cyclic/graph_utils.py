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

from pyplete import PyPlete

from django.conf import settings

CYCLE_COLOR = "#f8c85c"


def create_graph_test():
    gr = digraph()
    gr.add_nodes(["Portugal", "Spain", "France", "Germany", "Belgium", "Netherlands", "Italy"])
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


def create_graph():
    gr = digraph()
    gr.add_nodes(settings.INSTALLED_APPS)
    pyplete = PyPlete()
    for app_source in settings.INSTALLED_APPS:
        app_modules = app_source.split(".")
        importables_to_app = []
        pyplete.get_importables_rest_level(importables_to_app, app_modules[0], app_modules[1:], into_module=False)
        for importable_to_app, importable_type  in importables_to_app:
            if importable_type != 'module':
                continue
            code = pyplete.get_imp_loader_from_path(app_modules[0], app_modules[1:] + [importable_to_app])[0].get_source()
            imports_code = pyplete.get_pysmell_modules_to_text(code)['POINTERS']
            for import_code in imports_code.values():
                if not import_code.startswith(app_source):
                    for app_destination in settings.INSTALLED_APPS:
                        if import_code.startswith(app_destination):
                            if not gr.has_edge((app_source, app_destination)):
                                gr.add_edge((app_source, app_destination))
                            break
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
        gr.set_edge_label((item, next_item), "Cycle %s" % number_cycle)
        gr.add_edge_attribute((item, next_item), ("color", CYCLE_COLOR))
        gr_copy.del_edge((item, next_item))
        i += 1


def print_graph(gr, name):
    dot = write(gr)
    gvv = gv.readstring(dot)
    gv.layout(gvv, 'dot')
    format = name.split('.')[-1]
    gv.render(gvv, format, name)
