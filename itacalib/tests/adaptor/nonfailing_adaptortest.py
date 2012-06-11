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
# This are the test cases of LearningAdaptor when TER=0
#
# Name:   nonfailing_adpatortest.py - Test cases for LearningAdaptor when TER=0
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
log = logging.getLogger('nonfailing_adaptortest')



class NonFailingAdaptorTest(LearningAdaptorTest):
    """It tests that, when TER=0, LearningAdaptor + SynchroniserFails is the \
    same as LearningAdaptor + Synchroniser
    """


    def setUp(self):
        self.PREFIX = "NF";


    def buildSynchroniser(self):
        return synchronisation.SynchroniserFails(self.LIMIT,0);



del LearningAdaptorTest

if __name__ == "__main__":
    unittest.main();
