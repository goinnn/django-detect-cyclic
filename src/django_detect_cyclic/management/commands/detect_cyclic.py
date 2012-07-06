from django.core.management.base import BaseCommand
from django_detect_cyclic.utils import create_graph_test, find_all_cycle, print_graph


class Command(BaseCommand):

    def handle(self, *args, **options):
        gr = create_graph_test()
        find_all_cycle(gr)
        print_graph(gr, 'enurope.png')
