#!/usr/bin/env python

# **************************************** #

#############
#  IMPORTS  #
#############
# standard python packages
import inspect, os, sys

# ------------------------------------------------------ #
# import sibling packages HERE!!!
packagePath  = os.path.abspath( __file__ + "/../.." )
sys.path.append( packagePath )

from utils      import tools

# **************************************** #

C4_EVALUATOR_DEBUG = True
C4_EXEC_PATH       = os.path.dirname(os.path.abspath( __file__ )) + "/../../lib/c4/build/src/c4i/c4i"
#C4_SAVE_PATH       = os.path.dirname(os.path.abspath( __file__ )) + "/programFiles/c4_run_output.txt"


#####################
#  CLEAN TABLE STR  #
#####################
def cleanTableStr( tableStr ) :

  tableStr = tableStr.split( "," )
  arr = []
  for i in tableStr :
    if not i in arr :
      arr.append( i )
  newStr = ",".join( arr[:-1] ) # delete extra space

  return newStr

#####################
#  GET PROG TABLES  #
#####################
# assumes table names are listed in a single string and delimited by one comma only; no spaces.
def getTables( table_path ) :
  tableListStr = ""

  # safety first
  if os.path.exists( table_path ) :
    fo = open( table_path, "r" )
    tableListStr = fo.readline()
    fo.close()
  else :
    sys.exit( "Table list for C4 Overlog input file for pyLDFI program not found at : " + table_path + "\nAborting..." )

  tableListStr = cleanTableStr( tableListStr )

  return tableListStr


############
#  RUN C4  #
############
# runs c4 on generated overlog program
# posts the results to standard out while capturing in a file for future processing.
def runC4_directly( c4_file_path, table_path, savepath ) :

  if C4_EVALUATOR_DEBUG :
    print "c4_file_path = " + c4_file_path
    print "table_path   = " + table_path
    print "savepath     = " + savepath

  # check if executable and input file exist
  if os.path.exists( C4_EXEC_PATH ) :
    if os.path.exists( c4_file_path ) :
      tableListStr = getTables( table_path )

      if C4_EVALUATOR_DEBUG :
        print "tableListStr = " + tableListStr
        print "savepath     = " + savepath

      #os.system( "(" + C4_EXEC_PATH + " " + c4_file_path + tableListStr + ") 2>&1 | tee " + C4_SAVE_PATH )
      #os.system( C4_EXEC_PATH + " " + c4_file_path + ' "' + tableListStr + '"' + " 2>&1 " + C4_SAVE_PATH )
      #os.system( C4_EXEC_PATH + " " + c4_file_path + ' "' + tableListStr + '"' + " > " + C4_SAVE_PATH )
      os.system( C4_EXEC_PATH + " " + c4_file_path + ' "' + tableListStr + '" "' + savepath + '"' )

      # check if dump file is empty.
      if not os.path.exists( savepath ) :
        tools.bp( __name__, inspect.stack()[0][3], "ERROR: c4 file dump does not exist at " + savepath )
      else :
        if not os.path.getsize( savepath ) > 0 :
          tools.bp( __name__, inspect.stack()[0][3], "ERROR: no c4 dump results at " + savepath  )

      return savepath

    else :
      sys.exit( "C4 Overlog input file for pyLDFI program not found at : " + c4_file_path + "\nAborting..." )

  else :
    sys.exit( "C4 executable not found at : " + C4_EXEC_PATH + "\nAborting..." )


#########
#  EOF  #
#########
