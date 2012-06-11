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
#
# Name:   dot.py - Functions for GraphViz export of LTS/STS.
# Author: Javier Camara.
# Date:   12-8-2008
##
################################################################################

import string
import os
from os.path import *
from itacalib.model import lts, sts, interface, contract

     
##
# Exports STS XML contract and interfaces to FSP.
# @param filename Name of the output FSP file.
# @param mycontract A Contract object
# @param myinterfaces A dictionary of Interface objects
def writeDOT(filename, fsm, hideUnconnectedStates=False):
    file_object = open(filename, "w")
    _fsm2DOT(file_object,fsm,hideUnconnectedStates)
    file_object.close()

##
# Generates an interface STS description in FSP.
# @param name Name of the interface
# @param myinterface Interface object
# @defreturn String
def _fsm2DOT(file_object,fsm, hideUnconnectedStates=False):
    file_object.write('digraph finite_state_machine {\n\n' + \
            '\t\tnode [shape = ' + \
            'circle,label="",fixedsize=true,height=0.2,width=0.2];\n');
    if not hideUnconnectedStates:
        for objState in fsm.getStates():
            result='\t\t'+str(hash(objState))
            if objState in fsm.getFinals():
                result=result+'[shape=doublecircle,style=filled]'
            result=result+'; // '+objState+'\n'
            file_object.write(result);
        for tran in fsm.getTransitions():
            label_key = tran.getLabel();
            name, label = None, None;
            if tran.getLabel().upper() == "TAU":
                name,label = "TAU","TAU";
            else:
                label = fsm.getLabel(tran.getLabel());
                name = label.getName();
            file_object.write("".join(('\t\t',str(hash(tran.getSource())),
                            ' -> ', str(hash(tran.getTarget())),
                            ' [ label = "',str(tran.getLabel()),
                            '" ]; // ',"label_key=",repr(tran.getLabel()),
                            ', ',"label_name={0}, label_str={1} \n".format(\
                               str(name), 
                               str(label)))));
    else:
        # @TODO: NOT TESTED YET!
        raise Exception('hideUnconnectedStates is untested!');
        __processed_trans = set();
        __processed_states = set();
        result += _state2DOT(fsm,fsm.getInitial());
    file_object.write('}\n');
    return None;

__processed_trans = set();
__processed_states = set();

def _trans2DOT(sts,tran):
    if tran in __processed_trans:
        return "";
    __processed_trans.add(tran);
    to_return = _state2DOT(sts,tran.getSource());
    to_return += '\t\t'+str(hash(tran.getSource()))+' -> '+ \
       str(hash(tran.getTarget())) + \
       ' [ label = "'+str(tran.getLabel())+'" ];\n';
    to_return += _state2DOT(sts,tran.getTarget());
    return to_return;

def _state2DOT(sts,state):
    if state in __processed_states:
        return "";
    __processed_states.add(state);
    to_return = '\t\t'+str(hash(state));
    if state in sts.getFinals(): to_return += '[style=filled]'
    to_return += ';\n'
    transitions = [_trans2DOT(sts,tran) for tran in \
            sts.outgoingTransitions(state)];
    transitions.insert(0,to_return);
    to_return = "".join(transitions);
    return to_return;


