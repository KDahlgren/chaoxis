    var tablearea = document.getElementById("tables")
    var title = document.getElementById("title")
    title.appendChild(document.createTextNode(data.dedname))

        console.log(tablearea)
var resdata = data.tableList;
//console.log(resdata);
var tableNames = Object.keys(resdata);
for (var table = 0; table < Object.keys(resdata).length; table ++){
    console.log(tableNames[table])
    var tableName = document.createElement('tableName');
    tableName.innerHTML = tableNames[table]
    var tableHTML = document.createElement('table');
    //console.log(resdata[0][tableNames[table]])
    tableObj = resdata[tableNames[table]]['values']
    tableHeaders = resdata[tableNames[table]]['headers']
    var tr = document.createElement('tr');
    for (var header = 0; header < tableHeaders.length;header++){
        tr.appendChild( document.createElement('td') );
        tr.cells[header].appendChild(document.createTextNode(tableHeaders[header]) ) 
    }
    tableHTML.appendChild(tr)
   
    for (var tup = 0; tup < tableObj.length; tup++){
        var tr = document.createElement('tr');
        
        
        //console.log(tableObj[tup])
        //console.log(tableObj[tup].length)
        
        for (var item = 0; item < tableObj[tup].length; item++){
            
            //console.log(tableObj[tup][item])
            tr.appendChild( document.createElement('td') );
            tr.cells[item].appendChild(document.createTextNode(tableObj[tup][item]) )
            
        
        }
       
        tableHTML.appendChild(tr);
        
    }
    tablearea.appendChild(tableName);
    tablearea.appendChild(tableHTML);
}

