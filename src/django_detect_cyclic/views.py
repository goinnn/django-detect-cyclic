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
import random

from django.conf import settings
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import simplejson
from django.utils.translation import ugettext as _

from django_detect_cyclic.forms import DetectCyclicForm


@permission_required('detect_cyclic.view_graph')
def detect_cyclic(request):
    data = None
    img_src = None
    gr_js = None
    if request.method == 'POST':
        data = request.POST
    form = DetectCyclicForm(data=data)
    if form.is_valid():
        gr, file_path = form.detect_cyclic()
        if file_path:
            img_src = file_path.replace(settings.MEDIA_ROOT, '')
            if img_src and img_src[0] == '/':
                img_src = img_src[1:]
            img_src = os.path.join(settings.MEDIA_URL, img_src)
        else:
            gr_js = _get_gr_to_js(gr)
    return render_to_response('detect_cyclic/detect_cyclic.html',
                              {'form': form,
                               'title': _('Detect cyclic'),
                               'img_src': img_src,
                               'gr': gr_js},
                              context_instance=RequestContext(request))


def _get_gr_to_js(gr):
    gr_js = {'edges': {},
             'nodes': {}}
    attrs_edge_convert = {'color': 'stroke',
                          'color': 'fill'}
    old_edges = []
    for edge in gr.edges():
        attrs = dict(gr.edge_attributes(edge))
        properties = gr.edge_properties.get(edge) or {}
        attrs.update(properties)
        attrs['directed'] = True
        for attr_gr, attr_gr_js in attrs_edge_convert.items():
            attr = attrs.get(attr_gr, None)
            if attr:
                attrs[attr_gr_js] = attr
        if attrs.get('style') == 'dotted':
            attrs['stroke-dasharray'] = "1,5"
        else:
            attrs['stroke-dasharray'] = ""
        seed = 0
        random_seed = random.randint(1, 10)
        for char in edge[0] + edge[1]:
            seed += ord(char)
        attrs['seed_in'] = random_seed * seed % 31
        attrs['seed_out'] = random_seed * seed % 37
        attrs['label'] = '%s --> %s %s' % (edge[0],
                                           edge[1],
                                           attrs['label'])
        if (edge[1], edge[0]) in old_edges:
            attrs['seed_label'] = 40
        old_edges.append(edge)
        gr_js['edges'][edge] = simplejson.dumps(attrs)
    for node in gr.nodes():
        attrs = dict(gr.node_attributes(node))
        attrs['label'] = node
        gr_js['nodes'][node] = simplejson.dumps(attrs)
    return gr_js
