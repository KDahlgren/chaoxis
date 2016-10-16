#!/usr/bin/env python

#######################
#  PARAM INPUT ERROR  #
#######################
def LDFI_ParamInputError( ) :
  return "Please run the program again without arguments to see usage info."

################
#  PRINT HELP  #
################
def printHelp( filename ) :
  info = """\n\n     -t <value> | --EOT <value>
     end of time (default 3)
    -f <value> | --EFF <value>
       end of finite failures (default 2)
    -c <value> | --crashes <value>
       crash failures (default 0)
    -N <value> | -n <value> | --nodes <value>
       a comma-separated set of nodes (required)
    --solver <value>
       the solver to use ('z3' or 'sat4j' or 'ilp')
    --strategy <value>
       the search strategy ('sat', 'random' or 'pcausal')
    --use-symmetry
       use symmetry to skip equivalent failure scenarios
    --prov-diagrams
       generate provenance diagrams for each execution
    --disable-dot-rendering
       disable automatic rendering of `dot` diagrams
    --find-all-counterexamples
       continue after finding the first counterexample
    --negative-support
       Negative support.  Slow, but necessary for completeness
    <file>... (at least one file required)
       Absolute paths to Dedalus files"""

  example = """\n\nExample:
     python """ + filename + " ./simplog.ded ./deliv_assert.ded" + """ \\
     --EOT 4 \\
     --EFF 2 \\
     --nodes a,b,c \\
     --crashes 0 \\
     --prov-diagrams"""

  print "Usage: " + filename + " [options] <file>..." + info + example
