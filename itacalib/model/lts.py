##
#
# Name:   lts.py - Classes for LTS manipulation.
# Author: Javier Camara(extended by Gwen Sala\"un).
# Date:   10-2-2008
##
################################################################################
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


from copy import copy; # For copying STS with states.

##
# Abstract label class. Should not be directly used. Use child classes instead.
class Label(object):
    def __init__(self):
        self._type=None
        self._id = None
    
    ##
    # Returns the label type code: TAU|IN|OUT. Handy for XML processing etc.
    # @defreturn Boolean.
    def getType(self):
        return self._type
             
    ##
    # Returns True if label is TAU.
    # @defreturn Boolean.
    def isTau(self):
        return False

    ##
    # Returns True if label is input.
    # @defreturn Boolean.
    def isInput(self):
        return False

    ##
    # Returns True if label is output.
    # @defreturn Boolean.
    def isOutput(self):
        return False

    ##
    # Returns whether the label is equal or not
    # @defreturn Boolean.
    def __eq__(self,label):
        return isinstance(label,Label) and \
                (label.getType() == self.getType());

    ##
    # Returns the hashvalue of this label
    # @defreturn integer.
    def __hash__(self):
        to_return = hash(self.getType());
        if self.isInput(): to_return ^= 110;
        if self.isOutput(): to_return ^= 1001;
        if self.isTau(): to_return ^= 10101;
        return to_return;

    ##
    # Returns the (optional) id of this label
    # @defreturn str.
    def getId(self):
        return self._id;

    ##
    # Sets the (optional) id of this label
    def setId(self,id):
        self._id = id;


##
# TAU unnamed Label
class TLabel(Label):
    def __init__(self):
        Label.__init__(self)
        self._type="TAU"

    ##
    # Returns True if label is TAU.
    # @defreturn Boolean.
    def isTau(self):
        return True
    
    ##
    # Returns the object's representation as a string.
    # @defreturn String.
    def __str__(self):
        return self._type

##
# Named label class. A message or String.
# Should not be directly instantiated. Use child classes instead (except for simple
# label transitions - e.g. used for vector Id's in contracts).
class NLabel(Label):
    def __init__(self,name):
        Label.__init__(self)
        self.setName(name);

    def cmp(self, other):
        return (self.name == other.name)
    
    ##
    # Returns label name.
    # @return Label name.
    # @defreturn String.
    def getName(self):
        return self._name
    
    ##
    # Set label name.
    # @param name Label name.
    def setName(self,name):
        self._name=name
        self.setId(name);
    
    ##
    # Returns the object's representation as a string.
    # @defreturn String.
    def __str__(self):
        if self._type=="IN": typestr="REC"
        elif self._type=="OUT": typestr="EM"
        else: typestr="UNK"
        return self._name+'_'+typestr

    ##
    # Returns wether this label is equal to another
    # @defreturn Boolean.
    def __eq__(self,label):
        return isinstance(label,NLabel) and \
                (self.getName() == label.getName()) and \
                (super(NLabel,self) == label);

    ##
    # Returns the hash value of this sabel
    # @defreturn integer.
    def __hash__(self):
        return super(NLabel,self).__hash__() ^ hash(self.getName());


##
# Input Label -> a message + direction (?)
class InputLabel(NLabel):
    def __init__(self,name):
        NLabel.__init__(self,name)
        self._type="IN"
        # This following line is yet to be tested
        self.setId(name+"_REC");

    ##
    # Returns True if label is Input.
    # @defreturn Boolean.
    def isInput(self):
        return True

##
# Output Label -> a message + direction (!)
class OutputLabel(NLabel):
    def __init__(self,name):
        NLabel.__init__(self,name)
        self._type="OUT"
        # This following line is yet to be tested
        self.setId(name+"_EM");
        
    ##
    # Returns True if label is output.
    # @defreturn Boolean.
    def isOutput(self):
        return True

##    
# State class -> name + [initial][final]       
class State:
    def __init__(self,name,initial=False,final=False):
        self._name=name
        self._final=final
        self._initial=initial
    
    ##
    # Returns True if state is final.
    # @defreturn Boolean.
    def isFinal(self):
        return self._final
    
    ##
    # Sets the state final value.
    # @param value Boolean.
    def setFinal(self,value):
        self._final=value
    
    ##
    # Returns True if state is initial.
    # @defreturn Boolean.
    def isInitial(self):
        return self._initial
    
    ##
    # Sets the state initial value.
    # @param value Boolean.
    def setInitial(self,value):
        self._initial=value
    
    ##
    # Sets the state's name.
    # @param name String indicating the new name.
    def setName(self,name):
        self._name=name
    
    ##
    # Returns state's name.
    # @return State name.
    # @defreturn String.
    def getName(self):
        return self._name

##
# Transition class -> source state + label + target state.
class Transition(object):
    def __init__(self,src,label,tgt):
        self._src=src
        self._tgt=tgt
        self._label=label
    
    ##
    # Returns the transition's source state.
    # @return source state name.
    # @defreturn String.
    def getSource(self):
        return self._src
    
    ##
    # Returns the transition's target state.
    # @return target state name.
    # @defreturn String.
    def getTarget(self):
        return self._tgt
    
    ##
    # Returns the transition's label.
    # @return transition label name.
    # @defreturn String.
    def getLabel(self):
        return self._label
    
    ##
    # Sets the transition's label.
    # @return transition label name.
    # @defreturn String.
    def setLabel(self,label):
        self._label=label
    
    ##
    # Returns True if transition is TAU.
    # @defreturn Boolean.
    def isTau(self):
        # @todo: WTF! Why you use a string as a label instead of all the elaborated label classes??? [jamartin]
        if self._label.upper()=="TAU": return True
        else: return False

    ##
    # Returns wether this transition is equal to another
    # @return: Equallity
    # @defreturn Boolean.
    def __eq__(self,transition):
        return isinstance(transition,Transition) and \
                (hash(transition) == hash(self));

    ##
    # Returns the hash value of this transition
    # @return: Transition's hash value
    # @defreturn int
    def __hash__(self):
        ## I changed the following line for the one bellow for efficiency reasons
        #return hash(self.getLabel()) ^ hash(self.getSource()) ^ hash(self.getTarget());
        return hash((self._label, self._src, self._tgt));


    def isInput(self):
        return self._label.upper().endswith("_REC");
    

    def isOutput(self):
        return self._label.upper().endswith("_EM");


    def getReducedLabel(self):
        if self.isInput():
            return self.getLabel()[:-4];
        elif self.isOutput():
            return self.getLabel()[:-3];
        else:
            return self.getLabel();
    

    ##
    # Represents transitions as strings
    # @return: A string representing the transition
    def __str__(self):
        direction = "";
        if self.isInput():
            direction = "?";
        elif self.isOutput():
            direction = "!";
        return "({!r} --{}{}--> {!r})".format(\
                self.getSource(),direction,self.getReducedLabel(),self.getTarget());


    ##
    # Returns a parseable representation of the transition, currently the same as str
    # @return: A parseable representation of the transition
    # @defreturn str
    def __repr__(self):
        return str(self);


##
# Generic LTS class. 
class LTS:

    def __init__(self):
        self._S = {}
        self._I = None
        self._F = []
        self._A = {}
        self._transitions = {};
        self._incoming = {};


    ##
    # Sets the initial state for the LTS.
    # @param name Name of the new initial state.
    def setInitial(self,name):
        self._I=name
        
    ##
    # Returns the initial state of the LTS.
    # @return name of the initial state for the LTS.
    # @defreturn String.
    def getInitial(self):
        return self._I
    
    ##
    # Adds a new state to the LTS.
    # @param state The State object to be added.
    def addState(self, state):
        self._S[state.getName()]=state
    
    ##
    # Adds a new transition to the LTS.
    # @param transition The Transition object to be added.
    def addTransition(self,transition):
        self._transitions.setdefault(transition.getSource(),list()).append(transition);
        self._incoming.setdefault(transition.getTarget(),list()).append(transition);
    
    
    ##
    # Removes a state from an LTS given a state identifier
    # @param name Name of the state s.
    def removeState(self,name):
        if name in self._S:
            # If s is set as initial, remove it.
            if name==self._I:
                self._I=None
            # If final, remove it from finals...
            if name in self._F:
                self.removeFinal(name)
            # Removing transitions containing s
            for t in self.outgoingTransitions(name):
                self.removeTransition(t);
            for t in self.incomingTransitions(name):
                self.removeTransition(t);
            # Remove state s
            del self._S[name];


    ##
    # Removes a state from an LTS given a state indentifier
    # Connected transitions remain untouched.
    def removeStateOnly(self,name):
        del self._S[name];
    
    
    ##
    # Removes a single transition from the LTS.
    # @param transition The Transition object to be removed.
    def removeTransition(self,transition):
        outgoing_transitions = self._transitions[transition.getSource()];
        incoming_transitions = self._incoming[transition.getTarget()];
        outgoing_transitions.remove(transition);
        incoming_transitions.remove(transition);
        # If there are multiple ocurrences of the same transition 
        #  between the same two states then only one is removed.
    

    ##
    # Returns the transitions from the LTS.
    # Returned transitions are not backed-up by the LTS instance.
    # @return The list of transitions for the LTS.
    # @defreturn Transition object list.
    def getTransitions(self):
        return [t for l in self._transitions.itervalues() for t in l];
    
    ##
    # Adds a new label to the LTS alphabet.
    # @param label The new label object.
    def addLabel(self,label):
        # @todo: Should it be getName or getId?
        self._A[label.getName()]=label
    
    ##
    # Removes a label from the LTS alphabet.
    # @param label The new label object.
    def removeLabel(self,label):
        newA={}
        for k in self._A.keys():
            if (label.getName()==k):
                pass
            else:
                newA[k]=self._A[k]
        self._A=newA
    
    ##
    # Returns a label from the LTS.
    # @param name The name of the label to be retrieved.
    # @return The label identified by name.
    # @defreturn Label object.
    def getLabel(self,name):
        return self._A[name] 
    
    ##
    # Returns a state from the LTS.
    # @param name The name of the state to be retrieved.
    # @return The state identified by name.
    # @defreturn State object.
    def getState(self,name):
        return self._S[name];
    
    ##
    # Returns the set of states from the LTS.
    # @return The set of states from the LTS.
    # @defreturn State object dictionary.
    def getStates(self):
        return self._S

    ##
    # Adds a final state to the LTS.
    # @param name The name of the final state.
    def addFinal(self,name):
        self._F.append(name)
    
    
    ##
    # Removes a final state from the LTS.
    # @param name The name of the final state.
    def removeFinal(self,name):
        newF=[]
        for s in self._F:
            if s!=name:
                newF.append(s)
        self._F=newF
    
    
    ##
    # Returns the set of labels from the LTS.
    # @return The set of labels from the LTS.
    # @defreturn Label object dictionary.
    def getLabels(self):
        return self._A
    
    ##
    # Sets the set of labels for the lts.
    # @param dic The new set of labels (Label object dictionary).
    def setLabels(self,dic):
       self._A=dic 
    
    ##
    # Sets the set of final states for the lts.
    # @param list The new set of states (String list).
    def setFinals(self,list):
       self._F=list
    
    ##
    # Sets the set of states for the lts.
    # @param dic The new set of states for the lts (State object dictionary).
    def setStates(self,dic):
       self._S=dic

    ##
    # Sets the set of transitions for the lts.
    # @param list List of Transition object. 
    def setTransitions(self,list):
       self._transitions.clear();
       self._incoming.clear();
       map(self.addTransition,list);
    
    ##
    # Returns the set of final states for the lts.
    # @return Set of final states (names) for the lts.
    # @defreturn String list.
    def getFinals(self):
      return self._F 
    
    ##
    # Return the list of outgoing transitions from an LTS
    # given a state identifier.
    # @param name Name of the state.
    # @param avoidlooping Boolean if True, method will not return looping transitions.
    # @return List of outgoing transitions from the state identified by name.
    # @defreturn List of Transition object.
    def outgoingTransitions(self,name,avoidlooping=False):
        res= self._transitions.get(name);
        if res is None:
            return [];
        elif avoidlooping:
            return [t for t in res if t.getSource() != t.getTarget()];
        else:
            return res;
    
    ##
    # Return the list of incoming transitions from an LTS
    # given a state identifier
    # @param name Name of the state.
    # @param avoidlooping Boolean if True, method will not return looping transitions.
    # @return List of incoming transitions from the state identified by name.
    # @defreturn List of Transition object.
    def incomingTransitions(self,name,avoidlooping=False):
        res= self._incoming.get(name);
        if res is None:
            return [];
        elif avoidlooping:
            return [t for t in res if t.getSource() != t.getTarget()];
        else:
            return res;
    
    ##
    # Determines the set of states reachable through TAU transitions from a 
    # specific state s.
    # @param sid State identifier
    # @return set of state ids
    # @defreturn string list
    def reachableStatesTAU(self,sid):
        result=[]
        for tran in self.getTransitions():
            if tran.getSource()==sid and tran.getLabel()=='TAU':
                if tran.getTarget() not in result: result.append(tran.getTarget())
        return result
    
    ##
    # Return the list of transitions from an LTS
    # given a state identifier, looping on that state
    # @param name Name of the state.
    # @return List of transitions looping on the state identified by name.
    # @defreturn List of Transition object.
    def loopingTransitions(self,name):
        res=[]
        for t in self.getTransitions():
            if t.getTarget()==name and t.getSource()==name:
                res.append(t)
        return res 

    
    ##
    # Removes transitions labelled in a specific way on an LTS
    # @param label string indicating the transitions to be removed.
    def removeTransitions(self, label):
        raise Exception('Function LTS.removeTransitions is not implemented!');
    
    ##
    # It copies the LTS instance, its states, transitions and labels.
    # However, it's not a deep copy so any deeper modification will
    # apply both to the copy and the original at the same time.
    #
    # @return: A copy of the LTS. 
    def copy(self):
        # Copy the instance.
        toReturn = copy(self);
        # Copy the states.
        states = {};
        for state in self.getStates():
            states[state] = copy(self.getState(state));
        toReturn.setStates(states);
        # Copy the transitions.
        toReturn.setTransitions(map(lambda x: copy(x), self.getTransitions()));
        # Copy the list of finals.
        # Initial doesn't need to be copied because it's just a string.
        toReturn.setFinals(copy(toReturn.getFinals()));
        # Copy the labels.
        toReturn.setLabels(self._copyLabels());
        return toReturn;
    
    ##
    # It copies the dictionary of labels.
    #
    # @return: A copy of the dictionary of labels.
    def _copyLabels(self):
        labels = {};
        for label in self.getLabels().values():
            labels[label.getName()] = copy(label);
        return labels;
    
##
# Computes the free product of two LTSs
# @param a,b LTS objects
# @defreturn LTS object
def product(a,b):
    prod=LTS()
    # We add all the labels in both LTSs
    for lak in a.getLabels().keys():
        prod.addLabel(a.getLabel(lak))
    for lbk in b.getLabels().keys():
        prod.addLabel(b.getLabel(lbk))
    # Main loop for the product
    for sa in a.getStates().keys():
        for sb in b.getStates().keys():
            # We add states...
            initial=False
            final=False
            if a.getState(sa).isInitial() and b.getState(sb).isInitial(): initial=True
            if a.getState(sa).isFinal() and b.getState(sb).isFinal(): final=True
            labelsab='-'+sa+'-'+sb+'-'
            sab=State(labelsab,initial,final)
            prod.addState(sab)
            # Setting initial and finals...
            if initial: prod.setInitial(sab.getName())
            if final: prod.addFinal(sab.getName())
            # Now for the transitions...
            for ta in a.outgoingTransitions(sa):
                prod.addTransition(labelsab,ta.getLabel(),'-'+ta.getTarget()+'-'+sb+'-')
            for tb in b.outgoingTransitions(sb):
                prod.addTransition(labelsab,tb.getLabel(),'-'+sa+'-'+tb.getTarget()+'-')
    return prod
