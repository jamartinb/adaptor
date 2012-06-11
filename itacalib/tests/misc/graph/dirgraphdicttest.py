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

import unittest
from itacalib.misc.graph.dirgraphdict import DirGraphDict

class DirGraphDictTest(unittest.TestCase):

    def buildGraph(test):
        return DirGraphDict();
    
    def testDirGraphDict(self):
        self.assertNotEqual(DirGraphDict(),None);
        
    def testAddNode(self):
        g = self.buildGraph();
        g.addNode("queso");
        self.assertEqual(set(["queso"]),set(g.getNodes()));
        g.addNode("queso");
        self.assertEqual(set(["queso"]),set(g.getNodes()));
        g.addNode("fresco");
        self.assertEqual(set(["queso","fresco"]),set(g.getNodes()));
    
    def testContainsNode(self):
        g = self.buildGraph();
        g.addNode("queso");
        self.assertTrue(g.containsNode("queso"));
        self.assertFalse(g.containsNode("fresco"));
        g.addNode("fresco");
        self.assertTrue(g.containsNode("queso"));
        self.assertTrue(g.containsNode("fresco"));
    
    def testAddEdge(self):
        g = self.buildGraph();
        g.addEdge((0,1));
        self.assertEqual(set([(0,1)]),set(g.getEdges()));
        g.addEdges((1,2),(0,0));
        self.assertEqual(set([(0,1),(1,2),(0,0)]),set(g.getEdges()));
        g.addEdge((0,1));
        self.assertEqual(set([(0,1),(1,2),(0,0)]),set(g.getEdges()));
        g.addEdge((0,3));
        self.assertEqual(set([(0,1),(1,2),(0,3),(0,0)]),set(g.getEdges()));
    
    def testRemoveNode(self):
        g = self.buildGraph();
        g.addEdge((0,1));
        g.addEdge((0,0));
        g.addEdge((1,1));
        g.addEdge((1,2));
        g.addEdge((0,1));
        g.addEdge((0,3));
        self.assertEqual(4,len(g.getNodes()));
        g.removeNode(1);
        self.assertEqual(set([(0,3),(0,0)]),set(g.getEdges()));
        self.assertEqual(3,len(g.getNodes()));
        g.removeNodes(0,3);
        self.assertEqual(set([2]),set(g.getNodes()));
        
    def testRemoveEdge(self):
        g = self.buildGraph();
        g.addEdges((0,1),(1,1),(1,2),(0,1),(0,3));
        g.removeEdge((0,1));
        self.assertEqual(set([(1,1),(1,2),(0,3)]),set(g.getEdges()));
        self.assertEqual(4,len(g.getNodes()));
        
    def testContainsEdge(self):
        g = self.buildGraph();
        g.addEdge((0,1));
        g.addEdge((1,2));
        g.addEdge((0,1));
        g.addEdge((0,3));
        self.assertTrue(g.containsEdge((1,2)));
        self.assertFalse(g.containsEdge((1,1)));
        self.assertFalse(g.containsEdge((1,3)));
    
    def testGetChildNodes(self):
        g = self.buildGraph();
        g.addEdge((0,1));
        g.addEdge((1,2));
        g.addEdge((1,1));
        g.addEdge((0,1));
        g.addEdge((0,3));
        self.assertEqual(set([1,3]),set(g.getChildNodes(0)));
        self.assertEqual(set([2,1]),set(g.getChildNodes(1)));
        self.assertEqual(set(),set(g.getChildNodes(2)));
        self.assertEqual(set(),set(g.getChildNodes(3)));
        
if __name__ == "__main__":
    unittest.main();
