#!/usr/bin/python
# coding=utf-8
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


##
# Runs all the tests in this folder
#
# Name:   all_tests.py - Run all the tests in this folder
# Author: José Antonio Martín Baena
# Date:   03-06-2010
##
########################################################################

import unittest;


def suite():
    module_names = ["adaptortest", "detadaptortest", \
            "learning_adaptortest", "nonfailing_adaptortest", \
            "failing_adaptortest", "thr_adaptortest", \
            "dthr_adaptortest", "multiple_adaptor_test"];

    return unittest.TestLoader().loadTestsFromNames(\
            ["itacalib.tests.adaptor."+name for name in module_names]);


if __name__ == "__main__":
    suite = suite();
    unittest.TextTestRunner(verbosity=1).run(suite);
