#!/usr/bin/env python

import os, sys, time

# TODO: place magical installation code here

C4_FINDAPR_PATH = "./lib/c4/cmake/FindApr.cmake"
SETUP_DEBUG     = True
DEBUG           = True

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


##########################
#  SET PYLDFI VIZ PATHS  #
##########################
# set the p5.js and p5.dom.js paths in pyLDFIviz.html
def set_PYLDFI_VIZ_paths() :

  p5_paths    = getP5_paths()
  p5dom_paths = getP5dom_paths()

  if DEBUG :
    print "ALL p5.js paths :"
    print p5_paths
    print "ALL p5.dom.js paths :"
    print p5dom_paths

  chosen_p5    = None
  chosen_p5dom = None

  # pick a p5.js path
  for path in p5_paths :
    if "/lib/p5.js" in path :
      chosen_p5 = path

  # pick a p5.dom.js path
  for path in p5dom_paths :
    if "/addons/p5.dom.js" in path and not "test/unit" in path :
      chosen_p5dom = path

  # sanity checks
  if not chosen_p5 :
    sys.exit( ">>> FATAL ERROR : could not find valid p5.js path. Aborting..." )
  if not chosen_p5dom :
    sys.exit( ">>> FATAL ERROR : could not find valid p5.dom.js path. Aborting..." )

  if DEBUG :
    print "chosen_p5    = " + chosen_p5
    print "chosen_p5dom = " + chosen_p5dom

  # make custom pyLDFIviz.html file
  html_tag   = "<html>\n"
  head_tag   = "  <head>\n"
  p5_line    = '  <script language="javascript" type="text/javascript" src="' + chosen_p5 + '"></script>\n'
  p5dom_line = '  <script language="javascript" src="' + chosen_p5dom + '"></script>\n'

  uiFile     = "./src/ui/pyLDFIviz.html"
  tempFile   = "./src/templateFiles/pyLDFIviz_temp.html"

  f = open( uiFile, "w" )
  f.write( html_tag )
  f.write( head_tag )
  f.write( p5_line )
  f.write( p5dom_line )

  f2 = open( tempFile, "r" )
  for line in f2 :
    f.write( line )



#####################
#  GETP5 DOM PATHS  #
#####################
def getP5dom_paths() :

  cmd_p5dom = 'find / -name "p5.dom.js" | grep -v "Permission denied" > p5dom_out.txt'
  print "Finding p5.dom.js using command: " + cmd_p5dom
  time.sleep(5) # message to user

  # execute find p5dom
  os.system( cmd_p5dom )

  # collect paths from save file
  fo = open( "p5dom_out.txt", "r" )
  pathList = []
  for path in fo :
    path = path.strip()
    pathList.append( path )
  
  os.system( 'rm p5dom_out.txt' )

  return pathList

#################
#  GETP5 PATHS  #
#################
def getP5_paths() :

  cmd_p5 = 'find / -name "p5.js" | grep -v "Permission denied" > p5_out.txt'
  print "Finding p5.js using command: " + cmd_p5
  time.sleep(5) # message to user

  # execute find p5
  os.system( cmd_p5 )

  # collect paths from save file
  fo = open( "p5_out.txt", "r" )
  pathList = []
  for path in fo :
    path = path.strip()
    pathList.append( path )

  os.system( 'rm p5_out.txt' )

  return pathList


########################
#  DE DUPLICATE SETUP  #
########################
# this script modifies the contents of FindAPR.cmake in the c4 submodule
# prior to compilation.
# need to ensure only one SET command exists in FindAPR.cmake after discovering
# a valid apr library.
def deduplicateSetup() :
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
  #os.system( "make deps" )
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
      if containsError( line ) :
        print "failed path apr = " + path
        flag = False
    fo.close()
    os.system( "rm ./c4_out.txt" ) # clean up
  return flag


####################
#  CONTAINS ERROR  #
####################
def containsError( line ) :
  if "error generated." in line :
    return True
  #elif "Error" in line :
  #  return True
  else :
    return False


##########
#  MAIN  #
##########
def main() :
  print "Running pyLDFI setup with args : \n" + str(sys.argv)

  # clean any existing libs
  os.system( "make clean" )

  # download submodules
  os.system( "make get-submodules" )
  # copy over template c4 main
  print "Copying template c4 main ..."
  os.system( "cp ./src/templateFiles/c4i_template.c ./lib/c4/src/c4i/c4i.c" )
  print "...done copying template c4 main."

  #os.system( "make c4" )

  # ---------------------------------------------- #
  # run make for c4
  # find candidate apr locations
  apr_path_cands = getAPR_list()
  
  # set correct apr location
  flag    = True
  for path in apr_path_cands :
    try :
      deduplicateSetup()
    except IOError :
      setAPR( path )

    setAPR( path )

    try :
      flag = checkForMakeError( path )
    except IOError :
      print "./c4_out.txt does not exist"
  
    # found a valid apr library
    if flag :
      print ">>> C4 installed successfully <<<"
      print "... Done installing C4 Datalog evaluator"
      print "C4 install using APR path : " + path
      print "done installing c4."
    else :
      sys.exit( "failed to install C4. No fully functioning APR found." )
  # ---------------------------------------------- #

  # run make for everything else
  #os.system( "make" )
 
  # ---------------------------------------------- #
  # set p5 file paths
  set_PYLDFI_VIZ_paths()
 

###################
#  CHECK PY DEPS  #
###################
# check python package dependencies
def checkPyDeps() :

  print "*******************************"
  print "  CHECKING PYTHON DEPENDECIES  "
  print "*******************************"

  # argparse
  import argparse
  if argparse.__name__ :
    print "argparse...verified"
  
  # pyparsing
  import pyparsing
  if pyparsing.__name__ :
    print "pyparsing...verified"
  
  # sqlite3
  import sqlite3
  if sqlite3.__name__ :
    print "sqlite3...verified"
  
  # pydatalog
  #import pyDatalog
  #if pyDatalog.__name__ :
  #  print "pyDatalog...verified"
  
  # pydot
  import pydot
  if pydot.__name__ :
    print "pydot...verified"
  
  # mpmath
  import mpmath
  if mpmath.__name__ :
    print "mpmath...verified"
  
  # sympy
  import sympy
  if not sympy.__version__ == "1.0.1.dev" :
    sys.exit( "FATAL ERROR : unsupported version of package 'sympy' : version " + sympy.__version__ + "\nPyLDFI currently only supports sympy version 1.0.1.dev.\nAborting..." )
  else :
    print "sympy...verified"

  # pycosat
  import pycosat
  if pycosat.__name__ :
    print "pycosat...verified"

  print "All python dependencies installed! Yay! =D"
  print "*******************************"
  print "*******************************"

  return None


##############################
#  MAIN THREAD OF EXECUTION  #
##############################
checkPyDeps()
main()


#########
#  EOF  #
#########
