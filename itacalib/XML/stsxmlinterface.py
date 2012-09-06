##
#
# Name:   stsxmlinterface.py - Functions for STS XML interface manipulation.
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
import itacalib.GL as igl
#from ..GL import shape

##
# Imports STS XML interfaces.
# @param filename Name of the input XML file.
# @return An Interface object containing all the information encoded on the
#         XML file.
# @defreturn Interface object.
def readXML(filename,shapeinfo=None):
    mydom = parse(filename)
    [base,ext]=os.path.splitext(os.path.basename(filename))
    myinterface=interface.Interface(base)
    
     # Shape info...
    if shapeinfo!=None:
        interfaceroot = mydom.getElementsByTagName("interface")[0]
        if interfaceroot.getAttribute("width") and interfaceroot.getAttribute("height"):
            shapeinfo.setSize(int(interfaceroot.getAttribute("width")),int(interfaceroot.getAttribute("height")))
        if interfaceroot.getAttribute("ports"):
            portsPos=igl.LEFT
            if interfaceroot.getAttribute("ports")=="right":
                portsPos=igl.RIGHT
            elif interfaceroot.getAttribute("ports")=="left":
                portsPos=igl.LEFT
            shapeinfo.setPortsPosition(portsPos)
        if interfaceroot.getAttribute("portorder"):
            if interfaceroot.getAttribute("portorder")=="true":
                shapeinfo.setPortsOrdered(True)
        
    processSignatures(mydom,myinterface)
    myinterface.setSTS(processInterfaceProtocol(mydom,shapeinfo))
    return myinterface

def processSignatures(mydoc, component):
    signatureElements = mydoc.getElementsByTagName("signature")
    for signatureElement in signatureElements:
        component.addSignature(processSignature(signatureElement,component))       

def processSignature(mydoc,component):
    signatureName=mydoc.getAttribute("name")  
    mysignature=interface.Signature(signatureName)
    
    sigInputs = mydoc.getElementsByTagName("inputs")
    signatureInputs=[]
    if len(sigInputs):
        signatureInputs= sigInputs[0].getElementsByTagName("dataItem")
    for input in signatureInputs:
        mysignature.addInput(input.getAttribute("name"))
    
    
    sigOutputs = mydoc.getElementsByTagName("outputs")
    signatureOutputs=[]
    if len(sigOutputs):
        signatureOutputs= sigOutputs[0].getElementsByTagName("dataItem")
    for output in signatureOutputs:
        mysignature.addOutput(output.getAttribute("name"))
    
    return mysignature

def processLabels(mydoc,mysts,shapeinfo=None):
    labels = mydoc.getElementsByTagName("label")
    for label in labels:
        mysts.addLabelById(processLabel(label,shapeinfo))       

def processLabel(mydoc,shapeinfo=None):
    labelName=mydoc.getAttribute("name")  
    labelType=mydoc.getAttribute("type") 
    labelId=mydoc.getAttribute("id") 
    
    if shapeinfo!=None and mydoc.getAttribute("ord"):
        shapeinfo.setPortOrder(labelId,int(mydoc.getAttribute("ord")))  

    
    labelData = mydoc.getElementsByTagName("dataItem")
    mydata=[]
    for dataItem in labelData:
        mydata.append(dataItem.getAttribute("name"))
    
    label=None
    if labelType=="IN":
        label=sts.DataInputLabel(labelName,mydata,labelId)
    elif labelType=="OUT":
        label=sts.DataOutputLabel(labelName,mydata,labelId)
        
    return label


def processInterfaceProtocol(mydoc,shapeinfo=None):
    
    states=mydoc.getElementsByTagName("state")
    mysts=sts.STS()
    
    processLabels(mydoc,mysts,shapeinfo)
    
    for state in states:
        objState=lts.State(state.getAttribute("id"))
        
        # Shape info...
        if shapeinfo!=None:
            if state.getAttribute("x") and state.getAttribute("y"):
                shapeinfo.addState(state.getAttribute("id"),int(state.getAttribute("x")),int(state.getAttribute("y")))
        
        if state.getAttribute("initial")=="True":
            objState.setInitial(True)
            mysts.setInitial(objState.getName())
        if state.getAttribute("final")=="True":
            objState.setFinal(True)
            mysts.addFinal(objState.getName())
            
        mysts.addState(objState)
            
    transitions=mydoc.getElementsByTagName("transition")
    for tran in transitions:
        
        
        # Shape info...
        if shapeinfo!=None:
            if tran.getAttribute("x") and tran.getAttribute("y"):
                shapeinfo.addTransition(tran.getAttribute("source"),tran.getAttribute("label"),tran.getAttribute("target"),int(tran.getAttribute("x")),int(tran.getAttribute("y")))
        
        source=tran.getAttribute("source")
        label=tran.getAttribute("label")
        target=tran.getAttribute("target")
        
        mysts.addTransition(lts.Transition(source,label,target))
       
    return mysts


##
# Exports STS XML interfaces.
# @param filename Name of the output XML file.
# @param myinterface An Interface object.
def writeXML(filename, myinterface, myshape=None):
    doc = Document()
    _interface2XML(doc,myinterface,myshape)
    file_object = open(filename, "w")
    file_object.write(doc.toprettyxml())
    file_object.close()

# Processes a data list generating <dataItem> Output tags.
# @param doc DOM document object.
# @param data List of data items (string list)
# @param tag Tag string used as list header (e.g. "inputs", etc.)
# @return DOM node object containing the list of data items.
def _processDataInTag(doc, data, tag):
    xmlnode = doc.createElement(tag)
    _processData(doc,xmlnode,data)
    return xmlnode

def _processData (doc,parent,data):
    for dataItemObject in data:
        dataItem=doc.createElement("dataItem")
        _setAttribute(doc,dataItem,"name",dataItemObject)
        parent.appendChild(dataItem)
    

# Sets an attribute for a particular node.
# @param doc DOM document object.
# @param node DOM node object to attach the attribute.
# @param attrname The attribute's name.
# @param attrvalue Attribute value.
def _setAttribute(doc,node,attrname,attrvalue):
    myAttr=doc.createAttribute(attrname)
    myAttr.value=attrvalue
    node.setAttributeNode(myAttr)
    

def _interface2XML(doc, myinterface, myshape=None):
    
    # We create the root element tag "interface"
    interfaceroot = doc.createElement("interface")
    if myshape!=None:
        _setAttribute(doc,interfaceroot,"width",str(myshape.getSize()[0]))
        _setAttribute(doc,interfaceroot,"height",str(myshape.getSize()[1]))
    
    # "signatures" tag element creation
    signatures = doc.createElement("signatures")
    # First we process the vector section
    for signatureKey in myinterface.getSignatures().keys():
        objSignature=myinterface.getSignature(signatureKey)
        signature=doc.createElement("signature")
        _setAttribute(doc,signature,"name",objSignature.getName())
        
        # Process each of the data input items for the signature
        if len(objSignature.getInputs()):
            signature.appendChild( _processDataInTag(doc, objSignature.getInputs(), "inputs"))
        
        # Process each of the data output items for the signature
        if len(objSignature.getOutputs()):
            signature.appendChild( _processDataInTag(doc, objSignature.getOutputs(), "outputs"))
           
        signatures.appendChild(signature)
    interfaceroot.appendChild(signatures)
    
    #Protocol processing
    protocol = doc.createElement("protocol")
    labels = doc.createElement("labels")
    
    for labelKey in myinterface.getSTS().getLabels().keys():
        objLabel=myinterface.getSTS().getLabel(labelKey)
        label=doc.createElement("label")
        
        _setAttribute(doc,label,"id",objLabel.getId())
        _setAttribute(doc,label,"name",objLabel.getName())
        _setAttribute(doc,label,"type",objLabel.getType())
        if isinstance(objLabel, sts.DataInputLabel) or \
                isinstance(objLabel, sts.DataOutputLabel):
            _processData(doc,label,objLabel.getData())
        
        labels.appendChild(label)
    protocol.appendChild(labels)
    
    # States
    states = doc.createElement("states")
    for stateKey in myinterface.getSTS().getStates().keys():
        objState=myinterface.getSTS().getState(stateKey)
        state=doc.createElement("state")
        _setAttribute(doc,state,"id",objState.getName())
        # Shape handling issues...
        if myshape!=None:
            shpState=myshape.getChild(objState.getName(),igl.STATE_SHAPE)
            _setAttribute(doc,state,"x",str(shpState.getPos()[0]-myshape.getPos()[0]))
            _setAttribute(doc,state,"y",str(shpState.getPos()[1]-myshape.getPos()[1]))
            
        if objState.isInitial():
            _setAttribute(doc,state,"initial","True")
        if objState.isFinal():
            _setAttribute(doc,state,"final","True")
        states.appendChild(state)
    protocol.appendChild(states)
    
    # Transitions
    transitions = doc.createElement("transitions")
    for objTransition in myinterface.getSTS().getTransitions():
        transition=doc.createElement("transition")
        
        # Shape handling issues...
        if myshape!=None:
            shpTransition=myshape.getLinksBetween(myshape.getChild(objTransition.getSource(),igl.STATE_SHAPE),myshape.getChild(objTransition.getTarget(),igl.STATE_SHAPE),objTransition.getLabel())[0]
            if objTransition.getSource()!=objTransition.getTarget():
                _setAttribute(doc,transition,"x",str(shpTransition.getHandle(0)[0]-myshape.getPos()[0]))
                _setAttribute(doc,transition,"y",str(shpTransition.getHandle(0)[1]-myshape.getPos()[1]))
        
        _setAttribute(doc,transition,"source",objTransition.getSource())
        _setAttribute(doc,transition,"label",objTransition.getLabel())
        _setAttribute(doc,transition,"target",objTransition.getTarget())
        transitions.appendChild(transition)
    protocol.appendChild(transitions)
    
    interfaceroot.appendChild(protocol)
    doc.appendChild(interfaceroot)

