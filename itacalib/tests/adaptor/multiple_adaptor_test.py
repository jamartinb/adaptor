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
# This test checks if two learning adaptors interfere with each other or not
#
# Name:   multiple_adaptor_test.py - Test cases multiple adaptor
# Author: José Antonio Martín Baena
# Date:   10-09-2012
##
########################################################################

import unittest;
import logging;
import xml;
import itacalib.XML.stsxmlinterface as xml2sts;
import itacalib.XML.stsxml as stsxml;
import itacalib.adaptor.adaptor as adaptor;
import itacalib.verification.synchronisation as synchronisation;

from expected_results import simple_invoke_LA_SA


## Logger for this module
log = logging.getLogger('multiple_adaptor_test')



class MultipleAdaptorTest(unittest.TestCase):


    def test_identity_adaptor(self):
        """Tests that identyty adaptors do not interfere with each other

        Two compatible services (a simple INVOKE) are mediated with two
        learning adaptors with identity contracts.

        Actions have been renamed to force the interaction through one
        adaptor and then another.
        """
        dir="../../../itaca/samples/adaptor/simple-invoke/"
        syn = synchronisation.SynchroniserFeedback()
        contracts = []
        adaptors = []
        services = []
        try:
            for i in range(1,3):
                contracts.append(stsxml.readXML(
                    "{}contracts_{}.xml".format(dir,i)))
                adaptors.append(adaptor.LearningAdaptor(contracts[i-1]))
                syn.subscribe(adaptors[i-1].getSubscriber(i))
                services.append(xml2sts.readXML(
                    "{}s{}.xml".format(dir,i)).getSTS())
        except xml.parsers.expat.ExpatError, message:
            log.fatal('One of the given files could not be parsed: \n\t%s' \
                    % message);
        everything = []
        everything[0:] = [services[0]]
        everything[1:] = adaptors
        everything[3:] = [services[1]]
        traces = syn.synchronise(everything)
        self.assertEqual(traces,simple_invoke_LA_SA)


        







#del LearningAdaptorTest;

if __name__ == "__main__":
    unittest.main();
