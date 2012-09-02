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

import datetime
import logging

from django.conf import settings

from pygraph.classes.digraph import digraph

from django_detect_cyclic.utils import PyPlete, SCOPE_GLOBAL, format_color

from django_detect_cyclic.graph_utils import find_all_cycle, print_graph, treatment_final_graph
from django_detect_cyclic.utils import get_applications, print_log_info, print_log_error


log = logging.getLogger('django_detect_cyclic.apps_dependence.py')


def create_graph_apps_dependence(file_name, include_apps=None, exclude_apps=None,
                                 exclude_packages=None, verbosity=1, show_modules=False,
                                 remove_isolate_nodes=False, remove_sink_nodes=False,
                                 remove_source_nodes=False, only_cyclic=False, scope=None,
                                 use_colors=True, dotted_scope_local=False,
                                 layout='dot'):
    if only_cyclic:
        remove_isolate_nodes = True
    start_time = datetime.datetime.now()
    gr = create_graph(include_apps, exclude_apps, exclude_packages, verbosity, show_modules, scope, use_colors, dotted_scope_local)
    find_all_cycle(gr, use_colors=use_colors)
    treatment_final_graph(gr, remove_isolate_nodes, remove_sink_nodes, remove_source_nodes,
                              only_cyclic, verbosity=verbosity)
    if file_name:
        print_graph(gr, file_name, layout)
    if print_log_info(verbosity):
        log.info("Duration: %s" % str(datetime.datetime.now() - start_time))
    return gr


def create_graph(include_apps=None, exclude_apps=None, exclude_packages=None, verbosity=0,
                 show_modules=False, scope=None, use_colors=True, dotted_scope_local=False):
    gr = digraph()
    applications = get_applications(include_apps, exclude_apps)
    if not show_modules:
        gr.add_nodes(applications)
    pyplete = PyPlete(scope=scope)
    pyplete_global = None
    if dotted_scope_local:
        pyplete_global = PyPlete(scope=SCOPE_GLOBAL)
    for app_source in applications:
        if print_log_info(verbosity):
            log.info("Analizing %s" % app_source)
        _add_edges_to_package(gr, app_source, app_source, applications, pyplete,
                              exclude_packages, show_modules, verbosity,
                              scope, use_colors, pyplete_global)
    return gr


def _add_edges_to_package(gr, package, app_source, applications,
                          pyplete=None, exclude_packages=None,
                          show_modules=False, verbosity=1,
                          scope=None, use_colors=True,
                          pyplete_global=None):
    pyplete = pyplete or PyPlete(scope=scope)
    package_modules = package.split(".")
    importables_to_app = []
    try:
        pyplete.get_importables_rest_level(importables_to_app, package_modules[0], package_modules[1:], into_module=False)
    except SyntaxError, e:
        if print_log_error(verbosity):
            log.error("\t File: %s SyntaxError %s" % (package_modules, e))

    for imp  in importables_to_app:
        importable_to_app = imp['text']
        importable_type = imp['category']
        if importable_type == 'package':
            if exclude_packages and importable_to_app in exclude_packages:
                if print_log_info(verbosity):
                    log.info('\t Ignore %s' % importable_to_app)
                continue
            subpackage = '%s.%s' % (package, importable_to_app)
            if subpackage not in settings.INSTALLED_APPS:
                _add_edges_to_package(gr, subpackage, app_source, applications, pyplete,
                                      exclude_packages=exclude_packages,
                                      show_modules=show_modules,
                                      verbosity=verbosity,
                                      scope=scope,
                                      use_colors=use_colors,
                                      pyplete_global=pyplete_global)
        if importable_type != 'module':
            continue
        if show_modules:
            node = package_modules + [importable_to_app]
            node_source = _add_node_init('.'.join(node), applications)
            if not gr.has_node(node_source):
                _add_node_module(gr, node_source, applications, app_source=app_source, use_colors=use_colors)
        else:
            node_source = None
        code = pyplete.get_imp_loader_from_path(package_modules[0], package_modules[1:] + [importable_to_app])[0].get_source()
        try:
            imports_code = pyplete.get_pysmell_modules_to_text(code)['POINTERS']
        except SyntaxError, e:
            if print_log_error(verbosity):
                log.error("\t File: %s SyntaxError %s" % (package_modules + [importable_to_app], e))
            continue
        for import_code in imports_code.values():
            if isinstance(import_code, list):
                for i in import_code:
                    _add_edge_from_import_code(gr, applications, app_source,
                                               package_modules, i,
                                               code,
                                               node_source=node_source,
                                               pyplete=pyplete,
                                               show_modules=show_modules,
                                               verbosity=verbosity,
                                               scope=scope,
                                               use_colors=use_colors,
                                               pyplete_global=pyplete_global)
            else:
                _add_edge_from_import_code(gr, applications, app_source,
                                           package_modules,
                                           import_code, code,
                                           node_source=node_source,
                                           pyplete=pyplete,
                                           show_modules=show_modules,
                                           verbosity=verbosity,
                                           scope=scope,
                                           use_colors=use_colors,
                                           pyplete_global=pyplete_global)


def _add_edge_from_import_code(gr, applications, app_source, package_modules, import_code, code,
                               node_source=None,
                               pyplete=None,
                               show_modules=False, verbosity=1,
                               scope=None, use_colors=True, pyplete_global=None):
    if show_modules:
        node = _get_module_to_generic_import(gr,
                                             import_code.split('.'),
                                             pyplete=pyplete,
                                             verbosity=verbosity,
                                             scope=scope)
        if not node:
            import_relative = package_modules + import_code.split('.')
            node = _get_module_to_generic_import(gr,
                                                 import_relative,
                                                 pyplete=pyplete,
                                                 verbosity=verbosity,
                                                 scope=scope)
        node_destination = _add_node_init(node, applications)
        if node_destination:
            added = _add_node_module(gr, node_destination, applications,
                                        use_colors=use_colors)
            if added:
                style = _edge_style(pyplete_global, gr, node_source,
                                    node_destination, import_code, code)
                _add_edge(gr, node_source, node_destination, verbosity, style)
    else:
        app_destination = _get_app_to_import(import_code, applications)
        if not app_destination:
            import_relative = '.'.join(package_modules + import_code.split('.'))
            app_destination = _get_app_to_import(import_relative, applications)
        if app_destination and app_source != app_destination:
            style = _edge_style(pyplete_global, gr, app_source,
                                app_destination, import_code, code)
            _add_edge(gr, app_source, app_destination, verbosity, style)


def _add_edge(gr, node1, node2, verbosity=1, style="filled"):
    if print_log_info(verbosity):
        log.info('\t %s --> %s' % (node1, node2))
    if not gr.has_edge((node1, node2)):
        gr.add_edge((node1, node2))
        gr.set_edge_label((node1, node2), "(1)")
    else:
        weight = gr.edge_weight((node1, node2)) + 1
        gr.set_edge_weight((node1, node2), weight)
        gr.set_edge_label((node1, node2), "(%s)" % weight)
    attributes = dict(gr.edge_attributes((node1, node2)))
    attributes['style'] = style
    gr.edge_attr[(node1, node2)] = attributes.items()


def _has_scope_global(gr, node1, node2):
    return dict(gr.edge_attributes((node1, node2))).get('style') == 'filled'


def _edge_style(pyplete_global, gr, node1, node2, import_code, code):
    dotted = "filled"
    if pyplete_global and not _has_scope_global(gr, node1, node2):
        imports_code_global = pyplete_global.get_pysmell_modules_to_text(code)['POINTERS']
        if not import_code in imports_code_global.values():
            dotted = "dotted"
    return dotted


#Functions to show modules

def _get_module_to_generic_import(gr, import_code, pyplete=None, verbosity=1, scope=None):
    module = '.'.join(import_code)
    if gr.has_node(module):
        return module
    if len(import_code) == 0:
        return None
    pyplete = pyplete or PyPlete(scope=scope)
    imports = []
    try:
        pyplete.get_importables_rest_level(imports, import_code[0], import_code[1:])
    except SyntaxError, e:
        if print_log_error(verbosity):
            log.error("\t File: %s SyntaxError %s" % (import_code, e))
        return None
    if imports:
        return module
    return _get_module_to_generic_import(gr, import_code[:-1], pyplete=pyplete, verbosity=verbosity, scope=scope)


def _get_app_to_import(node, applications):
    score = len(node)
    candidate = None
    for app in settings.INSTALLED_APPS:
        if node.startswith(app):
            current_score = len(node) - len(app)
            if current_score < score:
                score = current_score
                candidate = app
    if candidate in applications:
        return candidate
    return None


def _get_app_colors(app):
    color = 0
    for ch in app:
        color += ord(ch) * int('754321', 16)
    color = int(color % int('ffffff', 16))
    fillcolor = format_color(hex(color))
    fontcolor = format_color(hex(abs(color - int('7fffff', 16))))
    return (fillcolor, fontcolor)


def _add_node_module(gr, node, applications, app_source=None, use_colors=True):
    has_node = gr.has_node(node)
    if not has_node:
        app = app_source or _get_app_to_import(node, applications)
        if app:
            if not has_node:
                gr.add_node(node)
                if use_colors:
                    fillcolor, fontcolor = _get_app_colors(app)
                    gr.add_node_attribute(node, ("fillcolor", fillcolor))
                    gr.add_node_attribute(node, ("color", fontcolor))
                    gr.add_node_attribute(node, ("fontcolor", fontcolor))
                    gr.add_node_attribute(node, ("style", "filled"))
            return True
        return False
    return True


def _add_node_init(node, applications):
    if node in applications:
        return '%s.__init__' % node
    return node

# End functions to show modules
