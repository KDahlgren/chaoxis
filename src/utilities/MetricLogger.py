#!/usr/bin/env python

# class for recordning useful data about LDFICore executions.

import inspect, os, string, sys
import tools

class MetricLogger() :

  ################ 
  #  ATTRIBUTES  #
  ################

  # metrics for rule-goal-graphs
  rgg_num_nodes   = None
  rgg_num_edges   = None
  rgg_height      = None
  rgg_max_in_deg  = None
  rgg_max_out_deg = None

  # metrics for boolean formulas
  bf_num_literals          = None
  bf_num_nodes             = None
  bf_num_clocks            = None
  bf_depth                 = None
  bf_max_clause_width      = None
  bf_num_top_level_clauses = None

  # metrics for cnf formulas
  cnf_num_literals          = None
  cnf_num_nodes             = None
  cnf_num_clocks            = None
  cnf_depth                 = None
  cnf_max_clause_width      = None
  cnf_num_top_level_clauses = None

  # metrics for runtime
  time_to_cnf   = None
  time_to_solve = None
  num_c4_evals  = None


  #################
  #  CONSTRUCTOR  #
  #################
  # empty
  def __init__( self, save_dir, specialString ) :

    self.save_dir  = save_dir
    self.save_path = self.save_dir + "metrics_dump" + "_" + specialString + ".txt"


  ##################
  #  SAVE METRICS  #
  ##################
  # write metrics to file
  def save_metrics( self ) :

    # make sure data directory exists
    if not os.path.isdir( self.save_dir ) :
      print "Created data/ directory here : " + self.save_dir
      os.system( "mkdir " + self.save_dir )

    # save new contents
    f = open( self.save_path, "w" )

    f.write( "rgg_num_nodes              = " + str( self.rgg_num_nodes )   + "\n" )
    f.write( "rgg_num_edges              = " + str( self.rgg_num_edges )   + "\n" )
    f.write( "rgg_height                 = " + str( self.rgg_height )      + "\n" )
    f.write( "rgg_max_in_deg             = " + str( self.rgg_max_in_deg )  + "\n" )
    f.write( "rgg_max_out_deg            = " + str( self.rgg_max_out_deg ) + "\n" )

    f.write( "bf_num_literals            = " + str( self.bf_num_literals )          + "\n" )
    f.write( "bf_num_nodes               = " + str( self.bf_num_nodes )             + "\n" )
    f.write( "bf_num_clocks              = " + str( self.bf_num_clocks )            + "\n" )
    f.write( "bf_depth                   = " + str( self.bf_depth )                 + "\n" )
    f.write( "bf_max_clause_width        = " + str( self.bf_max_clause_width )      + "\n" )
    f.write( "bf_num_top_level_clauses   = " + str( self.bf_num_top_level_clauses ) + "\n" )

    f.write( "cnf_num_literals           = " + str( self.cnf_num_literals )          + "\n" )
    f.write( "cnf_num_nodes              = " + str( self.cnf_num_nodes )             + "\n" )
    f.write( "cnf_num_clocks             = " + str( self.cnf_num_clocks )            + "\n" )
    f.write( "cnf_depth                  = " + str( self.cnf_depth )                 + "\n" )
    f.write( "cnf_max_clause_width       = " + str( self.cnf_max_clause_width )      + "\n" )
    f.write( "cnf_num_top_level_clauses  = " + str( self.cnf_num_top_level_clauses ) + "\n" )

    f.write( "time_to_cnf                = " + str( self.time_to_cnf )   + "\n" )
    f.write( "time_to_solve              = " + str( self.time_to_solve ) + "\n" )
    f.write( "num_c4_evals               = " + str( self.num_c4_evals )  + "\n" )

    f.close()


  ###################
  #  PRINT METRICS  #
  ###################
  # write metrics to stdout
  def print_metrics( self ) :

    print
    print "====================="
    print "  PRINT METRICS LOG  "
    print "====================="
    print
    print "  rgg_num_nodes              = " + str( self.rgg_num_nodes )
    print "  rgg_num_edges              = " + str( self.rgg_num_edges )
    print "  rgg_height                 = " + str( self.rgg_height )
    print "  rgg_max_in_deg             = " + str( self.rgg_max_in_deg )
    print "  rgg_max_out_deg            = " + str( self.rgg_max_out_deg )
    print 
    print "  bf_num_literals            = " + str( self.bf_num_literals ) 
    print "  bf_num_nodes               = " + str( self.bf_num_nodes )
    print "  bf_num_clocks              = " + str( self.bf_num_clocks )
    print "  bf_depth                   = " + str( self.bf_depth )
    print "  bf_max_clause_width        = " + str( self.bf_max_clause_width )
    print "  bf_num_top_level_clauses   = " + str( self.bf_num_top_level_clauses )
    print
    print "  cnf_num_literals           = " + str( self.cnf_num_literals )
    print "  cnf_num_nodes              = " + str( self.cnf_num_nodes )
    print "  cnf_num_clocks             = " + str( self.cnf_num_clocks )
    print "  cnf_depth                  = " + str( self.cnf_depth )
    print "  cnf_max_clause_width       = " + str( self.cnf_max_clause_width )
    print "  cnf_num_top_level_clauses  = " + str( self.cnf_num_top_level_clauses )
    print
    print "  time_to_cnf                = " + str( self.time_to_cnf )
    print "  time_to_solve              = " + str( self.time_to_solve )
    print "  num_c4_evals               = " + str( self.num_c4_evals )
    print
    print "====================="
    print


  ################################
  #  SET RGG METRICS SIMPLIFIED  #
  ################################
  # input SimpTree object
  # set metric values
  def set_rgg_metrics_simplified( self, provTree ) :

    # ----------------------------------- #
    self.rgg_num_nodes = provTree.get_descendants_nodes_all()
    tools.bp( __name__, inspect.stack()[0][3], "rgg_num_nodes = " + str( self.rgg_num_nodes ) )

    #self.rgg_num_edges = provTree.get_edges_all()

    #clean_edgeset = self.cleanEdgeSet( provTree.edgeset )

    #self.rgg_height      = self.getHeight( clean_edgeset )
    #self.rgg_max_in_deg  = self.getMaxInDegree( clean_edgeset )
    #self.rgg_max_out_deg = self.getMaxOutDegree( clean_edgeset )

    # ----------------------------------- #
    # display results
    self.print_metrics()
    self.save_metrics()


  #####################
  #  SET RGG METRICS  #
  #####################
  # input provenance tree object
  # set attribute values
  def set_rgg_metrics( self, provTree ) :

    # ----------------------------------- #
    # make sure tree exists
    if provTree.nodeset == None or provTree.edgeset == None :
      tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : provenance tree not materialized. \nnodeset =" + str( provTree.nodeset) + "\nedgeset = " + str( provTree.edgeset )  )

    # ----------------------------------- #

    self.rgg_num_nodes = len( provTree.nodeset )
    self.rgg_num_edges = len( provTree.edgeset )

    clean_edgeset = self.cleanEdgeSet( provTree.edgeset )

    self.rgg_height      = self.getHeight( clean_edgeset )
    self.rgg_max_in_deg  = self.getMaxInDegree( clean_edgeset )
    self.rgg_max_out_deg = self.getMaxOutDegree( clean_edgeset )

    # ----------------------------------- #
    # display results
    self.print_metrics()
    self.save_metrics()


  #######################
  #  GET MAX IN DEGREE  #
  #######################
  def getMaxInDegree( self, edgeset ) :

    print "running getMaxInDegree..."

    inDegreeMap = {}

    for edge1 in edgeset :
      currsrc = edge1[0]
      currdes = edge1[1]

      inDeg = 0
      for edge2 in edgeset :
        src = edge2[0]
        des = edge2[1]

        if des == currdes :
          inDeg += 1

      inDegreeMap[ currdes ] = inDeg

    maxInDeg = 0
    for node in inDegreeMap :
      if inDegreeMap[node] > maxInDeg :
        maxInDeg = inDegreeMap[node]

    print inDegreeMap
    print maxInDeg
    tools.bp( __name__, inspect.stack()[0][3], "shits" )
    return maxInDeg


  ################
  #  GET HEIGHT  #
  ################
  # input pydot edgeset, which is a list of pydot node maps
  # output height of tree
  def getHeight( self, edgeset ) :

    for e in edgeset :
      for f in e :
        if "bcast" in f :
          print e

    print "rgg_num_nodes = " + str( self.rgg_num_nodes )
    print "rgg_num_edges = " + str( self.rgg_num_edges )
    tools.bp( __name__, inspect.stack()[0][3], "stop" )

    print "running getHeight..."

    rootName = edgeset[0][0] # first edge in pydot has src root.
    height   = self.getHeightHelper( rootName, edgeset )

    return height


  #######################
  #  GET HEIGHT HELPER  #
  #######################
  def getHeightHelper( self, rootName, edgeset ) :

    print "running getHeightHelper for rootName " + rootName

    # check if rootName is a leaf
    rootNameAppearsAsSrc = False
    for edge in edgeset :
      src = edge[0]
      if rootName == src :
        rootNameAppearsAsSrc = True

    # leaf subgraphs 
    if not rootNameAppearsAsSrc :
      return 1

    else :
      desList = []
      for edge in edgeset :
        src = edge[0]
        des = edge[1]
        if rootName == src :
          desList.append( des )

      heightMap = []
      for des in desList :
        des_height = self.getHeightHelper( des, edgeset )
        heightMap.append( [ des, des_height ] )

      maxDepth = 0
      for h in heightMap :
        if h[1] > maxDepth :
          maxDepth = h[1]

      return maxDepth + 1


  ####################
  #  CLEAN EDGE SET  #
  ####################
  # sanitize the pydot edge map list into binary arrays of strings.
  def cleanEdgeSet( self, provTree_edgeset ) :

    clean_edgeset = []

    # grab edges as strings
    for edge in provTree_edgeset :
      src = edge.get_source()
      des = edge.get_destination()

      src = src.replace( "'", "" )
      src = src.replace( '"', "" )
      src = src.translate( None, string.whitespace )

      des = des.replace( "'", "" )
      des = des.replace( '"', "" )
      des = des.translate( None, string.whitespace )

      clean_edgeset.append( [ src, des ] )

    return clean_edgeset


  ####################
  #  SET BF METRICS  #
  ####################
  # input boolean formula
  # set attribute values
  def set_bf_metrics( self, booleanfmla ) :
    return None


  #####################
  #  SET CNF METRICS  #
  #####################
  # input cnf formula
  # set attribute values
  def set_cnf_metrics( self, cnffmla ) :
    return None


#########
#  EOF  #
#########
