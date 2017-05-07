#!/usr/bin/env python

'''
Test_e2e.py
  Defines unit tests for end-to-end functionality.
'''

#############
#  IMPORTS  #
#############
# standard python packages
import filecmp, inspect, os, sqlite3, sys, unittest
from StringIO import StringIO

# ------------------------------------------------------ #
# import sibling packages HERE!!!
sys.path.append( os.path.abspath( __file__ + "/../../../../src" ) )
sys.path.append( os.path.abspath( __file__ + "/../../../../src/dedt" ) )

from dedt        import dedt, dedalusRewriter, provenanceRewriter
from core        import LDFICore
from translators import c4_translator, dumpers_c4
from utils       import tools
from solvers     import EncodedProvTree_CNF

import e2e_tools

# ------------------------------------------------------ #


DEBUG = False


###########################
#  TEST E2E (End-To-End)  #
###########################
class Test_e2e( unittest.TestCase ) :


  ###################
  #  FULL WORKFLOW  #
  ###################
  # WRITE THIS TEST AFTER RESOLVING SOLVER CORRECTNESS.
  def test_full_workflow_e2e( self ) :
    return None


  ###########################
  #  DEDALUS TO C4 DATALOG  #
  ###########################
  def test_dedalus_to_c4_datalog_e2e( self ) :

    # ------------------------------------------------------------------ #
    # create IR instance
    saveDB = os.getcwd() + "/IR_test_dedalus_to_c4_datalog_e2e.db"
    os.system( saveDB ) # delete db if it already exists.

    IRDB   = sqlite3.connect( saveDB ) # database for storing IR, stored in running script dir
    cursor = IRDB.cursor()
    dedt.createDedalusIRTables( cursor )

    # raw dedalus
    input_ded  = os.path.abspath( __file__ + "/../../../testfiles/simpleLog_v0.ded" )

    # file for storing table strs
    table_save = os.path.abspath( __file__ + "/../../../testfiles/simplelog_v0_tables.data" )

    # file for storing output the c4 datalog directly corresponding to the raw dedalus
    output_olg = os.path.abspath( __file__ + "/../../../testfiles/e2e_test.olg" )

    # file storing the expected c4 datalog
    expected_olg = os.path.abspath( __file__ + "/../../../testfiles/simpleLog_v0_to_c4_expected.olg" )

    # dictionary of commandline args for executing the run
    argDict = { 'prov_diagrams'            : False,           \
                'use_symmetry'             : False,           \
                'crashes': 0, 'solver'     : None,            \
                'disable_dot_rendering'    : False,           \
                'negative_support'         : False,           \
                'strategy'                 : None,            \
                'file'                     : input_ded,       \
                'EOT'                      : 4,               \
                'find_all_counterexamples' : False,           \
                'nodes'                    : ['a', 'b', 'c'], \
                'evaluator'                : 'c4',            \
                'EFF'                      : 2 }
    # ------------------------------------------------------------------ #

    # translate and save to output file
    dedt.runTranslator( cursor, input_ded, argDict, table_save, output_olg, "c4" )

    # compare test file translation with expected file translation
    self.assertTrue( e2e_tools.cmpDatalogFiles_c4( output_olg, expected_olg ) )

    # close database instance
    dedt.cleanUp( IRDB, saveDB )


  ###################################
  #  DEDALUS TO DEDALUS IR REWRITE  #
  ###################################
  def test_dedalus_to_dedalus_ir_rewrite_e2e( self ) :

    # ------------------------------------------------------------------ #
    # create IR instance
    saveDB = os.getcwd() + "/IR_test_dedalus_to_dedalus_ir_rewrite_e2e.db"
    os.system( saveDB ) # delete db if it already exists.

    IRDB   = sqlite3.connect( saveDB ) # database for storing IR, stored in running script dir
    cursor = IRDB.cursor()
    dedt.createDedalusIRTables( cursor )

    # raw dedalus
    input_ded = os.path.abspath( __file__ + "/../../../testfiles/simpleLog_v0.ded" )

    # path to test IR dump
    test_dump_save = os.getcwd() + "/test_dump.txt"
    os.system( test_dump_save ) # remove if file already exists

    # path to expected IR dump
    expected_dump_save = os.path.abspath( __file__ + "/../../../testfiles/expected_IR_dump_test_dedalus_to_dedalus_ir_rewrite_e2e.txt" )

    # dictionary of commandline args for executing the run
    argDict = { 'prov_diagrams'            : False,           \
                'use_symmetry'             : False,           \
                'crashes': 0, 'solver'     : None,            \
                'disable_dot_rendering'    : False,           \
                'negative_support'         : False,           \
                'strategy'                 : None,            \
                'file'                     : input_ded,       \
                'EOT'                      : 4,               \
                'find_all_counterexamples' : False,           \
                'nodes'                    : ['a', 'b', 'c'], \
                'evaluator'                : 'c4',            \
                'EFF'                      : 2 }
    # ------------------------------------------------------------------ #

    # populate the initial IR
    meta = dedt.dedToIR( input_ded, cursor )

    # generate the first clock
    dedt.starterClock( cursor, argDict )

    # perform the dedalus rewrite
    dedalusRewriter.rewriteDedalus( cursor )

    # dump contents of IR db to a save file
    dumpers_c4.dumpIR( cursor, test_dump_save )

    # compare test IR results with expected IR results by comparing save file dumps
    self.assertTrue( e2e_tools.cmpDatalogFiles_c4( test_dump_save, expected_dump_save ) )

    # close database instance
    dedt.cleanUp( IRDB, saveDB )


  ######################################
  #  DEDALUS TO PROVENANCE IR REWRITE  #
  ######################################
  def test_dedalus_to_provenance_ir_rewrite_e2e( self ) :

    # ------------------------------------------------------------------ #
    # create IR instance
    saveDB = os.getcwd() + "/IR_test_dedalus_to_provenance_ir_rewrite_e2e.db"
    os.system( saveDB ) # delete db if it already exists.

    IRDB   = sqlite3.connect( saveDB ) # database for storing IR, stored in running script dir
    cursor = IRDB.cursor()
    dedt.createDedalusIRTables( cursor )

    # raw dedalus
    input_ded = os.path.abspath( __file__ + "/../../../testfiles/simpleLog_v0.ded" )

    # path to test IR dump
    test_dump_save = os.getcwd() + "/test_dump.txt"
    os.system( test_dump_save ) # remove if file already exists
    
    # path to expected IR dump
    expected_dump_save = os.path.abspath( __file__ + "/../../../testfiles/expected_IR_dump_test_dedalus_to_provenance_ir_rewrite_e2e.txt" )

    # dictionary of commandline args for executing the run
    argDict = { 'prov_diagrams'            : False,           \
                'use_symmetry'             : False,           \
                'crashes': 0, 'solver'     : None,            \
                'disable_dot_rendering'    : False,           \
                'negative_support'         : False,           \
                'strategy'                 : None,            \
                'file'                     : input_ded,       \
                'EOT'                      : 4,               \
                'find_all_counterexamples' : False,           \
                'nodes'                    : ['a', 'b', 'c'], \
                'evaluator'                : 'c4',            \
                'EFF'                      : 2 }
    # ------------------------------------------------------------------ #

    # populate the initial IR
    meta     = dedt.dedToIR( input_ded, cursor )
    ruleMeta = meta[1]

    # generate the first clock
    dedt.starterClock( cursor, argDict )

    # perform the dedalus rewrite
    dedalusRewriter.rewriteDedalus( cursor )

    # add provenance rules
    provenanceRewriter.rewriteProvenance( ruleMeta, cursor )

    # dump contents of IR db to a save file
    dumpers_c4.dumpIR( cursor, test_dump_save )

    # compare test IR results with expected IR results by comparing save file dumps
    self.assertTrue( e2e_tools.cmpDatalogFiles_c4( test_dump_save, expected_dump_save ) )

    # close database instance
    dedt.cleanUp( IRDB, saveDB )


  ################################
  #  DEDALUS TO PROVENANCE TREE  #
  ################################
  def test_dedalus_to_provenance_tree_e2e( self ) :

    # ------------------------------------------------------------------ #
    # create IR instance
    saveDB = os.getcwd() + "/IR_test_dedalus_to_c4_datalog_e2e.db"
    os.system( saveDB ) # delete db if it already exists.

    IRDB   = sqlite3.connect( saveDB ) # database for storing IR, stored in running script dir
    cursor = IRDB.cursor()
    dedt.createDedalusIRTables( cursor )

    # raw dedalus
    input_ded  = os.path.abspath( __file__ + "/../../../testfiles/simpleLog_v0.ded" )

    # file for storing table strs
    table_save = os.path.abspath( __file__ + "/../../../testfiles/simplelog_v0_tables.data" )

    # file for storing output the c4 datalog directly corresponding to the raw dedalus
    output_olg = os.path.abspath( __file__ + "/../../../testfiles/e2e_test.olg" )

    # file storing the expected provTreeComplete
    expected_tree = os.path.abspath( __file__ + "/../../../testfiles/expected_provTreeComplete.txt" )

    # c4 evaluation results save path
    c4_results_save = os.path.abspath( __file__ + "/../../../testfiles/simpleLog_c4_results.txt" )

    # dictionary of commandline args for executing the run
    argDict = { 'prov_diagrams'            : False,           \
                'use_symmetry'             : False,           \
                'crashes': 0, 'solver'     : None,            \
                'disable_dot_rendering'    : False,           \
                'negative_support'         : False,           \
                'strategy'                 : None,            \
                'file'                     : input_ded,       \
                'EOT'                      : 4,               \
                'find_all_counterexamples' : False,           \
                'nodes'                    : ['a', 'b', 'c'], \
                'evaluator'                : 'c4',            \
                'EFF'                      : 2 }
    # ------------------------------------------------------------------ #

    # translate and save to output file
    dedt.runTranslator( cursor, input_ded, argDict, table_save, output_olg, "c4" )

    # create and LDFICore insatnce and run evaluator only
    coreInstance = LDFICore.LDFICore( c4_results_save, table_save, output_olg, argDict, cursor )
    resultsPath  = coreInstance.evaluate( "C4_WRAPPER", coreInstance.table_list_path, coreInstance.datalog_prog_path, coreInstance.c4_dump_savepath )
    parsedResults = tools.getEvalResults_file_c4( resultsPath ) # assumes C4 results stored in dump

    # build test proof/provenance/derivation tree
    fault_id         = 0
    provTreeComplete = coreInstance.buildProvTree( parsedResults, coreInstance.argDict[ "EOT" ], fault_id, coreInstance.cursor )

    # load expected prov tree edge set
    fo = open( expected_tree, "r" )
    expected_provTreeComplete = fo.readline()
    fo.close()

    # compare test file translation with expected file translation
    self.assertTrue( provTreeComplete, expected_provTreeComplete )

    # close database instance
    dedt.cleanUp( IRDB, saveDB )


  ####################
  #  DEDALUS TO CNF  #
  ####################
  def test_dedalus_to_cnf_rewrite_e2e( self ) :

    # ------------------------------------------------------------------ #
    # create IR instance
    saveDB = os.getcwd() + "/IR_test_dedalus_to_c4_datalog_e2e.db"
    os.system( saveDB ) # delete db if it already exists.

    IRDB   = sqlite3.connect( saveDB ) # database for storing IR, stored in running script dir
    cursor = IRDB.cursor()
    dedt.createDedalusIRTables( cursor )

    # raw dedalus
    input_ded  = os.path.abspath( __file__ + "/../../../testfiles/simpleLog_v0.ded" )

    # file for storing table strs
    table_save = os.path.abspath( __file__ + "/../../../testfiles/simplelog_v0_tables.data" )

    # file for storing output the c4 datalog directly corresponding to the raw dedalus
    output_olg = os.path.abspath( __file__ + "/../../../testfiles/e2e_test.olg" )

    # file storing the expected provTreeComplete
    expected_cnf_fmla_save = os.path.abspath( __file__ + "/../../../testfiles/expected_cnf_fmla_save.txt" )

    # c4 evaluation results save path
    c4_results_save = os.path.abspath( __file__ + "/../../../testfiles/simpleLog_c4_results.txt" )

    # dictionary of commandline args for executing the run
    argDict = { 'prov_diagrams'            : False,           \
                'use_symmetry'             : False,           \
                'crashes': 0, 'solver'     : None,            \
                'disable_dot_rendering'    : False,           \
                'negative_support'         : False,           \
                'strategy'                 : None,            \
                'file'                     : input_ded,       \
                'EOT'                      : 4,               \
                'find_all_counterexamples' : False,           \
                'nodes'                    : ['a', 'b', 'c'], \
                'evaluator'                : 'c4',            \
                'EFF'                      : 2 }
    # ------------------------------------------------------------------ #

    # translate and save to output file
    dedt.runTranslator( cursor, input_ded, argDict, table_save, output_olg, "c4" )

    # create and LDFICore insatnce and run evaluator only
    coreInstance = LDFICore.LDFICore( c4_results_save, table_save, output_olg, argDict, cursor )
    resultsPath  = coreInstance.evaluate( "C4_WRAPPER", coreInstance.table_list_path, coreInstance.datalog_prog_path, coreInstance.c4_dump_savepath )
    parsedResults = tools.getEvalResults_file_c4( resultsPath ) # assumes C4 results stored in dump

    # build test proof/provenance/derivation tree
    fault_id         = 0
    provTreeComplete = coreInstance.buildProvTree( parsedResults, coreInstance.argDict[ "EOT" ], fault_id, coreInstance.cursor )

    # generate formula from test
    provTree_fmla = EncodedProvTree_CNF.EncodedProvTree_CNF( provTreeComplete )
    cnf_fmla      = provTree_fmla.cnfformula

    # load expected CNF formula
    fo = open( expected_cnf_fmla_save, "r" )
    expected_cnf_fmla = fo.readline()
    fo.close()
 
    # compare test file translation with expected file translation
    self.assertTrue( cnf_fmla, expected_cnf_fmla )

    # close database instance
    dedt.cleanUp( IRDB, saveDB )


  #############################
  #  CNF TO FAULT HYPOTHESES  #
  #############################
  # WRITE THIS TEST AFTER RESOLVING SOLVER CORRECTNESS.
  def test_cnf_to_fault_hypotheses_e2e( self ) :
    return None



#########
#  EOF  #
#########
