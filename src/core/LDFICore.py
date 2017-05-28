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
  old_faults        = None  # list of previously tried faults. reassigned with every invocation of run_workflow.

  # --------------------------------- #

  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, c4_save, table_save, datalog_save, argDict, cursor ) :
    self.c4_dump_savepath  = c4_save
    self.table_list_path   = table_save
    self.datalog_prog_path = datalog_save
    self.argDict           = argDict
    self.cursor            = cursor


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
  def run_workflow( self, triggerFault, old_provTree, old_faults ) :

    # reassign old_faults
    self.old_faults = old_faults

    # initialize return array
    return_array = []
    return_array.append( None )  # := conclusion
    return_array.append( None )  # := provTree_merged
    return_array.append( None )  # := solutions

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

      self.getNewDatalogProg( [ triggerFault ], self.cursor, self.fault_id )

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
      print "CHECKING FOR BUGS on results from triggerFault = " + str(triggerFault)

    # check for bugs
    bugInfo         = self.checkForBugs( parsedResults, self.argDict[ "EOT" ] )
    conclusion      = bugInfo[0]
    explanation     = bugInfo[1]

    # update conclusion part of returns
    return_array[0] = conclusion


    ##############################################
    # CASE 1 :                                   # 
    #   Found a counterexample!                  #
    #   Return immediately.
    ##############################################
    if conclusion == "FoundCounterexample" :
      return return_array

    ##############################################
    # CASE 2 :                                   # 
    #   Found a vacuously correct execution.     #
    #   No new prov tree.                        #
    #   Find a new soln over previous tree.      #
    ##############################################
    elif conclusion == "NoCounterexampleFound" and explanation == "VACUOUS" :

      if old_provTree :

        # -------------------------------------------- #
        # 4. get provenance trees                      #
        #     no change in provTree by definition      #
        # -------------------------------------------- #

        return_array[1] = old_provTree

        # -------------------------------------------- #
        # 5. generate CNF formula                      #
        # -------------------------------------------- #

        provTree_fmla = self.tree_to_CNF( old_provTree )

        # -------------------------------------------- #
        # 6. solve CNF formula                         #
        # -------------------------------------------- #

        finalSolnList   = self.solveCNF( provTree_fmla )         # grab a soln to the prov tree
        finalSolnList   = self.removeSelfComms( finalSolnList )  # self comms are pointless
        return_array[2] = finalSolnList                          # update solutions part of returns

        return return_array # of the form [ conclusion/None, provTree_merged/None, solutions/None ]

      elif not old_provTree and not self.fault_id == 1 :
        tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : no previous prov tree and not initial run. Aborting..." )

      else :
        tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : illogical. hit a vacuous result without injecting faults. Aborting..." )


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

      provTreeComplete = self.buildProvTree( old_provTree, parsedResults, self.argDict[ "EOT" ], self.fault_id, self.cursor )
      # merge new prov tree with prov tree from previous iteration
      provTree_merged = None
      if old_provTree :
        provTree_merged  = provTreeComplete.mergeTrees( old_provTree ) 

      # update provTree_merged part of returns 
      if provTree_merged :
        return_array[1] = provTree_merged
      else :
        return_array[1] = provTreeComplete

      # -------------------------------------------- #
      # 5. generate CNF formula                      #
      # -------------------------------------------- #
  
      provTree_fmla   = self.tree_to_CNF( provTreeComplete )

      # -------------------------------------------- #
      # 6. solve CNF formula                         #
      # -------------------------------------------- #
  
      finalSolnList = self.solveCNF( provTree_fmla )         # grab a soln to the prov tree
      finalSolnList = self.removeSelfComms( finalSolnList )  # self comms are pointless
      #if DEBUG :
      #  finalSolnList = self.removeCrashes( finalSolnList ) # debugging only
      return_array[2] = finalSolnList  # update solutions part of returns
  
      return return_array # of the form [ conclusion/None, provTree_merged/None, solutions/None ]


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
  def buildProvTree( self, old_provTree, parsedResults, eot, iter_count, irCursor ) :
  
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
    
      # !!! RETURN EARLY IF POST CONTAINS NO EOT RECORDS !!!
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

    #print "PRINTING EDGE SET"
    #print provTreeComplete.getEdgeSet()

    #os.system( "rm /Users/KsComp/projects/pyldfi/qa/testfiles/expected_provTreeComplete.txt" ) 
    #fo = open( "/Users/KsComp/projects/pyldfi/qa/testfiles/expected_provTreeComplete.txt", "w" )
    #fo.write( str( provTreeComplete.getEdgeSet() ) )
    #fo.close()
    #sys.exit( "ermergerd! saved provTreeComplete for first good execution!" ) 

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

      #os.system( "rm /Users/KsComp/projects/pyldfi/qa/testfiles/expected_cnf_fmla_save.txt" )
      #fo = open( "/Users/KsComp/projects/pyldfi/qa/testfiles/expected_cnf_fmla_save.txt", "w" )
      #fo.write( str( provTree_fmla.cnfformula ) )
      #fo.close()
      #sys.exit( "ermergerd! just saved the cnf fmla for the initial good execution to a file!" )
 
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
  def solveCNF( self, provTree_fmla ) :
  
    finalSolnList = []

    # remove self comms
    cleanCNFFmla = self.removeSelfComms( provTree_fmla.cnfformula )

    # create a Solver_PYCOSAT insance
    solns = solverTools.solveCNF( "PYCOSAT", cleanCNFFmla, self.fault_id )
  
    if solns :
      if DEBUG :
        numid = 1   # for tracking the current soln number
  
      # --------------------------------------------------- #
      # pick one new solution

      aSoln = solns.oneNewSolution( )

      finalStr = self.getLegibleFmla( aSoln )

      if DEBUG :
        print "SOLN : " + str(numid) + "\n" + str( finalStr )
        numid += 1
  
      # add soln to soln list and clear temporary save list for the next iteration
      finalSolnList.append( finalStr )
  
      # remove duplicates
      finalSolnList = self.removeDuplicates( finalSolnList )

      # --------------------------------------------------- #
  
    return finalSolnList
  
  
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
  
  ######################
  #  GET LEGIBLE FMLA  #
  ######################
  # given messy raw solution
  # output legible version
  def getLegibleFmla( self, aSoln ) :
  
    fmlaStr = []  # stores the legible version of the soln.
  
    # make legible
    for var in aSoln :
      fmlaStr.append( solverTools.toggle_format_str( var, "legible" ) )
  
    return fmlaStr
  
  
  ##########################
  #  GET NEW DATALOG PROG  #
  ##########################
  # input a list of fault hypotheses
  # output the path to the new datalog program
  def getNewDatalogProg( self, faultHypoList, irCursor, iter_count ) :

    if len( faultHypoList ) > 0 :
      return newProgGenerationTools.buildNewProg( faultHypoList, irCursor, iter_count )
  
    else :
      tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : attempted to build a new datalog program, but no fault hypotheses exist." )


  #######################
  #  REMOVE SELF COMMS  #
  #######################
  # input a solution consisting only of clock facts.
  # outputs a list of containing solutions such that each solution contains 
  # the original set of clock facts, minus the self-comm clock facts ( e.g. clock('a','a',1,2) )
  def removeSelfComms( self, soln ) :

    print "soln    = " + str( soln )
    print "soln[0] = " + str( soln[0] )

    strInput = False
    if type( soln[0] ) == list :
      soln = soln[0]
    elif type( soln ) is str :
      strInput = True
      soln     = soln.split( " OR " )

    if DEBUG :
      print ">soln = " + str( soln )

    cleanSoln = []
    for clockFact in soln :
      print "clockFact = " + str(clockFact)
      content = newProgGenerationTools.getContents( clockFact )
      content = content.split( "," )
      if content[0] == content[1] : # sender is the same as the receiver
        pass
      else :
        cleanSoln.append( clockFact )

    if strInput :
      return " OR ".join( cleanSoln )
    else :
      return cleanSoln

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
