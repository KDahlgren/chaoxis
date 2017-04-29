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
packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

from utils import dumpers, tools

# **************************************** #

DEBUG      = True


####################
#  BUILD NEW PROG  #
####################
# input a set of solutions to the cnf formula in the form of sets of legible facts.
#   each set of legible facts represents one fault hypothesis.
# output chosen fault hypothesis (list of facts deleted from Clock)
def buildNewProg( solnSet, irCursor, iter_count ) :

  print "buildNewProg : iter_count  = " + str( iter_count )
  print "solnSet : ["
  for s in solnSet :
    print s
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
    tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR1: directory for storing datalog programs does not exist:\n" + testpath + "\nThat's pretty weird. Aborting... " )

  # save the old program
  oldprogpath = None
  if os.path.isfile( newProgSavePath ) :
    oldprogpath = testpath + "c4program_" + str(time.strftime("%d%b%Y")) + "_" + str(time.strftime("%Hh%Mm%Ss" ) ) + "_" + str( iter_count ) + "_saved_olg.txt"
    os.system( "mv " + newProgSavePath + " " + oldprogpath )

  ##############################################

  # need to pick one of the solutions
  if len( solnSet ) < 2 :
    preferredSoln = solnSet[0]
  else :
    preferredSoln = getPreferredSoln( solnSet, irCursor )
    # case no preferred soln exists
    if not preferredSoln :
      return None

  # ----------------------------------------- #
  # parse clock soln records
  parsedClockRecords = parseClock( preferredSoln )

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
  shootClockRecs( parsedClockRecords, irCursor )

  if DEBUG :
    print "CHECK CLOCK TABLE HERE"

  if DEBUG :
    print ">> CLOCK DUMP after <<"
    dumpers.clockDump( irCursor )

  # ----------------------------------------- #
  # build a copy of the old program, minus the clock fact lines
  copyProg( oldprogpath, testpath, newProgSavePath ) # edits the new program file directly

  # add the new clock lines.
  finalizeNewProg( testpath, newProgSavePath, irCursor )

  ##############################################

  # sanity checks are good for the soul  ~(^.^)~
  if newProgSavePath :
    return preferredSoln
  else :
    tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR: failed to write new program to " + newProgSavePath )


######################
#  SHOOT CLOCK RECS  #
######################
# flip the simInclude boolean in the clock relation from True to False for the fault hypothesis clock records.
def shootClockRecs( parsedClockRecords, irCursor ) :

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
      qDEST = ""
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


########################
#  GET PREFERRED SOLN  #
########################
# solnSet is an array
# pick the first soln containing only clock facts
# returns a list of one or more clock facts
def getPreferredSoln( solnSet, irCursor ) :

  solnChoice = None

  for aSoln in solnSet :
    if aSoln == [] : # skip empties
      pass

    # grab the first soln containing only clock facts
    valid = True
    for var in aSoln :
      if not "clock(" in var :
        valid = False
    if valid :
      solnChoice = aSoln
      break

  if solnChoice :
    dataList = parseClock( solnChoice )
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

  else :
    tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : no solution chosen." )

  return solnChoice


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
# extract the data from the clock fact
def getContents( clockFact ) :

  openParen   = None
  closedParen = None
  for i in range(0,len(clockFact)) :
    if clockFact[i] == "(" :
      openParen = i
    elif clockFact[i] == ")" :
      closedParen = i

  return clockFact[ openParen+2 : closedParen-1 ]


#################
#  RESET CLOCK  #
#################
def resetClock( parsedClockRecords, irCursor ) :

  # flip all the simIncludes to True
  simInclude = "True"
  irCursor.execute( "UPDATE Clock SET simInclude='" + simInclude + "'" )


###############
#  COPY PROG  #
###############
def copyProg( oldProgPath, testpath, newProgPath ) :

  programLines = []

  # copy old program, except for clock lines
  if os.path.isfile( oldProgPath ) :
    outfile = open( oldProgPath, "r" )
    programLines = outfile.readlines()
    outfile.close()
  else :
    sys.exit( "FATAL ERROR: cannot open old C4 Overlog program at : " + oldProgPath )

  # assumes program is formatted as a single line of concatenated program statements (may be c4 specific)
  #programLines = programLines[0].split( ";" )

  newProgLines = []
  for line in programLines :
    if not line.startswith( "clock(" ) :
      newProgLines.append( line )

  #newProg = "; ".join( newProgLines ) # <--- use this if program formatted as a series of concatenated lines.
  newProg = "".join( newProgLines ) # <--- use this if lines are delimited by carriage returns.

  ##############################################
  # save the new c4 program
  # existance check repetition is redundant, but very reassuring.
  if programLines :
    if os.path.isdir( testpath ) :
      outfile = open( newProgPath, "w" )
      outfile.write( newProg )
      outfile.close()
    else :
      sys.exit( "FATAL ERROR: directory for saving C4 Overlog program does not exist at : " + testpath )
  else :
    sys.exit( "FATAL ERROR: no old program specified. Aborting..." )
  ##############################################


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

  ##############################################
  # save the new c4 program
  # repetition is redundant, but very reassuring.
  if os.path.isdir( testpath ) :
    outfile = open( newProgSavePath, "a" )
    # appends to end of last line -> may mess with the correctness 
    # in copyProg wrt the assumption that the program exists as a single line
    outfile.write( newClockLines )
    outfile.close()
  else :
    sys.exit( "FATAL ERROR2: directory for saving C4 Overlog program does not exist: " + testpath )
  ##############################################


#########
#  EOF  #
#########
