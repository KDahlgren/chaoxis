# pyLDFI

pyLDIF is a Python implementation of the Lineage-Driven Fault Injection approach to fault-tolerance testing originally proposed in the paper "Lineage-Driven Fault Injection" published by Peter Alvaro et al. published at SIGMOD2015 and pioneered by the Molly implementation available here: [https://github.com/palvaro/molly](https://github.com/palvaro/molly)

## Getting Started

1. Clone the repo.
2. cd pyLDFI/tests/simpleLog/
3. bash run.sh
4. If the string "TEST PASSED" appears, then your computer has all the necessary packages to run the current version of the program. Otherwise, please consult the output for more information.
5. Next, cd into pyLDFI/tests/pyLDFI\_UnitTests/
6. Run "python pyLDFI\_TestEnsemble.py". If all the tests pass, then the functionality challenged by the current testing framework works on your computer.

## More Fun Exercises

1. Run simplelog/ with output: "python ../../src/drivers/driver1.py -n a,b,c,d -f ./simpleLog.ded"
2. Run tokens/ with output: "python ../../src/drivers/driver1.py -n a,b,c,d -f ./timeout\_svc.ded -f ./tokens.ded"
3. Run barrier\_test/ with output: "python ../../src/drivers/driver1.py -n a,b,c,d -f ./barrier\_test.ded"
4. Run real\_heartbeat/ with output: "python ../../src/drivers/driver1.py -n a,b,c,d -f ./real\_heartbeat.ded"

## Dependencies
Python Packages :
  * [argparse](https://pypi.python.org/pypi/argparse)
  * [pyparsing](http://pyparsing.wikispaces.com/Download+and+Installation)
  * [sqlite3](https://docs.python.org/2/library/sqlite3.html)

## More information

[Disorderly Labs](https://disorderlylabs.github.io)

pyLDFI is an alternative to Molly, an implementation of LDFI written primarily in Scala.<br />
Molly is described in a [SIGMOD paper](http://people.ucsc.edu/~palvaro/molly.pdf).

Dedalus is described [here](http://www.eecs.berkeley.edu/Pubs/TechRpts/2009/EECS-2009-173.html).
