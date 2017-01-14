#!/usr/bin/env python

import os, sys

# TODO: place magical installation code here

def getAPR_list() :
  os.system( 'find / -name "apr_file_io.h" | grep -v "Permission denied" > out.txt' )
  fo = open( "out.txt", "r" )

  pathList = []
  for path in fo :
    pathList.append( path )

  os.system( 'rm out.txt' )

print "Running pyLDFI setup with : \n" + str(sys.argv)

if "c4" in sys.argv :
  print "Installing C4 Datalog evaluator ... "

  # find candidate apr locations
  apr_path_cands = getAPR_list()

  # set correct apr location
  for path in apr_path_cands :
    os.system( "" ) # how can you tell if a make failed?

  os.system( "make" )
  print "... Done installing C4 Datalog evaluator"

elif "pyDatalog" in sys.argv :
  print "Using pyDatalog Datalog evaluator."

else :
  print "Using pyDatalog Datalog evaluator."

