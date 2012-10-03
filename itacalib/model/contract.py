##
#
# Name:   contract.py - Classes for contract.
# Author: Javier Camara.
# Date:   13-2-2008
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


from . import lts
import logging;

## Logger for this module
log = logging.getLogger('contract')

##
# Determines whether a parameter value is persistent (not consumed in the adaptor
# when sent from it.
# @param placeholder (string) placeholder associated to the param value
def isPersistentParameter(placeholder):
    return placeholder[len(placeholder)-1]=='*'

##
# Represents the participation of an interface in a vector
# the type of communication can either be IN,OUT, or TAU
# data is an empty list if no data is sent or received.
# Only one element is contained in the list if we are using just an
# argument (e.g., for name passing CLINT style)
class VectorElement:
    def __init__(self,name,type,data=[]):
        self._name=name
        self._type=type
        self._data=data
        
    def __str__(self):
        return "VElement:"+self._name+" Type:"+self._type+" Data"+str(self._data)
        
    ##
    # Returns the name of the vector element (message name).
    # @return Message name on the vector element.
    # @defreturn String. 
    def getName(self):
        return self._name
    
    ##
    # Sets the name of the vector element (message name).
    # @param name Element's name.
    def setName(self,name):
        self._name=name
    
    ##
    # Returns the type of the vector element (message direction).
    # @return Message type can be either "IN" or "OUT" 
    # (if TAU no element will appear on the vector).
    # @defreturn String. 
    def getType(self):
        return self._type
    
    ##
    # Returns !/? for emissions/receptions, respectively
    def getTypePrint(self):
        if self.getType()=="IN":
            return "?"
        elif self.getType()=="OUT":
            return "!"
        else:
            return "TAU"
    
    ##
    # Returns the label id of an element (eg: msg_EM/msg_REC)
    def getId(self):
        if self.getType()=="IN":
            return self.getName()+"_REC"
        elif self.getType()=="OUT":
            return self.getName()+"_EM"
        else:
            return "TAU"
    
    ##
    # Determines whether the element represents an EMISSION
    def isEmission(self):
        return self.getType()=="OUT"
    
    ##
    # Determines whether the element represents a RECEPTION
    def isReception(self):
        return self.getType()=="IN"
    
    
    ##
    # Returns the list of data items on the vector element.
    # @return List of data items (expressions).
    # @defreturn List of strings.
    def getData(self):
        return self._data
    
    ##
    # Returns whether two elements are equivalent or not.
    # @return Equivalence between elements.
    # @defreturn Boolean.
    def isEquivalent(self,other):
        return (self.getType() == other.getType()) and (self.getName() == other.getName()) and (self.getData() == other.getData());
    
##
# Vector containing a label in name and the different vectorElements in _E
class Vector:
    def __init__(self,name):
        self._name=name
        self._E = {}
        self._obs=False
    
    def __str__(self):
        res="Vector:["+self._name
        for ek in self._E.keys():
            res=res+"Index:"+ek+" "+str(self._E[ek])
        res=res+"]"
        return res
        
    ##
    # Sets the observability of a vector.
    # @param value Boolean
    def setObservable(self,value):
        self._obs=value
    ##
    # Returns the observability of a vector.
    # @defreturn boolean
    def isObservable(self):
        return self._obs
    
    ##
    # Returns true if vector actually binds two operations (excludes
    # vectors used for independent evolution and open vectors).
    # @defreturn boolean
    def isBinding(self):
        return len(self._E.keys())>1
    
    ##
    # Adds an element to the vector.
    # @param element is the vector element object to be added.
    # @index is the name of the interface which corresponds to the element. 
    def addElement(self,element,index):
        self._E[index]=element
    
    ##
    # Removes an element from the vector.
    # @index is the name of the interface which corresponds to the element. 
    def removeElement(self,index):
        elements={}
        for ek in self._E.keys():
            if ek!=index:
                elements[ek]=self._E[ek]
        self._E=elements
    
    
    ##
    # Returns the different elements from the vector.
    # @return all the vector elements contained in the vector. If a particular
    # interface does not participate in the interaction, no element exists in 
    # the vector for that interface.
    # @defreturn Dictionary of VectorElement objects. 
    def getElements(self):
        return self._E
    
    ##
    # Returns the vector element assigned to an interface.
    # @param key Name of the interface to which the element is assigned.
    # @return vector element for interface referenced by key.
    # @defreturn VectorElement object.
    def getElement(self,key):
        return self._E[key]
    
    ##
    # Returns the name of the vector.
    # @return Vector name.
    # @defreturn String. 
    def getName(self):
        return self._name
    
    ##
    # Sets the new name for the vector.
    # @param name string
    def setName(self,name):
        self._name=name
    
    ##
    # Returns whether two vectors are equivalent. Their names don't matter.
    # Don't forget that placeholders should be checked between vectors so, one single 
    # vector cannot be checked for its equivalence. However, same placeholders are
    # assumed.
    #
    # @return The equivalence between two vectors.
    # @defreturn Boolean.
    def isEquivalent(self,other):
        # @todo: Placeholders are not properly supported.
        if set(self.getElements().keys()) != set(other.getElements().keys()):
            return False;
        for key in self.getElements().keys():
            if not self.getElement(key).isEquivalent(other.getElement(key)):
                return False;
        return True;


##
# Definition of synthetic arguments
class SArgument:
    def __init__(self,name):
        self._name=name
        self._inputs=[]
        self._predicate=""
    
    ##
    # Set argument name
    # @param name Argument's name
    def setName(self, name):
        self._name=name
    
    ##
    # Retrieve Arguments's name.
    def getName(self):
        return self._name
    
    ##
    # Adds one of the input arguments required to build the new one
    def addInput(self, name):
        self._inputs.append(name)
    
    ##
    # Removes an input argument
    def removeInput(self, name):
        self._inputs.remove(name)
    
    ##
    # Gets the list of inputs
    # @defreturn string list
    def getInputs(self):
        return self._inputs

    ##
    # Set argument build function
    # @param pred Function def
    def setPredicate(self, pred):
        self._predicate=pred
    
    ##
    # Retrieve Arguments's build function
    def getPredicate(self):
        return self._predicate

    ##
    # String rep
    def __str__(self):
        res="Argument Definition ("+self._name+") - Inputs: "
        for input in self._inputs:
            res=res+" "+input
        res=res+" Function: "+self._predicate
        return res
    
##
# Contains a set of vectors and the dynamics of their application (STS).
class Contract:
    def __init__(self,name):
        self._name=name
        self._defs={}
        self._vectors={}
        self._LTS=lts.LTS()
    
    ##
    # Set contract name.
    # @param name Contract's name.
    def setName(self, name):
        self._name=name
    
    ##
    # Retrieve contract's name.
    def getName(self):
        return self._name
    
    ##
    # Adds an argument definition to the contract
    def addDef(self,definition):
        self._defs[definition.getName()]=definition
        print(str(self._defs[definition.getName()]))
        
    ##
    # Removes an argument definition from the contract.
    # @param key is the key of the def to be removed.
    def removeDef(self,key):
        res={}
        for dk in self._defs.keys():
            if dk != key: res[dk]=self._defs[dk]
        self._defs=res
    
    ##
    # Returns an argument definition from the contract.
    # @param key References the name of the defined parameter.
    # @return SArgument identified by key.
    # @defreturn SArgument object.
    def getDef(self,key):
        return self._defs[key]
    
    ##
    # Returns the list of synth. argument definitions from the contract
    # @defreturn string list (keys in the _defs dictionary)
    def getDefs(self):
        return self._defs.keys()
    
    ##
    # Adds a vector to the contract.
    # @param vector is the Vector object to be added.
    def addVector(self,vector):
        self._vectors[vector.getName()]=vector
    
    ##
    # Returns a vector from the contract.
    # @param key References the name of the vector.
    # @return Vector identified by key.
    # @defreturn Vector object.
    def getVector(self,key):
        return self._vectors[key]
    
    ##
    # Removes a vector from the contract.
    # @param key is the key of the vector to be removed.
    def removeVector(self,key):
        res={}
        for vk in self._vectors.keys():
            if vk != key: res[vk]=self._vectors[vk]
        self._vectors=res
         
    ##
    # Returns the names of the different vectors in the contract.
    # @return List of vector names in the contract.
    # @defreturn List of strings.
    def getVectorKeys(self):
        return self._vectors.keys()
    
    ##
    # Returns the o-vectors in the contract.
    def getOVectors(self):
        res={}
        for vk in self._vectors.keys():
            if self._vectors[vk].isObservable():
                res[vk]=self._vectors[vk]
        return res
    
    ##
    # Returns the tau-vectors in the contract.
    def getTAUVectors(self):
        res={}
        for vk in self._vectors.keys():
            if not self._vectors[vk].isObservable():
                res[vk]=self._vectors[vk]
        return res
    
    ##
    # Returns an open vector name from a port name
    def getOpenVector(self,index,labelId):
        for vk in self.getOVectors().keys():
            v=self._vectors[vk]
            for ek in v.getElements().keys():
                e=v.getElement(ek)
                if ek==index and e.getId()==labelId:
                    return v.getName()
        return None
    
    ##
    # Returns the dictionary of the different vectors in the contract.
    # @return Dictionary of vector objects in the contract.
    # @defreturn Vector object dictionary.
    def getVectors(self):
        # @todo: Intuitively this should return a set or list of vectors, not a dictionary. 
        return self._vectors
    

    ##
    # Sets vectors in the contract.
    # @param vectors Set of vector objects in the contract.
    def setVectors(self,vectors):
        self._vectors=vectors
    

    ##
    # Sets the LTS associated to the contract.
    # @param sts New LTS object for the contract.
    def setLTS(self,lts):
        self._LTS=lts
    
    ##
    # Returns the LTS associated to the contract.
    # @return STS associated to the contract.
    # @defreturn LTS object.
    def getLTS(self):
        return self._LTS
    
    ##
    # Returns whether the contract contains an equivalent vector to the given one.
    # Don't forget that placeholders should be checked between vectors so, one single 
    # vector cannot be checked for its equivalence. However, same placeholders are
    # assumed.
    #
    # @param vector: Vector whose equivalent is going to be searched for within the contract.
    # @return: Whether an equivalent vector is found or not.
    def containsEquivalentVector(self,vector):
        for v in self.getVectors().values():
            if v.isEquivalent(vector):
                if (log.isEnabledFor(logging.DEBUG)):
                    log.debug('Equivalent vector found for %s' % str(vector));
                return True;
        if (log.isEnabledFor(logging.DEBUG)):
            vectors = map(lambda x: str(x), self.getVectors().values());
            log.debug("No equivalent vector for (%s) was found in %s" % (str(vector),str(vectors)));
        return False;
    
    ##
    # Returns whether the contract contains equivalent vectors to the given ones.
    # WARNING: Placeholders are not properly supported, use at your own risk.
    #
    # @param vectors: Vectors whose equivalents are going to be searched for within the contract.
    # @return: Whether an equivalent vector has been found for every of the given ones or not.
    def containsEquivalentVectors(self,vectors):
        # @todo: Placeholders are not properly supported.
        for vector in vectors:
            if not self.containsEquivalentVector(vector):
                return False;
        return True;
        
        
###############################################################################
# Auxiliary functions for contract merge

##
# Merges two different contracts.
# @param a,b the contracts to merge
# @param parent of the parent composite of the rest of the children
# @children list of strings (children interfaces)
# @defreturn contract object
def merge(a,b,parent,children):
    result=Contract("Merge")
    # First we merge the vectors...
    opena={} # Obtaining the set of observable vectors
    for vk in a.getVectors().keys():
        v=a.getVector(vk)
        if v.isObservable(): opena[vk]=v
        else: result.addVector(v)
        
    # Now search for elements on b that match with the previous open elements...
    for vk in b.getVectors().keys():
        v=b.getVector(vk)
        vadded=False
        matche=None
        for ek in v.getElements().keys():
            e=v.getElement(ek)
            for ovk in opena.keys():
                ov=opena[ovk]
                match=None
                matchindex=None
                for oek in ov.getElements().keys():
                    oe=ov.getElement(oek)
                    if e.getName()==oe.getName() and e.getType()==oe.getType() and oek in children and parent==ek:
                        match=e
                        matchek=ek
                        matchindex=oek
                        print("MATCH FOUND!")

                if match!=None:
                    newVector=v
                    newVector.setName(v.getName()+'_'+ov.getName())
                    newVector.removeElement(matchek)
                    newVector.addElement(match,matchindex) 
                    result.addVector(newVector)
                    vadded=True
            if vadded: break  
        if not vadded:
            result.addVector(v)
     
    # Then the VLTSs..
    mylts=lts.LTS()
    
    for vectorId in result.getVectors().keys():
        mylts.addLabel(lts.NLabel(vectorId))
        source="s0"
        label=vectorId
        target="s0"
        mylts.addTransition(lts.Transition(source,label,target))   
    
    objState=lts.State("s0")
    objState.setInitial(True)
    mylts.setInitial(objState.getName())
    objState.setFinal(True)
    mylts.addFinal(objState.getName())
    mylts.addState(objState)
            
    
    result.setLTS(mylts)
    
    
    # return new contract
    return result
