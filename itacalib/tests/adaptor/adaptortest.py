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
# This are the test cases of adaptor
#
# Name:   adpatortest.py - Test cases for the adaptor.py module.
# Author: José Antonio Martín Baena
# Date:   01-11-2010
##
########################################################################

import unittest;
from itacalib.adaptor.adaptor import *;
from itacalib.verification.synchronisation import \
        Synchroniser, tracesToDot, is_same_accepted_language, \
        is_reachable_transition;
import itacalib.XML.stsxmlinterface as xml2sts;
import itacalib.XML.stsxml as stsxml;
import itacalib.XML.dot as dot;
import logging, os, xml;

from expected_results import *;


## Logger for this module
log = logging.getLogger('adaptortest')

# log.setLevel(logging.DEBUG);
# Load default logging configuration.
#logging.basicConfig(level=logging.DEBUG);
logging.basicConfig();

class ContractAdaptorTest(unittest.TestCase):
    

    LIMIT = 10;

    WRITE_DOT = False;


    def buildSynchroniser(self):
        """Instantiates a synchroniser

        @return: A synchroniser
        """
        return Synchroniser(self.LIMIT);


    def buildAdaptor(self,contract):
        """Instantiates an Adaptor with the given contract

        @return: An Adaptor with the given contract
        """
        return ContractAdaptor(contract);


    def loadContract(self,files):
        """Loads the given contract

        @param files: Contract file being the first of the sequence
        @return: Contract instance
        """
        contract = None;
        file = files[0];
        try:
            contract = stsxml.readXML(file);
        except xml.parsers.expat.ExpatError, message:
            log.fatal('The contract ("%s") could not be parsed: \n\t%s' % (file,message));
        return contract;


    def loadServices(self,files):
        """Loads the list of sts files into the returned set of STS instances

        @param files: STS files
        @return: Set of STS instances
        """
        services = [];
        try:
            for file in files:
                services.append(xml2sts.readXML(file).getSTS());
        except xml.parsers.expat.ExpatError, message:
            log.fatal('One of the given files ("%s") could not be parsed: \n\t%s' % (file,message));
        return services;


    def relativePaths(self,parent,paths):
        """Returns a sequence of evaluated paths to the examples

        @param parent: Path to the parent directory of the files
        @param paths: Sequence of filenames within parent folder
        @return: Sequence of evaluated paths
        """
        prefix =os.path.dirname(__file__);
        return [os.path.join(prefix, parent+path) for path in paths];


    def writeStsDot(self,name,sts):
        dot.writeDOT("".join((name,".dot")),sts);


    def writeTracesDot(self,name,traces):
        file = open("".join((name,".dot")),"w");
        file.write(tracesToDot(traces));
        file.close();


    def runAdaptation(self,exampleDir,files):
        """Calculates the possible synchronisations
        among the given STS services and an Adaptor generated from the contract
        in the first given file.

        @param exampleDir: Path to the directory of examples
        @param files: Sequence of filenames within the directory. The first being the contract.
        """
        contract = self.loadContract(self.relativePaths(exampleDir,files[0:1]));
        services = self.loadServices(self.relativePaths(exampleDir,files[1:]));
        if self.WRITE_DOT:
            for i in range(0,len(services)):
                self.writeStsDot("service_{0}".format(str(i)), services[i]);
        adaptor = self.buildAdaptor(contract);
        services.append(adaptor);
        syn = self.buildSynchroniser();
        to_return = syn.synchronise(services);
        if self.WRITE_DOT:
            self.writeStsDot("adaptor",adaptor);
            self.writeTracesDot("traces",to_return);
            #print "Hello World!: ", to_return;
            log.debug("==================================");
        return to_return;


    def assert_successful_example(self, result, expected):
        """Assertion to compare the example result and its expected outcome
        """
        self.assert_same_language(result, expected);


    def assert_same_language(self,result,expected):
        counter_example = is_same_accepted_language(result,expected);
        if counter_example:
            self.fail(("A trace was {0!s} (result traces:{2}, "+ \
                    "expected traces:{3}: {1!s}").\
                    format(counter_example[0], counter_example[1],\
                    len(result), len(expected)));

    
    def assert_reachable_transition(self, adaptor, transition):
        self.assertTrue(is_reachable_transition(transition, adaptor, \
                lambda x:x in adaptor.getExploredStates()), \
                "The following transition is not reachable \n"+ \
                "%s".format(transition));


    def assert_correct_adaptor(self, traces):
        """The traces are successful or empty"""
        # Empty adaptor is always correct
        synchronisations = [trans for trace in traces for trans in trace if \
                (trans[1] is not None and trans[1] != 'TAU')];
        if not synchronisations: # is empty
            return;
        for trace in sorted(traces, lambda x, y: len(x) - len(y)):
            self.assertTrue(trace[-1][-1], "A trace was not successful\n Trace: {!r}".format(trace));


    def test_sql_server_v6(self):
        """Test Acide/sql-server-v6 """
        example=["contract.xml","client.xml","server.xml"];
        dir="../../../itaca/samples/Acide/sql-server-v6/";
        result = self.runAdaptation(dir,example);
        expected = sql_server_v6_CA_10;
        #self.assertEqual(result,expected);
        #self.assertEqual(len(result),len(expected));
        self.assert_successful_example(result,expected);



if __name__ == "__main__":
    unittest.main();

