ITACA - Adaptor [![Build Status](https://secure.travis-ci.org/jamartinb/adaptor.png)](http://travis-ci.org/jamartinb/adaptor)
===============

This package includes the files require to synthesise or learn behavioural
adaptors between stateful services. This is part of the ITACA toolbox
(http://itaca.gisum.uma.es/) and it follows its convention regarding adaptation
contracts and service specifications.

The principal article behind adaptor.py is:

 * J.A. Martín and E. Pimentel. Learning from Failures: a Lightweight Approach
   to Run-Time Behavioural Adaptation, FACS'11, 2011 - http://goo.gl/0ii2F

... and it belongs to the ITACA toolbox:

 * J. Camara, J.A. Martín, G. Salaun, J. Cubo, M. Ouederni, C. Canal, E.
   Pimentel. ITACA: An integrated toolbox for the automatic composition and
   adaptation of Web services, ICSE'09, 2009 - http://goo.gl/oFGe8


The main script is itacalib/adaptor/adaptor.py but the general contents are the
following:

 * itaca/samples/adaptor - Contains services and contracts to try the toolbox
 * itacalib/model - Contains the python libraries to encode the model
 * itacalib/XML - Is able to extract the model from XML files
 * itacalib/verification/synchronisation.py - Is the simulator
 * itacalib/adaptor/adaptor.py - Contains the main script
 * itacalib/tests - Iclude the pyunit tests


Source packaging
----------------

To create a tarball ready for source distribution go to the root of the 
repository and execute

    > python2.7 setup.py sdist

The package will be created in the dist directory



Installing
----------

You can execute adaptor locally but don't forget to place the directory 
containing itaca and itacalib in the PYTHONPATH environment variable. If 
that's your current folder, you can do it by executing:

    > export $PYTHONPATH:$(pwd)

Graphviz and gnuplot are recommended in order to plot the services and adaptors
(these can be exported to the DOT language and visuaziled with Graphviz) and
plotting graphs according to the measures given by learning adaptors.

Alternativelly, for permanent installation you may execute:

    > python2.7 setup.py install



Some examples
-------------

    > python2.7 -m itacalib.adaptor.adaptor -t

Executes the tests located in itacalib/tests.
These are a subset of the tests executed using:

    > python2.7 setup.py test

In order to show help information, execute:

    > python2.7 -m itacalib.adaptor.adaptor -h

Finally, you can execute a specific example with the following command:

    > DIR=itaca/samples/adaptor/ecows11/; python2.7 -m itacalib.adaptor.adaptor \
        -c $DIR/contract-5.xml $DIR/SPIN_sink.xml $DIR/SPIN_source.xml \
        $DIR/tiny_diffusion.xml --times 1000 -p EXAMPLE \

Run a basic learning adaptor based on the evaluation example of FACS'11
(http://goo.gl/0ii2F -- where contracts and services are in directory $DIR)
with a training based in 1000 random traces and writting all the traces,
services, contract and adaptor in DOT files prefixed with "EXAMPLE". Running
statistics are printed in the terminal output.


Authors: José Antonio Martín Baena, Javier Cámara Moreno, Gwen Salaün,
Javier Cubo and Meriem Ouederni.

Contact: José Antonio Martín Baena <jose.antonio.martin.baena@gmail.com>

Copyright (C) 2012.

