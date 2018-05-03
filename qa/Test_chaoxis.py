#!/usr/bin/env python

'''
Test_chaoxis.py
'''

#############
#  IMPORTS  #
#############
# standard python packages
import copy, inspect, logging, os, shutil, sqlite3, sys, time, unittest

# ------------------------------------------------------ #
# import sibling packages HERE!!!

if not os.path.abspath( __file__ + "/../../src" ) in sys.path :
  sys.path.append( os.path.abspath( __file__ + "/../../src" ) )

from api import Chaoxis

# ------------------------------------------------------ #


##################
#  TEST CHAOXIS  #
##################
class Test_chaoxis( unittest.TestCase ) :

  logging.basicConfig( format='%(levelname)s:%(message)s', level=logging.DEBUG )
  #logging.basicConfig( format='%(levelname)s:%(message)s', level=logging.INFO )
  #logging.basicConfig( format='%(levelname)s:%(message)s', level=logging.WARNING )

  PRINT_STOP = False


  ###########
  #  RDLOG  #
  ###########
  def test_rdlog( self ) :

    test_id = "rdlog"
    logging.debug( ">> RUNNING TEST '" + test_id + "' <<<" )

    # --------------------------------------------------------------- #
    # specify input file paths

    inputfile = "./dedalus_drivers/" + test_id + "_driver.ded"

    # --------------------------------------------------------------- #
    # define sys.argv

    argDict = {}
    argDict[ "debug" ]          = True
    argDict[ "file" ]           = inputfile
    argDict[ "EOT" ]            = 4
    argDict[ "EFF" ]            = 2
    argDict[ "nodes" ]          = [ "a", "b", "c" ]
    argDict[ "settings" ]       = "./settings_files/settings.ini"
    argDict[ "evaluator"]       = "c4"
    argDict[ "crashes" ]        = 0
    argDict[ "data_save_path" ] = "./data/" + test_id

    # --------------------------------------------------------------- #
    # run chaoxis

    # instantiate chaoxis object
    c = None
    c = Chaoxis.Chaoxis( argDict, test_id )

    # run chaoxis
    c.run()

    # collect conclusion
    actual_conclusion = c.conclusion

    expected_conclusion = '''conclusion : found counterexample : ['clock("a","b",2,3);', 'clock("a","b",1,2);', 'clock("a","b",3,4);']'''
    self.assertEqual( actual_conclusion, expected_conclusion )

    logging.debug( "  TEST " + test_id + " : actual_conclusion   = " + actual_conclusion )
    logging.debug( "  TEST " + test_id + " : expected_conclusion = " + expected_conclusion )


  ################
  #  SIMPLOG DM  #
  ################
  def test_simplog_dm( self ) :

    test_id = "simplog_dm"
    logging.debug( ">> RUNNING TEST '" + test_id + "' <<<" )

    # --------------------------------------------------------------- #
    # specify input file paths

    inputfile = "./dedalus_drivers/simplog_driver.ded"

    # --------------------------------------------------------------- #
    # define sys.argv

    argDict = {}
    argDict[ "debug" ]          = True
    argDict[ "file" ]           = inputfile
    argDict[ "EOT" ]            = 4
    argDict[ "EFF" ]            = 2
    argDict[ "nodes" ]          = [ "a", "b", "c" ]
    argDict[ "settings" ]       = "./settings_files/settings_dm.ini"
    argDict[ "evaluator"]       = "c4"
    argDict[ "crashes" ]        = 0
    argDict[ "data_save_path" ] = "./data/" + test_id + "/"

    # --------------------------------------------------------------- #
    # run chaoxis

    # instantiate chaoxis object
    #c = Chaoxis.Chaoxis( argDict, test_id, ['clock("a","b",1,2);'] )
    #c = Chaoxis.Chaoxis( argDict, test_id, ['clock("a","c",1,2);'] )
    #c = Chaoxis.Chaoxis( argDict, test_id, ['clock("a","c",1,2);', 'clock("a","b",1,2);'] )
    c = Chaoxis.Chaoxis( argDict, test_id )

    # run chaoxis
    c.run()

    # collect conclusion
    actual_conclusion = c.conclusion

    expected_conclusion = '''conclusion : found counterexample : [\'clock("a","c",1,2);\']'''
    self.assertEqual( actual_conclusion, expected_conclusion )

    logging.debug( "  TEST " + test_id + " : actual_conclusion   = " + actual_conclusion )
    logging.debug( "  TEST " + test_id + " : expected_conclusion = " + expected_conclusion )


  #############
  #  SIMPLOG  #
  #############
  def test_simplog( self ) :

    test_id = "simplog"
    logging.debug( ">> RUNNING TEST '" + test_id + "' <<<" )

    # --------------------------------------------------------------- #
    # specify input file paths

    inputfile = "./dedalus_drivers/" + test_id + "_driver.ded"

    # --------------------------------------------------------------- #
    # define sys.argv

    argDict = {}
    argDict[ "debug" ]          = True
    argDict[ "file" ]           = inputfile
    argDict[ "EOT" ]            = 4
    argDict[ "EFF" ]            = 2
    argDict[ "nodes" ]          = [ "a", "b", "c" ]
    argDict[ "settings" ]       = "./settings_files/settings.ini"
    argDict[ "evaluator"]       = "c4"
    argDict[ "crashes" ]        = 0
    argDict[ "data_save_path" ] = "./data/" + test_id + "/"

    # --------------------------------------------------------------- #
    # run chaoxis

    # instantiate chaoxis object
    c = None
    #c = Chaoxis.Chaoxis( argDict, test_id, ['clock("a","b",1,2);'] )
    #c = Chaoxis.Chaoxis( argDict, test_id, ['clock("a","c",1,2);'] )
    #c = Chaoxis.Chaoxis( argDict, test_id, ['clock("a","c",1,2);', 'clock("a","b",1,2);'] )
    c = Chaoxis.Chaoxis( argDict, test_id )

    # run chaoxis
    c.run()
    #c.run_find_all_solns()

    # collect conclusion
    actual_conclusion = c.conclusion

    expected_conclusion = '''conclusion : found counterexample : ['clock("a","b",1,2);']'''
    self.assertEqual( actual_conclusion, expected_conclusion )

    logging.debug( "  TEST " + test_id + " : actual_conclusion   = " + actual_conclusion )
    logging.debug( "  TEST " + test_id + " : expected_conclusion = " + expected_conclusion )


#########################
#  THREAD OF EXECUTION  #
#########################
if __name__ == "__main__":
  unittest.main()


#########
#  EOF  #
#########
