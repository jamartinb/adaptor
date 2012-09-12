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
# This module performs all the possible synchronisations among several STSs
#
# Name:   synchronisation.py - Simulates all the possible synchronisations among STSs
# Author: José Antonio Martín Baena
# Date:   08-10-2010
##
########################################################################

# This module is documented by docstrings.


import logging;
# For TRANSITION_ERROR_RATE and synchronise with times parameter
import random;



log = logging.getLogger('synchronisation')


#log.setLevel(logging.INFO);
#log.setLevel(logging.DEBUG);
#logging.basicConfig(level=logging.DEBUG);
#logging.basicConfig();

import sys
try:
    # Used in main()
    import argparse;
    import sys;
    import os;
    from xml.parsers.expat import ExpatError;
    import itacalib.XML.stsxmlinterface as xml2sts;
except ImportError:
    if sys.hexversion < 0x02070000:
        print "This program (adaptor) only works with python 2.7 or above.";
        sys.exit(7);
    else:
        raise;



class Synchroniser(object):
    """This class generates all the possible traces among a given set of STSs.

    The main method for this class is synchronise
    """


    """Default limit for the length of the traces generated by the Synchroniser"""
    DEFAULT_LIMIT = 99;


    def __init__(self,limit=DEFAULT_LIMIT):
        """Initialises the Synchoriser instance

        @param limit: Maximum depth of the traces to generate. Truncated traces are not included in the results.
        """
        self.limit = limit;


    def synchronise(self, listOfSts, currentTrace=(), limit=None, times=None):
        """It performs every synchronisation possible among the given STSs at their current states.

        A state is a couple of current states and the last transition.
        The last transition might be None if we are at the initial state,
        otherwise, last transition is the name of the label of the last transition
        Example: (currentStates,lastTransition, isGloballyFinal)

        Current states is a tuple of the current states in the same order of their respective STSs in the listOfSts.
        Example: ((currentState_0,currentState_1,...), lastTransition,
           isGloballyFinal)

        A trace is a tuple of states.
        Example: (...,(states_-1, lastTransition_-1, isGloballyFinal_-1),
           (states_0, lastTransition_0, isGloballyFinal_0))

        Incomplete traces which reach the limit are also included.

        Two actions of two different services can synchronise if their source states are current states, 
        the name of the action is the same and they present different directions. Action renaming is
        necessary when we want to restrict possible synchronisations.
        
        TAU actions synchronise independently.

        If parameter time is not None, then the Synchroniser behaves 
        completely different and it only simulates individual traces
        randomly generated.

        However, individual traces do finish when they reach either
        the depth limit or a state without outgoing transitions or,
        in other words, final states in the middle of traces are
        counted as successful traces but are not counted towards
        the limit of individual traces.

        @param listOfSts: Sequence of STSs instances.
        @param currentTrace: Actual trace
        @param limit: Maximum depth of the traces to generate. Truncated traces are not included in the results.
        @param times: The number of individual traces to simulate.
        @returns: A set of traces
        """
        if limit == None: limit = self.limit;
        # Include incomplete traces which reached the limit

        if not currentTrace:
            initialStates = [sts.getInitial() for sts in listOfSts];
            currentTrace = ((tuple(initialStates), None, 
                self.isGloballyFinal(listOfSts,initialStates)),);

        currentStates = currentTrace[-1][0];

        if limit == 0:
            if currentTrace[-1][-1]:
                # Ask for outgoingTransitions of these last states
                # so that it counts as explored states in learning
                # adaptors.
                [listOfSts[i].outgoingTransitions(currentStates[i]) for
                        i in range(0, len(listOfSts))];
            return set([currentTrace]);

        toReturn = set();
        nextTraces = set();

        if log.isEnabledFor(logging.DEBUG):    
            log.debug("Current trace: %s" % (currentTrace,));
            log.debug("Current state: %s" % (currentStates,));

        if times and times > 1:
                map(toReturn.update, 
                        (self.synchronise(listOfSts, currentTrace, limit, 1) for 
                        t in range(0,times)));
                return toReturn;

        # Pre-calculate readyTransitions to optimise the following loops
        ready_transitions = \
                [self.readyTransitions(listOfSts[i],currentStates[i]) \
                for i in range(0, len(listOfSts))];

        for i in range(0,len(listOfSts)):
            P=listOfSts[i];
            sP = currentStates[i];

            for transition in self.tauTransitions(P,sP):
                nextState=list(currentStates);
                nextState[i]=transition.getTarget();
                nextState=tuple(nextState);
                nextTrace = currentTrace + ((nextState,"TAU",
                   self.isGloballyFinal(listOfSts,nextState)),);
                nextTraces.add(nextTrace);

            for j in range(i+1,len(listOfSts)):
                Q=listOfSts[j];
                sQ = currentStates[j];
                readyTransitions = [ (x,y) \
                        for x in ready_transitions[i] \
                        for y in ready_transitions[j] \
                        if self.canTransitionsSynchronise(
                            P.getLabel(x.getLabel()),
                            Q.getLabel(y.getLabel()))];
                for (x,y) in readyTransitions:
                    nextState=list(currentStates);
                    nextState[i]=x.getTarget();
                    nextState[j]=y.getTarget();
                    nextState=tuple(nextState);
                    nextTrace = currentTrace + \
                       ((nextState, P.getLabel(x.getLabel()).getName(), 
                       self.isGloballyFinal(listOfSts,nextState)),);
                    #log.debug("Next trace: %s" % str(nextTrace));
                    nextTraces.add(nextTrace);

        if len(nextTraces) == 0:
            toReturn.add(currentTrace);
        else:
            if not times:
                for trace in nextTraces:
                    toReturn |= self.synchronise(listOfSts,trace,limit - 1, times);
            else:
                trace = random.choice(list(nextTraces));
                toReturn = self.synchronise(listOfSts, trace, limit - 1, times);
        return toReturn;


    def isGloballyFinal(self,stss,currentStates):
        """Retruns True if all the current states are service final states.
        
        @param stss: Service STSs.
        @param currentStates: Service current states.
        @returns: True if currentStates is a globally final state.
        """
        to_return = True;
        for i in range(0,len(stss)):
            if currentStates[i] not in stss[i].getFinals():
                to_return = False;
                break;
        return to_return;



    def readyTransitions(self,sts,currentState):
        """Returns a list of non tau outgoing transitions from the current state

        @param sts: STS of the service.
        @param currentState: Current state of the service.
        @returns: List of outgoing non-tau transitions from the current state.
        """
        #transitions = sts.outgoingTransitions(currentState);
        #if log.isEnabledFor(logging.DEBUG):
        #    for t in transitions:
        #        log.debug("Ready transitions for service %r: %s" % (sts, t));
        return filter(lambda x:not x.isTau(), \
                sts.outgoingTransitions(currentState));


    def tauTransitions(self,sts,currentState):
        """Returns a list of tau outgoing transitions from the current state

        @param sts: STS of the service.
        @param currentState: Current state of the service.
        @returns: Iterable over outgoing tau transitions from the current state.
        """
        transitions = sts.outgoingTransitions(currentState);
        return filter(lambda x:x.isTau(),transitions);


    def canTransitionsSynchronise(self,labelA,labelB):
        """ Returns whether two labels can synchronise or not

        @param labelA: A label
        @param labelB: Another label
        @returns: Iterable over possible outgoing labels
        """
        return (labelA.getType() != \
                labelB.getType()) and \
                (labelA.getName() == \
                labelB.getName());
        #log.debug("{0} vs {1} = {2}".format(labelA,labelB,repr(to_return)));
        #return to_return;


class SynchroniserFeedback(Synchroniser):
    """A Synchroniser which keeps track of both unfinished and finished 
    traces and warns about them in real time.

    Unfinished traces are those which cannot continue synchonising and
    are in a state which is not globally final.

    For this purpose, it has a 'subscribe' and 'unsubscribe' method where
    subscribers must have a method such as:

        subscriber.notify(reason,details)

    where the reason is going to be "UNFINISHED_TRACE" and the details 
    is the actual trace.

    If you subscribe several times, you get several notifications of the
    same event.
    """

    # static constant
    UNFINISHED_TRACE = "UNFINISHED_TRACE";

    SUCCESSFUL_TRACE = "SUCCESSFUL_TRACE";

    INTERRUPTED_TRACE = "INTERRUPTED_TRACE";
    


    def __init__(self,limit=Synchroniser.DEFAULT_LIMIT):
        Synchroniser.__init__(self,limit);
        self._subscribers_list = [];
        self.resetStats();
        def notify(reason, details):
            if reason is SynchroniserFeedback.UNFINISHED_TRACE:
                self._failures += 1;
            if reason is SynchroniserFeedback.SUCCESSFUL_TRACE:
                self._successes += 1;
            if reason is SynchroniserFeedback.INTERRUPTED_TRACE:
                self._errors += 1;
        self.subscribe(notify);


    def resetStats(self):
        self._errors = 0;
        self._successes = 0;
        self._failures = 0;
        self._transitions = 0;


    def subscribe(self, subscriber):
        """Add a new subscriber to be notified about new unfinished_traces

        @param subscriber: New subscriber
        """
        if not callable(subscriber):
            log.error("The given subscriber is not callable: {!r}".\
                    format(subscriber));
        else:
            self._subscribers_list.append(subscriber);


    def unsusbscribe(self, subscriber):
        """Removes a subscriber

        If the subscriber was not subscribed then an exception is raised

        @param subscriber: Subscriber to be removed
        """
        _subscribers_list.remove(subscriber);


    def _unfinished_trace(self, trace):
        """Notifies of a new unfinished trace

        @param trace: New unfinished trace
        """
        [subscriber(SynchroniserFeedback.UNFINISHED_TRACE,trace) for \
                subscriber in self._subscribers_list];


    def _successful_trace(self, trace):
        """Notifies of a new successful trace

        @param trace: New successful trace
        """
        [subscriber(SynchroniserFeedback.SUCCESSFUL_TRACE,trace) for \
                subscriber in self._subscribers_list];


    def _interrupted_trace(self, trace):
        """Notifies of a new interrupted trace

        The interrupted trace is also a unfinished trace.

        @param trace: New interrupted trace
        """
        [subscriber(SynchroniserFails.INTERRUPTED_TRACE,trace) for \
                subscriber in self._subscribers_list];


    def getStats(self):
        """Returns the number of sporadic errors E, completed sessions S, \
                failed sessions F (>= E) and total transitions T.

        @returns: (E, S, F, T) E:sporadic errors, S:successes, F:failures, T:transitions
        """
        return (self._errors, self._successes, self._failures, self._transitions);


    def synchronise(self,listOfSts,currentTrace=(),limit=None, times=None):

        if times and times > 1:
            # This delegate will call back this synchronise with proper 
            # initialization and times=1
            return Synchroniser.synchronise(self, listOfSts,
                    currentTrace, limit, times);

        # Due to the previous if, from here on there will be a single trace
        assert times is None or currentTrace is not (), \
                "A variable (currentTrace) was not properly initialised"

        self._transitions += 1;
        # Delegate on Synchroniser the actual work
        new_traces = Synchroniser.synchronise(self, listOfSts, currentTrace, 
                                              limit, times);

        # If times is selected, then there must be a single trace at most
        assert times is None or len(new_traces) < 2, \
                "A problem occurred running random traces"

        if currentTrace is not () and currentTrace[-1][-1]:
            self._successful_trace(currentTrace);

        if len(new_traces) == 1 and currentTrace in new_traces and \
                not currentTrace[-1][-1]:
            # If no synchronisation was possible the single returned trace 
            # is the same as the current trace
            self._unfinished_trace(currentTrace);
        elif len(new_traces) == 1 and len(list(new_traces)[0]) == 1 and \
                not list(new_traces)[0][-1][-1]:
            # The trace is the initial, non-final state
            self._unfinished_trace(list(new_traces)[0]);

        return new_traces;



class SynchroniserFails(SynchroniserFeedback):
    """A synchroniser whose synchronsiations fail at a certain rate
    """


    """Default error rate: traces_interrupted / transitions (internal + communications)"""
    DEFAULT_TRANSITION_ERROR_RATE = 0.1;



    def __init__(self, limit=SynchroniserFeedback.DEFAULT_LIMIT, \
            transition_error_rate = DEFAULT_TRANSITION_ERROR_RATE):
        SynchroniserFeedback.__init__(self,limit);
        self._transition_error_rate = transition_error_rate;


    def setTER(self, ter):
        self._transition_error_rate = ter;


    def synchronise(self, listOfSts, currentTrace=(), limit=None, times=None):

        if times and times > 1:
            return SynchroniserFeedback.synchronise(self, listOfSts,
                    currentTrace, limit, times);

        ter = self._transition_error_rate

        if (currentTrace is ()) or (random.random() > ter):
            # No transition error
            return SynchroniserFeedback.synchronise(self, listOfSts, 
                    currentTrace, limit, times);
        else:
            # Transition error, no new traces
            if log.isEnabledFor(logging.DEBUG):
                log.debug("A trace was interrupted due to the defined "
                          "transition error rate (TER)");
            if not currentTrace[-1][-1]:
                self._interrupted_trace(currentTrace);
                self._unfinished_trace(currentTrace);
            else:
                self._successful_trace(currentTrace);
            new_traces = set();
            new_traces.add(currentTrace);

            return new_traces;



def tracesToDot(traces):
    """ Returns dot text representing the given tree of traces.

    @param traces: Traces as returned by synchronise method.
    @returns: DOT compliant string to generate the given tree of traces.
    """
    dot = "digraph trace {\n\n";
    dot += "    node[label=\"\",shape=circle];\n\n"; # Nodes without labels
    states = set();
    transitions = set();
    for trace in traces:
        previous_state = None;
        step_index = -1;
        trace_length = len(trace);
        for step in trace:
            step_index += 1;
            id,label = _statesToDotState(step[0]);
            transition = step[1];
            if id not in states:
                # Nodes with labels
                #dot += "    {0!s}[label=\"{1!s}\"".format(id,label);
                dot += "    {0!s}[".format(id);
                if step[2]: # The state is globally final
                    dot += "style=filled,fillcolor=green";
                elif step_index >= trace_length -1:
                    # The system finish here and it's not final :-(
                    dot += "shape=doublecircle,color=red";
                dot += "]; // {0!s}\n".format(step[0]);
                states.add(id);
            if (previous_state is not None) and \
               (transition is not None) and \
               ((previous_state,transition,id) not in transitions):
                dot += "    {0!s} -> {1!s} [label=\"{2!s}\"];\n".format(
                   previous_state,id,transition);
                transitions.add((previous_state,transition,id));
            previous_state = str(id);
    dot += "\n}";
    return dot;


def _statesToDotState(states):
    """ Returns a couple with an id and label for the given states.

    @param states: Current states as those in synchronise method.
    @return: Couple with the id and label for the DOT node.
    @rtype: (node_id, node_label)
    """
    node =  "({0})".format(", ".join([str(state) for state in states]));
    return (hash(node),node);


def is_same_accepted_word(traceA, traceB):
    """Returns True if the two given traces correspond (and accept) the same trace.

    @param traceA: A trace.
    @param traceB: Another trace.
    @returns: True iff the two traces correspond (and accept) the same trace.
    """
    indexB = 0;
    finalA, finalB = False, False;
    if len(traceA) != 0:
        finalA = traceA[0][2] 
    if len(traceB) != 0:
        finalB = traceB[0][2];
    for indexA in range(0,len(traceA)):
        if traceA[indexA][1] == "TAU":
            finalA = finalA or traceA[indexA][2];
            continue;
        while indexB < len(traceB) and \
                traceB[indexB][1] == "TAU":
            finalB = finalB or traceB[indexB][2];
            indexB += 1;
        if finalA is not finalB or \
                indexB >= len(traceB) or \
                traceA[indexA][1:2] != traceB[indexB][1:2]:
            return False
        indexB += 1;
    return True;


def is_sub_language(result, expected):
    """Verifies whether the first set of traces accept the same words
    as the second set.
    
    It returns None if the first language is a sublanguage of the second
    or a counter example otherwise. In the latter case, the counter example is
    a ("missing",trace) if the trace was expected but not in the given result.

    If there is any, it only returns ONE counter example. Others might exist.

    @param result: The obtained set of traces.
    @param expected: The expected set of traces.
    @returns: None if it is the same language or a counterexample if it is not.
    """
    unexpected = result - expected;
    for uTrace in sorted(unexpected, lambda x, y: len(x) - len(y)):
        ok_to_go = False;
        for eTrace in expected:
            if is_same_accepted_word(uTrace,eTrace):
                ok_to_go = True;
                break;
        if not ok_to_go:
            return ("unexpected",uTrace);
    return None;


def is_same_accepted_language(result, expected):
    """Verifies whether the given two set of traces generate (and accept)
    the same language.

    It returns None if the two languages are the same or a counter example
    otherwise. In the latter case, the counter example is either
    ("unexpected",trace) if the trace was in result but not in expected, or
    ("missing",trace) if the trace was expected but not in the given result.

    If there is any, it only returns ONE counter example. Others might exist.

    @param result: The obtained set of traces.
    @param expected: The expected set of traces.
    @returns: None if it is the same language or a counterexample if it is not.
    """
    # @TODO: This shuld be equal to is_sub_language(A, B) and 
    #           is_sub_language(B, A)
    to_return = is_sub_language(result, expected);
    if to_return:
        return to_return;
    to_return = is_sub_language(expected, result);
    if to_return:
        return ("missing", to_return[1]);
    return None;


def is_reachable_transition(transition, sts, filter=lambda x: True):
    if transition not in sts.getTransitions():
        return False;
    state = sts.getInitial();
    exploring = [state];
    while exploring:
        state = exploring.pop();
        if filter(state):
            outgoing = sts.outgoingTransitions(state);
            if transition in outgoing:
                return True;
            [exploring.append(t.getTarget()) for t in outgoing];
    return False;


def trace_to_string(trace, position=-1):
    if len(trace) == 0:
        return '_';
    else:
        to_return = '';
        previous_step = trace[0];
        for step in trace:
            if step[1] != 'TAU':
                if (position < 0) or \
                        (step[0][position] != previous_step[0][position]):
                    to_return += chr((hash(step[1]) % (122-65))+65);
            if step[2]:
                to_return += ".";
            previous_step = step;
        return to_return;


def trace_to_detailed_string(trace):
        return __cstate_to_string(trace[0])+''.join(\
                (e for t in \
                    (( ' -', step[1],'-> ',__cstate_to_string(step)) for \
                    step in trace[1:])
                for e in t));


def __cstate_to_string(step):
    to_return = '.'.join(step[0]);
    if step[2]:
        return '(('+to_return+'))';
    else:
        return to_return;


def main():
    """
    Performs every possible synchronisation among the given services (in STS)
    and it writes to file the resulting traces (in DOT)
    """
    logging.basicConfig(level=logging.INFO);
    log.info( """ITACA - synchronisation.py  Copyright (C) 2010 José Antonio Martín Baena 
This program comes with ABSOLUTELY NO WARRANTY. This is free software, and 
you are welcome to redistribute it under certain conditions.
""");
    parser = argparse.ArgumentParser(description="Returns all the possible "+
            "traces during the synchronisation among the given services");
    parser.add_argument("services", metavar='S', \
            help="services to synchronise", type=str, nargs="+");
    parser.add_argument('-l','--limit', metavar='L', type=int, default=20, \
            help="depth limit during the synchronisation, default = 20");
    parser.add_argument('-o','--output', metavar='O', \
            type=argparse.FileType('w'), \
            help="where to store the resulting traces");

    args = parser.parse_args();

    for path in args.services:
        if not os.path.exists(path):
            log.error("One of the given services doesn't exist: {}".format( \
                    path));
            sys.exit(3);

    services = [];
    for filename in args.services:
        try:
            services.append(xml2sts.readXML(filename).getSTS());
        except ExpatError, message:
            log.error('One of the given service files '+ \
                      '("%s") could not be parsed: \n\t%s' % (file,message));
            sys.exit(5);

    log.info("Synchronising...");
    syn = Synchroniser(args.limit);
    traces = syn.synchronise(services);

    if args.output:
        log.info("Writing the resulting traces...");
        args.output.write(tracesToDot(traces));




if __name__ == "__main__":
    main();

