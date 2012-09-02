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
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name="django-detect-cyclic",
    version="0.0.9",
    author="Pablo Martin",
    author_email="goinnn@gmail.com",
    description="Django application to detect cyclic imports",
    long_description=(read('README.rst') + '\n\n' + read('CHANGES')),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
    ],
    license="LGPL 3",
    install_requires=[
        "pysmell==0.7.3",
        "pyplete==0.0.2",
        "python-graph-core==1.8.1",
        "python-graph-dot==1.8.1",
        "django-form-admin==0.3.2"
    ],
    keywords="django,imports,cycle,cyclic imports,analyze code",
    url='https://github.com/goinnn/django-detect-cyclic',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
)
