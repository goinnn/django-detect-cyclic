from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        first_graph = ('digraph G {'
                       'ranksep=1.0;'
                       'node [style=filled,fontname=Helvetica,fontsize=10];'
                       'App1 -> App2;'
                       'App1 [label="App1",fillcolor="#f8c85c",peripheries=2];'
                       'App2 -> App3;'
                       'App2 [label="App2",fillcolor="#f8c85c"];'
                       'App3 [label="App3",fillcolor="#f8c85c"];'
                       '}')
        print first_graph
