                             -= ITACA - Adaptor =-

This package includes the files require to synthesise or learn behavioural
adaptors between stateful services. This is part of the ITACA toolbox
(http://itaca.gisum.uma.es/) and it follows its convention regarding adaptation
contracts and service specifications.

The principal article behind adaptor.py is: http://goo.gl/0ii2F

The main script is itacalib/adaptor/adaptor.py but the general contents are the
following:

 * itaca/samples/adaptor - Contains services and contracts to try the toolbox
 * itacalib/model - Contains the python libraries to encode the model
 * itacalib/XML - Is able to extract the model from XML files
 * itacalib/verification/synchronisation.py - Is the simulator
 * itacalib/adaptor/adaptor.py - Contains the main script
 * itacalib/tests - Iclude the pyunit tests

Don't forget to place the directory containing itaca and itacalib in the 
PYTHONPATH environment variable. If that's your current folder, you can do it 
by executing:

    > export $PYTHONPATH:$(pwd)

Graphviz and gnuplot are recommended in order to plot the services and adaptors
(these can be exported to the DOT language and visuaziled with Graphviz) and
plotting graphs according to the measures given by learning adaptors.

-- Some examples --

    > python2.7 -m itacalib.adaptor.adaptor -t

Executes the tests located in itacalib/tests.

    > python2.7 -m itacalib.adaptor.adaptor -h

Displays help information

    > DIR=itaca/samples/adaptor/ecows11/; python2.7 -m itacalib.adaptor.adaptor
        -c $DIR/contract-5.xml $DIR/SPIN_sink.xml $DIR/SPIN_source.xml
        $DIR/tiny_diffusion.xml --times 1000 -p EXAMPLE

Run a basic learning adaptor based on the evaluation example of FACS'11
(http://goo.gl/0ii2F -- where contracts and services are in directory $DIR)
with a training based in 1000 random traces and writting all the traces,
services, contract and adaptor in DOT files prefixed with "EXAMPLE". Running
statistics are printed in the terminal output.


Authors: José Antonio Martín Baena, Javier Cámara Moreno, Gwen Salaün,
Javier Cubo and Meriem Ouederni.

Contact: José Antonio Martín Baena <jose.antonio.martin.baena@gmail.com>

Copyright (C) 2012.

