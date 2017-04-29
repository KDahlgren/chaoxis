
//data is imported from vizresults.js

var processes = []
var processesLoc = {}
var messages = []
var selected = []
var nodes = []
function setup() {

  canvasWidth=(((data.nodes).length+1)*100)+100
  canvasLength=(int(data.endTime)+1)*100
  masterCanvas = createCanvas(canvasWidth, canvasLength);
  masterCanvas.parent('spacetimediagram')
  console.log(data.messageList[0].from);
  for (var i = 0; i < (data.nodes).length; i++){
  	var xP = (i*100)+100
    var y2P = (int(data.endTime))*100
  	processes.push(new Process(xP,50,y2P,data.nodes[i],data.endTime))
  	
  }
  //add messages
  console.log(processesLoc)
  console.log(data.messageList)
  for (var i = 0; i < (data.messageList).length; i++){
  	sender = data.messageList[i].from
  	reciever = data.messageList[i].to
  	recieverTime = data.messageList[i].DelivTime
  	senderTime = data.messageList[i].SndTime
  	value = data.messageList[i].relation
  	x1 = processesLoc[sender][senderTime]['x']
  	y1 = processesLoc[sender][senderTime]['y']
  	x2 = processesLoc[reciever][recieverTime]['x']
  	y2 = processesLoc[reciever][recieverTime]['y']
  	messages.push(new Message(x1,y1,x2,y2,value))
  }

button = createButton('clear')
button.position(100,500)
button.mousePressed(deselectAll)

}

function deselectAll(){
	for(var i =0; i < messages.length; i++) {
    messages[i].deselect();
  }
  for (var i = 0; i <nodes.length; i++){
  	nodes[i].deselect();
  }
}

function draw() {
 clear()
 background(200);
 text(selected,(((data.nodes).length+1)*100),50);

 for (var i= 0; i<processes.length;i++){
 
  	processes[i].display();
  }
  for (var i = 0; i <nodes.length; i++){
  	nodes[i].display();
  }
 

  for (var i = 0; i <messages.length;i++){
  	messages[i].display();
  }

}

function mousePressed() {
  for(var i =0; i < messages.length; i++) {
    messages[i].clicked();
  }
  for (var i = 0; i <nodes.length; i++){
  	nodes[i].clicked();
  }

}

//
function Process(x,y1,y2,pName,nodeCount){
	this.x = x
	this.y1 = y1
	this.y2 = y2
	this.pName = pName
	this.nodeCount = nodeCount-1
	this.nodes = []
	processesLoc[this.pName]={}
	for (var i = 0; i < nodeCount-1; i++){
		tempNode = new Node(pName,i+1,this.x,this.y1+((i+1)*100))
		this.nodes.push(tempNode)
		nodes.push(tempNode)
	}

	this.display = function (){

		text('Process '+this.pName, this.x-20,this.y1-10);
		stroke('black');
		line(this.x,this.y1,this.x,this.y2);
		
	}

}

function Node(process, time,x,y){
	this.process = process
	this.time = time
	this.x = x
	this.y = y
	this.value = data.nodeDict[this.process][this.time]
	this.select = false
	this.index = -1

	processesLoc[this.process][String(this.time)]={}
	processesLoc[this.process][String(this.time)]['x']=this.x
	processesLoc[this.process][String(this.time)]['y']=this.y
	this.display = function(){
		strokeWeight(1);
		if(this.select == false){
			fill('white');
		}else{
			fill('red');
		}
		noStroke()
		text(this.time,this.x-40,this.y)
		ellipse(this.x,this.y,50,30);
		stroke('black');
		strokeWeight(2);


	}

	this.clicked = function(){
		var d = dist(this.x, this.y, mouseX, mouseY);
		if (d < 30/ 2) {
     		if(this.select == false){
				this.select =true
				v = [process,time]
				selected.push(v)
				this.index = (selected.length)-1
				}else{
				this.select = false
				this.deselect()
			}
    	}
	}

	this.deselect = function (){
		console.log('HERE!')
		console.log(this.select)

			this.select = false
			selected.splice(this.index,1);
			console.log(selected)
			this.index = -1	
	}
}

function Message(x1,y1,x2,y2,value){
	this.x1 = x1
	this.y1 = y1
	this.x2 = x2
	this.y2 = y2
	this.select = false
	this.index = -1
	this.value = value

	this.display = function(){
		strokeWeight(3);
		if(this.select==false){
			stroke('black');
		}else{
			stroke('red');
		}
		text(this.value,this.x2 - this.x1,this.y2 - this.y1+100)
		line(this.x1,this.y1,this.x2,this.y2);
		stroke('black');
		strokeWeight(2);
	}
	this.clicked = function(){
		slopeY = float(this.y2 - this.y1)
		slopeX = float(this.x2 - this.x1)
			//equation of line: y=mx+b
		m = slopeY/slopeX;
		b = this.y1 - (m*this.x1)
			
		intersection = m*(mouseX)+b
		if (intersection<mouseY+3 && intersection>mouseY-3) {
     		if(this.select == false){
				this.select =true
				selected.push(this.value)
				this.index = (selected.length)-1
				}else{
				this.select = false
				this.deselect()
			}
    	}
		
	}

	//TODO: Find better way as this is buggy af
	this.deselect = function (){
			this.select = false
			selected.splice(this.index,1);
			this.index = -1	
	}
}