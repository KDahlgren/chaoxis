# TODO

An unordered log of some todo items associated with the development of pyLDFI.

* Verify correctness of CNF formula generation. Build simple test cases experimenting with different combinations of ANDs and ORs. 

* Verify correctness of pycosat solver solutions. Build simple test cases. Why are current solutions outputting one solution containing all the unique variables composing the formula???

* Implement CNF formula visualization.

* Build a tools.error as an alternative to tools.bp for error messages specifically.

* Support == and != operators in equations (see dedalusParser.py)

* Add more rigorous error encoding scheme.

* Add option for encapsulating similar clock facts in a single node representation (see Molly graphs, esp. clock node resolution).

* Add CMAKE check in makefile/setup.py as an installation predicate.

* Support negative subgoals in prov tree derivation.

* Support wildcards in prov tree derivation.

* Add code for providing default pre and post rules if users do not specify pre and post rules in the dedalus specifications.

* Fix c4 wrapper. Why are table dumps producing random integers?

* Support aggregate functions. For example, run barrier_test and examine how count<I> doesn't work.
