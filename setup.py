#!/usr/bin/env python

import os, sys

# TODO: place magical installation code here

C4_FINDAPR_PATH="./lib/c4/cmake/FindApr.cmake"
SETUP_DEBUG = True

#################
#  GETAPR_LIST  #
#################
def getAPR_list() :
  os.system( 'find / -name "apr_file_io.h" | grep -v "Permission denied" > out.txt' )
  fo = open( "out.txt", "r" )

  pathList = []
  for path in fo :
    pathList.append( path )

  os.system( 'rm out.txt' )


##############################
#  MAIN THREAD OF EXECUTION  #
##############################

print "Running pyLDFI setup with : \n" + str(sys.argv)

if "c4" in sys.argv :
  print "Installing C4 Datalog evaluator ... "

  # find candidate apr locations
  apr_path_cands = getAPR_list()

  # set correct apr location
  for path in apr_path_cands :

    NOT_INSTALLED = True
    while NOT_INSTALLED == True :
      # set one of the candidate APR paths
      os.system( "sed 's/" + '_apr_invoke(APR_VERSION   ""        --version)' + "/g'" + " " + C4_FINDAPR_PATH + " > " + '_apr_invoke(APR_VERSION   ""        --version)\nset(APR_INCLUDES "' + path + '")'  )
      os.system( "make" )
 
      fo = open( "./c4_out.txt", "r" )
      for line in fo :
        if ">>> C4 Installation SUCCESSFUL <<<" in line :
          NOT_INSTALLED = False
      fo.close()
      os.system( "rm ./c4_out.txt" ) # clean up

    print "Using APR path : " + path

  print "... Done installing C4 Datalog evaluator"

elif "pyDatalog" in sys.argv :
  print "Using pyDatalog Datalog evaluator."

else :
  print "Using pyDatalog Datalog evaluator."

