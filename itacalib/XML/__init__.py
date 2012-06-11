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

__all__ = ["adaptor", "stsxml", "stsxmlinterface", "bpelparser", "aldebaran", "importmodel", "wfparser", "utils", "adaptorinterface", "exceptions","fsp","dot","compositexml","wsdlparser"]

# File format types
UNDEFINED, STS_CONTRACT_XML, STS_INTERFACE_XML, ADAPTOR_CONTRACT_XML, ADAPTOR_INTERFACE_AUT, ADAPTOR_INTERFACE_XML, ADAPTOR_OLD = range(7)

# String identifiers for file format types 
_TYPE_STRING={UNDEFINED:"Undefined",STS_CONTRACT_XML:"STS XML Contract",STS_INTERFACE_XML:"STS XML Interface",ADAPTOR_CONTRACT_XML:"Adaptor XML Mapping",ADAPTOR_INTERFACE_AUT:"Adaptor Aldebaran Interface",ADAPTOR_INTERFACE_XML:"Adaptor XML Interface", ADAPTOR_OLD:"Adaptor legacy notation"}