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

import os
import pydot

from django import forms
from django.contrib.admin import widgets as widgets_admin
from django.conf import settings
from django.template.defaultfilters import slugify

from django_detect_cyclic.apps_dependence import create_graph_apps_dependence
from django_detect_cyclic.utils import DEFAULT_FILENAME, SCOPE_GLOBAL


class DetectCyclicForm(forms.Form):

    fieldsets = (
                    ('Basic options', {
                        'fields': ('applications', 'file_name', 'format')
                    }),
                    ('Advanced options', {
                        'fields': ('exclude_packages', 'force_colors', 'scope_global', 'dotted_scope_local')
                    }),
                    ('Limit nodes', {
                        'fields': ('only_cyclic', 'remove_isolate_nodes', 'remove_sink_nodes', 'remove_source_nodes')
                    }),
                )

    applications = forms.MultipleChoiceField(label='Applications', choices=[(app, app) for app in settings.INSTALLED_APPS])
    file_name = forms.CharField(initial=DEFAULT_FILENAME)
    format = forms.ChoiceField(initial='svg')
    exclude_packages = forms.CharField(required=False)
    force_colors = forms.BooleanField(required=False)
    scope_global = forms.BooleanField(required=False)
    dotted_scope_local = forms.BooleanField(initial=True, required=False)
    only_cyclic = forms.BooleanField(initial=True, required=False)
    show_modules = forms.BooleanField(required=False)
    remove_isolate_nodes = forms.BooleanField(required=False)
    remove_sink_nodes = forms.BooleanField(required=False)
    remove_source_nodes = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(DetectCyclicForm, self).__init__(*args, **kwargs)
        if 'south' in settings.INSTALLED_APPS:
            self.fields['exclude_packages'].initial = 'migrations'
        dot = pydot.Dot()
        formats = [(format, format) for format in dot.formats]
        formats.append(('svg-js', 'svg-js'))
        self.fields['format'].choices = [(format, format) for format in dot.formats]
        applications_label = self.fields['applications'].label
        applications_choices = self.fields['applications'].choices
        applications_initial = [app_value for app_label, app_value in applications_choices
                                              if not app_value.startswith('django.') and app_value != 'django_detect_cyclic']
        self.fields['applications'].initial = applications_initial
        self.fields['applications'].widget = widgets_admin.FilteredSelectMultiple(applications_label, False, choices=applications_choices)

    def clean_file_name(self):
        return str(slugify(self.cleaned_data['file_name']))

    def detect_cyclic(self):
        file_name = str(os.path.join(settings.MEDIA_ROOT,
                        '%s.%s' % (self.cleaned_data['file_name'], self.cleaned_data['format'])))
        applications = self.cleaned_data['applications']
        exclude_packages = self.cleaned_data['exclude_packages']
        if settings.DEBUG:
            verbosity = 2
        verbosity = 1
        show_modules = self.cleaned_data['show_modules']
        remove_isolate_nodes = self.cleaned_data['remove_isolate_nodes']
        remove_sink_nodes = self.cleaned_data['remove_sink_nodes']
        remove_source_nodes = self.cleaned_data['remove_source_nodes']
        only_cyclic = self.cleaned_data['only_cyclic']
        scope_global = self.cleaned_data['scope_global']
        scope = None
        if scope_global:
            scope = SCOPE_GLOBAL
        force_colors = self.cleaned_data['force_colors']
        dotted_scope_local = self.cleaned_data['dotted_scope_local']
        create_graph_apps_dependence(file_name=file_name, include_apps=applications,
                                     exclude_apps=None, exclude_packages=exclude_packages,
                                     verbosity=verbosity, show_modules=show_modules,
                                     remove_isolate_nodes=remove_isolate_nodes,
                                     remove_sink_nodes=remove_sink_nodes,
                                     remove_source_nodes=remove_source_nodes,
                                     only_cyclic=only_cyclic, scope=scope,
                                     force_colors=force_colors,
                                     dotted_scope_local=dotted_scope_local)
        return file_name

    def __unicode__(self):
        try:
            from formadmin.forms import as_django_admin
            return as_django_admin(self)
        except ImportError:
            return super(DetectCyclicForm, self).__unicode__()
