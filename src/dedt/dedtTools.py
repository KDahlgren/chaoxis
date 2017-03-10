#!/usr/bin/env python

'''
dedtTools.py
   Define additional functionality in a modular format
   to decrease the size of dedt.py
'''

import inspect, os, string, sqlite3, sys

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath1  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath1 )

from utils import tools

# ------------------------------------------------------ #


######################
#  REMOVE CONSTANTS  #
######################
# c4 cannot handle constants in attribute locations.
# need to replace constants with variable attributes and
# add an equation to the rule equating the new variable 
# to the old constant value.
def removeConstants( cursor ) :

  # iterate over rules
  # if any goal or subgoal att contains a constant or number
  #   then:
  #     0. for each constant/number X
  #     1. generate a random string R
  #     2. replace the constant/number in the appropriate att location
  #        with the random string
  #     3. create an eqn for the rid st R == X

  # get all rids
  cursor.execute( "SELECT rid FROM Rule" )
  allRIDs = cursor.fetchall()
  allRIDs = tools.toAscii_list( allRIDs )

  # examine goal atts and generate replacement eqns for constants and numbers.
  for rid in allRIDs :
    cursor.execute( "SELECT attID,attName FROM GoalAtt WHERE rid=='" + rid + "'" )
    goalAtts = cursor.fetchall()
    goalAtts = tools.toAscii_multiList( goalAtts )

    print ">> goalAtts = " + str(goalAtts)

    for att in goalAtts :
      attID   = att[0]
      attName = att[1]

      # check if string constant
      if ("'" in attName) or ('"' in attName) :
        # generate random new attName
        # replace the constant/number with the new attName
        # associate a new equation with the rule of the form 'newAttName == CONSTANTVAL'
        # TODO: syntax is very c4 specific.

        newAttName = tools.getID()

        cursor.execute( "UPDATE GoalAtt SET attName=='" + newAttName + "' WHERE rid=='" + rid + "' AND attID==" + str(attID)  )

        newEQN = newAttName + "==" + attName 
        newEID = tools.getID()
        cursor.execute( "INSERT INTO Equation VALUES ('" + rid + "','" + newEID  + "','" +  newEQN + "')" )

  return None


#########
#  EOF  #
#########
