#!/usr/bin/python
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


import pstats;
# For being main
import argparse

def main():
    parser = argparse.ArgumentParser(description="It shows the"+
            " statistics created using adaptor_optimisation_test.");
    parser.add_argument('stats', help="Statistics file");
    parser.add_argument('-c', help="Restriction to show callers");
    parser.add_argument('-e', help="Restriction to show callees");
    parser.add_argument('-r', help="Restrictions");

    args = parser.parse_args();

    p = pstats.Stats(args.stats);
    if args.r:
        p.strip_dirs().print_stats(args.r);
    else:
        p.strip_dirs().sort_stats('cumulative').print_stats(30);
    if args.c:
        p.strip_dirs().print_callers(args.c);
    if args.e:
        p.strip_dirs().print_callees(args.e);

if __name__ == "__main__":
    main();
