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


import itacalib.XML.stsxmlinterface as xml2sts;
from itacalib.discovery.addtree import *;

# Import graphviz
import os
import sys, getopt
import logging;
sys.path.append('..')
sys.path.append('/usr/lib/graphviz/python/')
sys.path.append('/usr/lib64/graphviz/python/')
import gv
from pygraph.readwrite.dot import write

logging.basicConfig(level=logging.DEBUG);
log = logging.getLogger('addtreetest');

##
#
# Name:   addtree.py - Test cases for AddTree.
# Author: José Antonio Martín Baena
# Date:   30-11-2009
##
########################################################################

import unittest
from itacalib.discovery.addtree import *;

class TestDirGraphDict(unittest.TestCase):
    
    def testAddTree(self):
        self.assertNotEqual(AddTree(),None);

"""
    def testAddNode(self):
        g = DirGraphDict();
        g.addNode("queso");
        self.assertEqual(set(["queso"]),set(g.getNodes()));
        g.addNode("queso");
        self.assertEqual(set(["queso"]),set(g.getNodes()));
        g.addNode("fresco");
        self.assertEqual(set(["queso","fresco"]),set(g.getNodes()));
    
    def testContainsNode(self):
        g = DirGraphDict();
        g.addNode("queso");
        self.assertTrue(g.containsNode("queso"));
        self.assertFalse(g.containsNode("fresco"));
        g.addNode("fresco");
        self.assertTrue(g.containsNode("queso"));
        self.assertTrue(g.containsNode("fresco"));
    
    def testAddEdge(self):
        g = DirGraphDict();
        g.addEdge((0,1));
        self.assertEqual(set([(0,1)]),set(g.getEdges()));
        g.addEdges((1,2),(0,0));
        self.assertEqual(set([(0,1),(1,2),(0,0)]),set(g.getEdges()));
        g.addEdge((0,1));
        self.assertEqual(set([(0,1),(1,2),(0,0)]),set(g.getEdges()));
        g.addEdge((0,3));
        self.assertEqual(set([(0,1),(1,2),(0,3),(0,0)]),set(g.getEdges()));
    
    def testRemoveNode(self):
        g = DirGraphDict();
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
        g = DirGraphDict();
        g.addEdges((0,1),(1,1),(1,2),(0,1),(0,3));
        g.removeEdge((0,1));
        self.assertEqual(set([(1,1),(1,2),(0,3)]),set(g.getEdges()));
        self.assertEqual(4,len(g.getNodes()));
        
    def testContainsEdge(self):
        g = DirGraphDict();
        g.addEdge((0,1));
        g.addEdge((1,2));
        g.addEdge((0,1));
        g.addEdge((0,3));
        self.assertTrue(g.containsEdge((1,2)));
        self.assertFalse(g.containsEdge((1,1)));
        self.assertFalse(g.containsEdge((1,3)));
    
    def testGetChildNodes(self):
        g = DirGraphDict();
        g.addEdge((0,1));
        g.addEdge((1,2));
        g.addEdge((1,1));
        g.addEdge((0,1));
        g.addEdge((0,3));
        self.assertEqual(set([1,3]),set(g.getChildNodes(0)));
        self.assertEqual(set([2,1]),set(g.getChildNodes(1)));
        self.assertEqual(set(),set(g.getChildNodes(2)));
        self.assertEqual(set(),set(g.getChildNodes(3))); """
        
def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "", []);
    except getopt.error, msg:
        log.fatal(msg);
        #log.fatal("for help use --");
        sys.exit(4);
    if len(args) == 0:
        log.fatal("You shuld give a .sts file as parameter.");
        sys.exit(3);
    file = args[0];
    if not os.path.exists(file):
        log.fatal("The given file does not exst: %s" % file);
        sys.exit(2);
    interface = xml2sts.readXML(file);
    builder = STS2AddTree();
    addTree = builder.sts2addTree(interface.getSTS());

    # Draw as PNG
    if addTree == None:
        log.warn("No AddTree was returned.");
        sys.exit(1);
    graph = addTree.graph;
    dot = write(graph)
    gvv = gv.readstring(dot)
    gv.layout(gvv,'dot')
    gv.render(gvv,'png','example.png')
    print "Start: %r; End: %r" % (addTree.start,addTree.end)

if __name__ == "__main__":
    main();
    #unittest.main();

