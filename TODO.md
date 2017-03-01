# TODO

An unordered log of some todo items associated with the development of pyLDFI.

* Support buggy provenance graph generation.

* Fix bug wrt mapping post records to post_prov records

* Make overall design not specific to c4!

* Insert a check in the parser to make sure users do not name tables with strings starting with "clock".

* Scan for valid relation names when using C4. C4 absolutely cannot handle camel case in relation names, or any capital letters in relation names, as far as I can tell. It also seems relation names must be at least 2 characters long.

* Boost parser to ensure no capital letters in dedalus table/relation/rule/fact names. C4 rejects the execution with a cryptic VAR_INT vs. TBL_INT error otherwise.

* Make sure parser pulls table names from fact declarations, in addition to rules, when populating the c4 table_str.

* Force setup.py to abort if any installation component fails.

* Make sure c4 clears the dump file before executing.

* Make sure execution fails in response to c4 evaluation failure.

* Add script for checking pyLDFI dependencies (esp. wrt python tools).

* Add pyLDFI to PyPI.

* Verify correctness of CNF formula generation. Build simple test cases experimenting with different combinations of ANDs and ORs. 

* Verify correctness of pycosat solver solutions. Build simple test cases. Why are current solutions outputting one solution containing all the unique variables composing the formula???

* Implement CNF formula visualization.

* Build a tools.error as an alternative to tools.bp for error messages specifically.

* Support != operator in equations instead of relying on the <, > hack.

* Add more rigorous error encoding scheme.

* Add option for encapsulating similar clock facts in a single node representation (see Molly graphs, esp. clock node resolution).

* Add CMAKE check in makefile/setup.py as an installation predicate.

* Support negative subgoals in prov tree derivation.

* Support wildcards in prov tree derivation.

* Add code for providing default pre and post rules if users do not specify pre and post rules in the dedalus specifications.

* Fix c4 wrapper. Why are table dumps producing random integers?

* Support aggregate functions. For example, run barrier_test and examine how count<I> doesn't work.

* Reminder: pydatalog evaluator not working.


#########
#  EOF  #
#########
