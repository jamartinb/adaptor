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
# These are the test cases of ThresholdAdaptor
#
# Name:   thr_adpatortest.py - Test cases for ThresholdAdaptor in adaptor.py module.
# Author: José Antonio Martín Baena
# Date:   04-06-2010
##
########################################################################

import unittest;
import logging;
from itacalib.adaptor.adaptor import ThresholdAdaptor;
from itacalib.tests.adaptor.learning_adaptortest import LearningAdaptorTest;
import itacalib.verification.synchronisation as synchronisation;
# For sys.maxint used for iteration_limit
import sys;

from expected_results import *;

## Logger for this module
log = logging.getLogger('thr_adaptortest')


@unittest.skip("Unsupported test")
class ThresholdAdaptorTest(LearningAdaptorTest):

    #WRITE_DOT = True;


    class THRAdaptorWithTests(ThresholdAdaptor):


        def __init__(self, contract, test):
            ThresholdAdaptor.__init__(self, contract);
            self._test = test;


        def forgetTransitions(self, transitions):
            self._test.assert_and_forget_transitions(transitions, self, ThresholdAdaptor);


    def setUp(self):
        self.PREFIX = "THR";


    def buildAdaptor(self, contract, threshold=0):
        adaptor = ThresholdAdaptorTest.THRAdaptorWithTests(contract, self);
        adaptor.setThreshold(threshold);
        return adaptor;


    def test_ecows11_contract5_THR_0(self):
        """Two successive trainnings with THR=0 yield the same results """
        examples=["contract-5.xml","SPIN_source.xml","tiny_diffusion.xml","SPIN_sink.xml"];
        dir="../../../itaca/samples/adaptor/ecows11/";

        (syn, services, adaptor) = self.loadExample(dir, examples);

        failures = set();
        def notify(reason, details):
            if reason is synchronisation.SynchroniserFeedback.\
                    UNFINISHED_TRACE:
                failures.add(details);
        syn.subscribe(notify);
        
        adaptor.setThreshold(0);

        def inhibit(trace):
            ThresholdAdaptorTest.THRAdaptorWithTests.\
                    inhibit(adaptor, trace);
            self.assertEqual(len(adaptor.inhibited),0,\
                    "Being THR=0, the set of inhibited traces should "+\
                    "always be empty and not contain {} elements".\
                    format(len(adaptor.inhibited)));
        adaptor.inhibit = inhibit;

        self.simulate(syn, services, adaptor, iterations=1);
        stats = syn.getStats();
        previous_failures = set(failures);

        for i in range(0,2):
            failures.clear();
            self.simulate(syn, services, adaptor, iterations=1);

            errors = [trc for trc in previous_failures if trc not in failures];
            errors = sorted(errors, lambda x, y: len(x) - len(y));
            if errors:
                print errors[0];

            self.assertEqual(failures, previous_failures, "Two simulations"+\
                    " have generated a different set of failures.");
            self.assertEqual(stats, syn.getStats(), \
                    "Two simulations had different results with TER=0 and "+\
                    "STHR=0 \n\t {!r} != {!r}".format(stats, syn.getStats()));



del LearningAdaptorTest

if __name__ == "__main__":
    unittest.main();
