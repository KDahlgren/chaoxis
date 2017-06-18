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
import inspect, os, sqlite3, sys, time

# ------------------------------------------------------ #
# import sibling packages HERE!!!

packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

from dedt           import dedt, dedalusParser
from derivation     import ProvTree
from utils          import parseCommandLineInput, tools
from evaluators     import c4_evaluator, evalTools
from solvers        import EncodedProvTree_CNF, newProgGenerationTools, solverTools
from visualizations import vizTools

# **************************************** #


DEBUG                = True
PROV_TREES_ON        = True
OUTPUT_PROV_TREES_ON = True
OUTPUT_TREE_CNF_ON   = True


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
  currSolnAttempt         = 1     # controls depth of soln search in pycosat. must start at 1.
  solver                  = None

  # --------------------------------- #


  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, argDict, cursor, solver ) :
    self.argDict           = argDict
    self.cursor            = cursor
    self.solver            = solver


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
  def run_workflow( self, triggerFault, old_provTree_fmla ) :

    # initialize return array
    return_array = []
    return_array.append( None )  # := conclusion
    return_array.append( None )  # := provTree_fmla
    return_array.append( None )  # := triggerFault
    return_array.append( None )  # := noNewSolns

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
    bugInfo         = self.checkForBugs( parsedResults, self.argDict[ "EOT" ] )
    conclusion      = bugInfo[0]
    explanation     = bugInfo[1]

    # update conclusion part of returns
    return_array[0] = conclusion


    ##############################################
    # CASE 1 :                                   # 
    #   Found a counterexample!                  #
    #   Return immediately.                      #
    ##############################################
    if conclusion == "FoundCounterexample" :
      return_array[2] = triggerFault
      return return_array


    ##############################################
    # CASE 2 :                                   # 
    #   Found a vacuously correct execution.     #
    #   No new prov tree.                        #
    #   Find another new soln over the previous  #
    #   CNF fmla.                                #
    #   fault_id already updated in              #
    #   FaultManager.                            #
    ##############################################
    elif conclusion == "NoCounterexampleFound" and explanation == "VACUOUS" :

      if old_provTree_fmla :

        # -------------------------------------------- #
        # 6. solve CNF formula                         #
        # -------------------------------------------- #

        return_array[1]       = old_provTree_fmla                   # no change in fmla
        self.currSolnAttempt += 1                                   # increment soln bound b/c still using same fmla
        triggerFault          = self.solveCNF( old_provTree_fmla )  # grab another soln to the old fmla
        return_array[2]       = triggerFault                        # update trigger fault part of returns
        return_array[3]       = self.solver.noNewSolns              # update soln status in returns

        return return_array # of the form [ conclusion/None, provTree_fmla/None, solutions/None ]

      elif not old_provTree_fmla and not self.fault_id > 1 :
        tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : no previous prov fmla and not initial run. Aborting..." )

      else :
        print "self.fault_id = " + str( self.fault_id )
        tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : illogical, captain. hit a vacuous result without injecting faults. Aborting..." )


    ##############################################
    # CASE 3 :                                   # 
    #   Found a correct execution, not vacuous.  #
    #   Can build new prov tree.                 #
    #   Find a new soln over the new tree.       #
    ##############################################
    else :

      # ----------------------------------------------- #
      # 4. get provenance trees                         #
      # ----------------------------------------------- #

      provTreeComplete = self.buildProvTree( parsedResults, self.argDict[ "EOT" ], self.fault_id, self.cursor )

      # -------------------------------------------- #
      # 5. generate CNF formula                      #
      # -------------------------------------------- #
 
      # fmla is of the form ~( CNF ) because we're 
      # equating solns with fault scenarios. 
      provTree_fmla = self.tree_to_CNF( provTreeComplete )

      # grab the textual version of the fmla
      finalFmla = provTree_fmla.cnfformula

      # update CNF component of returns
      return_array[1] = finalFmla

      # -------------------------------------------- #
      # 6. solve CNF formula                         #
      # -------------------------------------------- #

      self.currSolnAttempt = 1                          # reset soln bound b/c using new fmla
      triggerFault         = self.solveCNF( finalFmla ) # grab a soln to the prov tree
      return_array[2]      = triggerFault                      # update trigger fault part of returns
      return_array[3]      = self.solver.noNewSolns            # update soln status in returns

      return return_array # of the form [ conclusion/None, provTree_fmla/None, solutions/None ]


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
  
    # ------------------------------------------------------------- #
    # there exist results and eot post records.
    if DEBUG :
      print "\n~~~~ BUILDING PROV TREE ~~~~"
  
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    # initialize provenance tree structure
    provTreeComplete = ProvTree.ProvTree( "FinalState", parsedResults, irCursor )

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    # populate prov tree
    for seedRecord in postrecords_eot :
      if DEBUG :
        print " ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
        print "           NEW POST RECORD "
        print "seedRecord = " + str( seedRecord )
      newProvTree = provTreeComplete.generateProvTree( "post", seedRecord )
      provTreeComplete.subtrees.append( newProvTree )
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
  
    if OUTPUT_PROV_TREES_ON :
      provTreeComplete.createGraph( None, iter_count )
    # ------------------------------------------------------------- #

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
      print ">>> provTree_fmla.rawformula = " + str( provTree_fmla.rawformula )
      print
      print ">>> provTree_fmla.rawformula.display() = " + str( provTree_fmla.rawformula.display() )
      print
      print ">>> provTree_fmla.cnfformula = " + str( provTree_fmla.cnfformula )
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
  def solveCNF( self, finalFmla ) :
 
    self.solver.setFmla( finalFmla ) 

    # --------------------------------------------------- #
    # pick one new trigger fault

    triggerFault = self.solver.oneNewTriggerFault( )

    # --------------------------------------------------- #
  
    return triggerFault


  #######################
  #  REMOVE DUPLICATES  #
  #######################
  # given a list of strings
  # output list of unique strings
  def removeDuplicates( self, solnList ) :
   
    uniqueList = []
    for s in solnList :
      if s : # skip empties
        if not s in uniqueList :
          uniqueList.append( s )
  
    return uniqueList
  
  
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


  ####################
  #  REMOVE CRASHES  #
  ####################
  # input a soln consisting only of clock facts.
  # outputs a list of containing solutions such that each solution contains 
  # the original set of clock facts, minus the clock facts indicating crash failures( e.g. clock('a','_',1,_) )
  def removeCrashes( self, soln ) :
    
    cleanSoln = []
    for clockFact in soln :
      content = newProgGenerationTools.getContents( clockFact )
      content = content.split( "," )
      if content[1] == "_" : # sender is the same as the receiver
        pass
      else :
        cleanSoln.append( clockFact )

    return cleanSoln

#########
#  EOF  #
#########
