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
from pygraph.classes.digraph import digraph

from pyplete import PyPlete

from django_detect_cyclic.graph_utils import find_all_cycle, print_graph, treatment_final_graph
from django_detect_cyclic.utils import get_applications


log = logging.getLogger('django_detect_cyclic.apps_dependence.py')


def create_graph_apps_dependence(file_name, include_apps=None, exclude_apps=None, exclude_packages=None, verbosity=False,
                                 show_modules=False, remove_isolate_nodes=False, remove_sink_nodes=False,
                                 remove_source_nodes=False, only_cyclic=False):
    gr = create_graph(include_apps, exclude_apps, exclude_packages, verbosity, show_modules)
    find_all_cycle(gr)
    treatment_final_graph(gr, remove_isolate_nodes, remove_sink_nodes, remove_source_nodes,
                              only_cyclic, verbosity=verbosity)
    print_graph(gr, file_name)


def create_graph(include_apps=None, exclude_apps=None, exclude_packages=None, verbosity=False,
                 show_modules=False):
    gr = digraph()
    applications = get_applications(include_apps, exclude_apps)
    if not show_modules:
        gr.add_nodes(applications)
    pyplete = PyPlete()
    for app_source in applications:
        if verbosity:
            log.info("Analizing %s" % app_source)
        _add_edges_to_package(gr, app_source, app_source, applications, pyplete, exclude_packages, show_modules, verbosity)
    return gr


def _add_edges_to_package(gr, package, app_source, applications,
                          pyplete=None, exclude_packages=None,
                          show_modules=False, verbosity=False):
    pyplete = pyplete or PyPlete()
    package_modules = package.split(".")
    importables_to_app = []
    try:
        pyplete.get_importables_rest_level(importables_to_app, package_modules[0], package_modules[1:], into_module=False)
    except SyntaxError, e:
        if verbosity:
            log.error("\t File: %s SyntaxError %s" % (package_modules, e))

    for importable_to_app, importable_type  in importables_to_app:
        if importable_type == 'package':
            if exclude_packages and importable_to_app in exclude_packages:
                if verbosity:
                    log.info('\t Ignore %s' % importable_to_app)
                continue
            subpackage = '%s.%s' % (package, importable_to_app)
            if subpackage not in applications:
                _add_edges_to_package(gr, subpackage, app_source, applications, pyplete,
                                      exclude_packages=exclude_packages,
                                      show_modules=show_modules,
                                      verbosity=verbosity)
        if importable_type != 'module':
            continue
        if show_modules:
            node = package_modules + [importable_to_app]
            node_source = '.'.join(node)
            if not gr.has_node(node_source):
                _add_node_module(gr, node_source, applications)
        code = pyplete.get_imp_loader_from_path(package_modules[0], package_modules[1:] + [importable_to_app])[0].get_source()
        try:
            imports_code = pyplete.get_pysmell_modules_to_text(code)['POINTERS']
        except SyntaxError, e:
            if verbosity:
                log.error("\t File: %s SyntaxError %s" % (package_modules + [importable_to_app], e))
            continue
        if show_modules:
            for import_code in imports_code.values():
                node_destination = _get_module_to_generic_import(import_code.split('.'), pyplete=pyplete, verbosity=verbosity)
                if node_destination:
                    added = _add_node_module(gr, node_destination, applications)
                    if added:
                        _add_edge(gr, node_source, node_destination, verbosity)
        else:
            for import_code in imports_code.values():
                if not import_code.startswith(app_source):
                    for app_destination in applications:
                        if import_code.startswith(app_destination):
                            _add_edge(gr, app_source, app_destination, verbosity)
                            break


def _add_edge(gr, node1, node2, verbosity=False):
    if not gr.has_edge((node1, node2)):
        if verbosity:
            log.info('\t %s --> %s' % (node1, node2))
        gr.add_edge((node1, node2))
        gr.set_edge_label((node1, node2), "(1)")
    else:
        weight = gr.edge_weight((node1, node2))
        gr.set_edge_weight((node1, node2), weight + 1)
        gr.set_edge_label((node1, node2), "(%s)" % weight)


def _get_module_to_generic_import(import_code, pyplete=None, verbosity=False):
    if len(import_code) == 0:
        return None
    pyplete = pyplete or PyPlete()
    imports = []
    try:
        pyplete.get_importables_rest_level(imports, import_code[0], import_code[1:])
    except SyntaxError, e:
        if verbosity:
            log.error("\t File: %s SyntaxError %s" % (import_code, e))
        return None
    if imports:
        return '.'.join(import_code)
    return _get_module_to_generic_import(import_code[:-1], pyplete=pyplete, verbosity=verbosity)


def _get_app_to_import(node, applications):
    for app in applications:
        if node.startswith(app):
            return app
    return None


def _get_app_colors(app):
    color = 0
    for ch in app:
        color += ord(ch) * int('754321', 16)
    color = int(color % int('ffffff', 16))
    fillcolor = '#%s' % hex(color)
    fontcolor = '#%s' % hex(abs(color - int('7fffff', 16)))
    return (fillcolor, fontcolor)


def _add_node_module(gr, node, applications):
    app = _get_app_to_import(node, applications)
    if app:
        if not gr.has_node(node):
            fillcolor, fontcolor = _get_app_colors(app)
            gr.add_node(node)
            gr.add_node_attribute(node, ("fillcolor", fillcolor))
            gr.add_node_attribute(node, ("color", fontcolor))
            gr.add_node_attribute(node, ("fontcolor", fontcolor))
            gr.add_node_attribute(node, ("style", "filled"))
        return True
    return False
