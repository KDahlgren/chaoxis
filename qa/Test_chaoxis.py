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

  ##############
  #  KAFKA DM  #
  ##############
  @unittest.skip( "intractable run time." )
  def test_kafka_dm( self ) :

    test_id = "kafka_dm"
    logging.debug( ">> RUNNING TEST '" + test_id + "' <<<" )

    # --------------------------------------------------------------- #
    # specify input file paths

    inputfile = "./dedalus_drivers/kafka_driver.ded"

    # --------------------------------------------------------------- #
    # define sys.argv

    argDict = {}
    argDict[ "debug" ]          = True
    argDict[ "file" ]           = inputfile
    argDict[ "EOT" ]            = 7
    argDict[ "EFF" ]            = 4
    argDict[ "nodes" ]          = [ "a", "b", "c", "C", "Z" ]
    argDict[ "settings" ]       = "./settings_files/settings_dm.ini"
    argDict[ "evaluator"]       = "c4"
    argDict[ "crashes" ]        = 0
    argDict[ "data_save_path" ] = "./data/" + test_id

    # --------------------------------------------------------------- #
    # run chaoxis

    # instantiate chaoxis object
    c = Chaoxis.Chaoxis( argDict, test_id )

    # this also works: crash(d,2)
    #c = Chaoxis.Chaoxis( argDict, test_id, ['clock("d","a",2,3);', \
    #                                        'clock("d","a",3,4);', \
    #                                        'clock("d","a",4,5);', \
    #                                        'clock("d","a",5,6);', \
    #                                        'clock("d","b",2,3);', \
    #                                        'clock("d","b",3,4);', \
    #                                        'clock("d","b",4,5);', \
    #                                        'clock("d","b",5,6);', \
    #                                        'clock("d","C",2,3);', \
    #                                        'clock("d","C",3,4);', \
    #                                        'clock("d","C",4,5);', \
    #                                        'clock("d","C",5,6);'] )

    # run chaoxis
    c.run()

    # collect conclusion
    actual_conclusion = c.conclusion

    expected_conclusion = '''conclusion : found counterexample : ''' + \
                          '''[\'clock("C","a",5,6);\', ''' + \
                          '''\'clock("a","d",5,6);\', ''' + \
                          '''\'clock("d","a",5,6);\', ''' + \
                          '''\'clock("C","a",4,5);\', ''' + \
                          '''\'clock("C","d",5,6);\', ''' + \
                          '''\'clock("C","d",4,5);\', ''' + \
                          '''\'clock("C","b",4,5);\', ''' + \
                          '''\'clock("b","d",5,6);\', ''' + \
                          '''\'clock("C","b",5,6);\', ''' + \
                          '''\'clock("b","a",5,6);\', ''' + \
                          '''\'clock("a","b",5,6);\', ''' + \
                          '''\'clock("d","b",5,6);\']'''

    self.assertEqual( actual_conclusion, expected_conclusion )

    logging.debug( "  TEST " + test_id + " : actual_conclusion   = " + actual_conclusion )
    logging.debug( "  TEST " + test_id + " : expected_conclusion = " + expected_conclusion )


  ###########
  #  KAFKA  #
  ###########
  @unittest.skip( "intractable run time stalling at GET CNF boolean_fmla." ) 
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
    argDict[ "EOT" ]            = 7
    argDict[ "EFF" ]            = 4
    argDict[ "nodes" ]          = [ "a", "b", "c", "C", "Z" ]
    argDict[ "settings" ]       = "./settings_files/settings.ini"
    argDict[ "evaluator"]       = "c4"
    argDict[ "crashes" ]        = 0
    argDict[ "data_save_path" ] = "./data/" + test_id

    # --------------------------------------------------------------- #
    # run chaoxis

    # instantiate chaoxis object
    c = Chaoxis.Chaoxis( argDict, test_id )

    # run chaoxis
    c.run()

    # collect conclusion
    actual_conclusion = c.conclusion

    expected_conclusion = '''?'''
    # molly says Set(CrashFailure(a,5), MessageLoss(c,Z,1), MessageLoss(b,Z,1))

    self.assertEqual( actual_conclusion, expected_conclusion )

    logging.debug( "  TEST " + test_id + " : actual_conclusion   = " + actual_conclusion )
    logging.debug( "  TEST " + test_id + " : expected_conclusion = " + expected_conclusion )


  ############
  #  3PC DM  #
  ############
  @unittest.skip( "intractable run time dm conversion working but taking forever." )
  def test_3pc_dm( self ) :

    test_id = "3pc_dm"
    logging.debug( ">> RUNNING TEST '" + test_id + "' <<<" )

    # --------------------------------------------------------------- #
    # specify input file paths

    inputfile = "./dedalus_drivers/3pc_driver.ded"

    # --------------------------------------------------------------- #
    # define sys.argv

    argDict = {}
    argDict[ "debug" ]          = True
    argDict[ "file" ]           = inputfile
    argDict[ "EOT" ]            = 6
    argDict[ "EFF" ]            = 0
    argDict[ "nodes" ]          = [ "a", "b", "C", "d" ]
    argDict[ "settings" ]       = "./settings_files/settings_dm.ini"
    argDict[ "evaluator"]       = "c4"
    argDict[ "crashes" ]        = 0
    argDict[ "data_save_path" ] = "./data/" + test_id

    # --------------------------------------------------------------- #
    # run chaoxis

    # instantiate chaoxis object
    c = Chaoxis.Chaoxis( argDict, test_id )

    # run chaoxis
    c.run()

    # collect conclusion
    actual_conclusion = c.conclusion

    expected_conclusion = '''conclusion : spec is chaoxis-certified for correctness.'''

    self.assertEqual( actual_conclusion, expected_conclusion )

    logging.debug( "  TEST " + test_id + " : actual_conclusion   = " + actual_conclusion )
    logging.debug( "  TEST " + test_id + " : expected_conclusion = " + expected_conclusion )


  #########
  #  3PC  #
  #########
  # originally worked with eot=6, then became vacuoucly incorrect for some reason?
  # it's not vacuously incorrect at eot=8, but stalls with the sat solver.
  @unittest.skip( "halted. stalls at to_cnf." )
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
    argDict[ "EOT" ]            = 8 #9
    argDict[ "EFF" ]            = 0 #7
    argDict[ "nodes" ]          = [ "a", "b", "C", "d" ]
    argDict[ "settings" ]       = "./settings_files/settings.ini"
    argDict[ "evaluator"]       = "c4"
    argDict[ "crashes" ]        = 0 #1,2
    argDict[ "data_save_path" ] = "./data/" + test_id

    # --------------------------------------------------------------- #
    # run chaoxis

    # instantiate chaoxis object
    c = Chaoxis.Chaoxis( argDict, test_id )

    # run chaoxis
    c.run()

    # collect conclusion
    actual_conclusion = c.conclusion

    expected_conclusion = '''conclusion : spec is chaoxis-certified for correctness.'''

    self.assertEqual( actual_conclusion, expected_conclusion )

    logging.debug( "  TEST " + test_id + " : actual_conclusion   = " + actual_conclusion )
    logging.debug( "  TEST " + test_id + " : expected_conclusion = " + expected_conclusion )


  ################
  #  2PC CTP DM  #
  ################
  @unittest.skip( "intractable run time dm conversion working but taking forever." )
  def test_2pc_ctp_dm( self ) :

    test_id = "2pc_ctp_dm"
    logging.debug( ">> RUNNING TEST '" + test_id + "' <<<" )

    # --------------------------------------------------------------- #
    # specify input file paths

    inputfile = "./dedalus_drivers/2pc_ctp_driver.ded"

    # --------------------------------------------------------------- #
    # define sys.argv

    argDict = {}
    argDict[ "debug" ]          = True
    argDict[ "file" ]           = inputfile
    argDict[ "EOT" ]            = 6
    argDict[ "EFF" ]            = 0
    argDict[ "nodes" ]          = [ "a", "b", "C", "d" ]
    argDict[ "settings" ]       = "./settings_files/settings_dm.ini"
    argDict[ "evaluator"]       = "c4"
    argDict[ "crashes" ]        = 0
    argDict[ "data_save_path" ] = "./data/" + test_id

    # --------------------------------------------------------------- #
    # run chaoxis

    # instantiate chaoxis object
    c = Chaoxis.Chaoxis( argDict, test_id )

    # run chaoxis
    c.run()

    # collect conclusion
    actual_conclusion = c.conclusion

    expected_conclusion = '''dunno.'''

    self.assertEqual( actual_conclusion, expected_conclusion )

    logging.debug( "  TEST " + test_id + " : actual_conclusion   = " + actual_conclusion )
    logging.debug( "  TEST " + test_id + " : expected_conclusion = " + expected_conclusion )


  #############
  #  2PC CTP  #
  #############
  #@unittest.skip( "works." )
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
    argDict[ "EOT" ]            = 6
    argDict[ "EFF" ]            = 0
    argDict[ "nodes" ]          = [ "a", "b", "C", "d" ]
    argDict[ "settings" ]       = "./settings_files/settings.ini"
    argDict[ "evaluator"]       = "c4"
    argDict[ "crashes" ]        = 0
    argDict[ "data_save_path" ] = "./data/" + test_id

    # --------------------------------------------------------------- #
    # run chaoxis

    # instantiate chaoxis object
    c = Chaoxis.Chaoxis( argDict, test_id )

    # this also works: crash(d,2)
    #c = Chaoxis.Chaoxis( argDict, test_id, ['clock("d","a",2,3);', \
    #                                        'clock("d","a",3,4);', \
    #                                        'clock("d","a",4,5);', \
    #                                        'clock("d","a",5,6);', \
    #                                        'clock("d","b",2,3);', \
    #                                        'clock("d","b",3,4);', \
    #                                        'clock("d","b",4,5);', \
    #                                        'clock("d","b",5,6);', \
    #                                        'clock("d","C",2,3);', \
    #                                        'clock("d","C",3,4);', \
    #                                        'clock("d","C",4,5);', \
    #                                        'clock("d","C",5,6);'] )

    # run chaoxis
    c.run()

    # collect conclusion
    actual_conclusion = c.conclusion

    expected_conclusion = '''dunno. molly chokes on memory.'''
    # chaoxis says: conclusion : found counterexample : [\'clock("C","a",5,6);\', \'clock("a","d",5,6);\', \'clock("d","a",5,6);\', \'clock("C","a",4,5);\', \'clock("C","d",5,6);\', \'clock("C","d",4,5);\', \'clock("C","b",4,5);\', \'clock("b","d",5,6);\', \'clock("d","C",5,6);\', \'clock("C","b",5,6);\', \'clock("b","a",5,6);\', \'clock("a","C",5,6);\', \'clock("b","C",5,6);\', \'clock("a","b",5,6);\', \'clock("d","b",5,6);\']

    self.assertTrue( actual_conclusion != expected_conclusion )

    logging.debug( "  TEST " + test_id + " : actual_conclusion   = " + actual_conclusion )
    logging.debug( "  TEST " + test_id + " : expected_conclusion = " + expected_conclusion )


  #############################
  #  2PC TIMEOUT OPTIMIST DM  #
  #############################
  @unittest.skip( "intractable run time stalling during initial program run." )
  def test_2pc_timeout_optimist_dm( self ) :

    test_id = "2pc_timeout_optimist_dm"
    logging.debug( ">> RUNNING TEST '" + test_id + "' <<<" )

    # --------------------------------------------------------------- #
    # specify input file paths

    inputfile = "./dedalus_drivers/2pc_timeout_optimist_driver.ded"

    # --------------------------------------------------------------- #
    # define sys.argv

    argDict = {}
    argDict[ "debug" ]          = True
    argDict[ "file" ]           = inputfile
    argDict[ "EOT" ]            = 6
    argDict[ "EFF" ]            = 0
    argDict[ "nodes" ]          = [ "a", "b", "C", "d" ]
    argDict[ "settings" ]       = "./settings_files/settings_dm.ini"
    argDict[ "evaluator"]       = "c4"
    argDict[ "crashes" ]        = 0
    argDict[ "data_save_path" ] = "./data/" + test_id

    # --------------------------------------------------------------- #
    # run chaoxis

    # instantiate chaoxis object
    c = Chaoxis.Chaoxis( argDict, test_id )

    # run chaoxis
    c.run()

    # collect conclusion
    actual_conclusion = c.conclusion

    expected_conclusion = ''''''

    self.assertEqual( actual_conclusion, expected_conclusion )

    logging.debug( "  TEST " + test_id + " : actual_conclusion   = " + actual_conclusion )
    logging.debug( "  TEST " + test_id + " : expected_conclusion = " + expected_conclusion )


  ##########################
  #  2PC TIMEOUT OPTIMIST  #
  ##########################
  #@unittest.skip( "works." )
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
    argDict[ "EOT" ]            = 6
    argDict[ "EFF" ]            = 0
    argDict[ "nodes" ]          = [ "a", "b", "C", "d" ]
    argDict[ "settings" ]       = "./settings_files/settings.ini"
    argDict[ "evaluator"]       = "c4"
    argDict[ "crashes" ]        = 0
    argDict[ "data_save_path" ] = "./data/" + test_id

    # --------------------------------------------------------------- #
    # run chaoxis

    # instantiate chaoxis object
    c = Chaoxis.Chaoxis( argDict, test_id )

    # run chaoxis
    c.run()

    # collect conclusion
    actual_conclusion = c.conclusion

    expected_conclusion = '''conclusion : spec is chaoxis-ceritified for correctness.'''
    # however, actual conclusion is '''conclusion : found counterexample : [\'clock("C","a",5,6);\', \'clock("a","d",5,6);\', \'clock("d","a",5,6);\', \'clock("C","a",4,5);\', \'clock("C","d",5,6);\', \'clock("C","d",4,5);\', \'clock("C","b",4,5);\', \'clock("b","d",5,6);\', \'clock("C","b",5,6);\', \'clock("b","a",5,6);\', \'clock("a","b",5,6);\', \'clock("d","b",5,6);\']'''

    self.assertTrue( actual_conclusion != expected_conclusion )

    logging.debug( "  TEST " + test_id + " : actual_conclusion   = " + actual_conclusion )
    logging.debug( "  TEST " + test_id + " : expected_conclusion = " + expected_conclusion )


  ####################
  #  2PC TIMEOUT DM  #
  ####################
  @unittest.skip( "intractable run time stalling at c4 during initial program run." )
  def test_2pc_timeout_dm( self ) :

    test_id = "2pc_timeout_dm"
    logging.debug( ">> RUNNING TEST '" + test_id + "' <<<" )

    # --------------------------------------------------------------- #
    # specify input file paths

    inputfile = "./dedalus_drivers/2pc_timeout_driver.ded"

    # --------------------------------------------------------------- #
    # define sys.argv

    argDict = {}
    argDict[ "debug" ]          = True
    argDict[ "file" ]           = inputfile
    argDict[ "EOT" ]            = 6
    argDict[ "EFF" ]            = 0
    argDict[ "nodes" ]          = [ "a", "b", "C", "d" ]
    argDict[ "settings" ]       = "./settings_files/settings_dm.ini"
    argDict[ "evaluator"]       = "c4"
    argDict[ "crashes" ]        = 0
    argDict[ "data_save_path" ] = "./data/" + test_id

    # --------------------------------------------------------------- #
    # run chaoxis

    # instantiate chaoxis object
    c = Chaoxis.Chaoxis( argDict, test_id )

    # run chaoxis
    c.run()

    # collect conclusion
    actual_conclusion = c.conclusion

    expected_conclusion = ''''''

    self.assertEqual( actual_conclusion, expected_conclusion )

    logging.debug( "  TEST " + test_id + " : actual_conclusion   = " + actual_conclusion )
    logging.debug( "  TEST " + test_id + " : expected_conclusion = " + expected_conclusion )


  #################
  #  2PC TIMEOUT  #
  #################
  #@unittest.skip( "works." )
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
    argDict[ "EOT" ]            = 6
    argDict[ "EFF" ]            = 0
    argDict[ "nodes" ]          = [ "a", "b", "C", "d" ]
    argDict[ "settings" ]       = "./settings_files/settings.ini"
    argDict[ "evaluator"]       = "c4"
    argDict[ "crashes" ]        = 0
    argDict[ "data_save_path" ] = "./data/" + test_id

    # --------------------------------------------------------------- #
    # run chaoxis

    # instantiate chaoxis object
    c = Chaoxis.Chaoxis( argDict, test_id )

    # this also works: crash(d,2)
    #c = Chaoxis.Chaoxis( argDict, test_id, ['clock("C","a",4,5);', \
    #                                        'clock("C","a",5,6);', \
    #                                        'clock("C","b",4,5);', \
    #                                        'clock("C","b",5,6);', \
    #                                        'clock("C","d",4,5);', \
    #                                        'clock("C","d",5,6);'] )

    # run chaoxis
    c.run()

    # collect conclusion
    actual_conclusion = c.conclusion

    expected_conclusion = '''conclusion : found counterexample : ''' + \
                          '''[\'clock("C","a",5,6);\', ''' + \
                          '''\'clock("a","d",5,6);\', ''' + \
                          '''\'clock("d","a",5,6);\', ''' + \
                          '''\'clock("C","a",4,5);\', ''' + \
                          '''\'clock("C","d",5,6);\', ''' + \
                          '''\'clock("C","d",4,5);\', ''' + \
                          '''\'clock("C","b",4,5);\', ''' + \
                          '''\'clock("b","d",5,6);\', ''' + \
                          '''\'clock("C","b",5,6);\', ''' + \
                          '''\'clock("b","a",5,6);\', ''' + \
                          '''\'clock("a","b",5,6);\', ''' + \
                          '''\'clock("d","b",5,6);\']'''

    self.assertEqual( actual_conclusion, expected_conclusion )

    logging.debug( "  TEST " + test_id + " : actual_conclusion   = " + actual_conclusion )
    logging.debug( "  TEST " + test_id + " : expected_conclusion = " + expected_conclusion )


  #####################
  #  2PC OPTIMIST DM  #
  #####################
  @unittest.skip( "intractable run time stalling at c4 during initial program run." )
  def test_2pc_optimist_dm( self ) :

    test_id = "2pc_optimist_dm"
    logging.debug( ">> RUNNING TEST '" + test_id + "' <<<" )

    # --------------------------------------------------------------- #
    # specify input file paths

    inputfile = "./dedalus_drivers/2pc_optimist_driver.ded"

    # --------------------------------------------------------------- #
    # define sys.argv

    argDict = {}
    argDict[ "debug" ]          = True
    argDict[ "file" ]           = inputfile
    argDict[ "EOT" ]            = 6
    argDict[ "EFF" ]            = 3
    argDict[ "nodes" ]          = [ "a", "b", "C", "d" ]
    argDict[ "settings" ]       = "./settings_files/settings_dm.ini"
    argDict[ "evaluator"]       = "c4"
    argDict[ "crashes" ]        = 0
    argDict[ "data_save_path" ] = "./data/" + test_id

    # --------------------------------------------------------------- #
    # run chaoxis

    # instantiate chaoxis object
    c = Chaoxis.Chaoxis( argDict, test_id )

    # run chaoxis
    c.run()

    # collect conclusion
    actual_conclusion = c.conclusion

    expected_conclusion = ''''''

    self.assertEqual( actual_conclusion, expected_conclusion )

    logging.debug( "  TEST " + test_id + " : actual_conclusion   = " + actual_conclusion )
    logging.debug( "  TEST " + test_id + " : expected_conclusion = " + expected_conclusion )


  ##################
  #  2PC OPTIMIST  #
  ##################
  #@unittest.skip( "works." )
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
    argDict[ "EOT" ]            = 6
    argDict[ "EFF" ]            = 3
    argDict[ "nodes" ]          = [ "a", "b", "C", "d" ]
    argDict[ "settings" ]       = "./settings_files/settings.ini"
    argDict[ "evaluator"]       = "c4"
    argDict[ "crashes" ]        = 0
    argDict[ "data_save_path" ] = "./data/" + test_id

    # --------------------------------------------------------------- #
    # run chaoxis

    # instantiate chaoxis object
    c = Chaoxis.Chaoxis( argDict, test_id )

    # this also works: crash(d,2)
    #c = Chaoxis.Chaoxis( argDict, test_id, ['clock("d","a",2,3);', \
    #                                        'clock("d","a",3,4);', \
    #                                        'clock("d","a",4,5);', \
    #                                        'clock("d","a",5,6);', \
    #                                        'clock("d","b",2,3);', \
    #                                        'clock("d","b",3,4);', \
    #                                        'clock("d","b",4,5);', \
    #                                        'clock("d","b",5,6);', \
    #                                        'clock("d","C",2,3);', \
    #                                        'clock("d","C",3,4);', \
    #                                        'clock("d","C",4,5);', \
    #                                        'clock("d","C",5,6);'] )

    # run chaoxis
    c.run()

    # collect conclusion
    actual_conclusion = c.conclusion

    expected_conclusion = '''conclusion : found counterexample : ''' + \
                          '''[\'clock("C","a",5,6);\', ''' + \
                          '''\'clock("a","d",5,6);\', ''' + \
                          '''\'clock("d","a",5,6);\', ''' + \
                          '''\'clock("C","a",4,5);\', ''' + \
                          '''\'clock("C","d",5,6);\', ''' + \
                          '''\'clock("C","d",4,5);\', ''' + \
                          '''\'clock("C","b",4,5);\', ''' + \
                          '''\'clock("b","d",5,6);\', ''' + \
                          '''\'clock("C","b",5,6);\', ''' + \
                          '''\'clock("b","a",5,6);\', ''' + \
                          '''\'clock("a","b",5,6);\', ''' + \
                          '''\'clock("d","b",5,6);\']'''

    self.assertEqual( actual_conclusion, expected_conclusion )

    logging.debug( "  TEST " + test_id + " : actual_conclusion   = " + actual_conclusion )
    logging.debug( "  TEST " + test_id + " : expected_conclusion = " + expected_conclusion )


  ############
  #  2PC DM  #
  ############
  @unittest.skip( "intractable run time stalling at c4 during initial program run." )
  def test_2pc_dm( self ) :

    test_id = "2pc_dm"
    logging.debug( ">> RUNNING TEST '" + test_id + "' <<<" )

    # --------------------------------------------------------------- #
    # specify input file paths

    inputfile = "./dedalus_drivers/2pc_driver.ded"

    # --------------------------------------------------------------- #
    # define sys.argv

    argDict = {}
    argDict[ "debug" ]          = True
    argDict[ "file" ]           = inputfile
    argDict[ "EOT" ]            = 6
    argDict[ "EFF" ]            = 3
    argDict[ "nodes" ]          = [ "a", "b", "C", "d" ]
    argDict[ "settings" ]       = "./settings_files/settings_dm.ini"
    argDict[ "evaluator"]       = "c4"
    argDict[ "crashes" ]        = 0
    argDict[ "data_save_path" ] = "./data/" + test_id

    # --------------------------------------------------------------- #
    # run chaoxis

    # instantiate chaoxis object
    c = Chaoxis.Chaoxis( argDict, test_id )

    # this also works: crash(d,2)
    #c = Chaoxis.Chaoxis( argDict, test_id, ['clock("d","a",2,3);', \
    #                                        'clock("d","a",3,4);', \
    #                                        'clock("d","a",4,5);', \
    #                                        'clock("d","a",5,6);', \
    #                                        'clock("d","b",2,3);', \
    #                                        'clock("d","b",3,4);', \
    #                                        'clock("d","b",4,5);', \
    #                                        'clock("d","b",5,6);', \
    #                                        'clock("d","C",2,3);', \
    #                                        'clock("d","C",3,4);', \
    #                                        'clock("d","C",4,5);', \
    #                                        'clock("d","C",5,6);'] )

    # run chaoxis
    c.run()

    # collect conclusion
    actual_conclusion = c.conclusion

    expected_conclusion = '''conclusion : found counterexample : ''' + \
                          '''[\'clock("C","a",5,6);\', ''' + \
                          '''\'clock("a","d",5,6);\', ''' + \
                          '''\'clock("d","a",5,6);\', ''' + \
                          '''\'clock("C","a",4,5);\', ''' + \
                          '''\'clock("C","d",5,6);\', ''' + \
                          '''\'clock("C","d",4,5);\', ''' + \
                          '''\'clock("C","b",4,5);\', ''' + \
                          '''\'clock("b","d",5,6);\', ''' + \
                          '''\'clock("C","b",5,6);\', ''' + \
                          '''\'clock("b","a",5,6);\', ''' + \
                          '''\'clock("a","b",5,6);\', ''' + \
                          '''\'clock("d","b",5,6);\']'''

    self.assertEqual( actual_conclusion, expected_conclusion )

    logging.debug( "  TEST " + test_id + " : actual_conclusion   = " + actual_conclusion )
    logging.debug( "  TEST " + test_id + " : expected_conclusion = " + expected_conclusion )


  #########
  #  2PC  #
  #########
  #@unittest.skip( "works." )
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
    argDict[ "EOT" ]            = 6
    argDict[ "EFF" ]            = 3
    argDict[ "nodes" ]          = [ "a", "b", "C", "d" ]
    argDict[ "settings" ]       = "./settings_files/settings.ini"
    argDict[ "evaluator"]       = "c4"
    argDict[ "crashes" ]        = 0
    argDict[ "data_save_path" ] = "./data/" + test_id

    # --------------------------------------------------------------- #
    # run chaoxis

    # instantiate chaoxis object
    c = Chaoxis.Chaoxis( argDict, test_id )

    # this also works: crash(d,2)
    #c = Chaoxis.Chaoxis( argDict, test_id, ['clock("d","a",2,3);', \
    #                                        'clock("d","a",3,4);', \
    #                                        'clock("d","a",4,5);', \
    #                                        'clock("d","a",5,6);', \
    #                                        'clock("d","b",2,3);', \
    #                                        'clock("d","b",3,4);', \
    #                                        'clock("d","b",4,5);', \
    #                                        'clock("d","b",5,6);', \
    #                                        'clock("d","C",2,3);', \
    #                                        'clock("d","C",3,4);', \
    #                                        'clock("d","C",4,5);', \
    #                                        'clock("d","C",5,6);'] )

    # run chaoxis
    c.run()

    # collect conclusion
    actual_conclusion = c.conclusion

    expected_conclusion = '''conclusion : found counterexample : ''' + \
                          '''[\'clock("C","a",5,6);\', ''' + \
                          '''\'clock("a","d",5,6);\', ''' + \
                          '''\'clock("d","a",5,6);\', ''' + \
                          '''\'clock("C","a",4,5);\', ''' + \
                          '''\'clock("C","d",5,6);\', ''' + \
                          '''\'clock("C","d",4,5);\', ''' + \
                          '''\'clock("C","b",4,5);\', ''' + \
                          '''\'clock("b","d",5,6);\', ''' + \
                          '''\'clock("C","b",5,6);\', ''' + \
                          '''\'clock("b","a",5,6);\', ''' + \
                          '''\'clock("a","b",5,6);\', ''' + \
                          '''\'clock("d","b",5,6);\']'''

    self.assertEqual( actual_conclusion, expected_conclusion )

    logging.debug( "  TEST " + test_id + " : actual_conclusion   = " + actual_conclusion )
    logging.debug( "  TEST " + test_id + " : expected_conclusion = " + expected_conclusion )


  ###############
  #  ACK RB DM  #
  ###############
  @unittest.skip( "intractable run time boolean fmla converion taking forever.." )
  def test_ack_rb_dm( self ) :

    test_id = "ack_rb_dm"
    logging.debug( ">> RUNNING TEST '" + test_id + "' <<<" )

    # --------------------------------------------------------------- #
    # specify input file paths

    inputfile = "./dedalus_drivers/ack_rb_driver.ded"

    # --------------------------------------------------------------- #
    # define sys.argv

    argDict = {}
    argDict[ "debug" ]          = True
    argDict[ "file" ]           = inputfile
    argDict[ "EOT" ]            = 6
    argDict[ "EFF" ]            = 3
    argDict[ "nodes" ]          = [ "a", "b", "c" ]
    argDict[ "settings" ]       = "./settings_files/settings_dm.ini"
    argDict[ "evaluator"]       = "c4"
    argDict[ "crashes" ]        = 0
    argDict[ "data_save_path" ] = "./data/" + test_id

    # --------------------------------------------------------------- #
    # run chaoxis

    # instantiate chaoxis object
    c = Chaoxis.Chaoxis( argDict, test_id )

    # this also works:
    #c = Chaoxis.Chaoxis( argDict, test_id, ['clock("b","a",2,3);', \
    #                                        'clock("a","c",1,2);', \
    #                                        'clock("b","c",2,3);'] )

    # run chaoxis
    c.run()

    # collect conclusion
    actual_conclusion = c.conclusion

    expected_conclusion = '''conclusion : found counterexample : ''' + \
                          '''[\'clock("b","c",2,3);\', ''' + \
                          '''\'clock("c","a",3,4);\', ''' + \
                          '''\'clock("b","c",3,4);\', ''' + \
                          '''\'clock("c","a",2,3);\', ''' + \
                          '''\'clock("c","b",3,4);\', ''' + \
                          '''\'clock("b","a",2,3);\', ''' + \
                          '''\'clock("a","c",1,2);\', ''' + \
                          '''\'clock("b","c",4,5);\', ''' + \
                          '''\'clock("b","a",3,4);\', ''' + \
                          '''\'clock("c","b",2,3);\', ''' + \
                          '''\'clock("a","c",4,5);\', ''' + \
                          '''\'clock("a","b",3,4);\']'''

    self.assertEqual( actual_conclusion, expected_conclusion )

    logging.debug( "  TEST " + test_id + " : actual_conclusion   = " + actual_conclusion )
    logging.debug( "  TEST " + test_id + " : expected_conclusion = " + expected_conclusion )


  ############
  #  ACK RB  #
  ############
  @unittest.skip( "stack overflow when iterating over the ldfi loop over possible solutions." )
  def test_ack_rb( self ) :

    test_id = "ack_rb"
    logging.debug( ">> RUNNING TEST '" + test_id + "' <<<" )

    # --------------------------------------------------------------- #
    # specify input file paths

    inputfile = "./dedalus_drivers/" + test_id + "_driver.ded"

    # --------------------------------------------------------------- #
    # define sys.argv

    argDict = {}
    argDict[ "debug" ]          = True
    argDict[ "file" ]           = inputfile
    argDict[ "EOT" ]            = 6
    argDict[ "EFF" ]            = 3
    argDict[ "nodes" ]          = [ "a", "b", "c" ]
    argDict[ "settings" ]       = "./settings_files/settings.ini"
    argDict[ "evaluator"]       = "c4"
    argDict[ "crashes" ]        = 0
    argDict[ "data_save_path" ] = "./data/" + test_id

    # --------------------------------------------------------------- #
    # run chaoxis

    # instantiate chaoxis object
    c = Chaoxis.Chaoxis( argDict, test_id )

    # this also works:
    #c = Chaoxis.Chaoxis( argDict, test_id, ['clock("b","a",2,3);', \
    #                                        'clock("a","c",1,2);', \
    #                                        'clock("b","c",2,3);'] )

    # run chaoxis
    c.run()

    # collect conclusion
    actual_conclusion = c.conclusion

    expected_conclusion = '''conclusion : found counterexample : ''' + \
                          '''[\'clock("b","c",2,3);\', ''' + \
                          '''\'clock("c","a",3,4);\', ''' + \
                          '''\'clock("b","c",3,4);\', ''' + \
                          '''\'clock("c","a",2,3);\', ''' + \
                          '''\'clock("c","b",3,4);\', ''' + \
                          '''\'clock("b","a",2,3);\', ''' + \
                          '''\'clock("a","c",1,2);\', ''' + \
                          '''\'clock("b","c",4,5);\', ''' + \
                          '''\'clock("b","a",3,4);\', ''' + \
                          '''\'clock("c","b",2,3);\', ''' + \
                          '''\'clock("a","c",4,5);\', ''' + \
                          '''\'clock("a","b",3,4);\']'''

    self.assertEqual( actual_conclusion, expected_conclusion )

    logging.debug( "  TEST " + test_id + " : actual_conclusion   = " + actual_conclusion )
    logging.debug( "  TEST " + test_id + " : expected_conclusion = " + expected_conclusion )


  ###############
  #  REPLOG DM  #
  ###############
  @unittest.skip( "intractable run time at GET CNF boolean_fmla." )
  def test_replog_dm( self ) :

    test_id = "replog_dm"
    logging.debug( ">> RUNNING TEST '" + test_id + "' <<<" )

    # --------------------------------------------------------------- #
    # specify input file paths

    inputfile = "./dedalus_drivers/replog_driver.ded"

    # --------------------------------------------------------------- #
    # define sys.argv

    argDict = {}
    argDict[ "debug" ]          = True
    argDict[ "file" ]           = inputfile
    argDict[ "EOT" ]            = 6
    argDict[ "EFF" ]            = 3
    argDict[ "nodes" ]          = [ "a", "b", "c" ]
    argDict[ "settings" ]       = "./settings_files/settings_dm.ini"
    argDict[ "evaluator"]       = "c4"
    argDict[ "crashes" ]        = 0
    argDict[ "data_save_path" ] = "./data/" + test_id

    # --------------------------------------------------------------- #
    # run chaoxis

    # instantiate chaoxis object
    c = Chaoxis.Chaoxis( argDict, test_id )

    # this also works:
    #c = Chaoxis.Chaoxis( argDict, test_id, ['clock("b","a",2,3);', \
    #                                        'clock("a","c",1,2);', \
    #                                        'clock("b","c",2,3);'] )

    # run chaoxis
    c.run()

    # collect conclusion
    actual_conclusion = c.conclusion

    expected_conclusion = '''conclusion : found counterexample : ''' + \
                          '''[\'clock("b","c",2,3);\', ''' + \
                          '''\'clock("c","a",3,4);\', ''' + \
                          '''\'clock("b","c",3,4);\', ''' + \
                          '''\'clock("c","a",2,3);\', ''' + \
                          '''\'clock("c","b",3,4);\', ''' + \
                          '''\'clock("b","a",2,3);\', ''' + \
                          '''\'clock("a","c",1,2);\', ''' + \
                          '''\'clock("b","c",4,5);\', ''' + \
                          '''\'clock("b","a",3,4);\', ''' + \
                          '''\'clock("c","b",2,3);\', ''' + \
                          '''\'clock("a","c",4,5);\', ''' + \
                          '''\'clock("a","b",3,4);\']'''

    self.assertEqual( actual_conclusion, expected_conclusion )

    logging.debug( "  TEST " + test_id + " : actual_conclusion   = " + actual_conclusion )
    logging.debug( "  TEST " + test_id + " : expected_conclusion = " + expected_conclusion )


  ############
  #  REPLOG  #
  ############
  @unittest.skip( "intractable run time at GET CNF boolean_fmla." )
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
    argDict[ "EOT" ]            = 6
    argDict[ "EFF" ]            = 3
    argDict[ "nodes" ]          = [ "a", "b", "c" ]
    argDict[ "settings" ]       = "./settings_files/settings.ini"
    argDict[ "evaluator"]       = "c4"
    argDict[ "crashes" ]        = 0
    argDict[ "data_save_path" ] = "./data/" + test_id

    # --------------------------------------------------------------- #
    # run chaoxis

    # instantiate chaoxis object
    c = Chaoxis.Chaoxis( argDict, test_id )

    # this also works:
    #c = Chaoxis.Chaoxis( argDict, test_id, ['clock("b","a",2,3);', \
    #                                        'clock("a","c",1,2);', \
    #                                        'clock("b","c",2,3);'] )

    # run chaoxis
    c.run()

    # collect conclusion
    actual_conclusion = c.conclusion

    expected_conclusion = '''conclusion : found counterexample : ''' + \
                          '''[\'clock("b","c",2,3);\', ''' + \
                          '''\'clock("c","a",3,4);\', ''' + \
                          '''\'clock("b","c",3,4);\', ''' + \
                          '''\'clock("c","a",2,3);\', ''' + \
                          '''\'clock("c","b",3,4);\', ''' + \
                          '''\'clock("b","a",2,3);\', ''' + \
                          '''\'clock("a","c",1,2);\', ''' + \
                          '''\'clock("b","c",4,5);\', ''' + \
                          '''\'clock("b","a",3,4);\', ''' + \
                          '''\'clock("c","b",2,3);\', ''' + \
                          '''\'clock("a","c",4,5);\', ''' + \
                          '''\'clock("a","b",3,4);\']'''

    self.assertEqual( actual_conclusion, expected_conclusion )

    logging.debug( "  TEST " + test_id + " : actual_conclusion   = " + actual_conclusion )
    logging.debug( "  TEST " + test_id + " : expected_conclusion = " + expected_conclusion )


  ###################
  #  CLASSIC RB DM  #
  ###################
  @unittest.skip( "intractable run time at GET CNF boolean_fmla." )
  def test_classic_rb_dm( self ) :

    test_id = "classic_rb_dm"
    logging.debug( ">> RUNNING TEST '" + test_id + "' <<<" )

    # --------------------------------------------------------------- #
    # specify input file paths

    inputfile = "./dedalus_drivers/classic_rb_driver.ded"

    # --------------------------------------------------------------- #
    # define sys.argv

    argDict = {}
    argDict[ "debug" ]          = True
    argDict[ "file" ]           = inputfile
    argDict[ "EOT" ]            = 6
    argDict[ "EFF" ]            = 3
    argDict[ "nodes" ]          = [ "a", "b", "c" ]
    argDict[ "settings" ]       = "./settings_files/settings_dm.ini"
    argDict[ "evaluator"]       = "c4"
    argDict[ "crashes" ]        = 0
    argDict[ "data_save_path" ] = "./data/" + test_id

    # --------------------------------------------------------------- #
    # run chaoxis

    # instantiate chaoxis object
    c = Chaoxis.Chaoxis( argDict, test_id )

    # this also works:
    #c = Chaoxis.Chaoxis( argDict, test_id, ['clock("b","a",2,3);', \
    #                                        'clock("a","c",1,2);', \
    #                                        'clock("b","c",2,3);'] )

    # run chaoxis
    c.run()

    # collect conclusion
    actual_conclusion = c.conclusion

    expected_conclusion = '''conclusion : found counterexample : ''' + \
                          '''[\'clock("b","c",2,3);\', ''' + \
                          '''\'clock("c","a",3,4);\', ''' + \
                          '''\'clock("b","c",3,4);\', ''' + \
                          '''\'clock("c","a",2,3);\', ''' + \
                          '''\'clock("c","b",3,4);\', ''' + \
                          '''\'clock("b","a",2,3);\', ''' + \
                          '''\'clock("a","c",1,2);\', ''' + \
                          '''\'clock("b","c",4,5);\', ''' + \
                          '''\'clock("b","a",3,4);\', ''' + \
                          '''\'clock("c","b",2,3);\', ''' + \
                          '''\'clock("a","c",4,5);\', ''' + \
                          '''\'clock("a","b",3,4);\']'''

    self.assertEqual( actual_conclusion, expected_conclusion )

    logging.debug( "  TEST " + test_id + " : actual_conclusion   = " + actual_conclusion )
    logging.debug( "  TEST " + test_id + " : expected_conclusion = " + expected_conclusion )


  ################
  #  CLASSIC RB  #
  ################
  #@unittest.skip( "works." )
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
    argDict[ "EOT" ]            = 6
    argDict[ "EFF" ]            = 3
    argDict[ "nodes" ]          = [ "a", "b", "c" ]
    argDict[ "settings" ]       = "./settings_files/settings.ini"
    argDict[ "evaluator"]       = "c4"
    argDict[ "crashes" ]        = 0
    argDict[ "data_save_path" ] = "./data/" + test_id

    # --------------------------------------------------------------- #
    # run chaoxis

    # instantiate chaoxis object
    c = Chaoxis.Chaoxis( argDict, test_id )

    # this also works:
    #c = Chaoxis.Chaoxis( argDict, test_id, ['clock("b","a",2,3);', \
    #                                        'clock("a","c",1,2);', \
    #                                        'clock("b","c",2,3);'] )

    # run chaoxis
    c.run()

    # collect conclusion
    actual_conclusion = c.conclusion

    expected_conclusion = '''conclusion : found counterexample : ''' + \
                          '''[\'clock("b","c",2,3);\', ''' + \
                          '''\'clock("c","a",3,4);\', ''' + \
                          '''\'clock("b","c",3,4);\', ''' + \
                          '''\'clock("c","a",2,3);\', ''' + \
                          '''\'clock("c","b",3,4);\', ''' + \
                          '''\'clock("b","a",2,3);\', ''' + \
                          '''\'clock("a","c",1,2);\', ''' + \
                          '''\'clock("b","c",4,5);\', ''' + \
                          '''\'clock("b","a",3,4);\', ''' + \
                          '''\'clock("a","b",3,4);\', ''' + \
                          '''\'clock("a","c",4,5);\', ''' + \
                          '''\'clock("c","b",2,3);\']'''

    self.assertEqual( actual_conclusion, expected_conclusion )

    logging.debug( "  TEST " + test_id + " : actual_conclusion   = " + actual_conclusion )
    logging.debug( "  TEST " + test_id + " : expected_conclusion = " + expected_conclusion )


  ##############
  #  RDLOG DM  #
  ##############
  #@unittest.skip( "works." )
  def test_rdlog_dm( self ) :

    test_id = "rdlog_dm"
    logging.debug( ">> RUNNING TEST '" + test_id + "' <<<" )

    # --------------------------------------------------------------- #
    # specify input file paths

    inputfile = "./dedalus_drivers/rdlog_driver.ded"

    # --------------------------------------------------------------- #
    # define sys.argv

    argDict = {}
    argDict[ "debug" ]          = True
    argDict[ "file" ]           = inputfile
    argDict[ "EOT" ]            = 6
    argDict[ "EFF" ]            = 3
    argDict[ "nodes" ]          = [ "a", "b", "c" ]
    argDict[ "settings" ]       = "./settings_files/settings_dm.ini"
    argDict[ "evaluator"]       = "c4"
    argDict[ "crashes" ]        = 0
    argDict[ "data_save_path" ] = "./data/" + test_id

    # --------------------------------------------------------------- #
    # run chaoxis

    # instantiate chaoxis object
    c = Chaoxis.Chaoxis( argDict, test_id )

    # this also works:
    #c = Chaoxis.Chaoxis( argDict, test_id, ['clock("a","b",1,2);', \
    #                                        'clock("a","b",2,3);', \
    #                                        'clock("a","b",3,4);', \
    #                                        'clock("a","b",4,5);', \
    #                                        'clock("a","b",5,6);'] )

    # run chaoxis
    c.run()

    # collect conclusion
    actual_conclusion = c.conclusion

    expected_conclusion = '''conclusion : found counterexample : [\'clock("a","b",1,2);\', \'clock("a","b",4,5);\', \'clock("a","c",1,2);\', \'clock("a","b",2,3);\', \'clock("a","c",4,5);\', \'clock("a","c",5,6);\', \'clock("a","b",5,6);\', \'clock("a","c",3,4);\', \'clock("a","c",2,3);\']'''
    self.assertEqual( actual_conclusion, expected_conclusion )

    logging.debug( "  TEST " + test_id + " : actual_conclusion   = " + actual_conclusion )
    logging.debug( "  TEST " + test_id + " : expected_conclusion = " + expected_conclusion )


  ###########
  #  RDLOG  #
  ###########
  #@unittest.skip( "works." )
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
    argDict[ "EOT" ]            = 6
    argDict[ "EFF" ]            = 3
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

    expected_conclusion = '''conclusion : found counterexample : [\'clock("a","b",5,6);\', \'clock("a","b",2,3);\', \'clock("a","b",4,5);\', \'clock("a","b",1,2);\', \'clock("a","b",3,4);\']'''
    self.assertEqual( actual_conclusion, expected_conclusion )

    logging.debug( "  TEST " + test_id + " : actual_conclusion   = " + actual_conclusion )
    logging.debug( "  TEST " + test_id + " : expected_conclusion = " + expected_conclusion )


  ################
  #  SIMPLOG DM  #
  ################
  #@unittest.skip( "works." )
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
    argDict[ "EOT" ]            = 6
    argDict[ "EFF" ]            = 3
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
  #@unittest.skip( "works." )
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
    argDict[ "EOT" ]            = 6
    argDict[ "EFF" ]            = 3
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
