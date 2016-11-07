#!/usr/bin/env python

'''
clockRelation.py
   Define the functionality for creating clock relations.
'''

import os, sys

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

#from utils import parseCommandLineInput
# ------------------------------------------------------ #

#############
#  GLOBALS  #
#############
CLOCKRELATION_DEBUG = False

#########################
#  INIT CLOCK RELATION  #
#########################
# input IR database cursor and cmdline input
# create initial clock relation
# output nothing
def initClockRelation( cursor, argDict ) :
  # check if node topology defined in Fact relation
  nodeFacts = cursor.execute('''SELECT name FROM Fact WHERE Fact.name == "node"''')

  defaultStartSendTime  = '1'
  maxSendTime           = argDict[ "EOT" ]
  defaultDelivTime      = 'NULL'

  # --------------------------------------------------------------------- #
  # prefer cmdline topology
  if argDict[ "nodes" ] :
    print "Using node topology from command line: " + str(argDict[ "nodes" ]) 

    nodeSet          = argDict[ "nodes" ]

    for i in range( int(defaultStartSendTime), int(maxSendTime)+1 ) :
      for n1 in nodeSet :
        for n2 in nodeSet :
          cursor.execute("INSERT OR IGNORE INTO Clock VALUES ('" + n1 + "','" + n2 + "','" + str(i) + "','" + defaultDelivTime + "')")

    # check for bugs
    if CLOCKRELATION_DEBUG :
      clock = cursor.execute('''SELECT * FROM Clock''')
      for c in clock :
        print c

  # --------------------------------------------------------------------- #
  # otherwise use topology from input files
  elif nodeFacts :
    print "Using node topology from input file(s)."

    # collect all connection info
    # assumes topology facts characterized by name == "node"
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
    for i in range( int(defaultStartSendTime), int(maxSendTime)+1 ) :
      for conn in topology :
        src        = conn[0]
        dest       = conn[1]
        sndTime    = conn[2] # unicode raw
        newSndTime = sndTime.encode('utf-8')

        if i >= int( newSndTime ) :
          cursor.execute("INSERT OR IGNORE INTO Clock VALUES ('" + src + "','" + dest + "','" + str(i) + "','" + defaultDelivTime + "')") # ignore duplicates

    # collect total node set
    nodeSet = []
    for conn in topology :
      if not conn[0] in nodeSet :
        nodeSet.append( conn[0] )
      elif not conn[1] in nodeSet :
        nodeSet.append( conn[1] )

    # assume all nodes have self connection at time 1 (may not be specified in input file)
    for n in nodeSet :
      src     = n
      dest    = n
      sndTime = "1"
      cursor.execute("INSERT OR IGNORE INTO Clock VALUES ('" + src + "','" + dest + "','" + sndTime + "','" + defaultDelivTime + "')") # ignore duplicates

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
