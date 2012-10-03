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


__all__ = ["verification","adaptor","model"];


def test_all():
    import os
    import unittest
    # Get the current folder
    here = os.path.dirname(__file__)

    # Get the path to tests files
    testfiles = [os.path.join(d,f) for (d, subdirs, files) in os.walk(here)
                                     for f in files
                                     if os.path.isfile(os.path.join(d,f))
                                     and f.endswith(".py")
                                     and "__init__.py" != f
                                     # This is automatically created, why?
                                     and "dststest.py" != f]

    # Translate paths to dotted modules
    # @TODO: I'm sure this can be done better
    modules = ['.'.join(f.split('.py')[0].split(os.path.sep))
                for f in testfiles]

    # travis-ci.org does not set __package__
    package = __package__+'.' if __package__ else ''
    if modules and package in modules[0]:
        testmodules = [package+m.split(package)[1] 
                        for m in modules]
    else:
        raise Exception("Couldn't load test files")

    suite = unittest.TestSuite()

    for t in testmodules:
        try:
            # If the module defines a suite() function, call it to get the suite.
            mod = __import__(t, globals(), locals(), ['suite'])
            suitefn = getattr(mod, 'suite')
            suite.addTest(suitefn())
        except (ImportError, AttributeError):
            # else, just load all the test cases from the module.
            # It only allows the "dotted" name
            try:
                suite.addTest(unittest.defaultTestLoader.loadTestsFromName(t))
            except Exception, e:
                raise Exception("Couldn't load test module: "+repr(t),e)

    return suite

