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
import itacalib.adaptor.adaptor;
from .adaptortest import ContractAdaptorTest;
import logging;

from expected_results import *;



## Logger for this module
log = logging.getLogger('detadaptortest')

# Load default logging configuration.
#logging.basicConfig(level=logging.DEBUG);
logging.basicConfig();



class DetContractAdaptorTest(ContractAdaptorTest):
    

    def buildAdaptor(self,contract):
        """Instantiates an Adaptor with the given contract

        @return: An Adaptor with the given contract
        """
        return itacalib.adaptor.adaptor.DetContractAdaptor(contract);


    def test_sql_server_v6(self):
        """Test Acide/sql-server-v6 """
        example=["contract.xml","client.xml","server.xml"];
        dir="../../../itaca/samples/Acide/sql-server-v6/";
        result = self.runAdaptation(dir,example);
        expected = sql_server_v6_DA_10;
        #self.assertEqual(result,expected);
        self.assert_successful_example(result,expected);


del ContractAdaptorTest

if __name__ == "__main__":
    unittest.main();
