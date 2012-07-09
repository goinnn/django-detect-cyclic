Call to the command without options (only verbosity):


    ./bin/django detect_cyclic --file-name="examples/example-first.svg" --verbosity=2
    ./bin/django detect_cyclic --file-name="examples/example-first.png" --verbosity=2

<img src='https://github.com/goinnn/django-detect-cyclic/raw/master/examples/example-first.png'/>

In this image I can not see anything. I am interested in the cycles, I use this options (only-cyclic).:


    ./bin/django detect_cyclic --file-name="examples/example-only-cyclic.svg" --verbosity=2 --only-cyclic
    ./bin/django detect_cyclic --file-name="examples/example-only-cyclic.png" --verbosity=2 --only-cyclic

<img src='https://github.com/goinnn/django-detect-cyclic/raw/master/examples/example-only-cyclic.png'/>

I exclude the django applications (exclude-apps):


    ./bin/django detect_cyclic --file-name="examples/example-only-cyclic-exclude.svg" --exclude-apps="django.contrib.messages,django.contrib.auth,django.contrib.contenttypes,django.contrib.admin" --verbosity=2 --only-cyclic
    ./bin/django detect_cyclic --file-name="examples/example-only-cyclic-exclude.png" --exclude-apps="django.contrib.messages,django.contrib.auth,django.contrib.contenttypes,django.contrib.admin" --verbosity=2 --only-cyclic

<img src='https://github.com/goinnn/django-detect-cyclic/raw/master/examples/example-only-cyclic-exclude.png'/>

I want to analize the cycles. I need to know modules which are involved in these cycles. Now the nodes are the modules, before the nodes were the applications:


    ./bin/django detect_cyclic --file-name="examples/example-modules.svg" --verbosity=2 --only-cyclic --include-apps=bpmui,authentication,wfui,cmisadaptor,wfadaptor --show-modules
    ./bin/django detect_cyclic --file-name="examples/example-modules.png" --verbosity=2 --only-cyclic --include-apps=bpmui,authentication,wfui,cmisadaptor,wfadaptor --show-modules

<img src='https://github.com/goinnn/django-detect-cyclic/raw/master/examples/example-modules.png'/>