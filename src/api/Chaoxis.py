#!/usr/bin/env python

'''
Chaoxis.py
'''

# ------------------------------------------------ #
#  python package imports 

import ConfigParser, copy, logging, os, sqlite3, string, sys

# ------------------------------------------------ #
# IAPYX imports

IAPYX_SRC_PATH = __file__ + "/../../../lib/iapyx/src"

if not os.path.abspath( IAPYX_SRC_PATH ) in sys.path :
  sys.path.append( os.path.abspath( IAPYX_SRC_PATH ) )

from dedt       import dedt
from evaluators import c4_evaluator
from utils      import parseCommandLineInput, tools

# ------------------------------------------------ #
# ORIK imports

ORIK_SRC_PATH = __file__ + "/../../../lib/orik/src"

if not os.path.abspath( ORIK_SRC_PATH ) in sys.path :
  sys.path.append( os.path.abspath( ORIK_SRC_PATH ) )

from derivation import ProvTree

# ------------------------------------------------ #
# SNIPER imports

SNIPER_SRC_PATH = __file__+ "/../../../lib/sniper/src"

if not os.path.abspath( SNIPER_SRC_PATH ) in sys.path :
  sys.path.append( os.path.abspath( SNIPER_SRC_PATH ) )

from solvers import PYCOSAT_Solver

# ------------------------------------------------ #

# --------------------------------------------------------------- #
# set logging level

#if sys.argv[1] == "--debug" :
#  logging.basicConfig( format='%(levelname)s:%(message)s', level=logging.DEBUG )
#elif sys.argv[1] == "--info" :
#  logging.basicConfig( format='%(levelname)s:%(message)s', level=logging.INFO )
#elif sys.argv[1] == "--warning" : 
#  logging.basicConfig( format='%(levelname)s:%(message)s', level=logging.WARNING )


#############
#  CHAOXIS  #
#############
class Chaoxis( object ) :

  ##########
  #  INIT  #
  ##########
  def __init__( self, argDict      = None, \
                      label        = "", \
                      custom_fault = None ) :

    self.conclusion         = "No conclusion."
    self.NUM_RUN_ITERATIONS = 0
    self.graph_stats        = None
    self.argDict            = None
    self.label              = label
    self.custom_fault       = custom_fault
    self.tried_solns        = []

    # --------------------------------------------------------------- #
    # get dictionary of command line arguments

    if argDict :
      self.argDict = argDict
    else :
      self.argDict = parseCommandLineInput.parseCommandLineInput( )

    # --------------------------------------------------------------- #
    # make sure the data directory exists

    if not os.path.isdir( os.path.abspath( self.argDict[ "data_save_path" ] + "/../" ) ) :
      os.system( "mkdir " + os.path.abspath( self.argDict[ "data_save_path" ] + "/../" ) )
    if not os.path.isdir( os.path.abspath( self.argDict[ "data_save_path" ] )  ) :
      os.system( "mkdir " + os.path.abspath( self.argDict[ "data_save_path" ] ) )

    # --------------------------------------------------------------- #
    # initialize a database for the IR

    saveDB      = self.argDict[ "data_save_path" ] + "/IR_" + label + ".db"
    if os.path.isfile( saveDB ) :
      os.remove( saveDB )

    IRDB        = sqlite3.connect( saveDB ) # database for storing IR, stored in running script dir
    self.cursor = IRDB.cursor()

    # --------------------------------------------------------------- #
    # generate the initial program

    self.datalog_with_clocks = None
    self.datalog_with_clocks = dedt.translateDedalus( self.argDict, self.cursor )

    # --------------------------------------------------------------- #
    # maintain a current solution index and formula id

    self.CURR_FMLA_ID    = 0
    self.CURR_SOLN_INDEX = 0

    # --------------------------------------------------------------- #

    self.datalog_program_only = None
    self.clocks_only          = None
    self.table_list_only      = None
    self.datalog_program_only = self.get_program_only( self.datalog_with_clocks[0][0] )
    self.clocks_only          = self.get_clocks_only(  self.datalog_with_clocks[0][0] )
    self.table_list_only      = self.datalog_with_clocks[0][1]

    logging.debug( "  __INIT__ : self.datalog_program_only = " + str( self.datalog_program_only ) )
    logging.debug( "  __INIT__ : self.clocks_only          = " + str( self.clocks_only ) )
    logging.debug( "  __INIT__ : self.table_list_only      = " + str( self.table_list_only ) )

    # --------------------------------------------------------------- #
    # perform evaluaton on the current version of datalog_with_clocks

    logging.debug( "  __INIT__ : performing initial run..." )

    # run c4 evaluation
    results_array = None
    results_dict  = None
    results_array = c4_evaluator.runC4_wrapper( self.datalog_with_clocks[0], self.argDict )
    results_dict  = tools.getEvalResults_dict_c4( results_array )

    logging.debug( "  __INIT__ : performing initial run...done." )

    # --------------------------------------------------------------- #
    # check for vacuous correctness

    if self.is_vacuously_correct( results_dict[ "pre" ] ) :
      self.conclusion = "conclusion : spec is vacuously correct."

    else :

      # --------------------------------------------------------------- #
      # generate orik rgg
  
      logging.debug( "  __INIT__ : building initial provenance tree..." )

      orik_rgg = copy.deepcopy( None )
      orik_rgg = ProvTree.ProvTree( rootname       = "FinalState", \
                                    parsedResults  = results_dict, \
                                    cursor         = self.cursor, \
                                    treeType       = "goal", \
                                    isNeg          = False, \
                                    eot            = self.argDict[ "EOT" ], \
                                    prev_prov_recs = {}, \
                                    argDict        = self.argDict )
  
      self.graph_stats = None
      self.graph_stats = orik_rgg.create_pydot_graph( self.CURR_FMLA_ID, \
                                                      self.NUM_RUN_ITERATIONS, \
                                                      self.label )

      logging.debug( "  __INIT__ : building initial provenance tree...done." )

      # --------------------------------------------------------------- #
      # build a solution generator
  
      logging.debug( "  __INIT__ : performing initial solve..." )

      self.pycosat_solver = None
      self.pycosat_solver = PYCOSAT_Solver.PYCOSAT_Solver( self.argDict, orik_rgg )

      logging.debug( "  __INIT__ : performing initial solve...done." )


  #########
  #  RUN  #
  #########
  def run( self ) :

    logging.debug( "  CHAOXIS RUN : self.NUM_RUN_ITERATIONS = " + str( self.NUM_RUN_ITERATIONS ) )
    logging.debug( "  CHAOXIS RUN : self.CURR_SOLN_INDEX    = " + str( self.CURR_SOLN_INDEX ) )
    logging.debug( "  CHAOXIS RUN : self.CURR_FMLA_ID       = " + str( self.CURR_FMLA_ID ) )

    # --------------------------------------------------------------- #
    # run on the custom fault only, if applicable

    if self.custom_fault :
      self.run_on_custom_fault()

    else :

      # --------------------------------------------------------------- #
      # get a new soln
  
      a_new_soln = self.get_soln_at_index( self.pycosat_solver )
      logging.debug( "  CHAOXIS RUN : a_new_soln = " + str( a_new_soln ) )
      assert( a_new_soln != None )
  
      # --------------------------------------------------------------- #
      # edit the clock table
  
      a_new_soln_clean = self.get_clean_soln( a_new_soln )
      logging.debug( "  CHAOXIS RUN : a_new_soln_clean : " + str( a_new_soln_clean ) )
  
      # only try new solns
      if not self.already_tried( a_new_soln_clean ) :
    
        new_clock_table = self.perform_omissions( a_new_soln_clean )
        logging.debug( "  CHAOXIS RUN : adding to tried_solns '" + str( a_new_soln_clean ) + "'" )
        self.tried_solns.append( a_new_soln_clean )
    
        logging.debug( "  CHAOXIS RUN : new_clock_table " + str( new_clock_table ) )
    
        # --------------------------------------------------------------- #
        # perform another evaluation
    
        prog_cp = copy.deepcopy( self.datalog_program_only )
        prog_cp.extend( new_clock_table )
        final_prog_info = [ prog_cp, self.table_list_only ]
    
        logging.debug( "  CHAOXIS RUN : final_prog_info = " + str( final_prog_info ) )
    
        results_array = c4_evaluator.runC4_wrapper( final_prog_info, self.argDict )
        results_dict  = tools.getEvalResults_dict_c4( results_array )

        # -------------------------------------------------------------- #
        # evaluate results to draw a conclusion
    
        if self.pre_does_not_imply_post( results_dict[ "pre" ], results_dict[ "post" ] ) :
          self.conclusion = "conclusion : found counterexample : " + str( a_new_soln_clean )
    
        elif self.no_more_fmlas_or_solns( self.pycosat_solver ) :
          self.conclusion = "conclusion : spec is chaoxis-certified for correctness."
    
        else :
    
          # --------------------------------------------------------------- #
          # repeat until a corrupting fault appears or until
          # no more formulas and solns exist
      
          if self.another_soln_exists( self.pycosat_solver ) or \
             self.another_fmla_exists( self.pycosat_solver ) :
            self.NUM_RUN_ITERATIONS += 1
            self.run()
    
          else :
            self.conclusion = "conclusion : alright, something's weird." 
    
      else :
        if self.another_soln_exists( self.pycosat_solver ) or \
           self.another_fmla_exists( self.pycosat_solver ) :
          self.NUM_RUN_ITERATIONS += 1
          self.run()
  
        elif self.no_more_fmlas_or_solns( self.pycosat_solver ) :
          self.conclusion = "conclusion : spec is chaoxis-certified for correctness."
  
        else :
          logging.debug( "  CHAOXIS RUN : alright. this is weird." )
  
      logging.debug( "  CHAOXIS RUN : NUM_RUN_ITERATIONS == " + \
                     str( self.NUM_RUN_ITERATIONS ) + ", tried_solns = " )
      for d in self.tried_solns :
        logging.debug( "  " + str( d ) )



  ###################
  #  ALREADY TRIED  #
  ###################
  def already_tried( self, a_new_soln_clean ) :
    flag = False
    for soln in self.tried_solns :
      if soln == a_new_soln_clean :
        flag = True
    logging.debug( "  ALREADY TRIED : returing " + str( flag ) )
    return flag


  #########################
  #  RUN ON CUSTOM FAULT  #
  #########################
  def run_on_custom_fault( self ) :

    logging.debug( "  RUN ON CUSTOM FAULT : self.NUM_RUN_ITERATIONS = " + str( self.NUM_RUN_ITERATIONS ) )

    # --------------------------------------------------------------- #
    # edit the clock table

    a_new_soln_clean = self.custom_fault
    logging.debug( "  RUN ON CUSTOM FAULT : a_new_soln_clean : " + str( a_new_soln_clean ) )

    new_clock_table = self.perform_omissions( a_new_soln_clean )

    logging.debug( "  RUN ON CUSTOM FAULT : new_clock_table " + str( new_clock_table ) )

    # --------------------------------------------------------------- #
    # perform another evaluation

    self.datalog_program_only.extend( new_clock_table )
    final_prog_info = [ self.datalog_program_only, self.table_list_only ]

    logging.debug( "  RUN ON CUSTOM FAULT : final_prog_info = " + str( final_prog_info ) )

    results_array = c4_evaluator.runC4_wrapper( final_prog_info, self.argDict )
    results_dict  = tools.getEvalResults_dict_c4( results_array )

    # --------------------------------------------------------------- #
    # evaluate results to draw a conclusion

    if self.pre_does_not_imply_post( results_dict[ "pre" ], results_dict[ "post" ] ) :
      self.conclusion = "conclusion : found counterexample : " + str( a_new_soln_clean )
      return

    elif self.no_more_fmlas_or_solns( self.pycosat_solver ) :
      self.conclusion = "conclusion : spec is chaoxis-certified for correctness."

    print "+++++++++++++++++++++++++++++++"
    print "  RUN ON CUSTOM FAULT : "
    print "results:"
    for key in results_dict :
      print ">>>>>>>>>>>>>>>>>>>>>>>>>"
      print key
      for tup in results_dict[ key ] :
        print tup


    # --------------------------------------------------------------- #
    # generate orik rgg

    logging.debug( "  RUN ON CUSTOM FAULT : building provenance tree..." )

    orik_rgg = copy.deepcopy( None )
    orik_rgg = ProvTree.ProvTree( rootname       = "FinalState", \
                                  parsedResults  = results_dict, \
                                  cursor         = self.cursor, \
                                  treeType       = "goal", \
                                  isNeg          = False, \
                                  eot            = self.argDict[ "EOT" ], \
                                  prev_prov_recs = {}, \
                                  argDict        = self.argDict )

    self.graph_stats = None
    self.graph_stats = orik_rgg.create_pydot_graph( self.CURR_FMLA_ID, \
                                                    self.NUM_RUN_ITERATIONS, \
                                                    self.label )

    logging.debug( "  RUN ON CUSTOM FAULT : building provenance tree...done." )


  #########################
  #  ANOTHER SOLN EXISTS  #
  #########################
  def another_soln_exists( self, solver ) :

    # check if another soln exists
    curr_fmla = solver.cnf_fmla_list[ self.CURR_FMLA_ID ]
    try :
      a_new_soln = solver.get_a_soln( curr_fmla, self.CURR_SOLN_INDEX + 1 )
      logging.debug( "  ANOTHER SOLN EXISTS : returning True" )
      return True
    except IndexError :
      logging.debug( "  ANOTHER SOLN EXISTS : returning False" )
      return False


  #########################
  #  ANOTHER FMLA EXISTS  #
  #########################
  def another_fmla_exists( self, solver ) :

    # check if another fmla exists
    try :
      next_fmla = solver.cnf_fmla_list[ self.CURR_FMLA_ID + 1 ]
      logging.debug( "  ANOTHER FMLA EXISTS : returning True" )
      return True
    except IndexError :
      logging.debug( "  ANOTHER FMLA EXISTS : returning False" )
      return False


  ############################
  #  NO MORE FMLAS OR SOLNS  #
  ############################
  def no_more_fmlas_or_solns( self, solver ) :

    logging.debug( "  NO MORE FMLAS OR SOLNS : self.CURR_FMLA_ID    = " + str( self.CURR_FMLA_ID ) )
    logging.debug( "  NO MORE FMLAS OR SOLNS : self.CURR_SOLN_INDEX = " + str( self.CURR_SOLN_INDEX ) )
    logging.debug( "  NO MORE FMLAS OR SOLNS : self.cnf_fmla_list   = " + str( solver.cnf_fmla_list ) )

    # check if another fmla exists
    if self.another_fmla_exists( solver ) :
      no_more_fmlas = False
    else :
      no_more_fmlas = True

    # check if another soln exists
    if self.another_soln_exists( solver ) :
      no_more_solns = False
    else :
      no_more_solns = True

    if no_more_fmlas and no_more_solns :
      logging.debug( "  NO MORE FMLAS OR SOLNS : returning True." )
      return True
    else :
      logging.debug( "  NO MORE FMLAS OR SOLNS : returning False." )
      return False


  #######################
  #  PERFORM OMISSIONS  #
  #######################
  def perform_omissions( self, a_soln ) :
    new_clock_table = []
    for clock_fact in self.clocks_only :
      if not clock_fact in a_soln :
        new_clock_table.append( clock_fact )
    return new_clock_table


  #############################
  #  PRE DOES NOT IMPLY POST  #
  #############################
  def pre_does_not_imply_post( self, pre_table, post_table ) :
    pre_eot  = []
    post_eot = []
    for tup in pre_table :
      if tup[-1] == str( self.argDict[ "EOT" ] ) :
        pre_eot.append( tup )
    for tup in post_table :
      if tup[-1] == str( self.argDict[ "EOT" ] ) :
        post_eot.append( tup )

    logging.debug( "  PRE DOES NOT IMPLY POST : pre_eot  = " + str( pre_eot ) )
    logging.debug( "  PRE DOES NOT IMPLY POST : post_eot = " + str( post_eot ) )

    for tup in pre_eot :
      if not tup in post_eot :
        logging.debug( "  PRE DOES NOT IMPLY POST : returning True." )
        return True
    logging.debug( "  PRE DOES NOT IMPLY POST : returning False." )
    return False


  ##########################
  #  IS VACUOUSLY CORRECT  #
  ##########################
  def is_vacuously_correct( self, pre_table ) :

    # grab pre eot facts
    pre_eots  = []
    for tup in pre_table :
      if tup[-1] == str( self.argDict[ "EOT" ] ) :
        pre_eots.append( tup )

    if pre_eots == [] :
      return True
    else :
      return False


  ####################
  #  GET CLEAN SOLN  #
  ####################
  def get_clean_soln( self, a_new_soln ) :
    clean_list = []

    for clock_fact in a_new_soln :
      data_list = self.get_data_list( clock_fact )
      clean_list.append( 'clock("' + data_list[0] + \
                         '","'    + data_list[1] + \
                         '",'     + data_list[2] + \
                         ','      + data_list[3] + ');' )

    return clean_list


  ###################
  #  GET DATA LIST  #
  ###################
  def get_data_list( self, clock_fact ) :
    clock_fact = clock_fact.translate( None, string.whitespace )
    clock_fact = clock_fact.replace( "clock([", "" )
    clock_fact = clock_fact.replace( "])", "" )
    clock_fact = clock_fact.replace( '"', "" )
    clock_fact = clock_fact.replace( "'", "" )
    return clock_fact.split( "," )


  ######################
  #  GET PROGRAM ONLY  #
  ######################
  # only works b/c clocks appended last
  def get_program_only( self, all_lines ) :
    for i in range( 0, len( all_lines ) ) :
      if all_lines[i].startswith( "clock(" ) :
        break
    return all_lines[ : i ]


  #####################
  #  GET CLOCKS ONLY  #
  #####################
  # only works b/c clocks appended last
  def get_clocks_only( self, all_lines ) :
    for i in range( 0, len( all_lines ) ) :
      if all_lines[i].startswith( "clock(" ) :
        break
    return all_lines[ i : ]


  #######################
  #  GET SOLN AT INDEX  #
  #######################
  # use index at CURR_SOLN_INDEX
  def get_soln_at_index( self, pycosat_solver ) :

    # make sure fmla exists
    try :
      curr_fmla = pycosat_solver.cnf_fmla_list[ self.CURR_FMLA_ID ]
    except IndexError :
      logging.debug( "  GET SOLN AT INDEX : no more fmlas to explore. exiting loop." )
      return None

    # curr_fmla must exist here by defn of previous try-except.
    try :
      logging.debug( "  GET SOLN AT INDEX : running on self.CURR_FMLA_ID = " + str( self.CURR_FMLA_ID ) + ", self.CURR_SOLN_INDEX = " + str( self.CURR_SOLN_INDEX ) )
      a_new_soln = pycosat_solver.get_a_soln( curr_fmla, self.CURR_SOLN_INDEX )
      self.CURR_SOLN_INDEX += 1
      return a_new_soln
    except IndexError :
      logging.debug( "  GET SOLN AT INDEX : no more solns to explore wrt to this formula. incrementing to next fmla.")
      self.CURR_FMLA_ID    += 1 # increment to the next fmla
      self.CURR_SOLN_INDEX  = 0  # reset soln_id
      logging.debug( "  GET SOLN AT INDEX : incemented self.CURR_FMLA_ID to " + str( self.CURR_FMLA_ID ) + ". reseting soln_id." )
      return self.get_soln_at_index( pycosat_solver )


  ########################
  #  RUN FIND ALL SOLNS  #
  ########################
  # a template loop for getting all the solutions.
  # retrieves all the solns across all fmlas generated 
  # from the input provenance tree.
  def run_find_all_solns( self ) :

    self.run()

    all_solns = []
    fmla_id = 0
    soln_id = 0

    while True :

      # make sure fmla exists
      try :
        curr_fmla = self.pycosat_solver.cnf_fmla_list[ fmla_id ]
      except IndexError :
        logging.debug( "  RUN FIND ALL SOLNS : no more fmlas to explore. exiting loop." )
        break # break out of loop. no more solns exist

      # curr_fmla must exist here by defn of previous try-except.
      try :
        logging.debug( "  RUN FIND ALL SOLNS : running on fmla_id = " + str( fmla_id ) + ", soln_id = " + str( soln_id ) )
        a_new_soln = self.pycosat_solver.get_a_soln( curr_fmla, soln_id )
        soln_id   += 1
        all_solns.append( a_new_soln )
      except IndexError :
        logging.debug( "  RUN FIND ALL SOLNS : no more solns to explore wrt to this formula. incrementing to next fmla.")
        fmla_id += 1 # increment to the next fmla
        soln_id  = 0  # reset soln_id
        logging.debug( "  RUN FIND ALL SOLNS : incemented fmla_id to " + str( fmla_id ) + ". reseting soln_id." )

    for soln in all_solns :
      print soln


  #########################
  #  GET PROGRAM RESULTS  #
  #########################
  # convert the input dedalus program into c4 datalog and evaluate.
  # return evaluation results dictionary.
  def get_program_results( self, argDict, cursor ) :

    # convert dedalus into c4 datalog
    allProgramData = dedt.translateDedalus( argDict, cursor )

    # run c4 evaluation
    results_array = c4_evaluator.runC4_wrapper( allProgramData[0], argDict )
    parsedResults = tools.getEvalResults_dict_c4( results_array )

    return parsedResults


#########
#  EOF  #
#########
