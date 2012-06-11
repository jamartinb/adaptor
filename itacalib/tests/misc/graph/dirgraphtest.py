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
# This are the test cases of the dictionary-based implementation of a simple directed graph.
#
# Name:   dirgraphdicttest.py - Test cases for DirGraphDict.
# Author: José Antonio Martín Baena
# Date:   31-03-2009
##
########################################################################

import unittest;
from itacalib.misc.graph.dirgraph import DirGraph;
from dirgraphdicttest import DirGraphDictTest;

class DirGraphTest(DirGraphDictTest):
    
    def buildGraph(self):
        return DirGraph();
    
    def testGetOutgoingEdges(self):
        g = self.buildGraph();
        g.addEdge((0,1),9);
        g.addEdge((0,1),9);
        g.addEdge((1,2),8);
        g.addEdge((1,1),8);
        g.addEdge((0,1),7);
        g.addEdge((0,3),6);
        self.assertEqual(set([(1,9),(1,7),(1,9),(3,6)]),set(g.getOutgoingEdges(0)));
        self.assertEqual(set([(2,8),(1,8)]),set(g.getOutgoingEdges(1)));
        self.assertEqual(set(),set(g.getOutgoingEdges(2)));
        self.assertEqual(set(),set(g.getOutgoingEdges(3)));
    
    def testGetLabels(self):
        g = self.buildGraph();
        g.addEdge((0,1),9);
        g.addEdge((0,1),9);
        g.addEdge((1,2),8);
        g.addEdge((1,1),8);
        g.addEdge((0,1),7);
        g.addEdge((0,3),6);
        self.assertEqual(set(range(6,10)),set(g.getLabels()));
        
    def testRemoveLabel(self):
        g = self.buildGraph();
        g.addEdge((0,1),9);
        g.addEdge((0,1),9);
        g.addEdge((1,2),8);
        g.addEdge((1,1),8);
        g.addEdge((0,1),7);
        g.addEdge((0,3),6);
        g.removeLabel(8);
        self.assertEqual(set([(1,9),(1,7),(1,9),(3,6)]),set(g.getOutgoingEdges(0)));
        self.assertEqual(set(),set(g.getOutgoingEdges(1)));
        self.assertEqual(set(),set(g.getOutgoingEdges(2)));
        self.assertEqual(set(),set(g.getOutgoingEdges(3)));
        g.removeLabel(9);
        self.assertEqual(set([(1,7),(3,6)]),set(g.getOutgoingEdges(0)));
        self.assertEqual(set(),set(g.getOutgoingEdges(1)));
        self.assertEqual(set(),set(g.getOutgoingEdges(2)));
        self.assertEqual(set(),set(g.getOutgoingEdges(3)));
    
    def testRemoveInexistentLabel(self):
        g = self.buildGraph();
        g.removeLabel(1);
        
    def testRemoveAllEdgesBetween(self):
        g = self.buildGraph();
        g.addEdge((0,1),9);
        g.addEdge((0,1),9);
        g.addEdge((1,2),8);
        g.addEdge((1,1),8);
        g.addEdge((0,1),7);
        g.addEdge((0,3),6);
        g.removeAllEdgesBetween((0,1));
        self.assertEqual(set([(3,6)]),set(g.getOutgoingEdges(0)));
        self.assertEqual(set([(2,8),(1,8)]),set(g.getOutgoingEdges(1)));
        self.assertEqual(set(),set(g.getOutgoingEdges(2)));
        self.assertEqual(set(),set(g.getOutgoingEdges(3)));
    
    def testRemoveInexistentEdges(self):
        g = self.buildGraph();
        g.removeAllEdgesBetween((0,1));
        
if __name__ == "__main__":
    unittest.main();