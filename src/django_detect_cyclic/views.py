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

from django.conf import settings
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _

from django_detect_cyclic.forms import DetectCyclicForm


@permission_required('detect_cyclic.view_graph')
def detect_cyclic(request):
    data = None
    img_src = None
    if request.method == 'POST':
        data = request.POST
    form = DetectCyclicForm(data=data)
    if form.is_valid():
        file_path = form.detect_cyclic()
        img_src = file_path.replace(settings.MEDIA_ROOT, '')
        if img_src and img_src[0] == '/':
            img_src = img_src[1:]
        img_src = os.path.join(settings.MEDIA_URL, img_src)
    return render_to_response('detect_cyclic/detect_cyclic.html',
                              {'form': form,
                               'title': _('Detect cyclic'),
                               'img_src': img_src},
                              context_instance=RequestContext(request))
