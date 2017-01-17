#!/usr/bin/env python

import os, sys, time

# TODO: place magical installation code here

C4_FINDAPR_PATH="./lib/c4/cmake/FindApr.cmake"
SETUP_DEBUG = True

#################
#  GETAPR_LIST  #
#################
def getAPR_list() :
  cmd = 'find / -name "apr_file_io.h" | grep -v "Permission denied" > out.txt'
  print "Finding Apache Runtime library using command: " + cmd
  time.sleep(5) # message to user
  os.system( cmd )
  fo = open( "out.txt", "r" )

  pathList = []
  for path in fo :
    path = path.strip()
    path_split = path.split( "/" )
    path_split = path_split[:len(path_split)-1]
    path       = "/".join( path_split )
    pathList.append( path )

  os.system( 'rm out.txt' )

  return pathList


########################
#  DE DUPLICATE SETUP  #
########################
def deDuplicateSetup() :
  # http://stackoverflow.com/questions/4710067/deleting-a-specific-line-in-a-file-python
  # protect against multiple runs of setup
  f = open( C4_FINDAPR_PATH, "r+" )
  d = f.readlines()
  f.seek(0)
  for i in d:
    if not "set(APR_INCLUDES" in i :
      f.write(i)
  f.truncate()
  f.close()


#############
#  SET APR  #
#############
def setAPR( path ) :
  # set one of the candidate APR paths
  newCmd = 'set(APR_INCLUDES "' + path + '")'
  #cmd = "echo '" + newCmd + "' | cat - " + C4_FINDAPR_PATH + " > temp && mv temp " + C4_FINDAPR_PATH
  cmd = "(head -48 " + C4_FINDAPR_PATH + "; " + "echo '" + newCmd + "'; " + "tail -n +49 " + C4_FINDAPR_PATH + ")" + " > temp ; mv temp " + C4_FINDAPR_PATH + ";"
  os.system( cmd )
  os.system( "make c4" )


##########################
#  CHECK FOR MAKE ERROR  #
##########################
def checkForMakeError( path ) :
  flag = True
  if os.path.exists( os.path.dirname(os.path.abspath( __file__ )) + "/c4_out.txt" ) :
    fo = open( "./c4_out.txt", "r" )
    for line in fo :
      line = line.strip()
      if "error generated." in line :
        print "failed path apr = " + path
        flag = False
    fo.close()
    os.system( "rm ./c4_out.txt" ) # clean up
  return flag

##########
#  MAIN  #
##########
def main() :
  print "Running pyLDFI setup with : \n" + str(sys.argv)
  
  # ---------------------------------------------- #
  # run make for c4
  # find candidate apr locations
  apr_path_cands = getAPR_list()
  
  # set correct apr location
  flag    = True
  for path in apr_path_cands :
    deDuplicateSetup()
    setAPR( path )
    try :
      flag = checkForMakeError( path )
    except IOError :
      print "./c4_out.txt does not exist"
  
    # found a valid apr library
    if flag :
      print ">>> C4 installed successfully <<<"
      print "... Done installing C4 Datalog evaluator"
      break
    print "C4 install using APR path : " + path

  # ---------------------------------------------- #
  # copy over template c4 main
  os.system( "cp ./src/templateFiles/c4i_template.c ./lib/c4/src/c4i/c4i.c" )
 
  # ---------------------------------------------- #
  # run make for everything else
  os.system( "make" )
  


##############################
#  MAIN THREAD OF EXECUTION  #
##############################
main()


#########
#  EOF  #
#########
