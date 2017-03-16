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

from utils import dumpers, extractors, tools
# ------------------------------------------------------ #

DEBUG = True

opList = [ "notin" ] # TODO: make this configurable
operators = [ "+", "-", "*", "/", "<", ">", "<=", ">=" ]

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
  # return the body of the rule as a string
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


  ######################################################
  #  GET SUBGOAL LIST STRING NO TIME ARGS NO ADD ARGS  #
  ######################################################
  # return the body of the rule as a string sans subgoal time args
  def getSubgoalListStr_noTimeArgs_noAddArgs( self ) :
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

        currSubgoal += subgoalName + "("

        # add in all attributes
        for i in range(0,len(subAtts)) :
          if i < (len(subAtts) - 1) :
            currSubgoal += subAtts[i] + ","
          else :
            currSubgoal += subAtts[i] + ")"

        # conclude with time arg, if applicable
        #if not subTimeArg == "" :
        #  currSubgoal += "@" + subTimeArg

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
  # set the types for attributes located within a goal head
  # if goal is a fact, consult fact data
  # else goal is an IDB, so gather types recursively.
  def setAttTypes( self ) :
    body_str       = self.getSubgoalListStr_noTimeArgs_noAddArgs()
    allAttTypeMaps = self.allAttTypeMapsDriver( body_str )
    #tools.bp( __name__, inspect.stack()[0][3], "allAttTypeMaps = " + str(allAttTypeMaps) )

    # transform into dicionary for convenience
    typeDict = {}
    for record in allAttTypeMaps :
      for mapping in record :
        att = mapping[0]
        val = mapping[1]
        typeDict[ att ] = val

    if DEBUG :
      print "typeDict = " + str(typeDict)

    # set in db
    # get all attIDs
    self.cursor.execute( "SELECT attID,attName FROM GoalAtt WHERE rid=='" + self.rid + "'" )
    allAtts = self.cursor.fetchall()
    allAtts = tools.toAscii_multiList( allAtts )

    for att in allAtts :
      attID   = att[0]
      attName = att[1]

      print "attName        = " + attName,
      print "operators      = " + str(operators),
      for op in operators :
        print " op in attName = " + str( op in attName )
      # TODO : hacky soln for circumventing operators in att names.
      for op in operators :
        if op in attName :
          attType = 'int'
        else :
          attType = typeDict[ attName ]
        break

      self.cursor.execute( "UPDATE GoalAtt SET attType=='" + attType + "' WHERE rid=='" + self.rid + "' AND attID==" + str(attID) + " AND attName=='" + attName + "'" )


  ##############################
  #  ALL ATT TYPE MAPS DRIVER  #
  ##############################
  # return the type maps for all attribute vars appearing in the body of a rule.
  def allAttTypeMapsDriver( self, body_str ) :
    subgoals_namesAndAtts = self.getInfo_subgoals_namesAndAtts( body_str )

    # iterate over parsed subgoals
    allAttTypeMaps = []
    for sub in subgoals_namesAndAtts :
      allAttTypeMaps.append( self.getTypeMap( sub ) )

    return allAttTypeMaps


  ##################
  #  GET TYPE MAP  #
  ##################
  # return a list of attribute name, attribute type maps in the form of arrays
  def getTypeMap( self, subNameAndAtts ) :
    subname = subNameAndAtts[0]
    subatts = subNameAndAtts[1]

    atts_inRuleBody = subatts

    print "subNameAndAtts = " + str(subNameAndAtts)

    # --------------------------------------------------- #
    #     BASE CASE 1 !!! => subgoal references a fact
    # --------------------------------------------------- #
    if tools.isFact( subname, self.cursor ) :
      list_dataTypes_fromFact = self.getFactDataTypes( subname )
      atts_inRuleBody_typeMap = self.mapTypes_raw( atts_inRuleBody, list_dataTypes_fromFact )

    # --------------------------------------------------- #
    #     BASE CASE 2 !!! => subgoal references a fact
    # --------------------------------------------------- #
    elif subname == 'clock' :
      atts_inRuleBody_typeMap = self.mapTypes_raw( atts_inRuleBody, [ 'string', 'string', 'int', 'int' ] )

    # --------------------------------------------------- #
    #     RECURSIVE CASE !!! => subgoal is an idb
    # --------------------------------------------------- #
    else :
      sub_as_rule     = self.getRuleHeadAtts( subname )

      print "subname     = " + str(subname)
      print "subatts     = " + str(subatts)
      print "sub_as_rule = " + str(sub_as_rule)

      chosen_rid      = sub_as_rule[0]
      atts_asRuleHead = sub_as_rule[1]

      subRule                 = Rule( chosen_rid, self.cursor )
      bodyparse               = subRule.getSubgoalListStr_noTimeArgs_noAddArgs()
      allAttTypeMaps          = self.allAttTypeMapsDriver( bodyparse )
      atts_asRuleHead_typeMap = self.mapTypes_preprocessed( atts_asRuleHead, allAttTypeMaps )

      print "subRule                 = " + str(subRule)
      print "bodyparse               = " + str(bodyparse)
      print "allAttTypeMaps          = " + str(allAttTypeMaps)
      print "atts_asRuleHead_typeMap = " + str(atts_asRuleHead_typeMap)

      # following statement only works if atts_asRuleHead_types maintains ordering!!!
      orderedListOfTypes = [ mapping[1] for mapping in atts_asRuleHead_typeMap]
      print "orderedListOfTypes = " + str(orderedListOfTypes)

      #tools.bp( __name__, inspect.stack()[0][3], "orderedListOfTypes = " + str(orderedListOfTypes) + "\natts_asRuleHead_typeMap = " + str(atts_asRuleHead_typeMap) )
      atts_inRuleBody_typeMap = self.mapTypes_raw( atts_inRuleBody, orderedListOfTypes )
      print "atts_inRuleBody_typeMap = " + str(atts_inRuleBody_typeMap)

    #tools.bp( __name__, inspect.stack()[0][3], "atts_inRuleBody_typeMap = " + str(atts_inRuleBody_typeMap) )
    return atts_inRuleBody_typeMap


  ############################
  #  MAP TYPES PREPROCESSED  #
  ############################
  # map attribute vars to types based on ordering.
  # only use for subgoals referencing facts.
  def mapTypes_preprocessed( self, attList, typeMapList ) :

    attList = [ att[1] for att in attList ] # remove attIDs

    # check sanity : attributes defined across type maps should have the same type.
    attDict = {}
    for mappingList in typeMapList :
      for mapping in mappingList :
        att = mapping[0]
        val = mapping[1]

        if att in attDict.keys() :
          if attDict[att] == val :
            pass
          else :
            tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : inconsistent type assignments for attribute " + str(att) + "\n" + str(attDict[att]) + " is not the same as " + str(val) )
        else :
          attDict[att] = val

    # otherwise ... 
    finalMapping = []
    for att in attList : # maintains ordering!!!!
      print "att          = " + str(att)
      print "attDict[att] = " + str( attDict[att] )
      finalMapping.append( [ att, attDict[att] ] )

    return finalMapping


  ###################
  #  MAP TYPES RAW  #
  ###################
  # map attribute vars to types based on ordering.
  # only use for subgoals referencing facts.
  def mapTypes_raw( self, attList, orderedListOfTypes ) :

    # check sanity : arity of the facts should equal the arity of the referencing sub rule
    if len(attList) > len(orderedListOfTypes) :
      tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : more attribute variables than data types:\natt vars = " + str(attList) + "\ndata types = " + str(orderedListOfTypes) )

    # fewer atts may occur if subgoal appears in a rule without the time argument.
    # accordingly, because the reference to the subgoal is written without reference to 
    # the time argument, it is ok to just take the first N data types from the ordered type list,
    # where N is the arity of the subgoal reference.
    #elif len(attList) < len(orderedListOfTypes) :
    #  tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : fewer attribute variables than data types:\natt vars = " + str(attList) + "\ndata types = " + str(orderedListOfTypes)  )

    # otherwise ... 
    finalMapping = []
    for i in range(0,len(attList)) :
      finalMapping.append( [ attList[i], orderedListOfTypes[i] ] )

    return finalMapping


  #########################
  #  GET FACT DATA TYPES  #
  #########################
  # return an array containing an ordered list of the data types of
  # all components included in a fact
  def getFactDataTypes( self, subname ) :

    if subname == "clock" :
      return [ 'string', 'string', 'int', 'int' ]

    # retrieve all facts assocaited with the subname
    self.cursor.execute( "SELECT fid FROM Fact WHERE name=='" + subname + "'" )
    allFIDs = self.cursor.fetchall()
    allFIDs = tools.toAscii_list( allFIDs )

    factData_all = []
    for fid in allFIDs :

      # get timing data
      self.cursor.execute( "SELECT timeArg FROM Fact WHERE fid=='" + fid + "'" )
      timeData = self.cursor.fetchone()
      timeData = tools.toAscii_str( timeData )
      if not timeData.isdigit() :
        tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : timeing argument for a " + subname + " fact is not an integer:\n" + timeData + " is not an integer. =["  )

      # get input data
      self.cursor.execute( "SELECT attID,attName FROM FactAtt WHERE fid=='" + fid + "'" )
      factData = self.cursor.fetchall()
      factData = tools.toAscii_multiList( factData )

      # create and save full fact
      fullFact = [ data[1] for data in factData ]
      fullFact.append( timeData )
      factData_all.append( fullFact )

    if DEBUG :
      print "subname = " + subname,
      print "factData_all = " + str(factData_all)

    # pass 1: collect data type lists per fact record.
    factTypesList = []
    for data in factData_all :
      typeList = []
      for component in data :
        if ("'" in component) or ('"' in component) :
          typeList.append( 'string' )
        elif component.isdigit() :
          typeList.append( 'int' )
        else :
          tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR:\nencountered data of unrecognized type :\n data record " + data + "\n for table " + subname + " contains unregognized component " + str(component) + ". pyLDFI currently only supports strings and integers.\nDouble or single quotes must encapsulate the contents of a string.." )
      factTypesList.append( typeList )

    # pass 2: terminate if any type lists are inconsistent.
    for typeList1 in factTypesList :
      for typeList2 in factTypesList :
        for i in range(0,len(typeList)) :
          if typeList1[i] == typeList2[i] :
            pass
          else :
            tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR: type inconsistency in facts for table " + subname + "\n" + typeList1[i] + " does not equal " + typeList2[i]  )

    #tools.bp( __name__, inspect.stack()[0][3], "factTypesList = " + str(factTypesList) )
    return factTypesList[0]


  ########################
  #  GET RULE HEAD ATTS  #
  ########################
  # return a binary array containing the chosen rid for the subgoal rule
  # and the list of all attribute var names used in the goal/head of that
  # particular rule definition.
  def getRuleHeadAtts( self, subname ) :

    allRIDs = self.getAllRIDs( subname )

    subList = []
    for rid in allRIDs :
      sublist = self.getSubList_namesOnly( rid )

      if not subname in subList :
        return [ rid, self.getHeadAtts( rid ) ]


  ##################
  #  GET ALL RIDS  #
  ##################
  # return the complete list of rids associated with the given subgoal name.
  def getAllRIDs( self, subname ) :

    self.cursor.execute( "SELECT rid FROM Rule WHERE goalName=='" + subname + "'" )
    allRIDs = self.cursor.fetchall()
    allRIDs = tools.toAscii_list( allRIDs )

    return allRIDs


  #############################
  #  GET SUB LIST NAMES ONLY  #
  #############################
  # return an array of the subgoal names contained within the given rule.
  def getSubList_namesOnly( self, rid ) :

    self.cursor.execute( "SELECT subgoalName FROM Subgoals WHERE rid=='" + rid + "'" )
    subList_namesOnly = self.cursor.fetchall()
    subList_namesOnly = tools.toAscii_list( subList_namesOnly )

    return subList_namesOnly


  ###################
  #  GET HEAD ATTS  #
  ###################
  # return an array of the goal attribues for the given rule.
  def getHeadAtts( self, rid ) :

    self.cursor.execute( "SELECT attID,attName FROM GoalAtt WHERE rid=='" + rid + "'" )
    headAtts = self.cursor.fetchall()
    headAtts = tools.toAscii_multiList( headAtts )

    return headAtts


  ######################################
  #  GET INFO SUBGOALS NAMES AND ATTS  #
  ######################################
  # for a given rule body string, return an array of binary arrays
  # st the binary arrays contain a subgoal name and an array of the corresponding
  # attribute variable strings.
  def getInfo_subgoals_namesAndAtts( self, body_str_no_time_args ) :
    subsAndAtts = body_str_no_time_args.split( ")," )

    # remove parens and commas
    temp_list = []
    for sub in subsAndAtts :
      temp_sub = ""
      for c in sub :
        if c == "(" :
          temp_sub += "___STARTHERE___"
        elif c == "," :
          temp_sub += "___COMMAHERE___"
        elif c == ")" :
          pass
        else :
          temp_sub += c
      temp_list.append( temp_sub )

    # convert into binary arrays containing subname and parsed array of sub atts.
    temp_list_2 = []
    for sub in temp_list :
      temp_sub       = sub.split( "___STARTHERE___" )
      subname        = temp_sub[0]
      subAttList_str = temp_sub[1]
      subAttList     = subAttList_str.split( "___COMMAHERE___" )
      temp_list_2.append( [ subname, subAttList ] )
    subNamesAndAtts = temp_list_2

    return subNamesAndAtts


  ##############
  #  GET TYPE  #
  ##############
  # comp := lhs or rhs of an equation extracted from a rule
  def getType( self, comp ) :

    # check if constant string
    if ("'" in comp) or ('"' in comp) :
      return "string"

    # check if constant integer
    elif comp.isdigit() :
      return "int"

    # get type from rule definition
    else :
      # check goal att types
      self.cursor.execute( "SELECT attID,attName,attType FROM GoalAtt WHERE rid=='" + self.rid + "'" )
      attInfo_goal = self.cursor.fetchall()
      attInfo_goal = tools.toAscii_multiList( attInfo_goal )

      goalTypeMap = {}
      for att in attInfo_goal :
        attID   = att[0]
        attName = att[1]
        attType = att[2]
        goalTypeMap[ attName ] = attType

      # iterate over subgoals
      self.cursor.execute( "SELECT SubgoalAtt.sid,attID,attName,attType FROM Subgoals,SubgoalAtt WHERE Subgoals.rid=='" + self.rid + "' AND Subgoals.rid==SubgoalAtt.rid" )
      attInfo = self.cursor.fetchall()
      attInfo = tools.toAscii_multiList( attInfo )

      for att in attInfo :
        sid     = att[0]
        attID   = att[1]
        attName = att[2]
        attType = att[3]

        # sanity check : the types of the goal atts must correspond to the types in the corresponding subgoalatts
        if (not attName == "_") and (not attType == goalTypeMap[ attName ]) :
          # get goal type dump
          self.cursor.execute( "SELECT Rule.rid,goalName,attID,attName,attType FROM Rule,GoalAtt WHERE Rule.rid=='" + self.rid+ "' AND Rule.rid==GoalAtt.rid" )
          goalTypeDump = self.cursor.fetchall()
          goalTypeDump = tools.toAscii_multiList( goalTypeDump )

          # get subgoal type dump
          self.cursor.execute( "SELECT Subgoals.rid,Subgoals.sid,subgoalName,attID,attName,attType FROM Subgoals,SubgoalAtt WHERE Subgoals.rid=='" + self.rid+ "' AND Subgoals.rid==SubgoalAtt.rid" )
          subgoalTypeDump = self.cursor.fetchall()
          subgoalTypeDump = tools.toAscii_multiList( subgoalTypeDump )

          tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : Type inconsistency between goal and subgoal attribute type declarations: \nIn rule " + dumpers.reconstructRule( self.rid, self.cursor ) + ",\nattribute '" + attName + "' is of type '" + goalTypeMap[ attName ] + " in the goal, but is of type '" + attType + "' in one of the subgoals.\ngoalTypeDump:\n(rid,goalName,attID,attName,attType)\n" + "\n".join([ str(item) for item in goalTypeDump ]) + "\nsubgoalTypeDump:\n(rid,sid,subgoalName,attID,attName,attType)\n" + "\n".join([ str(item) for item in subgoalTypeDump ])  )

        if comp == attName :
          print "attName = " + attName + ", attType = " + attType
          return attType

    tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : component '" + comp + "' of equation detected in rule '" + dumpers.reconstructRule( self.rid, self.cursor ) + "' has no detected type." )


  #######################
  #  PROMOTE COMPONENT  #
  #######################
  # promote the type of a component derived from an equation extracted from a string
  # to a more general data type.
  # observe the code will never attempt to promote a string
  def promoteComponent( self, lhs, op, rhs, eid, cat ) :

    tools.bp( __name__, inspect.stack()[0][3], "hit promoteComponent" )

    # =============================================== #
    # handle lhs case 
    # promote integer constants to string
    if lhs.isdigit() :
      newEqn = str(lhs) + op + rhs
      self.cursor.execute( "UPDATE Equation SET eqn=='" + newEqn + "' WHERE rid=='" + rid + "' AND eid=='" + eid + "'" )

    else :
      # promote attributes in original rules to strings
      # reset original goal atts
      self.cursor.execute( "SELECT attID,attName FROM GoalAtt WHERE rid=='" + self.rid + "'" )
      attList = self.cursor.fetchall()
      attList = tools.toAscii_multiList( attList )

      for att in attList :
        attID   = att[0]
        attName = att[1]

        if cat == "lhs" :
          if lhs == attName :
            self.cursor.execute( "UPDATE GoalAtt SET attType=='string' WHERE rid=='" + self.rid + "' AND attID==" + str(attID) )
        elif cat == "rhs" :
          if rhs == attName :
            self.cursor.execute( "UPDATE GoalAtt SET attType=='string' WHERE rid=='" + self.rid + "' AND attID==" + str(attID) )
        else :
          tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : cat is not lhs or rhs. cat = " + str(cat) + "\nUnrecognized option. Aborting..." )

      # reset original subgoal atts
      self.cursor.execute( "SELECT SubgoalAtt.sid,attID,attName FROM Subgoals,SubgoalAtt WHERE Subgoals.rid=='" + self.rid + "' AND Subgoals.rid==SubgoalAtt.rid" )
      attList = self.cursor.fetchall()
      attList = tools.toAscii_multiList( attList )

      for att in attList :
        sid     = att[0]
        attID   = att[1]
        attName = att[2]

        if cat == "lhs" :
          if lhs == attName :
            self.cursor.execute( "UPDATE SubgoalAtt SET attType=='string' WHERE rid=='" + self.rid + "' AND sid=='" + sid + "' AND attID==" + str(attID) )
        elif cat == "rhs" :
          if rhs == attName :
            self.cursor.execute( "UPDATE SubgoalAtt SET attType=='string' WHERE rid=='" + self.rid + "' AND sid=='" + sid + "' AND attID==" + str(attID) )
        else :
          tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : cat is not lhs or rhs. cat = " + str(cat) + "\nUnrecognized option. Aborting..." )

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
