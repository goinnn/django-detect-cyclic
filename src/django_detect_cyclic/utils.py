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

import compiler

from django.conf import settings

from pyplete import PyPleteModuleDict
from pyplete import PyPlete as PyPleteOriginal
from pysmell.codefinder import CodeFinder, getName, getFuncArgs


SCOPE_GLOBAL = 'global'
DEFAULT_FILENAME = 'detect'
DEFAULT_LAYOUT = 'dot'
DEFAULT_FORMAT = 'svg'


def get_applications(include=None, exclude=None):
    if include:
        return include
    apps = settings.INSTALLED_APPS
    if exclude:
        apps = tuple(set(apps) - set(exclude))
    return apps


class PyPlete(PyPleteOriginal):

    def __init__(self, func_info=None, pythonpath=None, separator='.', scope=None, *args, **kwargs):
        super(PyPlete, self).__init__(func_info=func_info,
                                      pythonpath=pythonpath,
                                      separator=separator,
                                      *args, **kwargs)
        self.scope = scope

    def get_pysmell_code_walk_to_text(self, text):
        code = compiler.parse(text)

        class GlobalCodeFinder(CodeFinder):

            def visitFunction(self, func):
                self.enterScope(func)
                if self.inClassFunction:
                    if func.name != '__init__':
                        if func.decorators and 'property' in [getName(n) for n in func.decorators]:
                            self.modules.addProperty(self.currentClass, func.name)
                        else:
                            self.modules.addMethod(self.currentClass, func.name,
                                            getFuncArgs(func), func.doc or "")
                    else:
                        self.modules.setConstructor(self.currentClass, getFuncArgs(func))
                elif len(self.scope) == 1:
                    self.modules.addFunction(func.name, getFuncArgs(func,
                                        inClass=False), func.doc or "")

                #self.visit(func.code) Remove this line
                self.exitScope()

        if self.scope == SCOPE_GLOBAL:
            codefinder = GlobalCodeFinder()
        else:
            codefinder = CodeFinder()
        codefinder.modules = PyPleteModuleDict()
        return compiler.walk(code, codefinder)


def print_log_info(verbosity):
    return verbosity > 1


def print_log_error(verbosity):
    return verbosity > 0


def compatible_scope(dotted_scope_local, scope_global):
    if dotted_scope_local and scope_global:
        return False
    return True


def format_color(number_hex):
    if number_hex.startswith('0x'):
        number_hex = number_hex[2:]
    if len(number_hex) < 6:
        zeros = '0' * (6 - len(number_hex))
        number_hex = '%s%s' % (zeros, number_hex)
    return '#%s' % number_hex
