#!/usr/bin/env python

'''
Test_others.py
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


#################
#  TEST OTHERS  #
#################
class Test_others( unittest.TestCase ) :

  logging.basicConfig( format='%(levelname)s:%(message)s', level=logging.DEBUG )
  #logging.basicConfig( format='%(levelname)s:%(message)s', level=logging.INFO )
  #logging.basicConfig( format='%(levelname)s:%(message)s', level=logging.WARNING )

  PRINT_STOP = False

  ###############################
  #  TEST SIMPLOG OPTIMIZE NOT  #
  ###############################
  #@unittest.skip( "intractable run time. stalls at c4 eval." )
  def test_simplog_optimize_not( self ) :

    test_id = "simplog_optimize_not"
    logging.debug( ">> RUNNING TEST '" + test_id + "' <<<" )

    # --------------------------------------------------------------- #
    # specify input file paths

    inputfile = "./dedalus_drivers/simplog_driver.ded"

    # --------------------------------------------------------------- #
    # define sys.argv

    argDict = {}
    argDict[ "debug" ]          = True
    argDict[ "file" ]           = inputfile
    argDict[ "EOT" ]            = 3
    argDict[ "EFF" ]            = 0
    argDict[ "nodes" ]          = [ "a", "b", "c" ]
    argDict[ "settings" ]       = "./settings_files/settings_dm_optimize_not.ini"
    argDict[ "evaluator"]       = "c4"
    argDict[ "crashes" ]        = 0
    argDict[ "data_save_path" ] = "./data/" + test_id + "/"

    # --------------------------------------------------------------- #
    # run chaoxis

    # instantiate chaoxis object
    c = Chaoxis.Chaoxis( argDict, test_id )
    #c = Chaoxis.Chaoxis( argDict, test_id, [ 'clock("a","b",1,2);' ] )

    # run chaoxis
    c.run()

    # collect conclusion
    actual_conclusion = c.conclusion

    expected_conclusion = '''conclusion : found counterexample : [\'clock("a","c",1,2);\', \'_NOT_clock("a","b",1,2);\']'''

    self.assertEqual( actual_conclusion, expected_conclusion )

    logging.debug( "  TEST " + test_id + " : actual_conclusion   = " + actual_conclusion )
    logging.debug( "  TEST " + test_id + " : expected_conclusion = " + expected_conclusion )


  ###########
  #  KAFKA  #
  ###########
  @unittest.skip( "intractable run time. stalls at c4 eval." )
  def test_kafka( self ) :

    test_id = "kafka"
    logging.debug( ">> RUNNING TEST '" + test_id + "' <<<" )

    # --------------------------------------------------------------- #
    # specify input file paths

    inputfile = "./dedalus_drivers/" + test_id + "_driver.ded"

    # --------------------------------------------------------------- #
    # define sys.argv

    argDict = {}
    argDict[ "debug" ]          = True
    argDict[ "file" ]           = inputfile
    argDict[ "EOT" ]            = 3
    argDict[ "EFF" ]            = 0
    argDict[ "nodes" ]          = [ "a", "b", "C", "Z" ]
    argDict[ "settings" ]       = "./settings_files/settings_dm_allow_not_clocks.ini"
    argDict[ "evaluator"]       = "c4"
    argDict[ "crashes" ]        = 0
    argDict[ "data_save_path" ] = "./data/" + test_id + "/"

    # --------------------------------------------------------------- #
    # run chaoxis

    # instantiate chaoxis object
    c = Chaoxis.Chaoxis( argDict, test_id )

    # run chaoxis
    c.run()

    # collect conclusion
    actual_conclusion = c.conclusion

    expected_conclusion = '''?'''

    self.assertEqual( actual_conclusion, expected_conclusion )

    logging.debug( "  TEST " + test_id + " : actual_conclusion   = " + actual_conclusion )
    logging.debug( "  TEST " + test_id + " : expected_conclusion = " + expected_conclusion )


  #########
  #  3PC  #
  #########
  @unittest.skip( "intractable run time. lots of work type extrapolation." )
  def test_3pc( self ) :

    test_id = "3pc"
    logging.debug( ">> RUNNING TEST '" + test_id + "' <<<" )

    # --------------------------------------------------------------- #
    # specify input file paths

    inputfile = "./dedalus_drivers/" + test_id + "_driver.ded"

    # --------------------------------------------------------------- #
    # define sys.argv

    argDict = {}
    argDict[ "debug" ]          = True
    argDict[ "file" ]           = inputfile
    argDict[ "EOT" ]            = 3
    argDict[ "EFF" ]            = 0
    argDict[ "nodes" ]          = [ "a", "b", "C", "d" ]
    argDict[ "settings" ]       = "./settings_files/settings_dm_allow_not_clocks.ini"
    argDict[ "evaluator"]       = "c4"
    argDict[ "crashes" ]        = 0
    argDict[ "data_save_path" ] = "./data/" + test_id + "/"

    # --------------------------------------------------------------- #
    # run chaoxis

    # instantiate chaoxis object
    c = Chaoxis.Chaoxis( argDict, test_id )

    # run chaoxis
    c.run()

    # collect conclusion
    actual_conclusion = c.conclusion

    expected_conclusion = '''?'''

    self.assertEqual( actual_conclusion, expected_conclusion )

    logging.debug( "  TEST " + test_id + " : actual_conclusion   = " + actual_conclusion )
    logging.debug( "  TEST " + test_id + " : expected_conclusion = " + expected_conclusion )


  ##########################
  #  2PC TIMEOUT OPTIMIST  #
  ##########################
  @unittest.skip( "intractable run time. stalls at c4 eval." )
  def test_2pc_timeout_optimist( self ) :

    test_id = "2pc_timeout_optimist"
    logging.debug( ">> RUNNING TEST '" + test_id + "' <<<" )

    # --------------------------------------------------------------- #
    # specify input file paths

    inputfile = "./dedalus_drivers/" + test_id + "_driver.ded"

    # --------------------------------------------------------------- #
    # define sys.argv

    argDict = {}
    argDict[ "debug" ]          = True
    argDict[ "file" ]           = inputfile
    argDict[ "EOT" ]            = 3
    argDict[ "EFF" ]            = 0
    argDict[ "nodes" ]          = [ "a", "b", "C", "d" ]
    argDict[ "settings" ]       = "./settings_files/settings_dm_allow_not_clocks.ini"
    argDict[ "evaluator"]       = "c4"
    argDict[ "crashes" ]        = 0
    argDict[ "data_save_path" ] = "./data/" + test_id + "/"

    # --------------------------------------------------------------- #
    # run chaoxis

    # instantiate chaoxis object
    c = Chaoxis.Chaoxis( argDict, test_id )

    # run chaoxis
    c.run()

    # collect conclusion
    actual_conclusion = c.conclusion

    expected_conclusion = '''?'''

    self.assertEqual( actual_conclusion, expected_conclusion )

    logging.debug( "  TEST " + test_id + " : actual_conclusion   = " + actual_conclusion )
    logging.debug( "  TEST " + test_id + " : expected_conclusion = " + expected_conclusion )


  #################
  #  2PC TIMEOUT  #
  #################
  @unittest.skip( "intractable run time. stalls at c4 eval." )
  def test_2pc_timeout( self ) :

    test_id = "2pc_timeout"
    logging.debug( ">> RUNNING TEST '" + test_id + "' <<<" )

    # --------------------------------------------------------------- #
    # specify input file paths

    inputfile = "./dedalus_drivers/" + test_id + "_driver.ded"

    # --------------------------------------------------------------- #
    # define sys.argv

    argDict = {}
    argDict[ "debug" ]          = True
    argDict[ "file" ]           = inputfile
    argDict[ "EOT" ]            = 3
    argDict[ "EFF" ]            = 0
    argDict[ "nodes" ]          = [ "a", "b", "C", "d" ]
    argDict[ "settings" ]       = "./settings_files/settings_dm_allow_not_clocks.ini"
    argDict[ "evaluator"]       = "c4"
    argDict[ "crashes" ]        = 0
    argDict[ "data_save_path" ] = "./data/" + test_id + "/"

    # --------------------------------------------------------------- #
    # run chaoxis

    # instantiate chaoxis object
    c = Chaoxis.Chaoxis( argDict, test_id )

    # run chaoxis
    c.run()

    # collect conclusion
    actual_conclusion = c.conclusion

    expected_conclusion = '''?'''

    self.assertEqual( actual_conclusion, expected_conclusion )

    logging.debug( "  TEST " + test_id + " : actual_conclusion   = " + actual_conclusion )
    logging.debug( "  TEST " + test_id + " : expected_conclusion = " + expected_conclusion )


  #############
  #  2PC CTP  #
  #############
  @unittest.skip( "intractable run time. lots of work in dm rewrite." )
  def test_2pc_ctp( self ) :

    test_id = "2pc_ctp"
    logging.debug( ">> RUNNING TEST '" + test_id + "' <<<" )

    # --------------------------------------------------------------- #
    # specify input file paths

    inputfile = "./dedalus_drivers/" + test_id + "_driver.ded"

    # --------------------------------------------------------------- #
    # define sys.argv

    argDict = {}
    argDict[ "debug" ]          = True
    argDict[ "file" ]           = inputfile
    argDict[ "EOT" ]            = 3
    argDict[ "EFF" ]            = 0
    argDict[ "nodes" ]          = [ "a", "b", "C", "d" ]
    argDict[ "settings" ]       = "./settings_files/settings_dm_allow_not_clocks.ini"
    argDict[ "evaluator"]       = "c4"
    argDict[ "crashes" ]        = 0
    argDict[ "data_save_path" ] = "./data/" + test_id + "/"

    # --------------------------------------------------------------- #
    # run chaoxis

    # instantiate chaoxis object
    c = Chaoxis.Chaoxis( argDict, test_id )

    # run chaoxis
    c.run()

    # collect conclusion
    actual_conclusion = c.conclusion

    expected_conclusion = '''?'''

    self.assertEqual( actual_conclusion, expected_conclusion )

    logging.debug( "  TEST " + test_id + " : actual_conclusion   = " + actual_conclusion )
    logging.debug( "  TEST " + test_id + " : expected_conclusion = " + expected_conclusion )


  ##################
  #  2PC OPTIMIST  #
  ##################
  @unittest.skip( "intractable run time. stalls at c4 eval." )
  def test_2pc_optimist( self ) :

    test_id = "2pc_optimist"
    logging.debug( ">> RUNNING TEST '" + test_id + "' <<<" )

    # --------------------------------------------------------------- #
    # specify input file paths

    inputfile = "./dedalus_drivers/" + test_id + "_driver.ded"

    # --------------------------------------------------------------- #
    # define sys.argv

    argDict = {}
    argDict[ "debug" ]          = True
    argDict[ "file" ]           = inputfile
    argDict[ "EOT" ]            = 3
    argDict[ "EFF" ]            = 0
    argDict[ "nodes" ]          = [ "a", "b", "C", "d" ]
    argDict[ "settings" ]       = "./settings_files/settings_dm_allow_not_clocks.ini"
    argDict[ "evaluator"]       = "c4"
    argDict[ "crashes" ]        = 0
    argDict[ "data_save_path" ] = "./data/" + test_id + "/"

    # --------------------------------------------------------------- #
    # run chaoxis

    # instantiate chaoxis object
    c = Chaoxis.Chaoxis( argDict, test_id )

    # run chaoxis
    c.run()

    # collect conclusion
    actual_conclusion = c.conclusion

    expected_conclusion = '''?'''

    self.assertEqual( actual_conclusion, expected_conclusion )

    logging.debug( "  TEST " + test_id + " : actual_conclusion   = " + actual_conclusion )
    logging.debug( "  TEST " + test_id + " : expected_conclusion = " + expected_conclusion )


  #########
  #  2PC  #
  #########
  @unittest.skip( "intractable run time. stalls at c4 eval." )
  def test_2pc( self ) :

    test_id = "2pc"
    logging.debug( ">> RUNNING TEST '" + test_id + "' <<<" )

    # --------------------------------------------------------------- #
    # specify input file paths

    inputfile = "./dedalus_drivers/" + test_id + "_driver.ded"

    # --------------------------------------------------------------- #
    # define sys.argv

    argDict = {}
    argDict[ "debug" ]          = True
    argDict[ "file" ]           = inputfile
    argDict[ "EOT" ]            = 3
    argDict[ "EFF" ]            = 0
    argDict[ "nodes" ]          = [ "a", "b", "C", "d" ]
    argDict[ "settings" ]       = "./settings_files/settings_dm_allow_not_clocks.ini"
    argDict[ "evaluator"]       = "c4"
    argDict[ "crashes" ]        = 0
    argDict[ "data_save_path" ] = "./data/" + test_id + "/"

    # --------------------------------------------------------------- #
    # run chaoxis

    # instantiate chaoxis object
    c = Chaoxis.Chaoxis( argDict, test_id )

    # run chaoxis
    c.run()

    # collect conclusion
    actual_conclusion = c.conclusion

    expected_conclusion = '''?'''

    self.assertEqual( actual_conclusion, expected_conclusion )

    logging.debug( "  TEST " + test_id + " : actual_conclusion   = " + actual_conclusion )
    logging.debug( "  TEST " + test_id + " : expected_conclusion = " + expected_conclusion )


  ################
  #  CLASSIC RB  #
  ################
  #@unittest.skip( "." )
  def test_classic_rb( self ) :

    test_id = "classic_rb"
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
    argDict[ "EFF" ]            = 0
    argDict[ "nodes" ]          = [ "a", "b", "c" ]
    argDict[ "settings" ]       = "./settings_files/settings_dm_allow_not_clocks.ini"
    argDict[ "evaluator"]       = "c4"
    argDict[ "crashes" ]        = 0
    argDict[ "data_save_path" ] = "./data/" + test_id + "/"

    # --------------------------------------------------------------- #
    # run chaoxis

    # instantiate chaoxis object
    c = Chaoxis.Chaoxis( argDict, test_id )

    # this also works:
    #c = Chaoxis.Chaoxis( argDict, test_id, [ 'clock("a","c",1,2);', \
    #                                         'clock("b","a",2,3);', \
    #                                         'clock("b","c",2,3);'] )

    # run chaoxis
    c.run()
    #c.run_find_all_solns()

    # collect conclusion
    actual_conclusion = c.conclusion

    if argDict[ "EOT" ] == 3 :
      expected_conclusion = '''conclusion : found counterexample : ''' + \
                            '''[\'clock("a","c",1,2);\', ''' + \
                            '''\'_NOT_clock("a","b",1,2);\']'''
    elif argDict[ "EOT" ] == 4 :
      expected_conclusion = '''conclusion : found counterexample : ''' + \
                            '''[\'clock("b","c",2,3);\', ''' + \
                            '''\'clock("c","a",2,3);\', ''' + \
                            '''\'clock("b","a",2,3);\', ''' + \
                            '''\'clock("a","c",1,2);\', ''' + \
                            '''\'_NOT_clock("a","b",1,2);\', ''' + \
                            '''\'clock("c","b",2,3);\']'''
    else :
      expected_conclusion = '''?'''

    self.assertEqual( actual_conclusion, expected_conclusion )

    logging.debug( "  TEST " + test_id + " : actual_conclusion   = " + actual_conclusion )
    logging.debug( "  TEST " + test_id + " : expected_conclusion = " + expected_conclusion )


  ############
  #  REPLOG  #
  ############
  def test_replog( self ) :

    test_id = "replog"
    logging.debug( ">> RUNNING TEST '" + test_id + "' <<<" )

    # --------------------------------------------------------------- #
    # specify input file paths

    inputfile = "./dedalus_drivers/" + test_id + "_driver.ded"

    # --------------------------------------------------------------- #
    # define sys.argv

    argDict = {}
    argDict[ "debug" ]          = True
    argDict[ "file" ]           = inputfile
    argDict[ "EOT" ]            = 3
    argDict[ "EFF" ]            = 0
    argDict[ "nodes" ]          = [ "a", "b", "c" ]
    argDict[ "settings" ]       = "./settings_files/settings_dm_allow_not_clocks.ini"
    argDict[ "evaluator"]       = "c4"
    argDict[ "crashes" ]        = 0
    argDict[ "data_save_path" ] = "./data/" + test_id + "/"

    # --------------------------------------------------------------- #
    # run chaoxis

    # instantiate chaoxis object
    c = Chaoxis.Chaoxis( argDict, test_id )

    # run chaoxis
    c.run()

    # collect conclusion
    actual_conclusion = c.conclusion

    expected_conclusion = '''conclusion : found counterexample : ''' + \
                          '''[\'clock("b","c",2,3);\', ''' +\
                          '''\'clock("c","a",2,3);\', ''' + \
                          '''\'clock("b","a",2,3);\', ''' + \
                          '''\'clock("a","c",1,2);\', ''' + \
                          '''\'clock("a","b",2,3);\', ''' + \
                          '''\'clock("a","b",1,2);\', ''' + \
                          '''\'_NOT_clock("a","c",2,3);\', ''' + \
                          '''\'clock("c","b",2,3);\']'''

    self.assertEqual( actual_conclusion, expected_conclusion )

    logging.debug( "  TEST " + test_id + " : actual_conclusion   = " + actual_conclusion )
    logging.debug( "  TEST " + test_id + " : expected_conclusion = " + expected_conclusion )


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
    argDict[ "EOT" ]            = 3
    argDict[ "EFF" ]            = 0
    argDict[ "nodes" ]          = [ "a", "b", "c" ]
    argDict[ "settings" ]       = "./settings_files/settings_dm_allow_not_clocks.ini"
    argDict[ "evaluator"]       = "c4"
    argDict[ "crashes" ]        = 0
    argDict[ "data_save_path" ] = "./data/" + test_id + "/"

    # --------------------------------------------------------------- #
    # run chaoxis

    # instantiate chaoxis object
    c = Chaoxis.Chaoxis( argDict, test_id )

    # run chaoxis
    c.run()

    # collect conclusion
    actual_conclusion = c.conclusion

    expected_conclusion = '''conclusion : found counterexample : ''' + \
                          '''[\'clock("a","c",1,2);\', ''' + \
                          '''\'clock("a","b",2,3);\', ''' + \
                          '''\'clock("a","b",1,2);\', ''' + \
                          '''\'_NOT_clock("a","c",2,3);\']'''

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
    argDict[ "EOT" ]            = 3
    argDict[ "EFF" ]            = 0
    argDict[ "nodes" ]          = [ "a", "b", "c" ]
    argDict[ "settings" ]       = "./settings_files/settings_dm_allow_not_clocks.ini"
    argDict[ "evaluator"]       = "c4"
    argDict[ "crashes" ]        = 0
    argDict[ "data_save_path" ] = "./data/" + test_id + "/"

    # --------------------------------------------------------------- #
    # run chaoxis

    # instantiate chaoxis object
    c = Chaoxis.Chaoxis( argDict, test_id )

    # run chaoxis
    c.run()

    # collect conclusion
    actual_conclusion = c.conclusion

    expected_conclusion = '''conclusion : found counterexample : ''' + \
                          '''[\'clock("a","c",1,2);\', ''' + \
                          '''\'_NOT_clock("a","b",1,2);\']'''

    self.assertEqual( actual_conclusion, expected_conclusion )

    logging.debug( "  TEST " + test_id + " : actual_conclusion   = " + actual_conclusion )
    logging.debug( "  TEST " + test_id + " : expected_conclusion = " + expected_conclusion )


  #############
  #  ASYNC 1  #
  #############
  def test_async_1( self ) :

    test_id = "async_1"
    logging.debug( ">> RUNNING TEST '" + test_id + "' <<<" )

    # --------------------------------------------------------------- #
    # specify input file paths

    inputfile = "./dedalus_drivers/" + test_id + "_driver.ded"

    # --------------------------------------------------------------- #
    # define sys.argv

    argDict = {}
    argDict[ "debug" ]          = True
    argDict[ "file" ]           = inputfile
    argDict[ "EOT" ]            = 3
    argDict[ "EFF" ]            = 0
    argDict[ "nodes" ]          = [ "Node1", "Node2", "Server" ]
    argDict[ "settings" ]       = "./settings_files/settings_dm_allow_not_clocks.ini"
    argDict[ "evaluator"]       = "c4"
    argDict[ "crashes" ]        = 0
    argDict[ "data_save_path" ] = "./data/" + test_id + "/"

    # --------------------------------------------------------------- #
    # run chaoxis

    # instantiate chaoxis object
    c = Chaoxis.Chaoxis( argDict, test_id )
    #c = Chaoxis.Chaoxis( argDict, test_id, [ '_NOT_clock("Node2","Server",2,1);' ] )

    # run chaoxis
    c.run()

    # collect conclusion
    actual_conclusion = c.conclusion

    expected_conclusion = '''conclusion : found counterexample : ''' + \
                          '''[\'_NOT_clock("Node2","Server",2,1);\', ''' + \
                          '''\'_NOT_clock("Node2","Server",3,2);\', ''' + \
                          '''\'_NOT_clock("Node1","Server",3,1);\', ''' + \
                          '''\'_NOT_clock("Node2","Server",2,2);\', ''' + \
                          '''\'clock("Node1","Server",2,2);\', ''' + \
                          '''\'clock("Node2","Server",1,1);\', ''' + \
                          '''\'_NOT_clock("Node1","Server",1,2);\', ''' + \
                          '''\'clock("Node2","Server",3,1);\', ''' + \
                          '''\'clock("Node1","Server",2,1);\', ''' + \
                          '''\'clock("Node1","Server",3,2);\', ''' + \
                          '''\'clock("Node1","Server",1,1);\']'''

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
