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
# This are the test cases of LearningAdaptor
#
# Name:   learning_adpatortest.py - Test cases for LearningAdaptor in adaptor.py module.
# Author: José Antonio Martín Baena
# Date:   02-11-2010
##
########################################################################

import unittest;
import itacalib.adaptor.adaptor;
import logging;
from itacalib.tests.adaptor.learning_adaptortest import LearningAdaptorTest;

from expected_results import *;

# For profiling
import cProfile;
import pstats;

## Logger for this module
log = logging.getLogger('adaptor_optimisation_test')

#log.setLevel(logging.DEBUG);
log.setLevel(logging.INFO);

# Load default logging configuration.
#logging.basicConfig(level=logging.DEBUG);
#logging.basicConfig(level=logging.INFO);



class OptimisationAdaptorTest(LearningAdaptorTest):


    LIMIT = 20;

    REPETITIONS = 2;


    def setUp(self):
        self.PREFIX = "O";

                
    def test_sql_server_v6_session_aware_thrise(self):
        """Test adaptor/sql-server-v6_session-aware """
        example=["contract.xml","client.xml","server.xml"];
        dir="../../../itaca/samples/adaptor/sql-server-v6_session-aware/";
        for i in range(0,self.REPETITIONS):
            result = self.runAdaptation(dir,example);
        expected = sql_server_v6_LA_SA_14;
        #self.assertEqual(result,expected);
        log.debug("Resulted traces: {0!r}".format(result));
        self.assert_successful_example(result,expected);


    def test_ecows11_optimisation(self):
        """Test adaptor/ecows11 """
        example=["contract-5.xml","SPIN_sink.xml","tiny_diffusion.xml","SPIN_source.xml"];
        dir="../../../itaca/samples/adaptor/ecows11/";
        for i in range(0,self.REPETITIONS):
            log.info("=== Running iteration {0}... ===".format(i+1));
            result = self.runAdaptation(dir,example);
        #expected = sql_server_v6_LA_SA_14;
        #self.assertEqual(result,expected);
        #log.debug("Resulted traces: {0!r}".format(result));
        #self.assert_successful_example(result,expected);


    @staticmethod
    def suite():
        tests = ['test_sql_server_v6_session_aware_thrise','test_ecows11_optimisation'];
        #tests = ['test_ecows11_optimisation'];
        return unittest.TestSuite(map(OptimisationAdaptorTest, tests));


if __name__ == "__main__":
    suite = OptimisationAdaptorTest.suite();
    test = lambda :unittest.TextTestRunner().run(suite);
    cProfile.run('test()','optimisation.stats');
    p = pstats.Stats('optimisation.stats')
    p.sort_stats('cumulative').print_stats(30);

