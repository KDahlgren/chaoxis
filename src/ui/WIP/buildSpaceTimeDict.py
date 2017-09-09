#!/usr/bin/env python

# **************************************** #

#############
#  IMPORTS  #
#############
# standard python packages
import time
import os, sys, re,json


# import sibling packages HERE!!!
if not os.path.abspath( __file__ + "/../../" ) in sys.path :
  sys.path.append( os.path.abspath( __file__ + "/../../" ) )
print packagePath

C4_SAVE_PATH       = os.path.dirname(os.path.abspath( __file__ )) + "/../evaluators/programFiles/c4_run_output.txt"
JSON_SAVE_PATH = os.path.dirname(os.path.abspath( __file__ )) + "visualizations/run.json"

from utilities import tools


#TODO: don't hard code these, pull them in from the other files
nodes = ["a","b","c"]
dedname = ["simpleLog.ded"]
ruleList = ['node(Node,Neighbor,SndTime+1) :- node(Node,Neighbor,SndTime), clock(Node,_,SndTime,_) ;', 
'log(Node,Pload,SndTime+1) :- log(Node,Pload,SndTime), clock(Node,_,SndTime,_) ;', 
'log(Node2,Pload,DelivTime) :- bcast(Node1,Pload,SndTime),node(Node1,Node2,SndTime), clock(Node1,Node2,SndTime,DelivTime) ;',
'log(Node,Pload,SndTime) :- bcast(Node,Pload,SndTime), clock(Node,Node,SndTime,_) ;',
'pre(X,Pl,SndTime) :- log(X,Pl,SndTime),notin bcast(X,Pl,1),notin crash(X,X,_,SndTime), clock(X,X,SndTime,_) ;',
'post(X,Pl,SndTime) :- log(X,Pl,SndTime),notin missing_log(_,Pl,SndTime), clock(X,X,SndTime,_) ;',
'node_provfmvhlnhwwetnomes(Node,Neighbor,SndTime+1,SndTime) :- node(Node,Neighbor,SndTime),clock(Node,_,SndTime,_) ;',
'log_provqwqvufmncjkemksh(Node,Pload,SndTime+1,SndTime) :- log(Node,Pload,SndTime),clock(Node,_,SndTime,_) ;', 
'log_provxbeprhvjlboiwpxt(Node2,Pload,DelivTime,Node1,SndTime) :- bcast(Node1,Pload,SndTime),node(Node1,Node2,SndTime),clock(Node1,Node2,SndTime,DelivTime) ;',
'log_provzccctpiwvylghvhe(Node,Pload,SndTime) :- bcast(Node,Pload,SndTime),clock(Node,Node,SndTime,_) ;',
'pre_provehsdszbjfmzhmqqb(X,Pl,SndTime) :- log(X,Pl,SndTime),notin bcast(X,Pl,1),notin crash(X,X,_,SndTime),clock(X,X,SndTime,_) ;', 
'post_provfherlperqkcibbow(X,Pl,SndTime) :- log(X,Pl,SndTime),notin missing_log(_,Pl,SndTime),clock(X,X,SndTime,_) ;']

#Notes###########
#only look at _prov
#SndTime+1, 
#SndTime,
#DelivTime

endTime = 1

#pull the c4results dict
c4results = tools.getEvalResults_file_c4(C4_SAVE_PATH)

#rework rule list to just the first parts, only care about _prov
tableList ={'clock': {'headers':['to','from','SndTime','DelivTime'],'values':[]}}
#tableList ={'clock':{'to':[],'from':[],'SndTime':[],'DelivTime':[]}}
for rule in ruleList:
  rawRule = re.split(' :-',rule)[0]
  ruleName = rawRule.split("(")[0]
  ruleParts = re.split(',',(rawRule.split("(")[1])[:-1])
  tableList[ruleName] = {}
  tableList[ruleName]['headers']=ruleParts
  tableList[ruleName]['values']=[]
  #print ruleName
  #print ruleParts
  #for r in ruleParts:	
  #	tableList[ruleName][r]=[]
#print tableList

messageList=[]
nodeDict ={}
for node in nodes:
	nodeDict[node]={}
	
for table in c4results:
	#print table
	if table not in tableList.keys():
		tableList[table] = {}
		tableList[table]['headers']=[]
		tableList[table]['values']=[]
	for relation in c4results[table]:
		tableList[table]['values'].append(relation)

	if "_prov" in table:

		for node in nodes:
			#go through the table to find the node's relations
			for relation in tableList[table]['values']:
				#if it's the node
				if relation[0]==node:
					#check if we have the SndTime for that 
					#node already in dict
					rLength = len(relation)-1
					if relation[rLength] not in nodeDict[node].keys():
						nodeDict[node][relation[rLength]]={}
						if int(relation[rLength]) > endTime:
							endTime = int(relation[rLength])
					if table not in nodeDict[node][relation[rLength]].keys():
						nodeDict[node][relation[rLength]][table]=[]
		for node in nodes:
			for relation in tableList[table]['values']:
				if relation[0]==node:
					rLength = len(relation)-1
					if "DelivTime" in tableList[table]['headers']:
						recieveTimeIndex = tableList[table]['headers'].index('DelivTime')
						tempRelation = relation[1:-1]
						for n in nodes:
							if n in tempRelation:
								senderNode = n
								if relation[rLength] not in nodeDict[n].keys():
									nodeDict[n][relation[rLength]]={}
									if int(relation[rLength]) > endTime:
										endTime = int(relation[rLength])
								if table not in nodeDict[n][relation[rLength]].keys():
									nodeDict[n][relation[rLength]][table]=[]
								nodeDict[n][relation[rLength]][table].append(relation)
								msgDict={'to':relation[0],'from':n,'SndTime':relation[rLength],
								'DelivTime':relation[recieveTimeIndex],'relation':relation}
								messageList.append(msgDict)
								break
					else:
						nodeDict[node][relation[rLength]][table].append(relation)
endTime = endTime+1		
#vizDict['clock']=tableList['clock']
#for table in vizDict:
#	vizDict[table]['values'].sort(key=lambda x: (x[0],x[(len(x)-1)]))
#	print table
#	print vizDict[table]['headers'] 
#	for val in vizDict[table]['values']:
#		print val
#print tableList
#print vizDict
print "AAAAAAAAAAAAAAAAAAAAAAAA"
for node in nodes:
	print node
	i = 1
	
	while i < endTime:
		print i
		print nodeDict[node][str(i)]
		i=i+1

print tableList
print messageList
jsonDict = {}
jsonDict['nodes']= nodes
jsonDict['dedname']= dedname
jsonDict['endTime']= endTime
jsonDict['nodeDict'] = nodeDict
jsonDict['tableList'] = tableList
jsonDict['messageList']=messageList

#rewrite to .js
with open('result.json', 'w') as jdump:
	json.dump(jsonDict,jdump)




