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
# This are the test cases for dsts
#
# Name:   dsts.py - Test cases for the dsts.py module.
# Author: José Antonio Martín Baena
# Date:   03-11-2010
##
########################################################################

import unittest;
from itacalib.model.dsts import DetSts;
from itacalib.model.sts import STS;
import itacalib.model.lts as lts;
import itacalib.XML.dot as dot;
import logging;


## Logger for this module
log = logging.getLogger('dststest')


# Load default logging configuration.
#logging.basicConfig(level=logging.DEBUG);
logging.basicConfig();


class DetStsTest(unittest.TestCase):


    def build_example_1(self):
        sts = STS();
        state = "s_0";
        sts.setInitial(state);
        sts.addTransition(lts.Transition(state,"a","s_1"));
        sts.addTransition(lts.Transition(state,"a","s_2"));
        sts.addTransition(lts.Transition("s_1","b","s_3"));
        sts.addTransition(lts.Transition("s_1","b","s_5"));
        sts.addTransition(lts.Transition("s_1","d","s_4"));
        sts.addTransition(lts.Transition("s_2","c","s_3"));
        sts.addTransition(lts.Transition("s_2","b","s_3"));
        for t in sts.getTransitions():
            sts.addLabel(lts.NLabel(t.getLabel()));
        return (sts, None);

    
    def test_example_1(self):
        sts, result = self.build_example_1();
        dsts = DetSts(sts);
        #dot.writeDOT("example_1.dot",dsts);
        self.assertEqual(len(dsts.outgoingTransitions("s_0")),1);
        self.assertEqual(len(dsts.outgoingTransitions("s_1++s_2")),3);



if __name__ == "__main__":
    unittest.main();
