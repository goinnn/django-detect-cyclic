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


def _add_edges_to_package(gr, package, app_source, applications, pyplete=None, exclude_packages=None, show_modules=False, verbosity=False):
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
            if subpackage not in applications:
                _add_edges_to_package(gr, subpackage, app_source, applications, pyplete,
                                      exclude_packages=exclude_packages,
                                      show_modules=show_modules,
                                      verbosity=verbosity)
        if importable_type != 'module':
            continue
        if show_modules:
            node = package_modules + [importable_to_app]
            if not gr.has_node('.'.join(node)):
                gr.add_node('.'.join(node))
        code = pyplete.get_imp_loader_from_path(package_modules[0], package_modules[1:] + [importable_to_app])[0].get_source()
        try:
            imports_code = pyplete.get_pysmell_modules_to_text(code)['POINTERS']
        except SyntaxError, e:
            if verbosity:
                log.error("\t File: %s SyntaxError %s" % (package_modules + [importable_to_app], e))
            continue
        if show_modules:
            for import_code in imports_code.values():
                import_module = _get_module_to_generic_import(import_code.split('.'), pyplete=pyplete)
                import_module_is_into_app = False
                if import_module:
                    for app in applications:
                        if import_module.startswith(app):
                            import_module_is_into_app = True
                            break
                    if import_module_is_into_app:
                        if not gr.has_node(import_module):
                            gr.add_node(import_module)
                        node_source = '.'.join(node)
                        if not gr.has_edge((node_source, import_module)):
                            if verbosity:
                                log.info('\t %s --> %s' % (node_source, import_module))
                            gr.add_edge((node_source, import_module))
                            gr.set_edge_label((node_source, import_module), "(1)")
                        else:
                            weight = gr.edge_weight((node_source, import_module))
                            gr.set_edge_weight((node_source, import_module), weight + 1)
                            gr.set_edge_label((node_source, import_module), "(%s)" % weight)

        else:
            for import_code in imports_code.values():
                if not import_code.startswith(app_source):
                    for app_destination in applications:
                        if import_code.startswith(app_destination):
                            if not gr.has_edge((app_source, app_destination)):
                                if verbosity:
                                    log.info('\t %s --> %s' % (app_source, app_destination))
                                gr.add_edge((app_source, app_destination))
                                gr.set_edge_label((app_source, app_destination), "(1)")
                            else:
                                weight = gr.edge_weight((app_source, app_destination))
                                gr.set_edge_weight((app_source, app_destination), weight + 1)
                                gr.set_edge_label((app_source, app_destination), "(%s)" % weight)
                            break


def _get_module_to_generic_import(import_code, pyplete=None):
    if len(import_code) == 0:
        return None
    pyplete = pyplete or PyPlete()
    imports = []
    pyplete.get_importables_rest_level(imports, import_code[0], import_code[1:])
    if imports:
        return '.'.join(import_code)
    return _get_module_to_generic_import(import_code[:-1], pyplete=pyplete)
