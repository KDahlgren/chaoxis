# Chaoxis

Chaoxis is a Python implementation of the Lineage-Driven Fault Injection approach to fault-tolerance testing originally proposed in the paper "Lineage-Driven Fault Injection" published by Peter Alvaro et al. published at SIGMOD2015 and pioneered by the Molly implementation available here: [https://github.com/palvaro/molly](https://github.com/palvaro/molly)

## Installation

To install Chaoxis, run the following command from the top directory:
```
python setup.py
```
To clean up after a previous installation, run the following command from the top directory:
```
make clean
```

## Getting Started

1. Clone the repo.
2. ```cd chaoxis/tests/simpleLog/```
3. ```bash run.sh```
4. If the string "TEST PASSED" appears, then your computer has all the necessary packages to run the current version of the program. Otherwise, please consult the output for more information.
5. Next, ```cd into chaoxis/tests/chaoxis\_UnitTests/```
6. Run ```python chaoxis\_TestEnsemble.py```. If all the tests pass, then the functionality challenged by the current testing framework works on your computer.

The "run.sh" scripts essentially wrap a full execution over the relevant Dedalus files in the directory. If the run exits normally, then the "test" passes. Otherwise, stdout populates with the error message followed by all the lines of the execution printed to the screen leading up to the error. Accordingly, the unit tests represent a more rigorous examinations of functionality correctness. The non-unit tests are most valuable as windows offering a view into the abilities of the current version of Chaoxis.

## Running Unit Tests
To run the unit tests, go to chaoxis/qa/chaoxis_TestEnsemble/ and run:
```
python chaoxis_TestEnsemble.py
```

* All provenance graph visualizations are stored in chaoxis/save_data/graphOutput/ with a time stamp indicating execution generation time.
* All fault injection solution recommendations are stored in chaoxis/save_data/fault_injection_solns/ with a time stamp indicating execution generation time.
* You can view a dump of the last execution simulation results in chaoxis/save_data/c4Output/c4dump.txt
* You can view the sequence of datalog programs, decorated with timestamps indicating generation time, used over the course of an LDFI simulation in chaoxis/src/evaluators/programFiles/

## Dedalus Specification Writing GOTCHAS!
1. relation names must be all lower case and contain only alphanumeric characters or underscores.
2. variable names may be strings of one or more alphanumeric characters, but the first character must be a capital letter.

## More Exercises

* Run simplelog/ with output from chaoxis/dev_tests/simpleLog/ :
```
python ../../src/drivers/driver1.py -n a,b,c -f ./simpleLog.ded --evaluator c4
```
or simply run (using bash or your other favorite shell) for full stdout :
```
bash run.sh cmd
```
or simply run the following command for a sparse determination of execution success :
```
bash run.sh
```
Provenance graph :
![provtree_render_05-03-2017_10hrs-59mins-44secs_0](https://cloud.githubusercontent.com/assets/16612428/23590379/849e1680-0193-11e7-8bb2-d90451211abd.png)

----
* Ditto instructions for running fun_example_1/ with output from chaoxis/dev_tests/fun_example_1/ :
```
python ../../src/drivers/driver1.py -n a,b,c -f ./fun_example_1.ded --evaluator c4
```
Provenance graph :
![provtree_render_05-03-2017_10hrs-42mins-39secs_0](https://cloud.githubusercontent.com/assets/16612428/23590386/a2d46974-0193-11e7-8f86-25ddf88eb7b4.png)

----
* Ditto instructions for running fun_example_2/ with output from chaoxis/dev_tests/fun_example_2/ :
```
python ../../src/drivers/driver1.py -n a,b,c -f ./fun_example_2.ded --evaluator c4
```
Provenance graph :
![provtree_render_05-03-2017_10hrs-42mins-48secs_0](https://cloud.githubusercontent.com/assets/16612428/23590382/932a2c84-0193-11e7-8420-085448bed22e.png)


## Dependencies
Python Packages (not automatically installed with Chaoxis) :
  * [argparse](https://pypi.python.org/pypi/argparse)
  * [pyparsing](http://pyparsing.wikispaces.com/Download+and+Installation)
  * [sqlite3](https://docs.python.org/2/library/sqlite3.html)
  * [pyDatalog](https://sites.google.com/site/pydatalog/installation)
  * [pyDot](https://pypi.python.org/pypi/pydot)
  * [mpmath](https://github.com/fredrik-johansson/mpmath#1-download--installation)
  * [SymPy (v1.0.1.dev)](http://docs.sympy.org/latest/install.html)
  * [pycosat](https://pythonhosted.org/PuLP/://pypi.python.org/pypi/pycosat)

Other Tools :
  * [p5.js](https://github.com/processing/p5.js/wiki/Development#setup)
  * [cmake](http://brewformulas.org/Cmake)
  * [C4 Overlog Runtime](https://github.com/bloom-lang/c4) (installed locally automatically)
  * [Z3 Theorem Prover](https://github.com/Z3Prover/z3) (installed locally automatically)

## More information

[Disorderly Labs](https://disorderlylabs.github.io)

Chaoxis is an alternative to Molly, an implementation of LDFI written primarily in Scala.<br><br>
Molly is described in a 2015 [SIGMOD paper](http://people.ucsc.edu/~palvaro/molly.pdf).<br><br>
Dedalus is described [here](http://www.eecs.berkeley.edu/Pubs/TechRpts/2009/EECS-2009-173.html).
