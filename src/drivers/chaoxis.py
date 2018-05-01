#!/usr/bin/env python

'''
chaoxis.py
'''

# **************************************** #


#############
#  IMPORTS  #
#############

import os, sys

# ------------------------------------------------------ #
# import sibling packages HERE!!!

SRC_PATH = __file__ +  "/../../"
if not os.path.abspath( SRC_PATH ) in sys.path :
  sys.path.append( os.path.abspath( SRC_PATH )  )

from api import Chaoxis

# **************************************** #


#############
#  CHAOXIS  #
#############
def chaoxis() :

  # --------------------------------------------- #
  # initialize chaoxis object

  c = Chaoxis.Chaoxis()

  # --------------------------------------------- #
  # run LDFI on given spec (in file provided in argDict)

  c.run()

  sys.exit( c.conclusion )


#########################
#  THREAD OF EXECUTION  #
#########################
if __name__ == "__main__" :
  chaoxis()


#########
#  EOF  #
#########
