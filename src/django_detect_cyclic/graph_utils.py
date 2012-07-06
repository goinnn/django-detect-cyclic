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

from pyplete import PyPlete

from django_detect_cyclic.utils import get_applications

CYCLE_COLOR_SEED = "f8c85c"

log = logging.getLogger('django_detect_cyclic.graph_utils.py')


def create_graph_test(*args, **kwargs):
    gr = digraph()
    gr.add_nodes(["Portugal", "Spain", "France", "Germany", "Belgium", "Netherlands", "Italy"])
    gr.add_node_attribute("Spain", ("color", "red"))
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


def create_graph(include_apps=None, exclude_apps=None, exclude_packages=None, verbosity=False, remove_nodes_isolated=False):
    gr = digraph()
    applications = get_applications(include_apps, exclude_apps)
    gr.add_nodes(applications)
    pyplete = PyPlete()
    for app_source in applications:
        if verbosity:
            log.info("Analizing %s" % app_source)
        _add_edges_to_package(gr, app_source, app_source, applications, pyplete, exclude_packages, verbosity)
    if remove_nodes_isolated:
        for node, incidence in gr.node_incidence.items():
            if not incidence:
                if verbosity:
                    log.info("Remove the node %s" % node)
                gr.del_node(node)
    return gr


def _add_edges_to_package(gr, package, app_source, applications, pyplete=None, exclude_packages=None, verbosity=False):
    pyplete = pyplete or PyPlete()
    package_modules = package.split(".")
    importables_to_app = []
    pyplete.get_importables_rest_level(importables_to_app, package_modules[0], package_modules[1:], into_module=False)
    for importable_to_app, importable_type  in importables_to_app:
        if importable_type == 'package':
            if exclude_packages and importable_to_app in exclude_packages:
                if verbosity:
                    log.info('\t Ignore %s' % importable_to_app)
                continue
            subpackage = '%s.%s' % (package, importable_to_app)
            _add_edges_to_package(gr, subpackage, app_source, applications, pyplete,
                                  exclude_packages=exclude_packages, verbosity=verbosity)
        if importable_type != 'module':
            continue
        code = pyplete.get_imp_loader_from_path(package_modules[0], package_modules[1:] + [importable_to_app])[0].get_source()
        try:
            imports_code = pyplete.get_pysmell_modules_to_text(code)['POINTERS']
        except SyntaxError, e:
            if verbosity:
                log.error("\t File: %s SyntaxError %s" % (package_modules + [importable_to_app], e))
            continue
        for import_code in imports_code.values():
            if not import_code.startswith(app_source):
                for app_destination in applications:
                    if import_code.startswith(app_destination):
                        if not gr.has_edge((app_source, app_destination)):
                            if verbosity:
                                log.info('\t %s --> %s' % (app_source, app_destination))
                            gr.add_edge((app_source, app_destination))
                        break


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
        cycle_color = '#%s' % ((number_cycle * int('369369', 16) + int(CYCLE_COLOR_SEED, 16)) % int('ffffff', 16))
        gr.add_edge_attribute((item, next_item), ("color", cycle_color))
        gr_copy.del_edge((item, next_item))
        i += 1


def print_graph(gr, name):
    dot = write(gr)
    gvv = gv.readstring(dot)
    gv.layout(gvv, 'dot')
    format = name.split('.')[-1]
    gv.render(gvv, format, name)
