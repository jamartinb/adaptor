##
#
# Name:   sts.py - Classes for STS manipulation.
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


from . import lts
from copy import copy

##
# Data input Label -> a message + direction (?) + list of data
class DataInputLabel(lts.InputLabel):
    def __init__(self,name,data,id):
        lts.InputLabel.__init__(self,name)
        self._data=data
        self._id=id
    
    ##
    # Sets the data associated to the label.
    # @param data List of strings identifying the data items.
    def setData(self,data):
        self._data=data

    ##
    # Returns the data associated to the label.
    # @return List of data associated to the label.
    # @defreturn String List.
    def getData(self):
        return self._data
    
    ##
    # Sets a unique Id associated to the label.
    # @param id New id for the label.
    def setId(self,id):
        self._id=id
        
    ##
    # Returns the unique id associated to the label.
    # @return Unique label id.
    # @defreturn String.
    def getId(self):
        return self._id
    
##
# Data output label -> a message + direction (!) + list of data
class DataOutputLabel(lts.OutputLabel):
    def __init__(self,name,data,id):
        lts.OutputLabel.__init__(self,name)
        self._data=data
        self._id=id
    
    ##
    # Sets the data associated to the label.
    # @param data List of strings identifying the data items.    
    def setData(self,data):
        self._data=data
    
    ##
    # Returns the data associated to the label.
    # @return List of data associated to the label.
    # @defreturn String List.
    def getData(self):
        return self._data
 
    ##
    # Sets a unique Id associated to the label.
    # @param id New id for the label.
    def setId(self,id):
        self._id=id
        
    ##
    # Returns the unique id associated to the label.
    # @return Unique label id.
    # @defreturn String.
    def getId(self):
        return self._id

##
# STS Class
class STS(lts.LTS):
    def __init__(self):
        lts.LTS.__init__(self)
    
    ## 
    # Adds a label to the sts alphabet using the id attribute rather than 
    # the name to index the label.
    # @param label Label object to add.
    def addLabelById(self,label):
        if self.getLabelById(label.getId())==None:
            self._A[label.getId()]=label
    
    ##
    # Returns a label from the sts alphabet referenced by id attribute.
    # @param id Label unique id.
    # @return Label referenced by id.
    # @defreturn Label object.
    def getLabelById(self,id):
        for labelKey in self._A.keys():
            if labelKey==id:
                return self._A[id]
        return None
    
    ##
    # It copies the dictionary of labels.
    #
    # @return: A copy of the dictionary of labels.
    def _copyLabels(self):
        labels = {};
        for label in self.getLabels().values():
            labels[label.getId()] = copy(label);
        return labels;