from optparse import make_option

from django.core.management.base import BaseCommand
from django_detect_cyclic.apps_dependence import create_graph_apps_dependence


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
            make_option('-i', '--include-apps', dest='include_apps',
                    help='Only use these applications to the graph (separated by commas)'),
            make_option('-e', '--exclude-apps', dest='exclude_apps',
                    help='Exclude these apps to the graph (separated by commas)'),
            make_option('-f', '--file-name', dest='file_name', default='detect.png',
                    help='Exclude these apps to the graph (separated by commas)'),
            make_option('-p', '--exclude-packages', dest='exclude_packages',
                    help='Exclude the next packages. For example migrations,templatetags (separated by commas)'),
            make_option('-r', '--remove-isolate-nodes', dest='remove_isolate_nodes',  action="store_true",
                    help='Remove the isolate nodes'),
            make_option('-k', '--remove-sink-nodes', dest='remove_sink_nodes',  action="store_true",
                    help='Remove the sink nodes'),
            make_option('-a', '--remove-source-nodes', dest='remove_source_nodes',  action="store_true",
                    help='Remove the source nodes'),
            make_option('-o', '--only-cyclic', dest='only_cyclic',  action="store_true",
                    help='Remove the nodes without cyclic'),
            make_option('-s', '--show-modules', dest='show_modules',  action="store_true",
                    help='The nodes now are the modules (by default are the applications)'),
    )

    def handle(self, *args, **options):
        include_apps = exclude_apps = exclude_packages = None
        if options['include_apps']:
            include_apps = options['include_apps'].split(',')
        if options['exclude_apps']:
            exclude_apps = options['exclude_apps'].split(',')
        if options['exclude_packages']:
            exclude_packages = options['exclude_packages'].split(',')
        verbosity = options['verbosity'] == "2"
        remove_isolate_nodes = options['remove_isolate_nodes']
        remove_sink_nodes = options['remove_sink_nodes']
        remove_source_nodes = options['remove_source_nodes']
        only_cyclic = options['only_cyclic']
        if only_cyclic:
            remove_isolate_nodes = True
        show_modules = options['show_modules']
        file_name = options['file_name']
        create_graph_apps_dependence(file_name, include_apps, exclude_apps, exclude_packages,
                                     verbosity, show_modules, remove_isolate_nodes,
                                     remove_sink_nodes, remove_source_nodes, only_cyclic)
