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
# This are the test cases of the synchroniser
#
# Name:   synchronisationtest.py - Test cases for Synchroniser.
# Author: José Antonio Martín Baena
# Date:   11-10-2010
##
########################################################################

import unittest;
from itacalib.verification.synchronisation import Synchroniser;
import itacalib.XML.stsxmlinterface as xml2sts;
import logging, os, xml;



## Logger for this module
log = logging.getLogger('synchronisationtest')

# Load default logging configuration.
#logging.basicConfig(level=logging.DEBUG);
#logging.basicConfig();

class SynchroniserTest(unittest.TestCase):
    

    def buildSynchroniser(self):
        """Instantiates a synchroniser

        @return: A synchroniser
        """
        return Synchroniser();


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


    def runSynchronisation(self,exampleDir,files):
        """Calculates the possible synchronisation among the given STS services

        @param exampleDir: Path to the directory of examples
        @param files: Sequence of filenames within the directory
        """
        services = self.loadServices(self.relativePaths(exampleDir,files));
        syn = self.buildSynchroniser();
        return syn.synchronise(services);


    def test_simpletest(self):
        """Test Acide/simpletest

        A single transition on action d.
        """
        example=["client.xml","clientc.xml"];
        dir="../../../itaca/samples/Acide/simpletest/";
        result = self.runSynchronisation(dir,example);
        self.assertEqual(result,
                set([(((u'0', u'0'), None, False), ((u'1', u'1'), u'd', True))]));


    def test_pc_store_v5(self):
        """Test pc-store-v5

        Two possible traces: either request and buy or request and halt due
        to an internal choice.
        """
        example=["buyer.xml","supplier.xml"];
        dir="../../../itaca/samples/stsxml/examples-adaptor/pc-store-v5/"
        result = self.runSynchronisation(dir,example);
        solution = set([(((u'0', u'0'), None, False), ((u'1', u'1'), u'request', False), ((u'4', u'1'), 'TAU', False), ((u'3', u'2'), u'buy', True)), (((u'0', u'0'), None, False), ((u'1', u'1'), u'request', False), ((u'2', u'1'), 'TAU', False))]);
        self.assertEqual(result,solution);


    
if __name__ == "__main__":
    logging.basicConfig();
    unittest.main();
