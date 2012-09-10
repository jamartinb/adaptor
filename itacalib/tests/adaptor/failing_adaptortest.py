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
# This are the test cases of LearningAdaptor and SynchroniserFails
#
# Name:   learning_adpatortest.py - Test cases for LearningAdaptor and SynchroniserFails
# Author: José Antonio Martín Baena
# Date:   02-06-2011
##
########################################################################

import unittest;
import logging;
import itacalib.adaptor.adaptor; # Otherwise we have a infinite import recursion
from itacalib.tests.adaptor.learning_adaptortest import LearningAdaptorTest;
import itacalib.verification.synchronisation as synchronisation;

from expected_results import *;


## Logger for this module
log = logging.getLogger('failing_adaptortest')



@unittest.skip("All tests based on TER>0 still fail")
class FailingAdaptorTest(LearningAdaptorTest):
    """It tests that LearningAdaptor is correct but incomplete adaptor when \
       there are sporadic failures
    """


    def setUp(self):
        self.PREFIX = "F";


    def getIterationLimit(self):
        return 3;


    def buildSynchroniser(self, ter=0.01):
        return synchronisation.SynchroniserFails(self.LIMIT,ter);


    def assert_sub_language(self, result, expected):
        counter_example = synchronisation.is_sub_language(result, expected);
        if counter_example:
            self.fail("There is a trace in the adaptor "+ \
                    "which is not valid {0!s}".format(counter_example));

    def assert_successful_example(self, result, expected):
        self.assert_sub_language(result, expected);




del LearningAdaptorTest;

if __name__ == "__main__":
    unittest.main();
