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
# Script to plot an adaptor's stat, or compare vaious of them
#
# Name:   plot_stats.py
# Author: José Antonio Martín Baena
# Date:   07-06-2011
##
########################################################################

import sys;

if sys.hexversion < 0x02070000:
    print "This program (adaptor) only works with python 2.7 or above.";
    sys.exit(7);

import os;
import subprocess;

import argparse;


def main():
    parser = argparse.ArgumentParser(description=("Plots a compasion between"
            " several stastistics"));
    parser.add_argument('stat_files', metavar='F', nargs='+',
            help="the statistic files to compare");
    parser.add_argument("-b", "--base_line", metavar='B', 
            help="the statistics against the others will be compared to");
    parser.add_argument("-m", "--max_success", metavar="S", default=-100,
            type=int, help="the maximum number of successful traces");
    parser.add_argument("-r", metavar="R", type=str,
            help="force a particular range on the graphs");
    parser.add_argument('-c', metavar="C", 
            type=argparse.FileType('w'), 
            help="instead of plotting, write gnuplot config in file C");

    args = parser.parse_args();


    if args.base_line:
        old_stat_files = set(args.stat_files);
        args.stat_files = [process_baseline(file, args.base_line) for 
                           file in args.stat_files];
        assert not (old_stat_files & set(args.stat_files)),"Could not evaluate the baseline";

    if args.c:
        out = args.c;
    else:
        gnuplot = subprocess.Popen(["gnuplot","-p"],stdin=subprocess.PIPE,
                                   stdout=sys.stdout, stderr=sys.stderr);
        out = gnuplot.stdin;
    # Generate an abreviated legend
    if len(args.stat_files) == 1:
        out.write(single_stat_gnuplot(args.r).replace("<FILE>",
                args.stat_files[0]).replace(
                "<MAX_S>", str(args.max_success)));
    else:
        a = len(os.path.commonprefix(args.stat_files));
        b = len(os.path.commonprefix([name[::-1] for name in args.stat_files]));
        legend = [file_name[a:-b] for file_name in args.stat_files];

        out.write("""
            set terminal x11 persist;

            set key default;
            set key box;

            set size 1, 1;
            set origin 0, 0;

            set multiplot;

            set key off;

            set title 'Error/failures ratio'
            set xlabel 'Iteration';
            set ylabel 'Percentage';
            set grid;

            set size 0.45, 1;
            set origin 0, 0;

            set ytics ("0" 0, "100" 100, "-100" -100, \
                    "25" 25, "50" 50, "75" 75, \
                    "-25" -25, "-50" -50, "-75" -75);
        """);
        if args.r:
            out.write("set yrange {}\n".format(args.r));
        elif args.base_line:
            out.write("""
            set yrange [-50:50];
            """);
        else:
            out.write("""
            set yrange [0:100];
            """);
        out.write("plot ");
        out.write(','.join(["'{}' u 1:13:14 t '{}' w yerrorlines".format(
                args.stat_files[i], legend[i]) for i in 
                range(0,len(args.stat_files))]));
        out.write("""

            set title 'Successes/max_successes'
            set xlabel 'Iteration';
            set ylabel 'Percentage';
            #unset ylabel;
            set grid;

            set size 0.45, 1;
            set origin 0.45, 0;

            set key at screen 0.995, 0.915;
            #set key samplen 1;
            set key Left reverse;
            #show key

            set ytics ("0" 0, "100" 100, "-100" -100, \
                    "25" 25, "50" 50, "75" 75, \
                    "-25" -25, "-50" -50, "-75" -75);
        """);
        if args.r:
            out.write("set yrange {}\n".format(args.r));
        elif args.base_line:
            out.write("""
            set yrange [-100:0];
            """);
        else:
            out.write("""
            set yrange [0:100];
            """);
        out.write("plot ");
        out.write(','.join(
                [("'{0}' u 1:($15*100/{2}):($16*100/{2}) "
                "t '{1}' w yerrorlines").format(args.stat_files[i],
                legend[i], args.max_success) for i in 
                range(0,len(args.stat_files))]));
        out.write("""
            unset multiplot;
            reset;
        """);
    out.close();
    if not args.c:
        gnuplot.wait();
    if args.base_line:
        map(os.remove,args.stat_files);


def is_number(s):
    return parse_number(s) is not None;


def process_baseline(file_name, base_line):
    file = open(file_name, 'r');
    base = open(base_line, 'r');
    out_name = file_name+'.tmp';
    out = open(out_name, 'w');
    for line in file:
        row = line.split();
        if not row or not is_number(row[0]):
            continue;
        for b in base:
            other = b.split();
            if other and is_number(other[0]) and \
                    parse_number(row[0]) == parse_number(other[0]):
                out.write(row[0]+" ");
                for i in range(1,len(row)):
                    if i in {4, 6, 8, 10, 12, 14, 16}:
                        out.write(str(parse_number(row[i]) - 
                                      parse_number(other[i]))+" ");
                    else:
                        out.write(row[i]+" ");
                out.write("\n");
                break;
    file.close();
    base.close();
    out.close();
    return out_name;


def parse_number(string):
    if string.endswith('%'):
        string = string[:-1];
    try:
        return float(string);
    except ValueError:
        return None;


def single_stat_gnuplot(_range):
    to_return = """
# Tutorial:  http://www.ibm.com/developerworks/library/l-gnuplot/
# Reference: http://www.gnuplot.info/docs_4.4/gnuplot.pdf


set terminal x11 persist;

set size 1, 1;
set origin 0, 0;

set multiplot;

set size 0.5, 1;
set origin 0, 0;

set title 'Inhibited traces, sporadic errors and failed sessions';
set xlabel 'Iteration';
set ylabel 'Number';
"""
    if _range:
        to_return += "set yrange {}\n".format(_range);
    to_return += """

plot '<FILE>' u 1:5:6 t 'I' w yerrorlines, '<FILE>' u 1:9:10 t 'E' w yerrorlines, '<FILE>' u 1:11:12 t 'F' w yerrorlines;

set size 0.5, 1;
set origin 0.5, 0;

set title 'Error/failures ratio, successes/sessions and successes/max_successes ratio';
set xlabel 'Iteration';
set ylabel 'Percentage';
"""
    if _range:
        to_return += "set yrange {}\n".format(_range);
    else:
        to_return += "set yrange [0:100];\n";
    to_return += """
set ytics ("0" 0, "100" 100, "-100" -100, \
        "25" 25, "50" 50, "75" 75, \
        "-25" -25, "-50" -50, "-75" -75);

plot '<FILE>' u 1:13:14 t 'E/F' w yerrorlines, '<FILE>' u 1:17:18 t 'F/S' w yerrorlines, '<FILE>' u 1:($15*100/<MAX_S>):($16*100/<MAX_S>) t 'S/max(S)' w yerrorlines;

unset multiplot;

reset;
""";
    return to_return;

        
    

    

if __name__ == "__main__":
    main();

