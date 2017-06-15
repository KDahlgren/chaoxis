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
  c4_dump_savepath  = None
  table_list_path   = None
  datalog_prog_path = None
  argDict           = None  # dictionary of commaned line args
  cursor            = None  # a reference to the IR database
  fault_id          = 1     # id of the current fault to inject. start at 1 for pycosat.
  currSolnAttempt   = 1     # controls depth of soln search in pycosat. must start at 1.
  solver            = None

  # --------------------------------- #


  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, c4_save, table_save, datalog_save, argDict, cursor, solver ) :
    self.c4_dump_savepath  = c4_save
    self.table_list_path   = table_save
    self.datalog_prog_path = datalog_save
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
 
    # save the previous c4 program for records (not used in future iterations).
    if os.path.isfile( self.c4_dump_savepath ) :
      os.system( "mv " + self.c4_dump_savepath + " " + self.c4_dump_savepath + "_" + time.strftime("%d%b%Y-%Hh%Mm%Ss") + "_iter" + str( self.fault_id ) + ".txt" )
  
    # ----------------------------------------------- #
    # 1. get datalog                                  #
    # ----------------------------------------------- #
    if self.fault_id == 1 :

      # ---------------------------------------------------------------- #
      # first LDFI core run                                              #
      # translate all input dedalus files into a single datalog program  #
      # ---------------------------------------------------------------- #

      self.dedalus_to_datalog( self.argDict, self.table_list_path, self.datalog_prog_path, self.cursor )

    else :

      # -------------------------------------------- #
      # 7. generate new datalog prog                 #
      # -------------------------------------------- #

      self.getNewDatalogProg( [ triggerFault ], self.argDict[ "EFF" ], self.cursor, self.fault_id )

    # ----------------------------------------------- #
    # 2. evaluate                                     #
    # ----------------------------------------------- #
 
    # use c4 wrapper 
    resultsPath   = self.evaluate( "C4_WRAPPER", self.table_list_path, self.datalog_prog_path, self.c4_dump_savepath )
    # use c4 from command line (deprecated)
    #resultsPath   = self.evaluate( "C4_CMDLINE", self.table_list_path, self.datalog_prog_path, self.c4_dump_savepath )
    parsedResults = tools.getEvalResults_file_c4( resultsPath ) # assumes C4 results stored in dump
  
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

      #if self.fault_id == 2 :
      #  tools.bp( __name__, inspect.stack()[0][3], "finalFmla = " + str(finalFmla) )

      # update CNF component of returns
      return_array[1] = finalFmla

      # -------------------------------------------- #
      # 6. solve CNF formula                         #
      # -------------------------------------------- #

      #if old_provTree_fmla :
      #  print old_provTree_fmla
      #  print finalFmla
      #  tools.bp( __name__, inspect.stack()[0][3], "asdlfkjh" )

      self.currSolnAttempt = 1                          # reset soln bound b/c using new fmla
      triggerFault         = self.solveCNF( finalFmla ) # grab a soln to the prov tree
      return_array[2]      = triggerFault                      # update trigger fault part of returns
      return_array[3]      = self.solver.noNewSolns            # update soln status in returns

      return return_array # of the form [ conclusion/None, provTree_fmla/None, solutions/None ]


  ########################
  #  DEDALUS TO DATALOG  #
  ########################
  # translate all input dedalus files into a single datalog program
  def dedalus_to_datalog( self, argDict, table_list_path, datalog_prog_path, cursor ) :
    return dedt.translateDedalus( argDict, table_list_path, datalog_prog_path, cursor )
  
  
  ##############
  #  EVALUATE  #
  ##############
  # evaluate the datalog program using some datalog evaluator
  # return some data structure or storage location encompassing the evaluation results.
  def evaluate( self, evaluatorType, table_list_path, datalog_prog_path, savepath ) :
  
    evaluators = [ 'C4_CMDLINE', 'C4_WRAPPER' ]
  
    # C4_CMDLINE
    if evaluatorType == evaluators[0] :
      return c4_evaluator.runC4_directly( datalog_prog_path, table_list_path, savepath )
  
    # C4_WRAPPER
    elif evaluatorType == evaluators[1] :
      return c4_evaluator.runC4_wrapper( datalog_prog_path, table_list_path, savepath )
  
    # WHAAAAA????
    else :
      tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : unrecognized evaluator type '" + evaluatorType + "', currently recognized evaluators are : " + str(evaluators) )
  
  
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
  def getNewDatalogProg( self, faultHypoList, eff, irCursor, iter_count ) :

    if len( faultHypoList ) > 0 :
      return newProgGenerationTools.buildNewProg( faultHypoList, eff, irCursor, iter_count )
  
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
