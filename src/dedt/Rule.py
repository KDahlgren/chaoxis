#!/usr/bin/env python

'''
Rule.py
   Defines the Rule class.
   Establishes all relevant attributes and get/set methods.
'''

import inspect, os, sqlite3, sys

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

from utils import extractors, tools
# ------------------------------------------------------ #

opList = [ "notin" ] # TODO: make this configurable

class Rule :

  ################
  #  ATTRIBUTES  #
  ################
  rid        = ""
  cursor     = None

  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, rid, cursor ) :
    self.rid    = rid
    self.cursor = cursor

  # ------------------------------------- #
  #                GET                    #
  # ------------------------------------- #

  ###################
  #  GET GOAL NAME  #
  ###################
  def getGoalName( self ) :
    self.cursor.execute( "SELECT goalName FROM Rule WHERE rid = '" + self.rid + "'" )
    nameList = self.cursor.fetchall()
    nameList = tools.toAscii_list( nameList )
    if not nameList == None :
      if len(nameList) == 1 :
        return nameList[0]
      else :
        sys.exit( "ERROR: Rule possesses more than one goal : " + nameList )

  ###################
  #  GET REWRITTEN  #
  ###################
  def getRewritten( self ) :
    self.cursor.execute( "SELECT rewritten FROM Rule WHERE rid = '" + self.rid + "'" )
    rewrittenList = self.cursor.fetchall()
    rewrittenList = tools.toAscii_list( nameList )
    if not rewrittenList == None :
      if len(rewrittenList) == 1 :
        return rewrittenList[0]
      else :
        sys.exit( "ERROR: Rule possesses more than one rewritten flag : " + rewrittenList )

  #############################
  #  GET GOAL ATTRIBUTE LIST  #
  #############################
  def getGoalAttList( self ) :
    self.cursor.execute( "SELECT attName FROM GoalAtt WHERE rid = '" + self.rid + "'" )
    attList = self.cursor.fetchall()
    attList = tools.toAscii_list( attList )
    return attList

  ###########################
  # GET GOAL TIME ARGUMENT  #
  ###########################
  def getGoalTimeArg( self ) :
    self.cursor.execute( "SELECT goalTimeArg FROM Rule WHERE rid = '" + self.rid + "'" )
    timeArgList = self.cursor.fetchall()
    timeArgList = tools.toAscii_list( timeArgList )
    if not timeArgList == None :
      if len(timeArgList) == 1 :
        return timeArgList[0]
      else :
        sys.exit( "ERROR: Rule goal possesses more than 1 time argument : " + timeArgList )

  #############################
  #  GET SUBGOAL LIST STRING  #
  #############################
  def getSubgoalListStr( self ) :
    self.cursor.execute( "SELECT sid FROM Subgoals WHERE rid = '" + self.rid + "'" )
    subIDList = self.cursor.fetchall()
    subIDList = tools.toAscii_list( subIDList )

    subgoalList = ""
    currSubgoal = ""

    # iterate over sids
    for k in range(0,len(subIDList)) :
      sid = subIDList[ k ]

      # get subgoal name
      self.cursor.execute( "SELECT subgoalName FROM Subgoals WHERE rid == '" + self.rid + "' AND sid == '" + sid + "'" )
      subgoalName = self.cursor.fetchone()

      if not subgoalName == None :
        subgoalName = tools.toAscii_str( subgoalName )

        # get subgoal attribute list
        subAtts = self.cursor.execute( "SELECT attName FROM SubgoalAtt WHERE rid == '" + self.rid + "' AND sid == '" + sid + "'" )
        subAtts = tools.toAscii_list( subAtts )

        # get subgoal time arg
        self.cursor.execute( "SELECT subgoalTimeArg FROM Subgoals WHERE rid == '" + self.rid + "' AND sid == '" + sid + "'" ) # get list of sids for this rule
        subTimeArg = self.cursor.fetchone() # assume only one additional arg
        subTimeArg = tools.toAscii_str( subTimeArg )

        ## get subgoal additional args
        self.cursor.execute( "SELECT argName FROM SubgoalAddArgs WHERE rid == '" + self.rid + "' AND sid == '" + sid + "'" ) # get list of sids for this rule
        subAddArg = self.cursor.fetchone() # assume only one additional arg
        if not subAddArg == None :
          subAddArg = tools.toAscii_str( subAddArg )

        # all subgoals have a name and open paren
        if not subAddArg == None :
          currSubgoal += subAddArg + " "
        currSubgoal += subgoalName + "("

        # add in all attributes
        for i in range(0,len(subAtts)) :
          if i < (len(subAtts) - 1) :
            currSubgoal += subAtts[i] + ","
          else :
            currSubgoal += subAtts[i] + ")"

        # conclude with time arg, if applicable
        if not subTimeArg == "" :
          currSubgoal += "@" + subTimeArg

        # cap with a comma, if applicable
        if k < len( subIDList ) - 1 :
          currSubgoal += ","

      subgoalList += currSubgoal
      currSubgoal = ""

    return subgoalList


  ##############################
  #  GET EQUATION LIST STRING  #
  ##############################
  def getEquationListStr( self ) :
    self.cursor.execute( "SELECT eid FROM Equation" ) # get list of eids for this rule
    eqnIDs = self.cursor.fetchall()
    eqnIDs = tools.toAscii_list( eqnIDs )

    eqnList = ""

    # iterate over equations in rule
    for e in range(0,len(eqnIDs)) :
      currEqnID = eqnIDs[e]

      # get associated equation
      if not currEqnID == None :
        self.cursor.execute( "SELECT eqn FROM Equation WHERE rid == '" + self.rid + "' AND eid == '" + str(currEqnID) + "'" )
        eqn = self.cursor.fetchone()
        if not eqn == None :
          eqn = tools.toAscii_str( eqn )

          # convert eqn info to pretty string
          eqnList += eqn
          if not e < len(eqnIDs) :
            eqnList += ","

    return eqnList

  #############################
  #  GET EQUATION LIST ARRAY  #
  #############################
  def getEquationListArray( self ) :
    self.cursor.execute( "SELECT eid FROM Equation" ) # get list of eids for this rule
    eqnIDs = self.cursor.fetchall()
    eqnIDs = tools.toAscii_list( eqnIDs )

    eqnList = []

    # iterate over equations in rule
    for e in range(0,len(eqnIDs)) :
      currEqnID = eqnIDs[e]

      # get associated equation
      if not currEqnID == None :
        self.cursor.execute( "SELECT eqn FROM Equation WHERE rid == '" + self.rid + "' AND eid == '" + str(currEqnID) + "'" )
        eqn = self.cursor.fetchone()
        if not eqn == None :
          eqn = tools.toAscii_str( eqn )

          # convert eqn info to pretty string
          if not e < len(eqnIDs) :
            eqn += ","
          eqnList.append(eqn)

    return eqnList



  # ------------------------------------- #
  #                SET                    #
  # ------------------------------------- #

  ###################
  #  SET GOAL INFO  #
  ###################
  # set goal name and time arg
  def setGoalInfo( self, name, timeArg, rewrittenFlag ) :
    #if timeArg == None :
    #  timeArg = 'async'
    self.cursor.execute("INSERT INTO Rule (rid, goalName, goalTimeArg, rewritten) VALUES ('" + self.rid + "','" + name + "','" + timeArg + "','" + str(rewrittenFlag) + "')")


  #######################
  #  SET GOAL ATT LIST  #
  #######################
  # set goal attribute list
  def setGoalAttList( self, attList ) :
    attID = 0  # allows duplicate attributes in attList
    for attName in attList :
      self.cursor.execute("INSERT INTO GoalAtt VALUES ('" + self.rid + "','" + str(attID) + "','" + attName + "','UNDEFINEDTYPE')")
      attID += 1


  #############################
  #  SET SINGLE SUBGOAL INFO  #
  #############################
  # set single subgoal name and time argument
  def setSingleSubgoalInfo( self, sid, subgoalName, subgoalTimeArg ) :
    # replace any ops with empty
    for op in opList :
      op = "___" + op + "___"
      if op in subgoalName :
        subgoalName = subgoalName.replace( op, "" )

    self.cursor.execute("INSERT INTO Subgoals VALUES ('" + self.rid + "','" + sid + "','" + subgoalName + "','" + subgoalTimeArg + "')")


  #################################
  #  SET SINGLE SUBGOAL ATT LIST  #
  #################################
  # set single subgoal attribute list
  def setSingleSubgoalAttList( self, sid, subgoalAttList ) :
    attID = 0 # allows duplicate attributes in list
    for attName in subgoalAttList :
      self.cursor.execute("INSERT INTO SubgoalAtt VALUES ('" + self.rid + "','" + sid + "','" + str(attID) + "','" + attName + "','UNDEFINEDTYPE')")
      attID += 1


  ########################
  #  SET SINGLE SUBGOAL  #
  ########################
  # set single subgoal additional arguments
  def setSingleSubgoalAddArgs( self, sid, subgoalAddArgs ) :
    for addArg in subgoalAddArgs :
      self.cursor.execute("INSERT INTO SubgoalAddArgs VALUES ('" + self.rid + "','" + sid + "','" + addArg + "')")


  ####################
  #  SET SINGLE EQN  #
  ####################
  # set single equation
  def setSingleEqn( self, eid, eqn ) :
    self.cursor.execute("INSERT INTO Equation VALUES ('" + self.rid + "','" + eid + "','" + eqn + "')")


  ###################
  #  SET ATT TYPES  #
  ###################
  def setAttTypes( self ) :

    # ----------------------------------------------------------- #
    # set the types for rule subgoal atts
    # get goal name
    self.cursor.execute( "SELECT goalName FROM Rule WHERE rid = '" + self.rid + "'" )
    goalName = self.cursor.fetchone()
    goalName = tools.toAscii_str( goalName )

    # if it's a prov rule, get the original goal name
    provGoalNameOrig = None
    if "_prov" in goalName :
      provGoalNameOrig = goalName.split( "_prov" )
      provGoalNameOrig = provGoalNameOrig[0]

    # get goal attribute list
    self.cursor.execute( "SELECT attID,attName From GoalAtt WHERE rid = '" + self.rid + "'" )
    goalAttList = self.cursor.fetchall()
    goalAttList = tools.toAscii_multiList( goalAttList )

    # iterate over goal atts for this rule and set types
    for k in range(0,len(goalAttList)) :
      att     = goalAttList[ k ]
      attID   = att[0]
      attName = att[1]

      # TODO: not generalizable. Also does not combine hints 
      # from multiple appearances of the same sub/goal 
      # to combat underscores.
      #
      # Time references are always integers.
      if "Time" in attName :
        self.cursor.execute( "UPDATE GoalAtt SET attType=='int' WHERE rid=='" + self.rid + "' AND attID==" + str(attID) )

      # use types of data in fact definitions as clues for table definition field types
      elif tools.isFact( goalName, self.cursor ) or tools.isFact( provGoalNameOrig, self.cursor ) :

        # case working with an original rule definition
        if goalName :
          self.cursor.execute( "SELECT Fact.fid,attID,attName FROM Fact,FactAtt WHERE Fact.fid==FactAtt.fid AND Fact.name=='" + str(goalName) + "'")
#
        # case working with a provenance rule definition
        if provGoalNameOrig :
          self.cursor.execute( "SELECT Fact.fid,attID,attName FROM Fact,FactAtt WHERE Fact.fid==FactAtt.fid AND Fact.name=='" + str(provGoalNameOrig) + "'")

        attFIDsIDsNames = self.cursor.fetchall()
        attFIDsIDsNames = tools.toAscii_multiList( attFIDsIDsNames )

        # extract types from fact definitions
        # if kth fact attrib is int, then append int
        try :
          if attFIDsIDsNames[k][2].isdigit() :
            self.cursor.execute( "UPDATE GoalAtt SET attType=='int' WHERE rid=='" + self.rid + "' AND attID==" + str(attID) )
            continue # <---- NEEDED!!!! OR ELSE ADDS EXTRA STRING TYPES !!!!
        except :
          self.cursor.execute( "UPDATE GoalAtt SET attType=='string'  WHERE rid=='" + self.rid + "' AND attID==" + str(attID) )

        # if it's not an integer, then it's a string
        else :
          self.cursor.execute( "UPDATE GoalAtt SET attType=='string'  WHERE rid=='" + self.rid + "' AND attID==" + str(attID) )

      # otherwise, assume it's a string
      else :
        self.cursor.execute( "UPDATE GoalAtt SET attType=='string'  WHERE rid=='" + self.rid + "' AND attID==" + str(attID) )

      # //////////////////////////////////////////////////////// #
      # sanity check: all goal atts should have a type
      self.cursor.execute( "SELECT attID,attName FROM GoalAtt WHERE rid = '" + self.rid + "'" )
      post_goalAttList = self.cursor.fetchall()
      post_goalAttList = tools.toAscii_multiList( post_goalAttList )
      for att in post_goalAttList :
        if "UNDEFINEDTYPE" in att[1] :
          tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : goal '" + goalName + "' still has UNDEFINED attribute types:\npost_goalAttList = " + str(post_goalAttList) )
      # //////////////////////////////////////////////////////// #

    # ----------------------------------------------------------- #
    # set the types for rule subgoal atts

    # get list of all subgoal ids for the current rule
    self.cursor.execute( "SELECT sid FROM Subgoals WHERE rid = '" + self.rid + "'" )
    subIDList = self.cursor.fetchall()
    subIDList = tools.toAscii_list( subIDList )

    for sid in subIDList :
      self.cursor.execute( "SELECT subgoalName FROM Subgoals WHERE rid = '" + self.rid + "' AND sid = '" + sid + "'" )
      subgoalName = self.cursor.fetchone()
      subgoalName = tools.toAscii_str( subgoalName )

      self.cursor.execute( "SELECT attID,attName FROM SubgoalAtt WHERE rid = '" + self.rid + "' AND sid = '" + sid + "'" )
      subgoalAttList = self.cursor.fetchall()
      subgoalAttList = tools.toAscii_multiList( subgoalAttList )

      # ................................................... #
      if subgoalName == "cchange" :
        print "$$$$$$$$$$$$$ BEFORE $$$$$$$$$$$$$$$"
        print "subgoalName = " + subgoalName
        self.cursor.execute( "SELECT * FROM SubgoalAtt WHERE rid=='" + self.rid + "' AND sid=='" + sid + "'" )
        res = self.cursor.fetchall()
        res = tools.toAscii_multiList( res )
        print res
      # ................................................... #

      if subgoalName == "clock" :
        self.cursor.execute( "UPDATE SubgoalAtt SET attType=='string'  WHERE rid=='" + self.rid + "' AND sid=='" + sid + "' AND attID==0" )
        self.cursor.execute( "UPDATE SubgoalAtt SET attType=='string'  WHERE rid=='" + self.rid + "' AND sid=='" + sid + "' AND attID==1" )
        self.cursor.execute( "UPDATE SubgoalAtt SET attType=='int'     WHERE rid=='" + self.rid + "' AND sid=='" + sid + "' AND attID==2" )
        self.cursor.execute( "UPDATE SubgoalAtt SET attType=='int'     WHERE rid=='" + self.rid + "' AND sid=='" + sid + "' AND attID==3" )
      else :
        for att in subgoalAttList :
          attID   = att[0]
          attName = att[1]

          if "Time" in attName :
            self.cursor.execute( "UPDATE SubgoalAtt SET attType=='int'     WHERE rid=='" + self.rid + "' AND sid=='" + sid + "' AND attID==" + str(attID) )
          else :
            self.cursor.execute( "UPDATE SubgoalAtt SET attType=='string'  WHERE rid=='" + self.rid + "' AND sid=='" + sid + "' AND attID==" + str(attID) )

      # //////////////////////////////////////////////////////// #
      # sanity check: all subgoal atts should have a type
      self.cursor.execute( "SELECT attID,attType FROM SubgoalAtt WHERE rid = '" + self.rid + "' AND sid = '" + sid + "'" )
      post_subgoalAttList = self.cursor.fetchall()
      post_subgoalAttList = tools.toAscii_multiList( post_subgoalAttList )
      for att in post_subgoalAttList :
        if "UNDEFINEDTYPE" in att[1] :
          tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : subgoal '" + subgoalName + "' still has UNDEFINED attribute types:\npost_subgoalAttList = " + str(post_subgoalAttList) )
      # //////////////////////////////////////////////////////// #

      # ................................................... #
      if subgoalName == "cchange" :
        print "$$$$$$$$$$$$$ AFTER $$$$$$$$$$$$$$$"
        print "subgoalName = " + subgoalName
        self.cursor.execute( "SELECT * FROM SubgoalAtt WHERE rid=='" + self.rid + "' AND sid=='" + sid + "'" )
        res = self.cursor.fetchall()
        res = tools.toAscii_multiList( res )
        print res
      # ................................................... #

    return None


  # ------------------------------------- #
  #              DISPLAY                  #
  # ------------------------------------- #

  #############
  #  DISPLAY  #
  #############
  # print rule to stdout
  def display( self ) :
    prettyRule = ""

    # collect goal info
    goalName = self.getGoalName()
    goalAttList  = self.getGoalAttList()
    goalTimeArg  = self.getGoalTimeArg()

    goalAttStr = ""
    for i in range(0,len(goalAttList)) :
      goalAttStr += goalAttList[i]
      if i < len(goalAttList) - 1 :
        goalAttStr += ","

    # collect subgoal list
    subgoalStr = self.getSubgoalListStr()

    # collect equantion list
    eqnStr = self.getEquationListStr()

    # convert rule info to pretty string
    prettyRule += goalName + "(" + goalAttStr + ")" + " :- " + subgoalStr 
    if not eqnStr == None :
      prettyRule += "," + eqnStr + " ;"

    print prettyRule

    return prettyRule

#########
#  EOF  #
#########
