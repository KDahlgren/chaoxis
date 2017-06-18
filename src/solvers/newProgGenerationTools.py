#!/usr/bin/env python

'''
newProgGenerationTools.py
  code for building new datalog programs 
  given a previously determined solution set.
'''

# **************************************** #

#############
#  IMPORTS  #
#############
# python packages
import inspect, os, sys, time
from types import *

# ------------------------------------------------------ #
# import sibling packages HERE!!!
sys.path.append( os.path.abspath( __file__ + "/../.." ) ) # src/
sys.path.append( os.path.abspath( __file__ + "/../../dedt" ) ) # src/


from utils       import dumpers, tools
from translators import dumpers_c4

# **************************************** #

DEBUG = False


####################
#  BUILD NEW PROG  #
####################
# input a set of solutions to the cnf formula in the form of sets of legible facts.
#   each set of legible facts represents one fault hypothesis.
# output chosen fault hypothesis (list of facts deleted from Clock)
def buildNewProg( triggerFault, eff, irCursor, iter_count, allProgramData_noClocks ) :

  print "buildNewProg : iter_count  = " + str( iter_count )
  print "solnSet : ["
  print triggerFault
  print "]"

  if DEBUG :
    print "...running buildNewProg..."

  ##############################################
  # check if program save directory exists
  testpath        = os.path.abspath( __file__ + "/../.." ) + "/evaluators/programFiles/"
  newProgSavePath = os.path.abspath( __file__ + "/../.." ) + "/evaluators/programFiles/" + "c4program.olg"

  if os.path.isdir( testpath ) :
    pass
  else :
    tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : directory for storing datalog programs does not exist:\n" + testpath + "\nThat's pretty weird. Aborting... " )

  # save the old program
  oldprogpath = None
  if os.path.isfile( newProgSavePath ) :
    oldprogpath = testpath + "c4program_" + str(time.strftime("%d%b%Y")) + "_" + str(time.strftime("%Hh%Mm%Ss" ) ) + "_" + str( iter_count ) + "_saved_olg.txt"
    os.system( "mv " + newProgSavePath + " " + oldprogpath )

  ##############################################

  allFaultFacts = getAllClockFacts( triggerFault, irCursor ) # get all clock fact deletions associated with the trigger fault.

  # ----------------------------------------- #
  # parse clock soln records
  parsedClockRecords = parseClock( allFaultFacts )

  if DEBUG :
    print "parsedClockRecords = "
    for p in parsedClockRecords :
      print p

  resetClock( parsedClockRecords, irCursor )

  # ----------------------------------------- #
  # build new clock configuration

  if DEBUG :
    print ">> CLOCK DUMP before <<"
    dumpers.clockDump( irCursor )

  # falsify the appropriate record(s)
  shootClockRecs( parsedClockRecords, eff, irCursor )

  if DEBUG :
    print "CHECK CLOCK TABLE HERE"
    print ">> CLOCK DUMP after <<"
    dumpers.clockDump( irCursor )

  # ----------------------------------------- #
  # get new clock lines
  newClockSet = finalizeNewProg( testpath, newProgSavePath, irCursor )

  ##############################################

  allProgramLines_noClocks = allProgramData_noClocks[0]
  tableListArray           = allProgramData_noClocks[1]
  allProgramLines          = allProgramLines_noClocks + newClockSet

  if DEBUG :
    print "------------------------------------"
    print "allProgramLines_noClocks:"
    print allProgramLines_noClocks
    print
    print "tableListArray:"
    print tableListArray
    print
    print "newClockSet:"
    print newClockSet
    print
    print "allProgramLines:"
    print allProgramLines
    print "------------------------------------"

  return [ allProgramLines, tableListArray ]


######################
#  SHOOT CLOCK RECS  #
######################
# flip the simInclude boolean in the clock relation from True to False for the fault hypothesis clock records.
def shootClockRecs( parsedClockRecords, eff, irCursor ) :

  if DEBUG :
    print "parsedClockRecords :"
    for p in parsedClockRecords :
      print p

  # flip all the simIncludes to True to reset to newest clock soln configuration
  #simInclude = "True"
  #irCursor.execute( "UPDATE Clock SET simInclude='" + simInclude + "'" )

  # flip the simIncludes for the target clock records
  simInclude = "False"
  for rec in parsedClockRecords :
    src       = rec[0]
    dest      = rec[1]
    sndTime   = rec[2]
    delivTime = rec[3]

    # only shoot clock records less than or equal to eff (end of finite failures)
    if int( sndTime ) <= int( eff ) :
      # optimistic by default
      qSRC       = "src=='" + src + "'"
      qDEST      = " AND dest=='" + dest + "'"
      qSNDTIME   = " AND sndTime==" + sndTime + ""
      qDELIVTIME = " AND delivTime==" + delivTime + ""
  
      # erase query components as necessary
      # EXISTING BUG TODO : does not work if _ in src --> need to handle ANDs more intelligently
      #  if _ in src, then query = ... WHERE AND dest==...
      if "_" in src :
        qSRC = ""
      if "_" in dest :
        qDEST    = ""
        qSNDTIME = "AND delivTime > " + sndTime # node remains crashed for the remainder of the simulation.
      if "_" in sndTime :
        qSNDTIME = ""
      if "_" in delivTime :
        qDELIVTIME = ""
  
      # set query
      query = "UPDATE Clock SET simInclude='" + simInclude + "' WHERE " + qSRC + qDEST + qSNDTIME + qDELIVTIME
  
      if DEBUG :
        print "query = " + str(query)
  
      # execute query
      irCursor.execute( query )


#########################
#  GET ALL CLOCK FACTS  #
#########################
# returns a list of one or more clock facts.
# fills out node crashes.
def getAllClockFacts( triggerFault, irCursor ) :

  dataList = parseClock( triggerFault )
  dataList = dataList[0]
  if "_" in dataList :
    # get all corrsponding clock facts
    src       = dataList[0]
    dest      = dataList[1]
    sndTime   = dataList[2]
    delivTime = dataList[3]

    # optimistic by default
    qSRC       = "src=='" + src + "'"
    qDEST      = " AND dest=='" + dest + "'"
    qSNDTIME   = " AND sndTime==" + sndTime + ""
    qDELIVTIME = " AND delivTime==" + delivTime + ""

    # erase query components as necessary
    # EXISTING BUG TODO : does not work if _ in src --> need to handle ANDs more intelligently
    if "_" in src :
      qSRC  = ""
    if "_" in dest :
      qDEST = ""
    if "_" in sndTime :
      qSNDTIME = ""
    if "_" in delivTime :
      qDELIVTIME = ""

    # set query
    query = "SELECT src,dest,sndTime,delivTime FROM Clock WHERE " + qSRC + qDEST + qSNDTIME + qDELIVTIME

    if DEBUG :
      print "query = " + str(query)

    # execute query
    irCursor.execute( query )
    solnList = irCursor.fetchall()
    solnList = tools.toAscii_multiList( solnList )

    # format solns
    solnChoice = []
    for soln in solnList :
      soln = [ str(i) for i in soln ] # convert all data to strings
      atts = ",".join(soln)
      solnChoice.append( "clock([" + atts + "])" )

    return solnChoice

  else :
    return triggerFault


#################
#  PARSE CLOCK  #
#################
def parseClock( preferredSoln ) :

  parsedFacts = []

  for clockFact in preferredSoln :
    fact = getContents( clockFact )
    fact = fact.split( "," )
    parsedFacts.append( fact )

  return parsedFacts


##################
#  GET CONTENTS  #
##################
# input clock fact string
# extract the data from the clock fact
def getContents( clockFact ) :

  if DEBUG :
    print ">clockFact = " + str( clockFact )

  openParen   = None
  closedParen = None
  for i in range(0,len(clockFact)) :
    if clockFact[i] == "(" :
      openParen = i
    elif clockFact[i] == ")" :
      closedParen = i

  if DEBUG :
    print "done with " + str( clockFact ) + " : " + str(clockFact[ openParen+2 : closedParen-1 ])

  return clockFact[ openParen+2 : closedParen-1 ]


#################
#  RESET CLOCK  #
#################
def resetClock( parsedClockRecords, irCursor ) :

  # flip all the simIncludes to True
  simInclude = "True"
  irCursor.execute( "UPDATE Clock SET simInclude='" + simInclude + "'" )


#######################
#  FINALIZE NEW PROG  #
#######################
# build the final version of the new program with the new clock fact configuration
def finalizeNewProg( testpath, newProgSavePath, irCursor ) :

  # get all clock facts where simInclude == True
  irCursor.execute( "SELECT src,dest,sndTime,delivTime FROM Clock WHERE simInclude=='True'" )
  res = irCursor.fetchall()
  res = tools.toAscii_multiList( res )

  # copy all True clock facts into the new program
  newClockFacts = []
  for data in res :
    src       = data[0]
    dest      = data[1]
    sndTime   = data[2]
    delivTime = data[3]
    # replace any single quotes with double quotes
    src  = src.replace(  '"', "'" )
    dest = dest.replace( '"', "'" )
    newClockLine = 'clock("' + src + '","' + dest + '",' + str( sndTime ) + "," + str( delivTime ) + ") ;\n"
    newClockFacts.append( newClockLine )

  # concatenate all clock facts into a single line
  newClockLines = None
  newClockLines = "".join( newClockFacts )
  if not newClockLines :
    tools.bp( __name__, inspect.stack()[0][3], "ERROR: no new clock configurations to explore." )

  return [ x.rstrip() for x in newClockFacts ]

#########
#  EOF  #
#########
