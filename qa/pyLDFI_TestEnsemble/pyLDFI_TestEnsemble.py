#!/usr/bin/env python

'''
pyLDFI_TestEnsemble.py
  Primary file driving the execution of the initial
  unit test framework.
'''

#############
#  IMPORTS  #
#############
# standard python packages
import os, sys, unittest

# ------------------------------------------------------ #
# import sibling packages HERE!!!
sys.path.append( os.path.abspath( __file__ + "/../../src" )  )
# ------------------------------------------------------ #

# ------------------------------------ #
#             CORE TESTS               #
# ------------------------------------ #
from core_tests import Core_Tests

# ------------------------------------ #
#             DEDT TESTS               #
# ------------------------------------ #
from dedt_tests import Test_dedt,        \
                Test_clockRelation,      \
                Test_dedalusParser,      \
                Test_dedalusRewriter,    \
                Test_provenanceRewriter, \
                Test_Fact,               \
                Test_Rule

# ------------------------------------ #
#            DERIVATION TESTS          #
# ------------------------------------ #
from derivation_tests import Test_DerivTree, \
                             Test_FactNode,  \
                             Test_GoalNode,  \
                             Test_Node,      \
                             Test_ProvTree,  \
                             Test_RuleNode,  \
                             Test_provTools

# ------------------------------------ #
#            EVALUATORS TESTS          #
# ------------------------------------ #
from evaluators_tests import Evaluators_Tests

# ------------------------------------ #
#             SOLVERS TESTS            #
# ------------------------------------ #
from solvers_tests import Solvers_Tests

# ------------------------------------ #
#              UTILS TESTS             #
# ------------------------------------ #
from utils_tests import Test_clockTools,            \
                        Test_dumpers,               \
                        Test_extractors,            \
                        Test_parseCommandLineInput, \
                        Test_tools

# ------------------------------------ #
#         VISUALIZATIONS TESTS         #
# ------------------------------------ #
from visualizations_tests import Visualizations_Tests

# ------------------------------------ #

# ------------------------------------------------------ #


#########################
#  THREAD OF EXECUTION  #
#########################
if __name__ == "__main__" :

  print "*****************************************************"
  print
  print "Launching pyLDFI_TestEnsemble ..."

  ###########
  #  CORE/  #
  ###########
  print "\n"
  print "<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>"
  print "<><><><><><><><><><><><><><><><><><>"
  print "<>           CORE TESTS           <>"
  print "<><><><><><><><><><><><><><><><><><>"
  suite = unittest.TestLoader().loadTestsFromTestCase( Core_Tests.Core_Tests )
  unittest.TextTestRunner( verbosity=2 ).run( suite )


  ###########
  #  DEDT/  #
  ###########
  print "\n"
  print "<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>"
  print "<><><><><><><><><><><><><><><><><><>"
  print "<>           DEDT TESTS           <>"
  print "<><><><><><><><><><><><><><><><><><>"

  # dedt.py
  suite = unittest.TestLoader().loadTestsFromTestCase( Test_dedt.Test_dedt )
  unittest.TextTestRunner( verbosity=2 ).run( suite )

  # clockRelation.py
  suite = unittest.TestLoader().loadTestsFromTestCase( Test_clockRelation.Test_clockRelation )
  unittest.TextTestRunner( verbosity=2 ).run( suite )

  # dedalusParser.py
  suite = unittest.TestLoader().loadTestsFromTestCase( Test_dedalusParser.Test_dedalusParser )
  unittest.TextTestRunner( verbosity=2 ).run( suite )

  # dedalusRewriter.py
  suite = unittest.TestLoader().loadTestsFromTestCase( Test_dedalusRewriter.Test_dedalusRewriter )
  unittest.TextTestRunner( verbosity=2 ).run( suite )

  # provenanceRewriter.py
  suite = unittest.TestLoader().loadTestsFromTestCase( Test_provenanceRewriter.Test_provenanceRewriter )
  unittest.TextTestRunner( verbosity=2 ).run( suite )

  # Fact.py
  suite = unittest.TestLoader().loadTestsFromTestCase( Test_Fact.Test_Fact )
  unittest.TextTestRunner( verbosity=2 ).run( suite )

  # Rule.py
  suite = unittest.TestLoader().loadTestsFromTestCase( Test_Rule.Test_Rule )
  unittest.TextTestRunner( verbosity=2 ).run( suite )


  #################
  #  DERIVATION/  #
  #################
  print "\n"
  print "<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>"
  print "<><><><><><><><><><><><><><><><><><>"
  print "<>         DERIVATION TESTS       <>"
  print "<><><><><><><><><><><><><><><><><><>"

  # DerivTree.py
  suite = unittest.TestLoader().loadTestsFromTestCase( Test_DerivTree.Test_DerivTree )
  unittest.TextTestRunner( verbosity=2 ).run( suite )

  # FactNode.py
  suite = unittest.TestLoader().loadTestsFromTestCase( Test_FactNode.Test_FactNode )
  unittest.TextTestRunner( verbosity=2 ).run( suite )

  # GoalNode.py
  suite = unittest.TestLoader().loadTestsFromTestCase( Test_GoalNode.Test_GoalNode )
  unittest.TextTestRunner( verbosity=2 ).run( suite )

  # Node.py
  suite = unittest.TestLoader().loadTestsFromTestCase( Test_Node.Test_Node )
  unittest.TextTestRunner( verbosity=2 ).run( suite )

  # ProvTree.py
  suite = unittest.TestLoader().loadTestsFromTestCase( Test_ProvTree.Test_ProvTree )
  unittest.TextTestRunner( verbosity=2 ).run( suite )

  # RuleNode.py
  suite = unittest.TestLoader().loadTestsFromTestCase( Test_RuleNode.Test_RuleNode )
  unittest.TextTestRunner( verbosity=2 ).run( suite )

  # provTools.py
  suite = unittest.TestLoader().loadTestsFromTestCase( Test_provTools.Test_provTools )
  unittest.TextTestRunner( verbosity=2 ).run( suite )


  #################
  #  EVALUATORS/  #
  #################
  print "\n"
  print "<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>"
  print "<><><><><><><><><><><><><><><><><><>"
  print "<>         EVALUATORS TESTS       <>"
  print "<><><><><><><><><><><><><><><><><><>"
  suite = unittest.TestLoader().loadTestsFromTestCase( Evaluators_Tests.Evaluators_Tests )
  unittest.TextTestRunner( verbosity=2 ).run( suite )


  ##############
  #  SOLVERS/  #
  ##############
  print "\n"
  print "<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>"
  print "<><><><><><><><><><><><><><><><><><>"
  print "<>          SOLVERS TESTS         <>"
  print "<><><><><><><><><><><><><><><><><><>"
  suite = unittest.TestLoader().loadTestsFromTestCase( Solvers_Tests.Solvers_Tests )
  unittest.TextTestRunner( verbosity=2 ).run( suite )


  ############
  #  UTILS/  #
  ############
  print "\n"
  print "<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>"
  print "<><><><><><><><><><><><><><><><><><>"
  print "<>           UTLIS TESTS          <>"
  print "<><><><><><><><><><><><><><><><><><>"

  # clockTools.py
  suite = unittest.TestLoader().loadTestsFromTestCase( Test_clockTools.Test_clockTools )
  unittest.TextTestRunner( verbosity=2 ).run( suite )

  # dumpers.py
  suite = unittest.TestLoader().loadTestsFromTestCase( Test_dumpers.Test_dumpers )
  unittest.TextTestRunner( verbosity=2 ).run( suite )

  # extractors.py
  suite = unittest.TestLoader().loadTestsFromTestCase( Test_extractors.Test_extractors )
  unittest.TextTestRunner( verbosity=2 ).run( suite )

  # parseCommandLineInput.py
  suite = unittest.TestLoader().loadTestsFromTestCase( Test_parseCommandLineInput.Test_parseCommandLineInput )
  unittest.TextTestRunner( verbosity=2 ).run( suite )

  # tools.py
  suite = unittest.TestLoader().loadTestsFromTestCase( Test_tools.Test_tools )
  unittest.TextTestRunner( verbosity=2 ).run( suite )


  ####################
  #  VISUALIZATION/  #
  ####################
  print "\n"
  print "<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>"
  print "<><><><><><><><><><><><><><><><><><>"
  print "<>       VISUALIZATION TESTS      <>"
  print "<><><><><><><><><><><><><><><><><><>"
  suite = unittest.TestLoader().loadTestsFromTestCase( Visualizations_Tests.Visualizations_Tests )
  unittest.TextTestRunner( verbosity=2 ).run( suite )

  print "*****************************************************"

#########
#  EOF  #
#########
