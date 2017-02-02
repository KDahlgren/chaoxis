# TODO

An unordered log of some todo items associated with the development of pyLDFI.

* Refactor provenance tree code. Shuffle methods to more sensible locations. Make GoalNode, RuleNode, and FactNode inheritors of a parent Node class to better align with the OO philosophy. 

* Add code for providing default pre and post rules if users do not specify pre and post rules in the dedalus specifications.

* Modify template c4 main to output dump to a file and exit the c4 instance. The strategy accordingly means re-starting a new instance of c4 for every round of fault hypotheses. Accordingly, the strategy is infeasible in the long run, but essential for driving development progress in the short run.

* Fix c4 wrapper. Why are table dumps producing random integers?

* Support aggregate functions. For example, run barrier_test and examine how count<I> doesn't work.
