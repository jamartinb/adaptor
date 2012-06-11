##
#
# Name:   stsxml.py - Functions for STS XML manipulation.
# Author: Javier Camara.
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


from xml.dom.minidom import parse, parseString, Document, DocumentType
import string
import os
from os.path import *
from ..model import lts, sts, interface, contract

##
# Imports STS XML contracts.
# @param filename Name of the input XML file.
# @return A Contract object containing all the information encoded on the
#         XML file.
# @defreturn Contract object.
def readXML(filename):
    mydom = parse(filename)
    [base,ext]=os.path.splitext(os.path.basename(filename))
    mycontract=contract.Contract(base)
    _processDefs(mydom,mycontract) # Synth arg definitions
    _processVectors(mydom,mycontract)
    mycontract.setLTS(_processLTS(mydom,mycontract))
    return mycontract
    
    
def _processDefs(mydoc, mycontract):
    defs = mydoc.getElementsByTagName("definition")
    for definition in defs:
        mycontract.addDef(_processDef(definition))


def _processDef(mydoc):
     placeholder = mydoc.getAttribute("name")
     mydef=contract.SArgument(placeholder)
     
     inputArgs=mydoc.getElementsByTagName("input")
     for inputArg in inputArgs:
         mydef.addInput(inputArg.getAttribute("name"))
     
     func=mydoc.getElementsByTagName("function")
     mydef.setPredicate(func[0].getAttribute("predicate"))
     return mydef

def _processVectors(mydoc, mycontract):
    vectors = mydoc.getElementsByTagName("vector")
    for vector in vectors:
        mycontract.addVector(_processVector(vector))
        

def _processVector(mydoc):
     idvector = mydoc.getAttribute("id")
     myvector=contract.Vector(idvector)
     # Observable vector?
     if mydoc.getAttribute("observable"):
         myvector.setObservable(True)
     
     componentVectors=mydoc.getElementsByTagName("componentVector")
     for componentVector in componentVectors:
         _processComponentVector(componentVector,myvector)
     return myvector
 
def _processComponentVector(mydoc,myvector):
    evtIndex=mydoc.getAttribute("index")  
    evtName=mydoc.getAttribute("eventName")  
    evtType=mydoc.getAttribute("eventType")  
    
    messageData = mydoc.getElementsByTagName("dataItem")
    mydata=[]
    for dataItem in messageData:
        mydata.append(dataItem.getAttribute("name"))
    
    if evtType.upper()!="TAU":
        myvector.addElement(contract.VectorElement(evtName,evtType,mydata), evtIndex)
    
def _processLTS(mydoc,mycontract):
    states=mydoc.getElementsByTagName("state")
    mylts=lts.LTS()
    
    for vectorId in mycontract.getVectors().keys():
        mylts.addLabel(lts.NLabel(vectorId))
    
    for state in states:
        objState=lts.State(state.getAttribute("id"))
        if state.getAttribute("initial")=="True":
            objState.setInitial(True)
            mylts.setInitial(objState.getName())
        if state.getAttribute("final")=="True":
            objState.setFinal(True)
            mylts.addFinal(objState.getName())
            
        mylts.addState(objState)
            
        
    transitions=mydoc.getElementsByTagName("transition")
    for tran in transitions:
        source=tran.getAttribute("source")
        label=tran.getAttribute("label")
        target=tran.getAttribute("target")
        mylts.addTransition(lts.Transition(source,label,target))   
    
    return mylts
    
     

##
# Exports STS XML contracts.
# @param filename Name of the output XML file.
# @param mycontract A Contract object.
def writeXML(filename, mycontract):
    doc = Document()
    _contract2XML(doc,mycontract)
    file_object = open(filename, "w")
    file_object.write(doc.toprettyxml())
    file_object.close()


def _contract2XML(doc, mycontract):
    
    # We create the root element tag "contract"
    mappingroot = doc.createElement("contract")
    # "vectors" tag element creation
    vectors = doc.createElement("vectors")
    # First we process the vector section
    for vectorKey in mycontract.getVectors().keys():
        objVector=mycontract.getVector(vectorKey)
        vector=doc.createElement("vector")
        idAttr=doc.createAttribute("id")
        idAttr.value=objVector.getName()
        vector.setAttributeNode(idAttr)
        
        # Open vector?
        if objVector.isObservable():
            obsAttr=doc.createAttribute("observable")
            obsAttr.value="True"
            vector.setAttributeNode(obsAttr)
        
        # Processing each of the vector elements within the vector...
        for elementKey in objVector.getElements().keys():
            objElement=objVector.getElement(elementKey)
            element=doc.createElement("componentVector")
            indexAttr=doc.createAttribute("index")
            indexAttr.value=elementKey
            element.setAttributeNode(indexAttr)
            eventNameAttr=doc.createAttribute("eventName")
            eventNameAttr.value=objElement.getName()
            element.setAttributeNode(eventNameAttr)
            eventTypeAttr=doc.createAttribute("eventType")
            eventTypeAttr.value=objElement.getType()
            element.setAttributeNode(eventTypeAttr)
            
            # Process each of the data items for the vector element
            for dataItemObject in objElement.getData():
                dataItem=doc.createElement("dataItem")
                nameAttr=doc.createAttribute("name")
                nameAttr.value=dataItemObject
                dataItem.setAttributeNode(nameAttr)
                element.appendChild(dataItem)
            
            vector.appendChild(element)
        vectors.appendChild(vector)
    mappingroot.appendChild(vectors)
    
    #STS processing
    LTS = doc.createElement("LTS")
    # States
    states = doc.createElement("states")
    for stateKey in mycontract.getLTS().getStates().keys():
        objState=mycontract.getLTS().getState(stateKey)
        state=doc.createElement("state")
        idAttr=doc.createAttribute("id")
        idAttr.value=objState.getName()
        state.setAttributeNode(idAttr)
        if objState.isInitial():
            initialAttr=doc.createAttribute("initial")
            initialAttr.value="True"
            state.setAttributeNode(initialAttr)
        if objState.isFinal():
            finalAttr=doc.createAttribute("final")
            finalAttr.value="True"
            state.setAttributeNode(finalAttr)
        states.appendChild(state)
    LTS.appendChild(states)
    
    # Transitions
    transitions = doc.createElement("transitions")
    for objTransition in mycontract.getLTS().getTransitions():
        transition=doc.createElement("transition")
        srcAttr=doc.createAttribute("source")
        srcAttr.value=objTransition.getSource()
        transition.setAttributeNode(srcAttr)
        labelAttr=doc.createAttribute("label")
        labelAttr.value=objTransition.getLabel()
        transition.setAttributeNode(labelAttr)
        tgtAttr=doc.createAttribute("target")
        tgtAttr.value=objTransition.getTarget()
        transition.setAttributeNode(tgtAttr)
        transitions.appendChild(transition)
    LTS.appendChild(transitions)
    
    mappingroot.appendChild(LTS)
    doc.appendChild(mappingroot)
