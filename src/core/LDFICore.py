#!/usr/bin/env python

'''
LDFICore.py
  A class representation of the core LDFI workflow functionality.
'''

# **************************************** #


#############
#  IMPORTS  #
#############
# standard python packages
import ast, inspect, itertools, os, sqlite3, string, sys, time

# ------------------------------------------------------ #
# import sibling packages HERE!!!
sys.path.append( os.path.abspath( __file__ + "/../.." ) )

from dedt           import dedt, dedalusParser
from derivation     import ProvTree
from utils          import parseCommandLineInput, tools
from evaluators     import c4_evaluator, evalTools
from solvers        import EncodedProvTree_CNF, newProgGenerationTools, solverTools
from visualizations import vizTools

# **************************************** #


DEBUG                = tools.getConfig( "CORE", "LDFI_DEBUG", bool )
PROV_TREES_ON        = tools.getConfig( "CORE", "LDFI_PROV_TREES_ON", bool )
OUTPUT_PROV_TREES_ON = tools.getConfig( "CORE", "LDFI_OUTPUT_PROV_TREES_ON", bool )
OUTPUT_TREE_CNF_ON   = tools.getConfig( "CORE", "LDFI_OUTPUT_TREE_CNF_ON", bool )


####################
#  CLASS LDFICORE  #
####################
class LDFICore :

  # --------------------------------- #
  #############
  #  ATTRIBS  #
  #############
  argDict                 = None  # dictionary of commaned line args
  cursor                  = None  # a reference to the IR database
  allProgramData_noClocks = []    # [ allProgramLines (minus clocks), tableListArray ]
  fault_id                = 1     # id of the current fault to inject. start at 1 for pycosat.
  solver                  = None  # an instance of the chosen solver

  numCrashes              = 0     # number of crashes allowable in solutions for this execution
  crashFacts              = None  # the list of crash facts involved in a solution
  crashCombos             = []    # the complete list of crash combinations according to numCrashes
  faultTracker            = {}    # dictionary mapping omission faults to lists of previously combined crash failures
                                  # ( see setCrashes() )

  initFmla                = None  # the formula obtained from the initial good execution

  stopAtIt                = None  # flag for ensuring only one evaluation iteration over custom solutions
  customFault             = None  # a str for maintaining the trigger fault

  currSolnSet             = []    # a list of the current set of solutions to explore. 
                                  # filters out uninteresting solutions.
                                  # ordered by solution size.

  no_soln_constraints     = True  # boolean controlling the enforcement of constraints on the types,
                                  # characteristics, and/or orderings of solutions tested by the LDFICore

  N                       = None  # integer. the size of the solution buffer.
                                  # the max number of solutions in currSolnSet at any point during the execution.

  currTriggerFault        = None  # a long-lived version of the current trigger fault under investigation

  # --------------------------------- #

  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, argDict, cursor, solver ) :
    self.argDict             = argDict
    self.cursor              = cursor
    self.solver              = solver
    self.no_soln_constraints = tools.getConfig( "GENERAL", "NO_SOLN_CONSTRAINTS", bool )
    self.N                   = tools.getConfig( "GENERAL", "N", int )
    self.numCrashes          = self.argDict[ "crashes" ]

    # cannot run with no solution constraints if user speifies run constraints.
    if self.no_soln_constraints and self.numCrashes > -1 :
      tools.bp( __name__, inspect.stack()[0][3], "ERROR : NO_SOLN_CONSTRAINTS is true, but run specifies a requirement of 0 or more crashes : numCrashes = " + str( self.argDict[ "crashes" ] ) + "\nIf you wish to run with solution constraints (e.g. no crashes, 1 crash, ... ; solutions \nordered by smallest to largest ; etc. ), be sure to set \n'NO_SOLN_CONSTRAINTS = False' under the '[GENERAL]' heading of a settings.ini file in your run directory. \nNO_SOLN_CONSTRAINTS defaults to True for completeness." )


  ##################
  #  RUN WORKFLOW  #
  ##################
  # orchestrates the LDFI workflow
  #
  # core LDFI workflow:
  #  1. convert dedalus program to some version of datalog
  #  2. evaluate the datalog program using some evaluator
  #  3. check for bugs
  #  4. build the provenance tree for the evaluation execution
  #  5. build a CNF formula from the provenance tree
  #  6. solve the CNF formula using some solver
  #  7. generate the new datalog program for the next iteration
  #
  def run_workflow( self, triggerFault ) :

    # initialize return array
    return_array = []
    return_array.append( None )   # := conclusion
    return_array.append( None )   # := explanation
    return_array.append( None )   # := triggerFault
    return_array.append( False )  # := noNewSolns, default to False

    if DEBUG :
     print "*******************************************************"
     print "               RUNNING LDFI CORE WORKFLOW"
     print "*******************************************************"
     print

    # ----------------------------------------------- #
    # 1. get datalog                                  #
    # ----------------------------------------------- #
    if self.fault_id == 1 :

      # ---------------------------------------------------------------- #
      # first LDFI core run                                              #
      # translate all input dedalus files into a single datalog program  #
      # ---------------------------------------------------------------- #

      # allProgramData := [ allProgramLines, tableListArray ]
      allProgramData = self.dedalus_to_datalog( self.argDict, self.cursor )

      # The base datalog program does not change per iteration.
      # The tables used in the program do not change per iteration.
      # Only the collection of clock facts included in the program change per iteration.
      # Save the base program (program minus clock facts) and table list array for future use.
      self.allProgramData_noClocks.append( [ x for x in allProgramData[0] if not x[:6] == "clock(" ] ) # base program lines.
      self.allProgramData_noClocks.append( allProgramData[1] )  # table list array

    else :

      # -------------------------------------------- #
      # 7. generate new datalog prog                 #
      # -------------------------------------------- #

      allProgramData = self.getNewDatalogProg( triggerFault, self.argDict[ "EFF" ], self.cursor, self.fault_id )

    # ----------------------------------------------- #
    # 2. evaluate                                     #
    # ----------------------------------------------- #

    # use c4 wrapper 
    parsedResults = self.evaluate( "C4_WRAPPER", allProgramData )

    # ----------------------------------------------- #
    # 3. check for bugs                               #
    # ----------------------------------------------- #

    if DEBUG :
      print "CHECKING FOR BUGS on results from triggerFault = " + str( triggerFault )

    # check for bugs
    bugInfo     = self.checkForBugs( parsedResults, self.argDict[ "EOT" ] )
    conclusion  = bugInfo[0]
    explanation = bugInfo[1]

    # update conclusion part of returns
    return_array[0] = conclusion
    return_array[1] = explanation

    # break execution if running on a custom fault
    if self.stopAtIt == self.fault_id :
      return_array[2] = self.customFault  # the custom fault
      return_array[3] = True              # update trigger fault part of returns
      return return_array

    ##############################################
    # CASE 1 :                                   # 
    #   Found a counterexample!                  #
    #   Return immediately.                      #
    ##############################################
    if conclusion == "FoundCounterexample" :
      return_array[2] = triggerFault
      return_array[3] = True
      return return_array


    #############################################
    # CASE 2 :                                  # 
    #   Found a vacuously correct execution.    #
    #   No new prov tree.                       #
    #   Find another new soln over the initial  #
    #   CNF fmla.                               #
    #   fault_id already updated solver         #
    #   instance.                               #
    #############################################
    elif conclusion == "NoCounterexampleFound" and explanation == "VACUOUS" :

      if self.fault_id > 1 :

        # -------------------------------------------- #
        # 6. solve CNF formula                         #
        # -------------------------------------------- #

        newTriggerFault = self.getTriggerFault()
        return_array[2] = newTriggerFault

        # an empty newTriggerFault means no new solutions
        if not newTriggerFault and self.fault_id > 1 :
          return_array[2] = triggerFault
          return_array[3] = True

        return return_array # [ conclusion/None, explanation/None, nextTriggerFault/None, noNewSolns/None ]

      else :
        print "self.fault_id = " + str( self.fault_id )
        tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : illogical, captain. hit a vacuous result without injecting faults. Aborting..." )


    ###############################################
    # CASE 3 :                                    # 
    #   Found a correct execution.                #
    #   Find another soln over the initial fmla.  #
    ###############################################
    else :

      # ----------------------------------------------- #
      # 4. get provenance tree                          #
      # ----------------------------------------------- #

      if self.fault_id == 1 : 
        provTreeComplete = self.buildProvTree( parsedResults, self.argDict[ "EOT" ], self.fault_id, self.cursor )

      # -------------------------------------------- #
      # 5. generate CNF formula                      #
      # -------------------------------------------- #

      # only generate a CNF formula for the initial prov tree.
      # also, only collect crashFacts from the initial prov tree.
      if self.fault_id == 1 : 
        provTree_fmla = self.tree_to_CNF( provTreeComplete )

        # grab the textual version of the fmla
        #self.initFmla    = provTree_fmla.cnfformula             # not simplified
        self.initFmla    = provTree_fmla.cnfformula_simplified  # simplified
        self.crashFacts  = provTree_fmla.crashFacts             # establish the complete set of crash facts relevant for the initial good run.
        self.setCrashCombos()                                   # generate all combinations of crashes, given the numbers of crashes for the run.

      # -------------------------------------------- #
      # 6. solve CNF formula                         #
      # -------------------------------------------- #

      newTriggerFault  = self.getTriggerFault()  # grab a new soln to the formula
      return_array[2]  = newTriggerFault         # update trigger fault part of returns

      # an empty newTriggerFault means no new solutions
      if not newTriggerFault and self.fault_id > 1 :
        return_array[2] = triggerFault
        return_array[3] = True

      return return_array # [ conclusion/None, explanation/None, nextTriggerFault/None, noNewSolns/None ]


  #################
  #  SET CRASHES  #
  #################
  # given a triggerFault, add a set of crashes according to the number of crashes 
  # desired by the user.
  def setCrashes( self, triggerFault ) :

    orig_fault_str = str( triggerFault )

    # CASE : user wants crashes
    if self.numCrashes > 0 :
      previousCrashes = self.faultTracker[ orig_fault_str ]
      print "self.faultTracker[" + orig_fault_str + "] = " + str( self.faultTracker[ orig_fault_str ] )
      print "len( previousCrashes ) = " + str( len( previousCrashes ) )

      newCrashCombo = list( self.crashCombos[ len( previousCrashes ) ] )  # convert tuple to list

      # remove comm omission faults wrt crashed node(s) until EOT
      newTriggerFault = []
      for crash in newCrashCombo :
        crashContents = self.getClockFactContents( crash )

        for omission in triggerFault :
          omissionContents = self.getClockFactContents( omission )
          # CASE : same node and fault time greater than or equal to crash time
          if omissionContents[0] == crashContents[0] and int( omissionContents[2] ) >= int( crashContents[2] ) :
            pass
          # CASE : fact is outside the crash range
          else :
            newTriggerFault.append( omission )
      newTriggerFault.extend( newCrashCombo )

      # add the crash combination to the list associated with the fault in the fault tracker
      previousCrashes.append( newCrashCombo )
      self.faultTracker[ orig_fault_str ] = previousCrashes
      print "new self.faultTracker[ " + orig_fault_str + " ] = " + str( self.faultTracker[ orig_fault_str ] )

    # CASE : user doesn't want crashes
    else :
      newTriggerFault = triggerFault

    return newTriggerFault


  #############################
  #  GET CLOCK FACT CONTENTS  #
  #############################
  # given clock fact in the trigger fault format,
  # return contents as an array
  def getClockFactContents( self, clockFact ) :
    clockFact = clockFact.replace( "clock([", "" )
    clockFact = clockFact.replace( ")", "" )
    contents = clockFact.split( "," )
    return contents


  ######################
  #  SET CRASH COMBOS  #
  ######################
  # given the number of crashes specified by the user and the number of crashes
  # relevant to the good execution, generate the complete set of combinations
  # of crashes.
  def setCrashCombos( self ) :

    # CASE : user wants crashes
    if self.numCrashes > 0 :
      allCrashCombos = itertools.combinations( self.crashFacts, self.numCrashes )

      # generate all combinations of crashes 
      # not safe for executions with solutions containing lots of crashes
      while True :
        try :
          self.crashCombos.append( allCrashCombos.next() )
        except StopIteration :
          break

    # CASE : omission failures only => do not generate crash scenarios
    else :
      pass


  #######################
  #  GET TRIGGER FAULT  #
  #######################
  # grab one trigger fault to try during the next iteration
  def getTriggerFault( self ) :

    # no solution constraints: check every satisfying solution of the formula
    if self.no_soln_constraints :
      triggerFault = self.solveCNF( 1 )  # grab one new solution as the next trigger fault

    # yes solution constraints: check only interesting satisfying solutions of the formula
    else :

      # ---------------------------------------------------------------------- #
      # fill currSolnSet if necessary
      if self.currSolnSet == [] :

        # CASE : buffer size bigger than 1
        if self.N > 1 :
          # grab the solution set data
          triggerFaultSet = self.solveCNF( self.N )

          if not triggerFaultSet == [] :
            # refill the current solution set of constrained trigger faults.
            self.currSolnSet.extend( triggerFaultSet )

        # CASE : buffer size equal 1
        else :
          # refill the current solution set of constrained trigger faults.
          self.currSolnSet.append( self.solveCNF( 1 ) )

        # place smaller solutions earlier in the list.
        self.orderByMinimality( self.currSolnSet )

        # initialize solutions with empty crash logs in fault tracker
        for soln in self.currSolnSet :
          soln_str                      = str( soln )
          self.faultTracker[ soln_str ] = []

      # ---------------------------------------------------------------------- #
      # CASE : untested solutions exist
      if len( self.currSolnSet ) > 0 :

        if self.currTriggerFault :
          currCrashSet = self.faultTracker[ str( self.currTriggerFault ) ]

        # CASE : need a new current trigger fault
        if self.currTriggerFault == None or len( currCrashSet ) == len( self.crashCombos ) :
          # take the 0th element of the currSolnSet as the next trigger fault.
          triggerFault          = self.currSolnSet.pop( 0 )
          self.currTriggerFault = str( triggerFault ) # doesn't work when equating lists.

        # CASE : still crashes to test with current trigger fault
        else :
          triggerFault = ast.literal_eval( self.currTriggerFault )

        # only check faults with specified numbers of crashes
        triggerFault = self.setCrashes( triggerFault )

        return triggerFault

      # ---------------------------------------------------------------------- #
      # CASE : no untested solutions exist
      else :
        return None


  ##########################
  #  ORDER BY MINIIMALITY  #
  ##########################
  # bubble sort b/c quick and dirty
  def orderByMinimality( self, solnSet ) :

    for i in range( 0, len( solnSet ) ) :
      try :
        if len( solnSet[i] ) > len( solnSet[i+1] ) :
          temp         = solnSet[i]
          solnSet[i]   = solnSet[i+1]
          solnSet[i+1] = temp
      except IndexError :
        break

    return solnSet


  ########################
  #  DEDALUS TO DATALOG  #
  ########################
  # translate all input dedalus files into a single datalog program
  def dedalus_to_datalog( self, argDict, cursor ) :
    return dedt.translateDedalus( argDict, cursor )
  
  
  ##############
  #  EVALUATE  #
  ##############
  # evaluate the datalog program using some datalog evaluator
  # return some data structure or storage location encompassing the evaluation results.
  def evaluate( self, evaluatorType, allProgramData ) :

    evaluators    = [ 'C4_WRAPPER' ]  # evaluator options
    results_array = []                # evaluation results default is an empty array

    # ----------------------------------------------------------------- #
    # C4_WRAPPER
    if evaluatorType == evaluators[0] :
      results_array = c4_evaluator.runC4_wrapper( allProgramData )

    # ----------------------------------------------------------------- #
    # WHAAAAA????
    else :
      tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : unrecognized evaluator type '" + evaluatorType + "', currently recognized evaluators are : " + str(evaluators) )

    # ----------------------------------------------------------------- #
    # dump evaluation results locally
    eval_results_dump_dir = os.path.abspath( os.getcwd() ) + "/data/"

    # make sure data dump directory exists
    if not os.path.isdir( eval_results_dump_dir ) :
      print "WARNING : evalulation results file dump destination does not exist at " + eval_results_dump_dir
      print "> creating data directory at : " + eval_results_dump_dir
      os.system( "mkdir " + eval_results_dump_dir )
      if not os.path.isdir( eval_results_dump_dir ) :
        tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : unable to create evaluation results dump directory at " + eval_results_dump_dir )
      print "...done."

    # data dump directory exists
    self.eval_results_dump_to_file( results_array, eval_results_dump_dir )

    # ----------------------------------------------------------------- #
    # parse results into a dictionary
    parsedResults = tools.getEvalResults_dict_c4( results_array )

    # ----------------------------------------------------------------- #

    return parsedResults

 
  ###############################
  #  EVAL RESULTS DUMP TO FILE  #
  ###############################
  def eval_results_dump_to_file( self, results_array, eval_results_dump_dir ) :

    eval_results_dump_file_path = eval_results_dump_dir + "eval_dump_" + str( self.fault_id ) + ".txt"

    # save new contents
    f = open( eval_results_dump_file_path, "w" )

    for line in results_array :
      
      # output to stdout
      if DEBUG :
        print line

      # output to file
      f.write( line + "\n" )

    f.close()
 
  
  ####################
  #  CHECK FOR BUGS  #
  ####################
  # check for bugs in the results of evaluating a datalog program
  # returns a conclusion.
  def checkForBugs( self, parsedResults, eot ) :
    return evalTools.bugConditions( parsedResults, eot )
  
  
  #####################
  #  BUILD PROV TREE  #
  #####################
  # use the evaluation execution results to build a provenance tree of the evaluation execution.
  # return a provenance tree instance
  def buildProvTree( self, parsedResults, eot, iter_count, irCursor ) :
  
    if parsedResults :
      # 000000000000000000000000000000000000000000000000000000000000000000 #
      # grab the set of post records at EOT.
      # assume the right-most attribute/variable/field of the post schema
      # represents the last send time (aka EOT).
      # should be true b/c of the dedalus rewriter reqs for deductive rules.
      postrecords_all = parsedResults[ "post" ]
      postrecords_eot = []
    
      if DEBUG :
        print "postrecords_all = " + str(postrecords_all)
    
      for rec in postrecords_all :
    
        if DEBUG :
          print "rec     = " + str(rec)
          print "rec[-1] = " + str(rec[-1])
          print "eot     = " + str(eot)
    
        # collect eot post records only
        if int( rec[-1] ) == int( eot ) :
          postrecords_eot.append( rec )
    
      if DEBUG :
        print "postrecords_eot = " + str(postrecords_eot)
    
      # !!! BREAK EARLY IF POST CONTAINS NO EOT RECORDS !!!
      if len( postrecords_eot ) < 1 :
        tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : attempting to build a provenance tree when no post eot records exist. Aborting..." )
   
      # 000000000000000000000000000000000000000000000000000000000000000000 #
  
    # abort execution if evaluation results not accessible
    else :
      sys.exit( "ERROR: No access to evaluation results.\nAborting..." ) # sanity check
  
    # ------------------------------------------------------------------------------ #
    # there exist results and eot post records.
    if DEBUG :
      print "\n~~~~ BUILDING PROV TREE ~~~~"
  
    # ------------------------------------------------------------------------------ #
    # initialize provenance tree structure
    provTreeComplete = ProvTree.ProvTree( "FinalState", parsedResults, irCursor )

    # ------------------------------------------------------------------------------ #
    # populate prov tree
    for seedRecord in postrecords_eot :
      if DEBUG :
        print " ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
        print "           NEW POST RECORD "
        print "seedRecord = " + str( seedRecord )
      provTreeComplete.generateProvTree( "post", seedRecord )
    # ------------------------------------------------------------------------------ #

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    # KD : bcast node debugging session 6/21/17
    #provTreeComplete.createGraph( None, iter_count )
    #tools.bp( __name__, inspect.stack()[0][3], "built prov tree and created graph." )
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
 
    if OUTPUT_PROV_TREES_ON :
      provTreeComplete.createGraph( None, iter_count )
    # ------------------------------------------------------------------------------ #

    return provTreeComplete
  
  
  #################
  #  TREE TO CNF  #
  #################
  # input a provenance tree instance
  # output a cnf formula instance
  def tree_to_CNF( self, provTreeComplete ) :
  
    if DEBUG :
      print "\n~~~~ CONVERTING PROV TREE TO CNF ~~~~"
  
    provTree_fmla = EncodedProvTree_CNF.EncodedProvTree_CNF( provTreeComplete )
  
    if provTree_fmla.rawformula :
      print ">>> provTree_fmla.rawformula = \n" + str( provTree_fmla.rawformula )
      print
      print ">>> provTree_fmla.rawformula_simplified = \n" + str( provTree_fmla.rawformula_simplified )
      print
      print ">>> provTree_fmla.rawformula.display() = \n" + str( provTree_fmla.rawformula.display() )
      print
      print ">>> provTree_fmla.rawformula_simplified.display() = \n" + str( provTree_fmla.rawformula_simplified.display() )
      print
      print ">>> provTree_fmla.cnfformula = \n" + str( provTree_fmla.cnfformula )
      print
      print ">>> provTree_fmla.cnfformula_simplified = \n" + str( provTree_fmla.cnfformula_simplified )
      print

      if OUTPUT_TREE_CNF_ON :
        provTree_fmla.rawformula.graph()
  
    else :
      tools.bp( __name__, inspect.stack()[0][3], "ERROR: provTree_fmla.rawformula is empty. Aborting execution..." )
  
    return provTree_fmla
  
  
  ###############
  #  SOLVE CNF  #
  ###############
  # input a cnf formula instance
  # output a list of fault hypotheses to try during the next LDFI iteration
  # TODO: THIS IS PYCOSAT SPECIFIC!!! FW: GENERALIZE!!!
  def solveCNF( self, buffersize ) :

    # --------------------------------------------------------------- #
    # only solve over the fmla corresponding to the initial good run
    if self.fault_id == 1 : 
      self.solver.setFmla( self.initFmla ) 

    # --------------------------------------------------------------- #
    # get a new set of trigger faults
    # currSolnAttempt increment handled in Solver_PYCOSAT

    customFault = tools.getConfig( "CORE", "CUSTOM_FAULT", list )
    if not customFault == None and self.N > 1 :
      tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : specified a custom fault, " + str( customFault ) + ", but also specified a solution set buffer size greater than 1: N = " + str( self.N ) )

    # solve over a custom fault
    if customFault and not self.stopAtIt :
      triggerFaultSet  = customFault  # set of one fault
      self.stopAtIt    = self.fault_id + 1
      self.customFault = customFault

    # solve over solution set satisfying the fmla.
    # customFault is None and N (buffersize) >= 1
    else :
      if buffersize > 1 :
        triggerFaultSet  = self.solver.setOfNewTriggerFaults( buffersize )
        return triggerFaultSet
      else :
        triggerFaultSet = self.solver.oneNewTriggerFault( ) # set of one fault
        return triggerFaultSet


  ##########################
  #  GET NEW DATALOG PROG  #
  ##########################
  # input a list of fault hypotheses
  # output the path to the new datalog program
  def getNewDatalogProg( self, triggerFault, eff, irCursor, iter_count ) :

    if len( triggerFault ) > 0 :
      allProgramData = newProgGenerationTools.buildNewProg( triggerFault, eff, irCursor, iter_count, self.allProgramData_noClocks )
      return allProgramData

    else :
      tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : attempted to build a new datalog program, but no fault hypotheses exist." )


#########
#  EOF  #
#########
