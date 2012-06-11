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
# Module to generate the minimal acyclic version of an adaptor
#
# Name:   condense_adaptor.py
# Author: José Antonio Martín Baena
# Date:   07-11-2010
##
########################################################################


from itacalib.model.sts import STS;
from itacalib.model.lts import State, Transition;
import itacalib.adaptor.adaptor;




def condense_adaptor(adaptor):
    adaptor.removeUnexploredStates();
    traces = get_traces(adaptor);
    #print traces;
    while True:
        modified = False;
        states = sorted(adaptor.getStates(),
                        lambda x, y: len(traces[y]) - len(traces[x]));
        for state_a in states:
            for state_b in states:
                if state_a == state_b:
                    continue;
                if traces[state_a] == traces[state_b]:
                    #print("Merging {} {}".format(state_a, state_b));
                    modified = True;
                    merge_nodes(adaptor, state_a, state_b);
                    break;
            if modified:
                break;
        if not modified:
            break;
    return adaptor;


def merge_nodes(adaptor, a, b):
    #print "Merging states {} and {}".format(a, b);
    incoming = adaptor.incomingTransitions(b);
    for trans in incoming:
        new_transition = Transition(trans.getSource(), trans.getLabel(), a);
        adaptor.removeTransition(trans);
        adaptor.addTransition(new_transition);
    remove_unconnected(adaptor);


def remove_unconnected(adaptor):
    states = set(adaptor.getStates());
    transitions = set(adaptor.getTransitions());
    to_explore = [adaptor.getInitial()];
    while to_explore:
        exploring = to_explore.pop();
        states.discard(exploring);
        outgoing = STS.outgoingTransitions(adaptor,exploring);
        transitions.difference_update(outgoing);
        to_explore.extend([t.getTarget() for t in outgoing]);
    map(adaptor.removeStateOnly, states);
    map(adaptor.removeTransition, transitions);
        

def get_traces(adaptor, state=None, traces=None):
    if not traces:
        traces = dict();
    if not state:
        return get_traces(adaptor, adaptor.getInitial(), traces);
    traces[state] = set();
    is_final = state in adaptor.getFinals();
    if not STS.outgoingTransitions(adaptor, state):
        traces[state].add((("", is_final),));
    for trans in STS.outgoingTransitions(adaptor, state):
        target = trans.getTarget();
        get_traces(adaptor, target, traces);
        for trace in traces[target]:
            traces[state].add(tuple([(trans.getLabel(), is_final)] + 
                                    list(trace)));
    return traces;
            

