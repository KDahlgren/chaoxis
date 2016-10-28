#!/usr/bin/env python

import os, sys

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

from utils import sanityChecks, parseCommandLineInput
# ------------------------------------------------------ #

#########################
#  INIT CLOCK RELATION  #
#########################
# input IR database cursor and cmdline input
# create initial clock relation
# output nothing
def initClockRelation( cursor, argDict) :
  # check if node topology defined in Fact relation
  nodeFacts = cursor.execute('''SELECT name FROM Fact WHERE Fact.name == "node"''')

  # --------------------------------------------------------------------- #
  # prefer cmdline topology
  if argDict[ "nodes" ] :
    print "Using node topology from command line: " + str(argDict[ "nodes" ]) 

    nodeSet          = argDict[ "nodes" ]
    defaultSendTime  = '1'
    defaultDelivTime = 'NULL'

    for n1 in nodeSet :
      for n2 in nodeSet :
        cursor.execute("INSERT INTO Clock VALUES ('" + n1 + "','" + n2 + "','" + defaultSendTime + "','" + defaultDelivTime + "')")

    # double check success
    #clock = cursor.execute('''SELECT * FROM Clock''')
    #for c in clock :
    #  print c

  # --------------------------------------------------------------------- #
  # otherwise use topology from input files
  elif nodeFacts :
    print "Using node topology from input file(s)."

    # collect all connection info
    cursor.execute('''SELECT Fact.fid, FactAtt.attID, FactAtt.attName, Fact.timeArg FROM Fact, FactAtt WHERE Fact.fid == FactAtt.fid AND Fact.name == "node"''')

    # collect connections
    topology = []
    results = cursor.fetchall()

    for i in range(1, len(results)) :
      prevNode = results[i-1]
      currNode = results[i]
      connection = []

      if currNode[0] == prevNode[0] : # match fid's
        if (prevNode[1] == unicode("0")) and (currNode[1] == unicode("1")) :
          src  = prevNode[2]
          dest = currNode[2]
          time = currNode[3]

        elif (prevNode[1] == unicode("1")) and (currNode[1] == unicode("0")) :
          src  = currNode[2]
          dest = prevNode[2]
          time = currNode[3]

        else :
          sys.exit( "ERROR: attID ordering\n" + "  prevNode = " + str(prevNode) + "\n" + "  currNode = " + str(currNode) )

        connection.append( src )
        connection.append( dest )
        connection.append( time )

        topology.append( connection )

    # save connections as clock entries
    for conn in topology :
      src     = conn[0]
      dest    = conn[1]
      sndTime = conn[2]
      cursor.execute("INSERT INTO Clock VALUES ('" + src + "','" + dest + "','" + sndTime + "')")

    # collect total node set
    nodeSet = []
    for conn in topology :
      if not conn[0] in nodeSet :
        nodeSet.append( conn[0] )
      elif not conn[1] in nodeSet :
        nodeSet.append( conn[1] )

    # assume all nodes have self connection at time 1
    for n in nodeSet :
      src     = n
      dest    = n
      sndTime = "1"
      cursor.execute("INSERT OR REPLACE INTO Clock VALUES ('" + src + "','" + dest + "','" + sndTime + "')")

    # assume all nodes have self connection at time 1
    for n in nodeSet :
      src     = n
      dest    = n
      sndTime = "1"
      cursor.execute("INSERT OR IGNORE INTO Clock VALUES ('" + src + "','" + dest + "','" + sndTime + "')") # ignore duplicates

    # double check success
    print "Clock relation :"
    clock = cursor.execute('''SELECT * FROM Clock''')
    for c in clock :
      print c

  # --------------------------------------------------------------------- #
  else :
    sys.exit( "ERROR: No node topology specified! Aborting..." )

  return None

##########################
#  BUILD CLOCK RELATION  #
##########################
# input IR database cursor
# create a clock relation
# output nothing
def buildClockRelation( cursor ) :
  return None

#########
#  EOF  #
#########
