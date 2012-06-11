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

__all__ = ["primitives", "shape", "canvas", "shapeinfo", "text", "handle","connectorshape","compositeshape","ltsdraw"]

# Shape constants

# Shape types
STATE_SHAPE, TRANSITION_SHAPE, COMPONENT_SHAPE, PORT_SHAPE, DATAPORT_SHAPE, CONNECTOR_SHAPE, COMPOSITE_SHAPE = range(7)
# Shape positions
TOP, BOTTOM, LEFT, RIGHT = range(4)
# Port directions
IN, OUT = range(2)

# Primitive constants

# Colors
BLACK=[0.0,0.0,0.0]
WHITE=[1.0,1.0,1.0]
RED=[1.0,0.0,0.0]
GREEN=[0.0,1.0,0.0]
MAGENTA=[1.0,0.0,1.0]
ORANGE=[1.0,0.5,0.25]
BLUE=[0.0,0.0,1.0]
HIGHLIGHT=ORANGE

# Painting directions
LEFT_TO_RIGHT, RIGHT_TO_LEFT = range(2)

# Line patterns
LINE_SOLID=0xFFFF
LINE_DASHED=0xAAAA


# Canvas modes
PAN_MODE,SELECT_MODE,CREATE_NODE_MODE,CREATE_TRANSITION_SOURCE_MODE,CREATE_TRANSITION_TARGET_MODE,CREATE_COMPONENT_MODE,CREATE_INBOUND_PORT_MODE = range(7)