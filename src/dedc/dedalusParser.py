#!/usr/bin/env python

'''
dedalusParser.py
   Define the functionality for parsing Dedalus files.
'''

import os, string, sys
from pyparsing import *

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

#from utils import tools, parseCommandLineInput
# ------------------------------------------------------ #

#############
#  GLOBALS  #
#############
DEDALUSPARSER_DEBUG = False

keywords = [ "notin" ] # TODO: make this configurable

##################
#  CLEAN RESULT  #
##################
# input pyparse object of the form ([...], {...})
# output only [...]
def cleanResult( result ) :
  newResult = []

  numParsedStrings = len(result)
  for i in range(0, numParsedStrings) :
    newResult.append( result[i] )

  return newResult

###########
#  PARSE  #
###########
# input a ded line
# output parsed line
def parse( dedLine ) :

  # search and replace prepend keywords.
  for k in keywords :
    if k in dedLine :
      dedLine = dedLine.replace( k, "___"+k+"___")

  # make sure input line contains no whitespace
  dedLine = dedLine.translate(None, string.whitespace)

  # ------------------------------------------------------------- #
  #                          RULES                                #

  goal = Word( alphanums + "_" + "(" + ")" + "," + "+" + "-" + "*" + "/" + ">" + "<" + "<=" + ">=" )
  subgoal = goal
  arg = Optional( Literal ("@") + Word( alphanums ) )
  fmla = Word( alphanums + "+" + "-" + "*" + "/" + ">" + "<" + "<=" + ">=" )

  rule0 = goal + arg + ":-" + ZeroOrMore(OneOrMore(subgoal + arg) + ZeroOrMore( fmla ))
  rule1 = goal + arg + ":-" + ZeroOrMore(ZeroOrMore( fmla ) + OneOrMore(subgoal + arg) + ZeroOrMore( fmla ))
  rule  = rule0 | rule1

  #secondParse = Optional(Word(",")) + Word(alphanums + "_" ) + Word("(") + Word( alphanums + "," + "+" + "-" + "*" + "/" + ">" + "<" + "<=" + ">=" ) + Word(")") + Optional( Optional(Word(",")) + Word( alphanums + "+" + "-" + "*" + "/" + ">" + "<" + "<=" + ">=" ) )

  # describes second pass
  opt_comma         = Optional(Word(","))
  name              = Word(alphanums + "_" )
  open_paren        = Word("(")
  closed_paren      = Word(")")
  att_list          = Word( alphanums + "," + "+" + "-" + "*" + "/" + ">" + "<" + "<=" + ">=" + "_" )

  # subgoal followed by zero or more subgoals or zero or more fmlas
  subgoal_2 = opt_comma + name + open_paren + att_list + closed_paren + ZeroOrMore( Word(",") + name + open_paren + att_list + closed_paren ) + Optional( opt_comma + fmla )

  # fmla followed by zero or more subgoals or zero or more fmlas
  fmla_2 = opt_comma + fmla + ZeroOrMore( Word(",") + name + open_paren + att_list + closed_paren ) + ZeroOrMore( Word(",") + fmla )

  secondParse = subgoal_2 | fmla_2


  # ------------------------------------------------------------- #
  #                          FACTS                                #

  fact = Word( alphanums + "_" ) + Word("(") + Word( alphanums + "_" + "," + '"' + "'" ) + Word(")") + Optional(arg)

  # ------------------------------------------------------------- #
  #                         RULES                                 #

  # return tuples
  if (";" in dedLine) and (not "include" in dedLine) :

    # parse RULES
    if ":-" in dedLine :
      try :
        if DEDALUSPARSER_DEBUG :
          print "dedLine = " + dedLine

        result = rule.parseString( dedLine )
        ret    = cleanResult( result )

        if DEDALUSPARSER_DEBUG :
          print "ret = " + str(ret)

        # parse attribute lists
        parsed = []
        # parse any stubborn subgoals and fmlas
        for substr in ret :

          # check for bugs
          if DEDALUSPARSER_DEBUG :
            print "pass2: substr = " + substr

          if ("(" in substr) and (")" in substr) :
            ret2 = secondParse.parseString( substr )
            ret2 = cleanResult( ret2 )
            parsed.extend( ret2 )

            # check for bugs
            if DEDALUSPARSER_DEBUG :
              print "ret2 = " + str(ret2)

          else :
            parsed.append( substr )

        if DEDALUSPARSER_DEBUG :
          print "parsed = " + str(parsed)

        # clean up comma-separated attributes
        finalParsed = []
        for c in parsed :
          if c == "," : # keep the commas
            finalParsed.append( c )
          elif ("," in c) and (not "(" in c) and (not ")" in c) :
            finalParsed.extend( c.split(",") )
          else :
            finalParsed.append(c)

        if DEDALUSPARSER_DEBUG :
          print "*** finalParsed = " + str(finalParsed)
        return ("rule", finalParsed)
      except :
        sys.exit( "\nERROR: Invalid syntax in rule line : \n      " + dedLine + "\n     Note rule attributes cannot have quotes.\n")

    # ------------------------------------------------------------- #
    #                         FACTS                                 #
    else :
      # parse FACTS
      if DEDALUSPARSER_DEBUG :
        print "dedLine = " + dedLine

      #result = fact.parseString( dedLine )
      #ret    = cleanResult( result )

      #if DEDALUSPARSER_DEBUG :
      #  print "ret = " + str(ret)

      try :
        result = fact.parseString( dedLine )
        ret    = cleanResult( result )
        if DEDALUSPARSER_DEBUG :
          print "fact ret = " + str(ret)

        # clean up comma-separated attributes
        finalParsed = []
        for c in ret :
          if c == "," : # keep the commas
            finalParsed.append( c )
          elif ("," in c) and (not "(" in c) and (not ")" in c) :
            finalParsed.extend( c.split(",") )
          else :
            finalParsed.append(c)

        if DEDALUSPARSER_DEBUG :
          print "*** finalParsed = " + str(finalParsed)

        return ("fact", ret)
      except :
        sys.exit( "\nERROR: Invalid syntax in fact line : \n      " + dedLine + "\n     Note fact attributes must be surrounded by quotes.\n" )
  else :
    return None

###################
#  PARSE DEDALUS  #
###################
# input name of raw dedalus file
# output array of arrays containing the contents of parsed ded lines

# WARNING: CANNOT write rules or facts on multiple lines.
def parseDedalus( dedFile ) :
  parsedLines = []

  # "always check if files exist" -- Ye Olde SE proverb
  if os.path.isfile( dedFile ) :
    f = open( dedFile, "r" )

    # parse line
    for line in f :
      if "/" == line[0] : # skip lines beginning with a comment
        continue

      result = parse( line.translate(None, string.whitespace) )

      if not result == None :
        parsedLines.append( result )

  else :
    sys.exit( "ERROR: File at " + dedFile + " does not exist.\nAborting..." )

  return parsedLines

##########
#  MAIN  #
##########
if __name__ == "__main__" :
  #parse( "watch_state(F-1, H/1, S+1)@next :- watch_state(F/1, 5+H, 6*S) ; //asfhkjl asdf" )
  #parse( "watch_state(F) :- watch_state(F) ;" )
  #parse( "watch_state(F-1, h/1)@next :- 1 + 22 > Z, watch_state(F,A)@100,A(b,a,a), 3+124+sdaf>asdf ;".translate(None, string.whitespace) )
  #parse( "watch_state(max<N>,F, h/1)@next :- watch_state(F,A)@100,A(b,a,count<a>), 3+124+sdaf>asdf ;".translate(None, string.whitespace) )
  #parse("watch_state(max<N>,F, h/1)@next :- timer_svc(H, I, T);".translate(None, string.whitespace) )
  parse( "watch_state(max<N>,F, h/1)@next :- 1 + 22 > Z, watch_state(F,A)@100,A(b,a,count<a>), 3+124+sdaf>asdf ;".translate(None, string.whitespace) )
  #parse( "timer_state(H, I, T-1)@next :- timer_svc(H, I, T);".translate(None, string.whitespace) )
  #parse( "token(H,T):-send_token(H,_,T);".translate(None, string.whitespace) )

  #parse( "timer_state(H, I, T-1) :- timer_svc(H/213, I*asdf, T)@next,A(avg<B>, C);".translate(None, string.whitespace))

  #parse( 'node("a","b")@1;'.translate(None, string.whitespace) )

  #line = "timer_state(H, I, T-1)@next :- timer_state(H, I, T), notin timer_cancel(H, I), T > 1;"
  line = "watch('test', 'test')@1;"
  parse( line.translate(None, string.whitespace) )

#########
#  EOF  #
#########
