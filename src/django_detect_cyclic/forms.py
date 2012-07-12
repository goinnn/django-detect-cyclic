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
from django.forms.util import ErrorList
from django.contrib.admin import widgets as widgets_admin
from django.conf import settings
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

from django_detect_cyclic.apps_dependence import create_graph_apps_dependence
from django_detect_cyclic.utils import DEFAULT_FILENAME, SCOPE_GLOBAL, DEFAULT_FORMAT, DEFAULT_LAYOUT, compatible_scope

FORMAT_SPECIAL = 'svg-js'
LAYOUT_CHOICES = (('circo', 'circo'),
                  ('dot', 'dot'),
                  ('fdp', 'fdp'),
                  ('neato', 'neato'),
                  ('twopi', 'twopi'))


class DetectCyclicForm(forms.Form):

    fieldsets = (
                    (_('Basic options'), {
                        'fields': ('applications', 'file_name', 'format', 'layout')
                    }),
                    (_('Advanced options'), {
                        'fields': ('exclude_packages', 'force_colors', 'scope_global', 'dotted_scope_local', 'show_modules'),
                    }),
                    (_('Limits the graph'), {
                        'fields': ('only_cyclic', 'remove_isolate_nodes', 'remove_sink_nodes', 'remove_source_nodes'),
                    }),
                )

    applications = forms.MultipleChoiceField(label=_('Applications'),
                         choices=[(app, app) for app in settings.INSTALLED_APPS],
                         help_text=_('Choose the applications to analize'))
    file_name = forms.CharField(label=_('File name'),
                         initial=DEFAULT_FILENAME,
                         help_text=_('Choose a name to the generated file (without extension)'),
                         required=False)
    format = forms.ChoiceField(label=_('Format'), initial=DEFAULT_FORMAT)
    layout = forms.ChoiceField(label=_('Layout'), choices=LAYOUT_CHOICES, initial=DEFAULT_LAYOUT,
                        help_text=_('Node layout. This does not work if you select format svg-js'))
    exclude_packages = forms.CharField(label=_('Exclude packages'), required=False,
                       help_text=_('Exclude the next packages. For example migrations,templatetags (separated by commas)'))
    force_colors = forms.BooleanField(label=_('Force colors'), required=False,
        help_text=_('By default only if you choose svg format the result image will be colored. If you check this option the result image will be colored'))
    scope_global = forms.BooleanField(label=_('Scope global'), required=False,
        help_text=_('The imports into the functions are ignored'))
    dotted_scope_local = forms.BooleanField(label=_('Dotted scope local'), initial=True, required=False,
        help_text=_('The imports into the functions are printing with dotted line'))
    show_modules = forms.BooleanField(label=_('Show modules'), required=False,
        help_text=_('The nodes now are the modules (by default are the applications)'))
    only_cyclic = forms.BooleanField(label=_('Only cyclic'), initial=True, required=False,
       help_text=_('Removes the nodes that do not belong to any cycle'))
    remove_isolate_nodes = forms.BooleanField(label=_('Removes isolate nodes'), required=False,
        help_text=_('Removes the isolate nodes (without edgeds)'))
    remove_sink_nodes = forms.BooleanField(label=_('Removes sink nodes'), required=False,
        help_text=_('Removes the sink nodes (without output edges)'))
    remove_source_nodes = forms.BooleanField(label=_('Removes source nodes'), required=False,
        help_text=_('Removes the source nodes (without input edges)'))

    def __init__(self, *args, **kwargs):
        super(DetectCyclicForm, self).__init__(*args, **kwargs)
        if 'south' in settings.INSTALLED_APPS:
            self.fields['exclude_packages'].initial = 'migrations'
        dot = pydot.Dot()
        formats = [(format, format) for format in dot.formats]
        formats.append((FORMAT_SPECIAL, FORMAT_SPECIAL))
        formats.sort()
        self.fields['format'].choices = formats
        applications_label = self.fields['applications'].label
        applications_choices = self.fields['applications'].choices
        applications_initial = [app_value for app_label, app_value in applications_choices
                                              if not app_value.startswith('django.') and app_value != 'django_detect_cyclic']
        self.fields['applications'].initial = applications_initial
        self.fields['applications'].widget = widgets_admin.FilteredSelectMultiple(applications_label,
                                                                                  is_stacked=False,
                                                                                  choices=applications_choices)

    def clean_file_name(self):
        return str(slugify(self.cleaned_data['file_name']))

    def clean_layout(self):
        return str(self.cleaned_data['layout'])

    def clean(self):
        cleaned_data = super(DetectCyclicForm, self).clean()
        dotted_scope_local = cleaned_data['dotted_scope_local']
        scope_global = cleaned_data['scope_global']
        if not compatible_scope(dotted_scope_local, scope_global):
            scope_global_errors = self._errors.get('scope_global', ErrorList())
            scope_global_errors.append(_('This option is incompatible with dotted scope local'))
            self._errors['scope_global'] = scope_global_errors
        format = cleaned_data['format']
        file_name = cleaned_data['file_name']
        if format != FORMAT_SPECIAL and not file_name:
            file_name_errors = self._errors.get('file_name', ErrorList())
            file_name_errors.append(_('This field is required.'))
            self._errors['file_name'] = file_name_errors
        elif format == FORMAT_SPECIAL:
            cleaned_data['file_name'] = None
        return cleaned_data

    def detect_cyclic(self):
        applications = self.cleaned_data['applications']
        exclude_packages = self.cleaned_data['exclude_packages']
        verbosity = 1
        if settings.DEBUG:
            verbosity = 2
        show_modules = self.cleaned_data['show_modules']
        remove_isolate_nodes = self.cleaned_data['remove_isolate_nodes']
        remove_sink_nodes = self.cleaned_data['remove_sink_nodes']
        remove_source_nodes = self.cleaned_data['remove_source_nodes']
        only_cyclic = self.cleaned_data['only_cyclic']
        scope_global = self.cleaned_data['scope_global']
        layout = self.cleaned_data['layout']
        scope = None
        if scope_global:
            scope = SCOPE_GLOBAL
        force_colors = self.cleaned_data['force_colors']
        dotted_scope_local = self.cleaned_data['dotted_scope_local']
        file_name = self.cleaned_data['file_name']
        if file_name:
            graph_dir = os.path.join(settings.MEDIA_ROOT, 'graph')
            if not os.path.isdir(graph_dir):
                os.mkdir(graph_dir)
            file_name = str(os.path.join(graph_dir,
                            '%s.%s' % (file_name, self.cleaned_data['format'])))
        else:
            force_colors = True
        gr = create_graph_apps_dependence(file_name=file_name, include_apps=applications,
                                        exclude_apps=None, exclude_packages=exclude_packages,
                                        verbosity=verbosity, show_modules=show_modules,
                                        remove_isolate_nodes=remove_isolate_nodes,
                                        remove_sink_nodes=remove_sink_nodes,
                                        remove_source_nodes=remove_source_nodes,
                                        only_cyclic=only_cyclic, scope=scope,
                                        force_colors=force_colors,
                                        dotted_scope_local=dotted_scope_local,
                                        layout=layout)
        return (gr, file_name)

    def __unicode__(self):
        try:
            from formadmin.forms import as_django_admin
            return as_django_admin(self)
        except ImportError:
            return super(DetectCyclicForm, self).__unicode__()
