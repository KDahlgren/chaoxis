#!/usr/bin/env python

'''
Chaoxis.py
'''

# ------------------------------------------------ #
#  python package imports 

import ConfigParser, copy, logging, os, sqlite3, string, sys, z3

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

from solvers import PYCOSAT_Solver, Z3_Solver

# ------------------------------------------------ #

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
    # get configuration params

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

    # database for storing IR, stored in running script dir
    IRDB        = sqlite3.connect( saveDB )
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

    logging.debug( "  __INIT__ : self.datalog_program_only = " + \
                   str( self.datalog_program_only ) )
    logging.debug( "  __INIT__ : self.clocks_only          = " + \
                   str( self.clocks_only ) )
    logging.debug( "  __INIT__ : self.table_list_only      = " + \
                   str( self.table_list_only ) )

    # --------------------------------------------------------------- #
    # perform evaluaton on the current version of datalog_with_clocks

    logging.debug( "  __INIT__ : performing initial run..." )

    # run c4 evaluation
    results_array = None
    results_dict  = None
    results_array = c4_evaluator.runC4_wrapper( self.datalog_with_clocks[0], \
                                                self.argDict )
    results_dict  = tools.getEvalResults_dict_c4( results_array )

    logging.debug( "  __INIT__ : performing initial run...done." )

    # --------------------------------------------------------------- #
    # check for vacuous correctness

    if self.is_vacuously_correct( results_dict[ "pre" ] ) :
      self.conclusion = "conclusion : spec is vacuously correct."

    elif self.is_vacuously_incorrect( results_dict[ "pre" ], results_dict[ "post" ] ) :
      self.conclusion = "conclusion : spec is vacuously incorrect."

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

      SOLVER_TYPE = argDict[ "solver" ].lower()
      logging.debug( "  __INIT__ : using solver type '" + SOLVER_TYPE + "'"  )

      if SOLVER_TYPE == "z3" :
        self.solver = Z3_Solver.Z3_Solver( self.argDict, orik_rgg )
      elif SOLVER_TYPE == "pycosat" :
        self.solver = PYCOSAT_Solver.PYCOSAT_Solver( self.argDict, orik_rgg )
      else :
        raise ValueError( "  solver type '" + SOLVER_TYPE + "' not recognized." )

      logging.debug( "  __INIT__ : performing initial solve...done." )


  #########
  #  RUN  #
  #########
  def run( self ) :

    logging.debug( "  CHAOXIS RUN : -----------------------------------------" )
    logging.debug( "  CHAOXIS RUN : self.NUM_RUN_ITERATIONS = " + \
                   str( self.NUM_RUN_ITERATIONS ) )
    logging.debug( "  CHAOXIS RUN : self.CURR_SOLN_INDEX    = " + \
                   str( self.CURR_SOLN_INDEX ) )
    logging.debug( "  CHAOXIS RUN : self.CURR_FMLA_ID       = " + \
                   str( self.CURR_FMLA_ID ) )

    # --------------------------------------------------------------- #
    # break on vacuouc correctness

    if not self.conclusion == "No conclusion." :
      return

    # --------------------------------------------------------------- #
    # run on the custom fault only, if applicable

    if self.custom_fault :
      self.run_on_custom_fault()

    else :

      # --------------------------------------------------------------- #
      # get a new soln
  
      if self.solver.solver_type == "z3" :
        a_new_soln = self.solver.get_next_soln()

      elif self.solver.solver_type == "pycosat" :
        a_new_soln = self.get_soln_at_index( self.solver )
      else :
        raise ValueError( "alright. how did you get this far w/o specifying a " + \
                          "known solver? aborting..." )

      logging.debug( "  CHAOXIS RUN : a_new_soln = " + str( a_new_soln ) )
      assert( a_new_soln != None )
  
      # --------------------------------------------------------------- #
      # edit the clock table
  
      a_new_soln_clean = self.get_clean_soln( a_new_soln )
      logging.debug( "  CHAOXIS RUN : a_new_soln_clean : " + str( a_new_soln_clean ) )
  
      # only try new solns
      if not self.already_tried( a_new_soln_clean ) :
    
        new_clock_table = self.perform_clock_table_edits( a_new_soln_clean )
        logging.debug( "  CHAOXIS RUN : adding to tried_solns '" + \
                       str( a_new_soln_clean ) + "'" )
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
          self.conclusion = "conclusion : found counterexample : " + \
                            str( a_new_soln_clean )
    
        elif self.no_more_fmlas_or_solns() :
          self.conclusion = "conclusion : spec is chaoxis-certified for correctness."
    
        else :
    
          # --------------------------------------------------------------- #
          # repeat until a corrupting fault appears or until
          # no more formulas and solns exist

          if self.another_soln_exists() or \
             self.another_fmla_exists() :
            self.NUM_RUN_ITERATIONS += 1
            self.run()
    
          else :
            self.conclusion = "conclusion : alright, something's weird." 
    
      else :
        if self.another_soln_exists() or \
           self.another_fmla_exists() :
          self.NUM_RUN_ITERATIONS += 1
          self.run()
  
        elif self.no_more_fmlas_or_solns() :
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

    logging.debug( "  RUN ON CUSTOM FAULT : self.NUM_RUN_ITERATIONS = " + \
                   str( self.NUM_RUN_ITERATIONS ) )

    # --------------------------------------------------------------- #
    # edit the clock table

    a_new_soln_clean = self.custom_fault
    logging.debug( "  RUN ON CUSTOM FAULT : a_new_soln_clean : " + \
                   str( a_new_soln_clean ) )

    new_clock_table = self.perform_clock_table_edits( a_new_soln_clean )

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

    else :
      self.conclusion = "conclusion : spec is chaoxis-certified for " + \
                        "correctness on the given fault."

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
  def another_soln_exists( self ) :

    logging.debug( "  ANOTHER SOLN EXISTS : self.solver.solver_type = " + \
                   self.solver.solver_type )

    if self.solver.solver_type == "z3" :
      try :
        self.solver.get_a_soln( fmla_id=self.solver.fmla_id, add_constraint=False )
        logging.debug( "  ANOTHER SOLN EXISTS : returning True" )
        return True
      except z3.Z3Exception :
        logging.debug( "  ANOTHER SOLN EXISTS : returning False" )
        return False

    elif self.solver.solver_type == "pycosat" :
      res = self.another_soln_exists_pycosat()
      logging.debug( "  ANOTHER SOLN EXISTS : returning " + str( res ) )
      return res

    else :
      raise ValueError( "hold up. how'd you make it here w/o " + \
                        "a known solver? aborting..." )


  #########################
  #  ANOTHER FMLA EXISTS  #
  #########################
  def another_fmla_exists( self ) :

    logging.debug( "  ANOTHER FMLA EXISTS : self.solver.solver_type = " + \
                   self.solver.solver_type )

    if self.solver.solver_type == "z3" :
      try :
        self.solver.boolean_fmla_list[ self.solver.fmla_id + 1 ]
        logging.debug( "  ANOTHER FMLA EXISTS : returning True" )
        return True
      except IndexError :
        logging.debug( "  ANOTHER FMLA EXISTS : returning False" )
        return False

    elif self.solver.solver_type == "pycosat" :
      res = self.another_fmla_exists_pycosat()
      logging.debug( "  ANOTHER FMLA EXISTS : returning " + str( res ) )
      return res

    else :
      raise ValueError( "hold up. how'd you make it here w/o " + \
                        "a known solver? aborting..." )


  #################################
  #  ANOTHER SOLN EXISTS PYCOSAT  #
  #################################
  def another_soln_exists_pycosat( self ) :

    # check if another soln exists
    curr_fmla = self.solver.cnf_fmla_list[ self.CURR_FMLA_ID ]
    try :
      a_new_soln = self.solver.get_a_soln( curr_fmla, self.CURR_SOLN_INDEX + 1 )
      logging.debug( "  ANOTHER SOLN EXISTS PYCOSAT : returning True" )
      return True
    except IndexError :
      logging.debug( "  ANOTHER SOLN EXISTS PYCOSAT : returning False" )
      return False


  #################################
  #  ANOTHER FMLA EXISTS PYCOSAT  #
  #################################
  def another_fmla_exists_pycosat( self ) :

    # check if another fmla exists
    try :
      next_fmla = self.solver.cnf_fmla_list[ self.CURR_FMLA_ID + 1 ]
      logging.debug( "  ANOTHER FMLA EXISTS PYCOSAT : returning True" )
      return True
    except IndexError :
      logging.debug( "  ANOTHER FMLA EXISTS PYCOSAT : returning False" )
      return False


  ############################
  #  NO MORE FMLAS OR SOLNS  #
  ############################
  def no_more_fmlas_or_solns( self ) :

    if self.solver.solver_type == "z3" :
      return self.no_more_fmlas_or_solns_z3()

    elif self.solver.solver_type == "pycosat" :
      return self.no_more_fmlas_or_solns_pycosat()

    else :
      raise ValueError( "holy shit, you got this far w/o specifying a " + \
                        "known solver? aborting..." )


  ###############################
  #  NO MORE FMLAS OR SOLNS Z3  #
  ###############################
  def no_more_fmlas_or_solns_z3( self ) :

    # check for more fmlas
    try :
      self.solver.boolean_fmla_list[ self.solver.fmla_id + 1 ]
      no_more_fmlas = False
    except IndexError :
      no_more_fmlas = True

    # check for more solns
    try :
      self.solver.get_a_soln( fmla_id=self.solver.fmla_id, add_constraint=False )
      no_more_solns = False
    except z3.Z3Exception :
      no_more_solns = True

    if no_more_fmlas and no_more_solns :
      return True
    else :
      return False


  ####################################
  #  NO MORE FMLAS OR SOLNS PYCOSAT  #
  ####################################
  def no_more_fmlas_or_solns_pycosat( self ) :

    logging.debug( "  NO MORE FMLAS OR SOLNS PYCOSAT : self.CURR_FMLA_ID    = " + \
                   str( self.CURR_FMLA_ID ) )
    logging.debug( "  NO MORE FMLAS OR SOLNS PYCOSAT : self.CURR_SOLN_INDEX = " + \
                   str( self.CURR_SOLN_INDEX ) )
    logging.debug( "  NO MORE FMLAS OR SOLNS PYCOSAT : self.cnf_fmla_list   = " + \
                   str( self.solver.cnf_fmla_list ) )

    # check if another fmla exists
    if self.another_fmla_exists_pycosat() :
      no_more_fmlas = False
    else :
      no_more_fmlas = True

    # check if another soln exists
    if self.another_soln_exists_pycosat() :
      no_more_solns = False
    else :
      no_more_solns = True

    if no_more_fmlas and no_more_solns :
      logging.debug( "  NO MORE FMLAS OR SOLNS PYCOSAT : returning True." )
      return True
    else :
      logging.debug( "  NO MORE FMLAS OR SOLNS PYCOSAT : returning False." )
      return False


  ###############################
  #  PERFORM CLOCK TABLE EDITS  #
  ###############################
  def perform_clock_table_edits( self, a_soln ) :
    new_clock_table = []

    # divide into positive and negative clocks
    pos_clocks = []
    neg_clocks = []
    for clock_fact in a_soln :
      if clock_fact.startswith( "_NOT_" ) :
        neg_clocks.append( clock_fact.replace( "_NOT_", "" ) )
      else :
        pos_clocks.append( clock_fact )

    # perform omissions on positive clock facts
    for clock_fact in self.clocks_only :
      if not clock_fact in pos_clocks :
        new_clock_table.append( clock_fact )

    # perform injections for negative clock facts
    for clock_fact in neg_clocks :
      if not clock_fact in new_clock_table :
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


  ############################
  #  IS VACUOUSLY INCORRECT  #
  ############################
  def is_vacuously_incorrect( self, pre_table, post_table ) :

    # grab pre eot facts
    pre_eots  = []
    for tup in pre_table :
      if tup[-1] == str( self.argDict[ "EOT" ] ) :
        pre_eots.append( tup )

    # grab post eot facts
    post_eots  = []
    for tup in post_table :
      if tup[-1] == str( self.argDict[ "EOT" ] ) :
        post_eots.append( tup )

    for pre_tup in pre_eots :
      if not pre_tup in post_eots :
        return True
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
      print data_list
      clean_fact = ""
      if clock_fact.startswith( "_NOT_" ) :
        clean_fact += "_NOT_"
      clean_fact += 'clock("' + data_list[0] + \
                    '","' + data_list[1] + \
                    '",'  + data_list[2] + \
                    ','   + data_list[3] + ');'
      clean_list.append( clean_fact )

    return clean_list


  ###################
  #  GET DATA LIST  #
  ###################
  def get_data_list( self, clock_fact ) :
    clock_fact = clock_fact.translate( None, string.whitespace )
    clock_fact = clock_fact.replace( "_NOT_", "" )
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
  def get_soln_at_index( self, solver ) :

    # make sure fmla exists
    try :
      curr_fmla = solver.cnf_fmla_list[ self.CURR_FMLA_ID ]
    except IndexError :
      logging.debug( "  GET SOLN AT INDEX : no more fmlas to explore. exiting loop." )
      return None

    # curr_fmla must exist here by defn of previous try-except.
    try :
      logging.debug( "  GET SOLN AT INDEX : running on self.CURR_FMLA_ID = " + str( self.CURR_FMLA_ID ) + ", self.CURR_SOLN_INDEX = " + str( self.CURR_SOLN_INDEX ) )
      a_new_soln = solver.get_a_soln( curr_fmla, self.CURR_SOLN_INDEX )
      self.CURR_SOLN_INDEX += 1
      return a_new_soln
    except IndexError :
      logging.debug( "  GET SOLN AT INDEX : no more solns to explore wrt to this formula. incrementing to next fmla.")
      self.CURR_FMLA_ID    += 1 # increment to the next fmla
      self.CURR_SOLN_INDEX  = 0  # reset soln_id
      logging.debug( "  GET SOLN AT INDEX : incemented self.CURR_FMLA_ID to " + str( self.CURR_FMLA_ID ) + ". reseting soln_id." )
      return self.get_soln_at_index( solver )


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
        curr_fmla = self.solver.cnf_fmla_list[ fmla_id ]
      except IndexError :
        logging.debug( "  RUN FIND ALL SOLNS : no more fmlas to explore. exiting loop." )
        break # break out of loop. no more solns exist

      # curr_fmla must exist here by defn of previous try-except.
      try :
        logging.debug( "  RUN FIND ALL SOLNS : running on fmla_id = " + str( fmla_id ) + ", soln_id = " + str( soln_id ) )
        a_new_soln = self.solver.get_a_soln( curr_fmla, soln_id )
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
