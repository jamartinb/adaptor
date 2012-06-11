##
#
# Name:   interface.py - Classes for Component and Service Interfaces.
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


from . import lts, sts
import string

##
# Specifies the name and input and output types of a particular
# operation or method.
class Signature:
    def __init__(self,name):
        self._name=name
        self._input=[]
        self._output=[]
    
    ##
    # Adds an input parameter type to the current signature.
    # @param name Input value identifier.
    def addInput(self,name):
        self._input.append(name)
    
    ##
    # Adds an output parameter type to the current signature.
    # @param name Output value identifier.
    def addOutput(self,name):
        self._output.append(name)
    
    ##
    # Returns the list of input parameter types from the current signature.
    # @return List of input parameter types for the current signature.
    # @defreturn List of strings.
    def getInputs(self):
        return self._input
    
    ##
    # Returns the list of output parameter types from the current signature.
    # @return List of output parameter types for the current signature.
    # @defreturn List of strings.
    def getOutputs(self):
        return self._output

    ##
    # Returns the name of the method or operation for current signature.
    def getName(self):
        return self._name
    
    
    ##
    # Returns the name of the method or operation for current signature.
    # @param name The new name for the operation or method.
    def setName(self,name):
        self._name=name

##
# Contains the interface description comprising both signature and protocol 
# of a component/service.
class Interface:
    def __init__(self,name,mysignature=None,mysts=None):
        self._name=name
        if mysignature!=None:
            self._signature=mysignature
        else:
            self._signature={}
        
        if mysts!=None:
            self._STS=mysts
        else:
            self._STS=sts.STS()
    
    ##
    # Returns true if object is a composite
    # @defreturn boolean
    def isComposite(self):
        return False
    
    ##
    # Sets the name of the interface.
    # @param name Interface name.
    def setName(self,name):
        self._name=name
    
    ##
    # Returns the interface name.
    # @return Interface name.
    # @defreturn String.
    def getName(self):
        return self._name
    
    ##
    # Returns all the signatures contained on the interface.
    # @return List of method/operation signatures on the current interface.
    # @defreturn Dictionary of Signature objects.
    def getSignatures(self):
        return self._signature
    
    ##
    # Sets the signature for the current interface.
    # @param signature Signature dictionary to substitute the current signatures.
    def setSignatures(self,signatures):
        self._signature=signatures
    
    ##
    # Adds a signature to the current interface. The signature is not added if
    # there is already one available identified by the same name.
    # @param signature Signature object to be added.
    def addSignature(self,signature):
        if self.getSignature(signature.getName())==None:
            self._signature[signature.getName()]=signature
    
    ##
    # Returns the signature for a given key.
    # @param key Key identifying the signature (method/operation name).
    # @return Signature identified by the key (None if not found).
    # @defreturn Signature object.
    def getSignature(self,key):
        for signatureKey in self._signature.keys():
            if signatureKey==key:
                return self._signature[key]
        return None
    
    ##
    # Returns the message or signature name related to the label passed.
    # @param id Label id.
    # @defreturn String.
    def mapLabelToMessage(self,id):
        #return self.getSTS().getLabel(id).getName()
        for mySigk in self._signature.keys():
            mySig=self.getSignature(mySigk)
            if string.upper(mySig.getName())==string.upper(self.getSTS().getLabel(id).getName()):
                return mySig.getName()
    
    ##
    # Sets the current interface's STS.
    # @param sts New STS object.
    def setSTS(self,sts):
        self._STS=sts
    
    ##
    # Returns the current interface's STS.
    # @return current interface STS object.
    # @defreturn STS object.
    def getSTS(self):
        return self._STS
    