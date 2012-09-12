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
import itacalib.XML.dot as dot;
import itacalib.adaptor.adaptor as adaptor;
import itacalib.adaptor.condense_adaptor as condense_adaptor;
import itacalib.verification.synchronisation as synchronisation;
from itacalib.tests.adaptor.adaptortest import AdaptorTest;

from expected_results import simple_invoke_LA_SA, simple_reord_LA_SA,\
        simple_reord_b_LA_SA


## Logger for this module
log = logging.getLogger('multiple_adaptor_test')



class MultipleAdaptorTest(AdaptorTest):



    def buildAdaptor(self, contract):
        return adaptor.LearningAdaptor(contract);


    def test_identity_adaptor(self):
        """Tests that identity adaptors do not interfere with each other

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
        for i in range(1,3):
            contracts.append(self.loadContract(self.relativePaths(dir,
                    ["contracts_{}.xml".format(i)])));
            adaptors.append(self.buildAdaptor(contracts[i-1]));
            syn.subscribe(adaptors[i-1].getSubscriber(i))
            services.extend(self.loadServices(self.relativePaths(dir,
                    ["s{}.xml".format(i)])));
        everything = []
        everything[0:] = [services[0]]
        everything[1:] = adaptors
        everything[3:] = [services[1]]
        traces = syn.synchronise(everything)
        self.assertEqual(traces,simple_invoke_LA_SA)


    def test_reorder_adaptor(self):
        """Tests that identity adaptors do not interfere with each other

        Two services which need reordering are mediated with two
        learning adaptors with identity contracts.

        Actions have been renamed to force the interaction through one
        adaptor and then another.
        """
        dir="../../../itaca/samples/adaptor/simple-reord/"
        syn = synchronisation.SynchroniserFeedback()
        contracts = []
        adaptors = []
        services = []
        for i in range(1,3):
            contracts.append(self.loadContract(self.relativePaths(dir,
                    ["contracts_a{}.xml".format(i)])));
            adaptors.append(self.buildAdaptor(contracts[i-1]));
            syn.subscribe(adaptors[i-1].getSubscriber(i))
            services.extend(self.loadServices(self.relativePaths(dir,
                    ["s{}.xml".format(i)])));
        everything = []
        everything[0:] = [services[0]]
        everything[1:] = adaptors
        everything[3:] = [services[1]]
        continue_ = True
        inhibited_count = 0
        while continue_:
            log.debug(("Re-synchronising after inhibiting {} traces in "+
                    "the previous session").format(inhibited_count));
            traces = syn.synchronise(everything)
            inhibited_count = sum([a.resetInhibitedCount() for a in adaptors])
            continue_ = inhibited_count > 0
        if log.isEnabledFor(logging.DEBUG):
            with open("REORD_traces.dot",'w') as f:
                f.write(synchronisation.tracesToDot(traces))
            dot.writeDOT("REORD_adaptor_1.dot",adaptors[0])
            dot.writeDOT("REORD_adaptor_2.dot",adaptors[1])
        self.assert_same_language(traces,simple_reord_LA_SA)

        
    def test_reorder_conflict(self):
        """Tests that identity adaptors do not interfere with each other

        Two services which need reordering are mediated with two
        learning adaptors with identity contracts. One adaptor should reorder
        while the other should not.

        Actions have been renamed to force the interaction through one
        adaptor and then another.
        """
        dir="../../../itaca/samples/adaptor/simple-reord/"

        # Instantiating the synchroniser
        syn = synchronisation.SynchroniserFeedback()

        contracts = []
        adaptors = []
        services = []
        for i in range(1,3):
            contracts.append(self.loadContract(self.relativePaths(dir,
                    ["contracts_b{}.xml".format(i)])));
            adaptors.append(self.buildAdaptor(contracts[i-1]));
            syn.subscribe(adaptors[i-1].getSubscriber(i))
            services.extend(self.loadServices(self.relativePaths(dir,
                    ["s{}.xml".format(i)])));
        everything = []
        everything[0:] = [services[0]]
        everything[1:] = adaptors
        everything[3:] = [services[1]]
        inhibited_count = 0
        traces = None;

        for session in range(1,3+1):

            # Synchronise
            log.debug(("Re-synchronising after inhibiting {} traces in "+
                    "the previous session").format(inhibited_count));
            traces = syn.synchronise(everything)
            inhibited_count = sum([a.resetInhibitedCount() for a in adaptors])

            # DEBUG
            if log.isEnabledFor(logging.DEBUG):
                for i in range(1,3):
                    log.debug(("Adaptor {} inhibited: "+
                            "{!r}").format(i,adaptors[i-1].inhibited));

                # Write the traces
                with open("REORD_traces_{}.dot".format(session),'w') as f:
                    f.write(synchronisation.tracesToDot(traces))

                # Write the adaptors
                dot.writeDOT("REORD_adaptor_1_{}.dot".format(session),
                        adaptors[0])
                dot.writeDOT("REORD_adaptor_2_{}.dot".format(session),
                        adaptors[1])

            if inhibited_count == 0:
                # If nothing changes, why to continue?
                break;

        # Writing condensed adaptor
        if log.isEnabledFor(logging.DEBUG):
            for i in range(1,3):
                dot.writeDOT("REORD_adaptor_{}_final.dot".format(i),
                        condense_adaptor.condense_adaptor(adaptors[i-1]));

        # Assertions
        self.assert_same_language(traces, simple_reord_b_LA_SA);


#logging.basicConfig()
#log.setLevel(logging.DEBUG)
#adaptor.log.setLevel(logging.DEBUG)


#del LearningAdaptorTest;

if __name__ == "__main__":
    unittest.main();
