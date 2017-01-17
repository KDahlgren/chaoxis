# pyLDFI

pyLDIF is a Python implementation of the Lineage-Driven Fault Injection approach to fault-tolerance testing originally proposed in the paper "Lineage-Driven Fault Injection" published by Peter Alvaro et al. published at SIGMOD2015 and pioneered by the Molly implementation available here: [https://github.com/palvaro/molly](https://github.com/palvaro/molly)

## Installation

To install pyLDFI, run the following command from the top directory:
```
python setup.py
```
To clean up after a previous installation, run the following command from the top directory:
```
make clean
```

## Getting Started

1. Clone the repo.
2. ```cd pyLDFI/tests/simpleLog/```
3. ```bash run.sh```
4. If the string "TEST PASSED" appears, then your computer has all the necessary packages to run the current version of the program. Otherwise, please consult the output for more information.
5. Next, ```cd into pyLDFI/tests/pyLDFI\_UnitTests/```
6. Run ```python pyLDFI\_TestEnsemble.py```. If all the tests pass, then the functionality challenged by the current testing framework works on your computer.

The "run.sh" scripts essentially wrap a full execution over the relevant Dedalus files in the directory. If the run exits normally, then the "test" passes. Otherwise, stdout populates with the error message followed by all the lines of the execution printed to the screen leading up to the error. Accordingly, the unit tests represent a more rigorous examinations of functionality correctness. The non-unit tests are most valuable as windows offering a view into the abilities of the current version of pyLDFI.

## Running Unit Tests
To run the unit tests, go to pyLDFI/tests/pyLDFI_TestEnsemble/ and run:
```
python pyLDFI_TestEnsemble.py
```

## More Exercises

* Run simplelog/ with output: 
```
python ../../src/drivers/driver1.py -n a,b,c -f ./simpleLog.ded --evaluator c4
```
* Run tokens/ with output: 
```
python ../../src/drivers/driver1.py -n a,b,c -f ./timeout\_svc.ded -f ./tokens.ded --evaluator c4
```
* Run barrier\_test/ with output: 
```
python ../../src/drivers/driver1.py -n a,b,c -f ./barrier\_test.ded --evaluator c4
```
* Run real\_heartbeat/ with output: 
```
python ../../src/drivers/driver1.py -n a,b,c -f ./real\_heartbeat.ded --evaluator c4
```

## Dependencies
Python Packages :
  * [argparse](https://pypi.python.org/pypi/argparse)
  * [pyparsing](http://pyparsing.wikispaces.com/Download+and+Installation)
  * [sqlite3](https://docs.python.org/2/library/sqlite3.html)
  * [pyDatalog](https://sites.google.com/site/pydatalog/installation)

Other Tools :
  * [C4 Overlog Runtime](https://github.com/bloom-lang/c4) (installed locally automatically)
  * [Z3 Theorem Prover](https://github.com/Z3Prover/z3) (installed locally automatically)

## More information

[Disorderly Labs](https://disorderlylabs.github.io)

pyLDFI is an alternative to Molly, an implementation of LDFI written primarily in Scala.<br />
Molly is described in a [SIGMOD paper](http://people.ucsc.edu/~palvaro/molly.pdf).<br />
Dedalus is described [here](http://www.eecs.berkeley.edu/Pubs/TechRpts/2009/EECS-2009-173.html).
