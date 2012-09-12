#!/usr/bin/env python
# coding=utf-8
""""""
##
# This file is part of ITACA-Adaptor.
#
# ITACA-Adaptor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ITACA-Adaptor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ITACA-Adaptor.  If not, see <http://www.gnu.org/licenses/>.
##

import os

from distutils.core import setup

print list(os.walk('itaca/samples'))

packages = [root for (root, dirs, files) in os.walk('itacalib')]
packages = list(set(packages))
packages.remove('itacalib/adaptor/gnuplot')
packages.append('itaca')

files = ['/'.join((d+'/'+f).split('/')[1:])
        for (d, subdirs, files) in os.walk("itaca/samples")
        for f in files
        if os.path.isfile(d+'/'+f)];
files = list(set(files))

#@TODO: ./setuy.py --provides still doesn't work :-( 

setup(name='ITACA-Adaptor',
        version='1.1',
        description='Different behavioural adaptors between stateful services',
        author='José Antonio Martín Baena, Javier Cámara Moreno',
        author_email='jose.antonio.martin.baena@gmail.com',
        url='https://github.com/jamartinb/adaptor',
        download_url='https://github.com/jamartinb/adaptor/tarball/master',
        packages = packages,
        package_data = {'itaca':files},
        license="GPLv3",
        );
