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
# These are the test cases of DynamicThresholdAdaptor
#
# Name:   dthr_adpatortest.py - Test cases for DynamicThresholdAdaptor in adaptor.py module.
# Author: José Antonio Martín Baena
# Date:   03-06-2010
##
########################################################################

import unittest;
import logging;
from itacalib.adaptor.adaptor import DynamicThresholdAdaptor;
from itacalib.tests.adaptor.failing_adaptortest import FailingAdaptorTest;
from itacalib.tests.adaptor.learning_adaptortest import LearningAdaptorTest;
import itacalib.verification.synchronisation as synchronisation;
# For sys.maxint used for iteration_limit
import sys;

from expected_results import *;



## Logger for this module
log = logging.getLogger('dthr_adaptortest')




class DynamicThresholdAdaptorTest(FailingAdaptorTest):


    actual_assert_same_language = LearningAdaptorTest.assert_same_language;


    class DTHRAdaptorWithTests(DynamicThresholdAdaptor):


        def __init__(self, contract, test):
            DynamicThresholdAdaptor.__init__(self, contract);
            self._test = test;


        def forgetTransitions(self, transitions):
            self._test.assert_and_forget_transitions(transitions, self, \
                    DynamicThresholdAdaptor);



    def setUp(self):
        self.PREFIX = "DTHR";


    def buildAdaptor(self, contract):
        adaptor = DynamicThresholdAdaptorTest.DTHRAdaptorWithTests(contract, self);
        return adaptor;


    def test_ecows11_contract5_DTHR(self):
        """Test adaptor/ecows11 with contract #5 and DTHR"""
        #logging.getLogger('synchronisation').setLevel(logging.DEBUG);
        examples=["contract-5.xml","SPIN_source.xml","tiny_diffusion.xml","SPIN_sink.xml"];
        dir="../../../itaca/samples/adaptor/ecows11/";

        (syn, services, adaptor) = self.loadExample(dir, examples);
        adaptor.setThreshold(55);
        adaptor.setMinimumThreshold(55);

        self.simulate(syn, services, adaptor, depth_limit = 20);

        syn.setTER(0);
        adaptor.forget();
        result = self.simulate(syn, services, adaptor, depth_limit = 20, \
                iteration_limit=10);

        expected = ecows11_LA_SA_20_C5;

        # To assert same language and not sub-language as it is done
        # in FailingAdaptorTest.
        self.assert_correct_adaptor(result);
        self.actual_assert_same_language(result,expected);



del FailingAdaptorTest
del LearningAdaptorTest

if __name__ == "__main__":
    unittest.main(verbosity=2);
