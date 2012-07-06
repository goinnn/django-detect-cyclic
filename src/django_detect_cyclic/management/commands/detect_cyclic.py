from optparse import make_option

from django.core.management.base import BaseCommand
from django_detect_cyclic.graph_utils import create_graph, find_all_cycle, print_graph


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
            make_option('-a', '--remove-nodes_isolated', dest='remove_nodes_isolated',  action="store_true",
                    help='Remove the nodes isolated'),
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
        remove_nodes_isolated = options['remove_nodes_isolated']
        gr = create_graph(include_apps, exclude_apps, exclude_packages, verbosity, remove_nodes_isolated)
        find_all_cycle(gr)
        print_graph(gr, options['file_name'])
