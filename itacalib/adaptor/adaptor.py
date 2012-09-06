#!/usr/bin/env python
# coding=utf-8
"""
Module which contains different adaptors
"""
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
# Module which contains different adaptors
#
# Name:   adaptor.py
# Author: José Antonio Martín Baena
# Date:   01-11-2010 -- 04-09-2012
##
########################################################################

# This module is documented by docstrings.

import sys;

import logging;
import itacalib.model.lts as lts;
import random;
# Used to calculate the standard deviation
import math;

from itacalib.model.sts import STS;
from itacalib.model.contract import Contract;

import itacalib.adaptor.condense_adaptor;


log = logging.getLogger('adaptor');
log_det = logging.getLogger('det_adaptor');

try:
    # For the main function
    import os, argparse, sys;
    import itacalib.XML.dot as dot;
    import itacalib.XML.stsxmlinterface as xml2sts;
    import itacalib.XML.stsxml as stsxml;
    from itacalib.model.interface import Interface, Signature;
    from itacalib.verification.synchronisation import Synchroniser, \
            SynchroniserFeedback, SynchroniserFails, tracesToDot, \
            trace_to_string;
    import unittest;
    import itacalib.tests.adaptor.all_tests;
    #import xml;
    from xml.parsers.expat import ExpatError;
except ImportError:
    if sys.hexversion < 0x02070000:
        print "This program (adaptor) only works with python 2.7 or above.";
        sys.exit(7);
    else:
        raise;




class ContractAdaptor(STS):
    """An adaptor that enforces the given contract

    Every state in the adaptor is <contract_state>|<counter><><queue>. 
    The <counter> is there to force a tree.
    The <queue> is the queue of pending actions obtained from the second part
    of two-sided vectors.
    """

    
    def __init__(self,contract):
        STS.__init__(self);
        self.__counter = 0;
        self.SEPARATOR = "|";
        self.QUEUE_SEPARATOR = "<>";
        self.QUEUE_ELEMENT_SEPARATOR = ",";
        self._contract = contract;
        self.__contract_finals = contract.getLTS().getFinals();
        self.INITIAL_NAME = "initial";
        initialState = "%s%s%s" % (self._contract.getLTS().getInitial(), 
           self.SEPARATOR,
           self.INITIAL_NAME);
        state = lts.State(initialState,True);
        self.addState(state);
        self.setInitial(initialState);


    def outgoingTransitions(self,state):
        """Returns the outgoing transitions from the given state.

        If it is the first time the state is queried then the transitions are
        composed from the contract and stored in the adaptor.

        @param state: Current state in the adaptor
        """
        toReturn = STS.outgoingTransitions(self,state);
        createdTransitions = 0;
        if len(toReturn) == 0:
            toReturn = [];
            queue = self._getQueue(state);
            cstate = self._getContractState(state);
            #
            # -- Create queue transitions --
            for op in self._getQueueIterable(queue):
                label = lts.OutputLabel(op);
                new_queue = self._getQueueIterable(queue);
                new_queue.remove(op);
                new_queue = self._createQueue(new_queue);
                target = self._getNewState(cstate,new_queue);
                transition = self._createTransition(
                   state,label,target);
                toReturn.append(transition);
                createdTransitions += 1;
            #
            # -- Create contract transitions --
            trans = self._contract.getLTS().outgoingTransitions(cstate);
            #log.debug("Current state: %s ; Transitions: %s" % (cstate,trans));
            for tran in trans:
                vect = self._contract.getVector(tran.getLabel());
                length = len(vect.getElements());
                new_queue = queue;
                if length == 1:
                    ele = vect.getElements().values()[0];
                elif length == 2:
                    for el in vect.getElements().values():
                        if el.isEmission():
                            ele = el;
                        elif el.isReception(): 
                            new_queue = self._enqueue(queue,el.getName());
                        else:
                            log.warn("There was a vector element which was not \
                               IN nor OUT");
                else:
                    log.warn("There was a vector with more than one element");
                    continue;
                label = None;
                #log.debug("Vector: %s; Vector element: %r; Op name: %s" % (vect, ele,ele.getName()));
                if ele.isEmission():
                    label = lts.InputLabel(ele.getName());
                elif ele.isReception():
                    label = lts.OutputLabel(ele.getName());
                if label == None:
                    log.warn("There was a vector element which was not \
                        IN nor OUT");
                else:
                    target = self._getNewState(tran.getTarget(),new_queue);
                    transition = self._createTransition(
                       state,label,target);
                    toReturn.append(transition);
                    createdTransitions += 1;
        log.debug("Created {0} new transitions.".format(
           str(createdTransitions)));
        return toReturn;


    def _createTransition(self,source,label,target):
        """Creates and includes a new transition with the given label instance

        @param source: Name of the source state.
        @param label: Label instance.
        @param target: Name of the target state.
        @returns: Transition instance.
        """
        # Don't really know why these two following lines :-(
        labelName = str(label);
        self._A[labelName] = label;
        transition = lts.Transition(source,labelName,target);
        log.debug("Learned transition: %s" % transition);
        self.addTransition(transition);
        return transition;


    def _getCounter(self):
        """Increases and return the counter."""
        self.__counter += 1;
        return self.__counter-1;


    def _getNewState(self,contract_state,queue):
        """Creates a new state based on a given contract state

        @param contract_state: Current state in the contract
        """
        stateName = "".join((contract_state, self.SEPARATOR, 
           str(self._getCounter()), self.QUEUE_SEPARATOR, queue));
        if stateName not in self.getStates():
            isFinal = (queue == "") and \
                contract_state in self.__contract_finals;
            state = lts.State(stateName,False,isFinal);
            self.addState(state);
            if isFinal:
                self.addFinal(stateName);
            #log.debug("Number of generated states: {0}".format(len(self.getStates())));
        return stateName;


    def _getContractState(self,state):
        """It returns the current contract state knowing the adaptor state

        @param state: Adaptor state such as <contract_state>|<counter><><queue>
        """
        return state.partition(self.SEPARATOR)[0];


    def _getQueueIterable(self,queue):
        """Returns an iterable of the actions in the given queue."""
        it = queue.split(self.QUEUE_ELEMENT_SEPARATOR);
        if len(it) == 1 and it[0] == "":
            return [];
        else:
            return it;


    def _getQueue(self,state):
        """Returns the queue of the given state."""
        return state.partition(self.QUEUE_SEPARATOR)[2];


    def _createQueue(self,iterable):
        """Creates a queue with the given iterable."""
        return self.QUEUE_ELEMENT_SEPARATOR.join(iterable);


    def _enqueue(self,queue,new_element):
        """Creates a new queue enqueueing the new_element in the queue."""
        queue = self._getQueueIterable(queue)
        queue.append(new_element);
        return self._createQueue(queue);



class DetContractAdaptor(STS):
    """An adaptor directly based on the contract but forcing determinism.

    This allows lazy decisions and avoids several deadlock situations.
    It should be used in every case.

    Every composite state in the adaptor is 
    {<contract_state>|<counter><><queue>!!}*. 
    """


    def __init__(self, contract):
        STS.__init__(self);
        self._inner = ContractAdaptor(contract);
        self.STATE_SEPARATOR = "!!";
        # Same initial state as the inner ContractAdaptor
        initial_state_name = self._inner.getInitial();
        initial_state = self._inner.getState(initial_state_name);
        self.addState(initial_state);
        self.setInitial(initial_state_name);


    def __getStateIterable(self,cstate):
        """Returns an iterable of the states within the composite state.
        
        @param cstate: Composite state
        @returns: Iterable of ContractAdaptor states
        """
        it = cstate.split(self.STATE_SEPARATOR);
        if len(it) == 1 and it[0] == "":
            return [];
        else:
            return it;


    def __createCompositeState(self, iterable_states):
        """Creates a composite state"""
        # Sort states to make composite states order-independant
        sorted_states = list(iterable_states);
        sorted_states.sort();
        return self.STATE_SEPARATOR.join(sorted_states);


    def outgoingTransitions(self,state):
        """Returns the outgoing transitions from the given state.

        The inner ContractAdaptor is, as usual, dynamically created
        when new queries arrive. In addition, ContractAdaptor might
        be indeterministic, therefore this method performs a 
        powerset transformation to obtain its deterministic version.

        @param state: (Composite) adaptor state
        @returns: The transition outgoing from the given state
        """
        toReturn = STS.outgoingTransitions(self,state);
        if not toReturn:
            toReturn = set();

            indeterministic_transitions = set();
            for single_state in self.__getStateIterable(state):
                indeterministic_transitions |= \
                    set(self._inner.outgoingTransitions(single_state));

            labels = set([x.getLabel() for x in indeterministic_transitions]);

            for label in labels:
                # TAUs are not allowed!!!
                label_instance = self._inner.getLabel(label);
                dstates = set([t.getTarget() \
                    for t in indeterministic_transitions \
                    if t.getLabel() == label]);
                dstate = self._getNewState(dstates);
                toReturn.add(self._createTransition(state,label_instance,dstate));

            if log_det.isEnabledFor(logging.DEBUG):
                log_det.debug("There are {0!s} inner outgoing transitions".format(
                    str(self.__getStateIterable(state))));
                log_det.debug("Created {0} new transitions.".format(str(len(labels))));

        return toReturn;


    def _getNewState(self,iterable_states):
        """Creates a new composite state

        @param iterable_states: The description of the destination states under the same label
        """
        cstate = self.__createCompositeState(iterable_states);
        if cstate not in self.getStates():
            isFinal = False;
            #log_det.debug("States: {0}; Inner finals: {1}".format(str(iterable_states),str(self._inner.getFinals())));
            for state in iterable_states:
                if state in self._inner.getFinals():
                    isFinal = True;
                    break;
            new_state = lts.State(cstate,False,isFinal);
            self.addState(new_state);
            if isFinal:
                self.addFinal(cstate);
        return cstate;


    def _createTransition(self,source,label,target):
        """Creates and includes a new transition with the given label instance

        @param source: Name of the source state.
        @param label: Label instance.
        @param target: Name of the target state.
        @returns: Transition instance.
        """
        # Don't really know why these two following lines :-(
        labelName = str(label);
        self._A[labelName] = label;
        transition = lts.Transition(source,labelName,target);
        log_det.debug("Learned transition: %s" % transition);
        self.addTransition(transition);
        return transition;



class LearningAdaptor(DetContractAdaptor):
    """An adaptor which enforces the safety properties of the given contract
    and learns from previous mistakes.

    When the adaptor reaches a deadlock or perceives that certain transitions
    are not used by the services, it inhibit those transitions to prevent
    further failures.

    It can also forget what it learned in case services have changed.

    Transitions whose target state is never asked for outgoing transitions are
    possible mistakes, therefore candidates to be inhibited. The reason for this
    is that these transitions were not actually synchronised and therefore, not
    properly learned.
    """


    def __init__(self,contract):
        DetContractAdaptor.__init__(self,contract);
        self.inhibited = set();
        self.LIMIT_INHIBITED = sys.maxint;
        # __explored_states -- States which have been explored, \
        #   therefore actually learned
        self.__explored_states = set();
        self._inhibited_counter = 0;
        # @TODO: This is an eternal memory sink, only first level is reused, \
        #   the next is re-generated and included :-(
        self._inhibited_states = dict();


    def getExploredStates(self):
        return self.__explored_states;


    def outgoingTransitions(self,state):
        if state not in self.getStates():
            log.debug("The state {0} does not exist anymore!".format(state));
            return ();
        
        self.__explored_states.add(state);
        transitions = [t for t in DetContractAdaptor.outgoingTransitions(self,state) if \
                t not in self.inhibited];
        return transitions;


    def inhibit(self,transition):
        """From now on, this adaptor inhibits the given transition.

        @param transition: Transition instance to inhibit.
        """
        if transition in self.inhibited:
            log.debug("Transition already inhibited! {0}".format(hash(transition)));
        else:
            target = transition.getTarget();

            if target not in self._inhibited_states:
                self._inhibited_states[target] = self.getState(target);

            self._inhibited_counter += 1;
            self.inhibited.add(transition);
            self.removeDescendants(target);
            if log.isEnabledFor(logging.DEBUG):
                log.debug("Transition disabled: {0!s}".format(transition));
                if transition.getTarget() in self.getFinals() and \
                        transition.getTarget() in self.__explored_states:
                    log.debug(("Possibly inhibiting a good transition if "
                               "it does not depends on an uncontrollable "
                               "internal choice. Transition: "
                               "{0!s}".format(transition)));


    def resetInhibitedCount(self):
        to_return = self._inhibited_counter;
        self._inhibited_counter = 0;
        return to_return;



    class SubscriberInhibiter(object):
        """A subscriber which inhibits traces dynamically 
        if the reason is SynchroniserFeedback.UNFINISHED_TRACE
        """
        # @TODO: Remove subscribers as classes and replace them by methods


        def __init__(self, adaptor, position):
            """ It instantiates the class

            @param adaptor: The adaptor whose transitions must be dynamically inhibited
            @param position: The index of the adaptor in the trace
            """
            self.adaptor = adaptor;
            self.position = position;

    
        def notify(self, reason, details):
            """ Notifying method called by by the monitorised object

            @param reason: Reason for the notification
            @param details: Additional human-readable details
            """
            if reason is not SynchroniserFeedback.UNFINISHED_TRACE:
                return;
            #log.warn("The dreadful trace is : {}".format(trace_to_string(details,0)));
            if not details:
                log.warn("Something strange is happening inhibiting on real time");
            adaptor_current_state = details[-1][0][self.position];
            # Inhibit only if the adaptor is not in an accepted state by the contract
            if adaptor_current_state not in self.adaptor.getFinals():
                to_inhibit = self.adaptor.incomingTransitions(adaptor_current_state);
                if len(to_inhibit) > 1:
                    log.warn("More than 1 incoming transitions!");
                for t in to_inhibit:
                    log.debug("Inhibiting on real time: {0!r}".format(t));
                    self.adaptor.inhibit(t);



    def getSubscriber(self, position):
        """It returns a subscriber suitable for SynchroniserFeedback

        Such a subscriber is a method with two arguments: the reason
        (which should be UNFINISHED_TRACE, otherwise ignored) and the 
        trace.
        This method inhibits the trace it receives.
        
        @param position: The index of the adaptor in the trace
        """
        return LearningAdaptor.SubscriberInhibiter(self, position).notify;


    def removeTransitionAndDescendants(self, transition):
        """Removes the given transition and all its descendants
        It removes them as well from the set of inhibited traces

        @param transition: Transition to remove
        """
        self.removeDescendants(transition.getTarget());
        self.removeTransition(transition);


    def removeTransition(self, transition):
        """Remove the given transition.
        It removes it as well from the set of inhibited traces

        @param transition: Transition to remove"""
        #log.debug("Removing transition {!s}".format(transition));
        DetContractAdaptor.removeTransition(self,transition);
        self.inhibited.discard(transition);


    def removeDescendants(self, state):
        """Remove every transition and state reachable from (and including) the given state

        @param state: The parent state of every transition and state to be removed
        """
        if state in self.getStates():
            # If the list is not copied, it interferes during the removal
            outgoing_transitions = list(STS.outgoingTransitions(self,state));
            map(self.removeDescendants, \
                    [t.getTarget() for t in outgoing_transitions]);
            map(self.removeTransition, outgoing_transitions);
            self.__explored_states.discard(state);
            self.removeStateOnly(state); # This removes incoming and outgoing transitions from state


    def getTransitions(self):
        # @TODO: Maybe this does not work because, in LTS, getTransitions return a list.
        to_return = set(DetContractAdaptor.getTransitions(self));
        to_return.difference_update(self.inhibited);
        return to_return;


    def getExploredTransitions(self):
        states = set(self.getStates());
        states.difference_update(self.__explored_states);
        unexplored_transitions = [t for state in states for \
                t in self.incomingTransitions(state)];
        # Just to avoid modifying the transitions of the adaptor
        to_return = set(self.getTransitions());
        to_return.difference_update(unexplored_transitions);
        return to_return;


    def removeUnexploredStates(self):
        """Removes unexplored states"""
        states = set(self.getStates());
        states.difference_update(self.__explored_states);
        unexplored_transitions = [t for state in states for \
                t in self.incomingTransitions(state)];
        map(self.removeTransitionAndDescendants, unexplored_transitions);


    def getInhibited(self):
        """Returns the set of inhibited traces.

        @returns: The set of inhibited traces."""
        return self.inhibited;



class ForgettingAdaptor(LearningAdaptor):


    def _forget(self):
        """Forgets what is necessary if it is necessary"""
        pass;


    def forget(self):
        """Forgets everything learned so far."""
        self.forgetTransitions(self.inhibited);


    def forgetTransitions(self, to_remove):
        """Forgets all the given transitions"""
        self.inhibited.difference_update(set(to_remove));
        targets = [t.getTarget() for t in to_remove];
        map(self.removeDescendants, targets);
        [self.addState(self._inhibited_states[target]) for \
                target in targets];


    def inhibit(self, trace):
        to_return = LearningAdaptor.inhibit(self, trace);
        self._forget();
        return to_return;



class ThresholdAdaptor(ForgettingAdaptor):


    _threshold = sys.maxint;

    def __init__(self, contract):
        ForgettingAdaptor.__init__(self, contract);


    def _forget(self):
        """It forgets when the set of inhibited traces reaches the threshold"""
        to_forget = len(self.inhibited) - self._threshold;
        if to_forget <= 0:
            return;
        log.debug("Forgetting {} transitions.".format(to_forget));
        to_remove = random.sample(list(self.inhibited),to_forget);
        self.forgetTransitions(to_remove);


    def setThreshold(self, threshold):
        """Stablishes a threshold to the set of inhibited traces

        @pram threshold: New threshold for the set of inhibited traces
        """
        self._threshold = threshold;
        self._forget();


    def getThreshold(self):
        """Returns the current threshold

        @returns: The current threshold
        """
        return self._threshold;



class DynamicThresholdAdaptor(ThresholdAdaptor):


    INCREMENT_ON_SUCCESS = -1;

    INCREMENT_ON_FAILURE = +1;

    minimum_threshold = 0;



    def incrementThreshold(self, increment):
        self._threshold = max(self._threshold + increment, 
                                   self.minimum_threshold);
        self._forget();


    def alterThreshold(self, reason):
            if reason is SynchroniserFeedback.SUCCESSFUL_TRACE:
                self.incrementThreshold(
                        DynamicThresholdAdaptor.INCREMENT_ON_SUCCESS);
            if reason is SynchroniserFeedback.UNFINISHED_TRACE:
                self.incrementThreshold(
                        DynamicThresholdAdaptor.INCREMENT_ON_FAILURE);

    
    #@inherit_docstring
    def getSubscriber(self, position):
        parent_subscriber = ThresholdAdaptor.getSubscriber(self, position);
        def notify(reason, detail):
            self.alterThreshold(reason);
            parent_subscriber(reason, detail);
        return notify;
        

    #@append_to_docstring
    def _forget(self):
        """This forget includes a *reset* mechanism wich sets threshold to 0
        if the adaptor becomes empty.
        """
        if self._threshold > 0 and len(self.getExploredStates()) == 1:
            # Avoid convergence to empty adaptors.
            self.resetThreshold(); # Cannot use setThreshold
        ThresholdAdaptor._forget(self);


    def setMinimumThreshold(self, minimum_threshold):
        self.minimum_threshold = minimum_threshold;


    def resetThreshold(self):
        """It resets the threshold to 0. _forget{} must be called afterwards """
        if log.isEnabledFor(logging.DEBUG):
            log.debug("Reseting to avoid empty adaptor! (Explored states: "
                     "{})".format(len(self.getExploredStates())));
        self._threshold = 0;



class AdaptiveAdaptor(DynamicThresholdAdaptor):


    _threshold = 0;


    def alterThreshold(self, reason):
        """Permantently sets the threshold to the amount of explored states - 1

        This makes the DynamicThresholdAdaptor's reset superfluous because,
        when the adaptor is empty, it contains a single explored state and
        therefore, the threshold is effectivelly set to 0, hence resetting 
        the adaptor to avoid convergence to empty adaptors.
        """
        if reason is SynchroniserFeedback.SUCCESSFUL_TRACE or \
                reason is SynchroniserFeedback.UNFINISHED_TRACE:
            # @TODO: This should use getExploredTransitions() but it's inefficient
            self.setThreshold(max(self.minimum_threshold,
                                  len(self.getExploredStates()) - 1));


        
def test():
    log.info("Executing test...");
    suite = unittest.TestLoader().loadTestsFromName("suite", itacalib.tests.adaptor.all_tests);
    unittest.TextTestRunner().run(suite);
    sys.exit(0);


def writeAdaptorSTS(filename, adaptor):
    # Write the adaptor in STS
    # Create adaptor signature
    adaptor_signature = Signature("");
    #for label in adaptor.getLabels():
    #    label_instance = adaptor.getLabel(label);
    #    if label_instance.isInput():
    #        adaptor_signature.addInput(label);
    #    elif label_instance.isOutput():
    #        adaptor_signature.addOutput(label);
    #    else:
    #        log.debug("Found a (possibly) TAU label");
    # Create adaptor interface
    adaptor_interface = Interface("LearningAdaptorInterface");
    adaptor_interface.addSignature(adaptor_signature);
    adaptor_interface.setSTS(adaptor);
    # Write to file
    xml2sts.writeXML(filename, adaptor_interface);


def main():
    logging.basicConfig(level=logging.INFO);
    log.info( """ITACA - adaptor.py  Copyright (C) 2011 José Antonio Martín Baena 
This program comes with ABSOLUTELY NO WARRANTY. This is free software, and 
you are welcome to redistribute it under certain conditions.
""");
    parser = argparse.ArgumentParser(description="Generates, trains and " + 
        "simulates a LearningAdaptor with the given stsxml description of " +
        "services and contract.");
    group_adaptor = parser.add_mutually_exclusive_group();
    group_ter = parser.add_mutually_exclusive_group();
    parser.add_argument('-c', '--contract', metavar="C", 
            help="the adaptation contract");
    parser.add_argument('-t', help="run a test", action='store_true');
    parser.add_argument('-p', '--prefix', metavar="P", 
            help="the prefix of the output files");
    parser.add_argument('-l', '--limit', metavar="L", type=int, default=20, \
            help="depth limit during training and simulation, default = 20");
    group_ter.add_argument('--ter', metavar="TER", type=float, default=0., \
            help="transition error rate [0,1], default = 0");
    group_adaptor.add_argument('--sthr', metavar="THR", type=int, \
            help="the static threshold beyond the adaptor forgets, default = infinity");
    group_adaptor.add_argument('--dthr', metavar="DTHR", type=int, \
            help="enables dynamic threshold with a minimum set to DTHR, "+ \
            "excludes sthr");
    parser.add_argument('services', metavar="S", \
            help="service description", nargs="*");
    parser.add_argument('-i', metavar="I", type=int, \
            help="maximum number of trainning iterations, if it not set "+ \
            "it will wait until nothing is learnt in the last iteration");
    parser.add_argument('-n', metavar="N", type=int, default=1,
            help="for statistical purposes, how many samples we want");
    parser.add_argument('-s', '--stats', metavar="F", 
            type=argparse.FileType('w'), 
            help="a file where the stats will be written");
    group_ter.add_argument('--dter', metavar="DTER", type=str,
            help="a list of at least I values of TER, one for each iteration");
    parser.add_argument('--times', metavar="T", type=int,
            help="train using T randomly generated traces");
    group_adaptor.add_argument('--athr', metavar="ATHR", type=int,
            help=("enables adaptive adaptation with a minimum threshold of "
                  "ATHR, excludes dthr and sthr"));

    args = parser.parse_args();

    if args.t:
        test();

    #if not(args.contract):
    #    log.error("You must specify a contract with -c");
    #    sys.exit(33);

    if not(args.services):
        log.error("You must specify a one or more services S");
        sys.exit(34);

    paths = args.services + [args.contract] if args.contract else args.services;
    for path in paths:
        if not os.path.exists(path):
            log.error("One of the given paths doesn't exist: %s" % path);
            sys.exit(3);
    if args.i and args.dter:
        log.error("Parameters i and dter are incompatible");
        sys.exit(10);
    dter = None;
    if args.dter:
        try:
            dter = eval(args.dter);
            assert isinstance(dter, (list, tuple));
            for ter in dter:
                assert isinstance(ter, (float, int));
            args.i = len(dter);
            ter = dter[0];
        except Exception:
            log.error("Parameter --dter must be a python list or tuple "+
                      'of float numbers, i.e., "[ 0.1, 0.001, 0]"');
            sys.exit(1);

    services = [];
    # Load contract
    contract = None;
    if args.contract:
        try:
            contract = stsxml.readXML(args.contract);
        except ExpatError, message:
            log.error('The contract file ("%s") could not be parsed: \n\t%s' % (args.contract,message));
            sys.exit(4);
    elif not args.i:
        log.error("If there is no contract (and thus no adaptor) there must "+
                  "be an iteration limit '-i'");
        sys.exit(11);

    # Load services
    for filename in args.services:
        try:
            services.append(xml2sts.readXML(filename).getSTS());
        except ExpatError, message:
            log.error('One of the given service files ("%s") could not be parsed: \n\t%s' % (file,message));
            sys.exit(5);

    # Write input in DOT files for services
    if args.prefix:
        toWrite = services;
        for i in range(0,len(toWrite)):
            dot.writeDOT("{0}_service_{1}.dot".format(args.prefix, str(i)), 
                                                      toWrite[i]);

        # Write the DOT file of the contract
        if args.contract:
            dot.writeDOT("{0}_contract.dot".format(args.prefix), contract.getLTS());

    stats_format = ("#{:0>2d} - {} {} (TER={:.2e}; ETER={:<.2e}): |I|={:>4d}; "
                    "|T|={:>4d}; E ={:4n}; F={:4n}; E/F={:4.0%}; "
                    "S={:4n}; F/(F+S)={:7.2%}");
                   #"# 00 CORRECT 1.00e-02 1.00e-02 1234 1234 1234 1234 "
                   #"123% 1234 1.345%"
    file_header =  ("## Stats generated by adaptor.py\n#{}\n"
                    "# it STATUS_ __TER___ __ETER__ _|I|__ _s|I|_ "
                    "_|T|__ _s|T|_ __E___ __sE__ ___F___ __sF___ "
                    "_EFR__ _sEFR_ __S___ __sS__ __SFR__ _sSFR_ "
                    "samples={}\n").format(' '.join(sys.argv), args.n);
    file_format =  ("  {0:0>2d} {2} {6:.2e} {8:<.2e} {10:>6.1f} {11:>6.1f} "
                    "{12:>6.1f} {13:>6.1f} {14:6.1f} {15:6.1f} {16:7.1f}"
                    " {17:7.1f} {18:6.1%} {19:6.1%} "
                    "{20:6.1f} {21:6.1f} {22:7.2%} {23:6.2%}\n");


    if not range(0, args.n):
        log.fail("The population (N) has to be a positive natural");
        sys.exit(8);

    samples = {};

    for iteration in range(0,args.n):

        samples[iteration] = {};
        counter = 1;
        continue_ = (args.i is None) or (args.i >= counter);
        traces = None;
        accummulated_stats = (0,0,0,0);

        adaptor = None;
        if args.contract:
            if args.sthr is not None:
                log.info("Created an adaptor with static threshold {}".
                         format(args.sthr));
                adaptor = ThresholdAdaptor(contract);
                adaptor.setThreshold(args.sthr);
            elif args.dthr is not None:
                log.info("Created an adaptor with dynamic threshold "
                         "whose minimum is {}".format(args.dthr));
                adaptor = DynamicThresholdAdaptor(contract);
                adaptor.setThreshold(args.dthr);
                adaptor.setMinimumThreshold(args.dthr);
            elif args.athr is not None:
                log.info("Created an adaptive adaptor "
                         "whose minimum threshold is {}".format(args.athr));
                adaptor = AdaptiveAdaptor(contract);
                adaptor.setThreshold(args.athr);
                adaptor.setMinimumThreshold(args.athr);
            else:
                log.info("Created an adaptor without threshold");
                adaptor = LearningAdaptor(contract);

        log.info("Using a synchroniser with traces with a maximum length of"
                 " {} transitions.".format(args.limit));

        adaptor_and_services = [adaptor] + services \
                if args.contract else services;

        while continue_:

            log.info("==== Synchronising services - iteration "+ \
                     "#{:d}.{:0>2d} =====".format(iteration,counter));

            if dter:
                args.ter = dter[counter-1];

            syn = SynchroniserFails(args.limit, args.ter);
            if adaptor:
                syn.subscribe(adaptor.getSubscriber(0));
            traces = syn.synchronise(adaptor_and_services, times=args.times);

            # Gathering stats
            stats = syn.getStats();
            accummulated_stats = [x+y for (x, y) in \
                    zip(accummulated_stats,stats)];
            if adaptor:
                calculated_stats = calculate_stats(counter, syn, adaptor, 
                                               traces, args.ter)
                samples[iteration][counter-1] = calculated_stats;
                log.info("Iter. stats "+
                         stats_format.format(*calculated_stats));
            #if args.stats is not None and args.population == 1:
            #    args.stats.write(file_format.format(*calculated_stats));
            syn.resetStats();

            if args.prefix:
                # Write generated traces
                log.info("Writing the resulting traces and the adaptor...");
                tracesFile = open("{0}_traces_{1}.dot".format(args.prefix, \
                    str(counter)),"w");
                tracesFile.write(tracesToDot(traces));
                tracesFile.close();

                # Write the adaptor 
                if adaptor:
                    dot.writeDOT("{0}_adaptor_{1!s}.dot".format(args.prefix, \
                            counter), adaptor);
                    writeAdaptorSTS("{0}_adaptor_{1!s}.xml".format( \
                            args.prefix, counter), adaptor);


            # Shall we continue one iteration more?
            inhibited = adaptor is None or adaptor.resetInhibitedCount();
            continue_ = (args.i is None and inhibited != 0) or \
                    (args.i is not None and counter < args.i);


            counter += 1;

    stats = accummulated_stats;
    if adaptor:
        log.info("Acc. stats  "+
              stats_format.format(*calculate_stats(99, stats, adaptor, 
                                                   traces, args.ter)));
    
    if args.prefix:
        log.info("Writing raw final traces...");
        resultFile = open("{0}_raw_traces.txt".format(args.prefix), "w");
        resultFile.write(repr(traces));
        resultFile.close();
        if adaptor:
            log.info("Writing the condensed adaptor...");
            condensed_adaptor = \
                    itacalib.adaptor.condense_adaptor.condense_adaptor(adaptor);
            dot.writeDOT("{0}_adaptor_final.dot".\
                    format(args.prefix), condensed_adaptor);
            writeAdaptorSTS("{0}_adaptor_final.xml".format( \
                    args.prefix), condensed_adaptor);

            # Verifying that the condensed adaptor is CORRECT
            syn = SynchroniserFeedback(args.limit);
            final_adaptor = STS();
            final_adaptor.setStates(adaptor.getStates());
            final_adaptor.setInitial(adaptor.getInitial());
            final_adaptor.setFinals(adaptor.getFinals());
            final_adaptor.setLabels(adaptor.getLabels());
            final_adaptor.setTransitions(adaptor.getTransitions());
            final_adaptor.getExploredTransitions = \
                    lambda: final_adaptor.getTransitions();
            final_adaptor.inhibited = adaptor.inhibited;
            adaptor_and_services = [final_adaptor] + services;
            traces = syn.synchronise(adaptor_and_services);
            log.info("Final stats " + 
                    stats_format.format(*calculate_stats(99, syn.getStats(), 
                    final_adaptor, traces, args.ter)));


    log.info("Writing stats...");
    # Write stats header
    stats_out = args.stats if args.stats is not None else sys.stdout;
    stats_out.write(file_header);
    write_stats(samples, stats_out, file_format);

    if args.stats is not None:
        args.stats.close();

    log.info("Have a nice day!");


def write_stats(samples, file, file_format):
    def sum_if_numbers((x, y)):
        if isinstance(y, str):
            return y;
        else:
            return x + y;
    for iteration in range(0,len(samples[0])):
        iteration_row = [];
        for element in range(0, len(samples[0][0])):
            if isinstance(samples[0][iteration][element], str):
                iteration_row += [samples[0][iteration][element], ''];
            else:
                values = [samples[s][iteration][element] for s in samples];
                avg = calculate_avg(values);
                stdv = None;
                if (len(values) > 1):
                    stdv = calculate_sample_standard_deviation(avg, values);
                else:
                    stdv = calculate_standard_deviation(avg, values);
                iteration_row += [avg, stdv];
        iteration_row[0:2] = [iteration, 0];
        file.write(file_format.format(*iteration_row));


def calculate_avg(values):
    return float(sum(values))/len(values);


def calculate_standard_deviation(avg, values):
    value = sum([(v - avg)**2 for v in values]);
    return math.sqrt(float(value)/len(values));


def calculate_sample_standard_deviation(avg, values):
    value = sum([(v - avg)**2 for v in values]);
    return math.sqrt(float(value)/(len(values)-1));


def is_correct_adaptor(traces):
    """All the traces end successfully or the adaptor is empty
    
    @param: Traces of the sytem
    """
    # Empty adaptor is always correct
    synchronisations = [trans for trace in traces for trans in trace if \
            (trans[1] is not None and trans[1] != 'TAU')];
    if not synchronisations: # is empty
        return True;
    for trace in traces:
        if not trace[-1][-1]:
            return False;
    return True;


def calculate_stats(iteration, syn, adaptor, traces, ter):
    """Returns various stats of the simulation

    * iter, the iteration number of the simulation.
    * CORRECT or WRONG depending on if all the traces where successfull or not.
    * "empty" or "" depending on whether the adaptor is empty or not.
    * TER, percentage of transitions which must be subject to sporadic errors.
    * ETER, effective TER, evaluated after the simulation with the data.
    * |I|, the ammount of inhibited traces in the adaptor.
    * |T|, the ammount of regular explored transitions in the adaptor.
    * E, the ammount of sporadic errors which causef failures.
    * F, the ammount of failures (E <= F).
    * EFR = E/F, percentage of failures caused by sporadic errors.
    * S, the ammount of successful traces.
    * SFR = F/(F+S), the percentage of failed traces.

    @param iteration: Simulation iteration.
    @param syn: The synchroniser used for the simulation or its stats.
    @param adaptor: The adaptor involved in the simulation.
    @param traces: The traces generated by the simulation.
    @param ter: The TER given as initial parameter to the synchronsier.
    @returns: (iter, STATUS, EMPTY, TER, ETER, |I|, |T|, E, F, EFR, S, SFR)
    """
    stats = None;
    if isinstance(syn, Synchroniser):
        stats = syn.getStats();
    else:
        stats = syn;
    trans = len(adaptor.getExploredTransitions());
    correct_adaptor = "  WRONG";
    empty_adaptor = "";
    if len(adaptor.getStates()) < 2:
        empty_adaptor = "empty";
    if is_correct_adaptor(traces):
        correct_adaptor = "CORRECT";
    i = len(adaptor.inhibited);
    return (iteration, correct_adaptor, empty_adaptor, ter, 
            calculate_ETER(*stats), i, trans, stats[0], 
            stats[2], calculate_EFR(*stats), 
            stats[1], calculate_SFR(*stats));


def calculate_SFR(errors, successes, failures, transitions):
    """Returns the SFR (session-failure rate) = F/(S+F)"""
    if successes + failures == 0:
        return 0.;
    else:
        return float(failures)/(failures + successes);
    

def calculate_ETER(errors, successes, failures, transitions):
    """Returns the ETER (effective transition error rate) = E/T"""
    if transitions == 0:
        return 0.;
    else:
        return float(errors)/transitions;

def calculate_EFR(errors, successes, failures, transitions):
    """Returns the EFR (errors-failures rate) = E/F"""
    if failures == 0:
        return 1.
    else:
        return float(errors)/failures;


__author__ = "José Antonio Martín Baena";
__copyright__ = "Copyright 2011, José Antonio Martín Baena";
#__credits__ = [];
__license__ = "GPLv3";
__version__ = "1.0";
__maintainer__ = "José Antonio Martín Baena";
__email__ = "jose.antonio.martin.baena@gmail.com";
__status__ = "Prototype";


if __name__ == "__main__":
    main();

