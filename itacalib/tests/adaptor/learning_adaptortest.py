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
import logging;
from itacalib.adaptor.adaptor import LearningAdaptor;
from itacalib.tests.adaptor.detadaptortest import DetContractAdaptorTest;
from itacalib.verification.synchronisation import \
        SynchroniserFeedback, SynchroniserFails;
# For sys.maxint in getIterationLimit
import sys;

from expected_results import *;



## Logger for this module
log = logging.getLogger('learning_adaptortest')

#log.setLevel(logging.DEBUG);
log.setLevel(logging.INFO);

# Load default logging configuration.
#logging.basicConfig(level=logging.DEBUG);
#logging.basicConfig(level=logging.INFO);
#logging.basicConfig();



class LearningAdaptorTest(DetContractAdaptorTest):

    LIMIT = 20;

    # WRITE_DOT = True;


    class AdaptorWithTests(LearningAdaptor):


        def __init__(self, contract, test):
            LearningAdaptor.__init__(self, contract);
            self._test = test;


        def forgetTransitions(self, transitions):
            test.assert_and_forget_transitions(transitions, self, \
                    LearningAdaptor);

        

    def assert_and_forget_transitions(self, transitions, adaptor, super):
        number = len(transitions);
        old_inhibited_size = len(adaptor.inhibited);
        old_transition_size = len(adaptor.getTransitions());
        super.forgetTransitions(adaptor, transitions);
        self.assertTrue(len(adaptor.inhibited) + number == \
                old_inhibited_size, \
                "We haven't forget as many traces as needed");
        self.assertTrue(len(adaptor.getTransitions()) == number +\
                old_transition_size, \
                "Forgotten traces are not back in pasition");
        [self.assert_reachable_transition(adaptor, transition) for \
                transition in transitions];
            

    def getIterationLimit(self):
        return sys.maxint;


    def setUp(self):
        self.PREFIX = "L";


    def buildAdaptor(self,contract):
        return LearningAdaptorTest.AdaptorWithTests(contract, self);


    def buildSynchroniser(self):
        return SynchroniserFeedback(self.LIMIT);


    def loadExample(self, exampleDir, files):
        contract = self.loadContract(self.relativePaths(exampleDir,files[0:1]));
        services = self.loadServices(self.relativePaths(exampleDir,files[1:]));
        adaptor = self.buildAdaptor(contract);
        services.insert(0,adaptor);
        syn = self.buildSynchroniser();
        if isinstance(syn, SynchroniserFeedback) and \
                isinstance(adaptor, LearningAdaptor):
            # Subscribe for dynamic inhibiting
            syn.subscribe(adaptor.getSubscriber(0));
        return (syn, services, adaptor)


    def runAdaptation(self,exampleDir,files,prefix=None,depth_limit=None):
        """Calculates the possible synchronisations
        among the given STS services and an Adaptor generated from the contract
        in the first given file.

        @param exampleDir: Path to the directory of examples
        @param files: Sequence of filenames within the directory. The first being the contract.
        """
        elements = self.loadExample(exampleDir, files);
        return self.simulate(*elements,prefix=prefix,depth_limit=depth_limit);


    def simulate(self,syn,services,adaptor, iteration_limit = None, iterations = None, prefix = None, depth_limit = None):
        if iteration_limit is None:
            if iterations is not None:
                iteration_limit = iterations;
            else:
                iteration_limit = self.getIterationLimit();
        if prefix == None:
            prefix = self.PREFIX;
        continue_ = True;
        traces = [];
        counter = 0;
        if isinstance(syn, SynchroniserFeedback):
            syn.resetStats();
        if self.WRITE_DOT:
            toWrite = filter(lambda x: x is not adaptor,services);
            for i in range(0,len(toWrite)):
                self.writeStsDot("{0}_service_{1}".format(prefix, str(i)), \
                        toWrite[i]);
        while continue_ and counter < iteration_limit:
            log.debug("Synchronising...");
            traces = syn.synchronise(services,limit = depth_limit);
            log.debug("Writing results into files...");
            self.__writeTraces(counter,traces);
            self.__writeSts("{0}_adaptor".format(prefix), \
                    "{0!s}a".format(str(counter)),adaptor);
            log.debug("Batch learning...");
            inhibited = adaptor.resetInhibitedCount();
            continue_ = (iterations is not None) or inhibited != 0;
            #log.info("{0} transitions inhibited.".format(str(inhibited)));
            log.debug("Writing post-learning adaptor...");
            self.__writeSts("{0}_adaptor".format(prefix), \
                    "{0!s}b".format(str(counter)),adaptor);
            counter += 1;
        return traces;


    def __writeTraces(self,counter,traces):
        if self.WRITE_DOT:
            self.writeTracesDot("{0}_traces_{1}".format(self.PREFIX,str(counter)),traces);


    def __writeSts(self,name,counter,sts):
        if self.WRITE_DOT:
            self.writeStsDot("{0}_{1}".format(name,str(counter)),sts);


    def test_sql_server_v6(self):
        """Test Acide/sql-server-v6 """
        example=["contract.xml","client.xml","server.xml"];
        dir="../../../itaca/samples/Acide/sql-server-v6/";
        result = self.runAdaptation(dir,example, depth_limit=13);
        expected = sql_server_v6_LA_13;
        #self.assertEqual(result,expected);
        log.debug("Resulted traces: {0!r}".format(result));
        self.assert_same_language(result,expected);

                
    def test_sql_server_v6_session_aware(self):
        """Test adaptor/sql-server-v6_session-aware """
        example=["contract.xml","client.xml","server.xml"];
        dir="../../../itaca/samples/adaptor/sql-server-v6_session-aware/";
        result = self.runAdaptation(dir,example, depth_limit=14);
        expected = sql_server_v6_LA_SA_14;
        #self.assertEqual(result,expected);
        log.debug("Resulted traces: {0!r}".format(result));
        self.assert_same_language(result,expected);
        self.assert_correct_adaptor(result);


    def test_med_online_renamed_session_aware(self):
        """Test adaptor/med-online_renamed_session-aware"""
        #logging.getLogger('synchronisation').setLevel(logging.DEBUG);
        example=["contract.xml","client.xml","server.xml","db.xml"];
        dir="../../../itaca/samples/adaptor/med-online_renamed_session-aware/";
        result = self.runAdaptation(dir,example, depth_limit = 20);
        expected = med_online_renamed_SA_20;
        #self.assertEqual(result,expected);
        log.debug("Resulted traces: {0!r}".format(result));
        #logging.getLogger('synchronisation').setLevel(logging.WARN);
        self.assert_same_language(result,expected);
        self.assert_correct_adaptor(result);


    def test_ecows11_contract5(self):
        """Test adaptor/ecows11 with contract #5"""
        #logging.getLogger('synchronisation').setLevel(logging.DEBUG);
        example=["contract-5.xml","SPIN_source.xml","tiny_diffusion.xml","SPIN_sink.xml"];
        dir="../../../itaca/samples/adaptor/ecows11/";
        result = self.runAdaptation(dir,example, depth_limit = 20);
        expected = ecows11_LA_SA_20_C5;
        #self.assertEqual(result,expected);
        log.debug("Resulted traces: {0!r}".format(result));
        #logging.getLogger('synchronisation').setLevel(logging.WARN);
        self.assert_same_language(result,expected);
        self.assert_correct_adaptor(result);



del DetContractAdaptorTest

if __name__ == "__main__":
    unittest.main();
