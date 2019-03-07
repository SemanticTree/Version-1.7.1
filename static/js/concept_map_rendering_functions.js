function create_core_obj(container){
	var cy;
	if(container){
			cy=new cytoscape({
			container:document.getElementById(container_id)
		});
	}
	else{
		cy= new cytoscape();
	}
	return cy;
}

function LoadFile() {

	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {

			jsontext = this.response.split('|split|')[0];
			orignalText = this.response.split('|split|')[1];
		    responseData=JSON.parse(jsontext);
			load_graph();
		};
	}
		xhttp.open("GET", "/juggad", true);
		// xhttp.open("GET", "static/js/new_tree.json", true);
		xhttp.send();
}

function setLayout(lt, cy) {
	layout={
		name : lt,
		idealEdgeLength : 200,
		numIter:5000,
	};
	cy.layout(layout).run();
}

function addStyle(level_limit, ele) {

	cy.nodes().data("is_central",false);
	cy.collection().add(ele).data("is_central",true);
	cy.elements().style({
		"opacity" : '1',
		"visibility":"visible"
	});

	// old code
	central=cy.elements("node[?is_central]")[0];
	dijkstra=cy.elements("*").dijkstra({
		"root": "node[?is_central]"
	});

	cy.nodes().forEach( function(ele) {
		ele_level = this.distanceTo(ele);
		if (ele_level > level_limit){
			ele.style("visibility","hidden");
			ele.connectedEdges().style("visibility","hidden")
		}
	},dijkstra);

	// Add color
	cy.nodes().forEach( function(ele) {
		ele_level = this.distanceTo(ele);
		if (ele_level <= level_limit){
			ele.style("background-color", levelColor(1000));
			ele.style("color", "black");
		}
	},dijkstra);

	central.style({
		"background-color": levelColor(1),
		"color" : "white",
	})

	cy.animate({
		fit: {eles : cy.elements(":visible"), padding: 10}
	})

}

function load_graph(){
	jsonObject=responseData;
  	cy.add(jsonObject['elements']);
  	cy.style(style);
  	// cy.nodes().ungrabify();
  	cy.nodes().style({"visibility":"visible"});
  	cy.edges().style({"visibility":"visible"});
	cy.nodes().on("select",function(ele) {
		var box_position=ele.target.renderedPosition();
		var min_offset =50;
		box_position.x+=(edge_length+min_offset)*cy.zoom();
		box_position.y-=(edge_length+min_offset)*cy.zoom();
		var maparea_rect	= document.getElementById("map-area").getBoundingClientRect();
		var popup_rect		= document.getElementById("pop-up").getBoundingClientRect();

		//DO other pop-up related ops here eg. setting text, meaning etc...
		//{{{

		document.getElementById("title").innerHTML="<b>"+ele.target.data("title")+"</b>";
		
		data = ele.target.data();
		origin_sent = orignalText.substring(data.i,data.j);
		document.getElementById("b1").onclick=function(){
			document.getElementById("meaning").innerHTML=origin_sent;
		}
		document.getElementById("b2").onclick=function(){
			get_wiki_text(ele.target.data("title"));
		}
		// document.getElementById("origin-text").innerHTML = origin_sent;
		get_wiki_text(ele.target.data("title"));

		// document.getElementById("meaning").innerHTML="<b>"+ele.target.data("title")+"</b>";

		//}}}

		var box_left	=maparea_rect.left+box_position.x;
		var box_right	=box_left+popup_rect['width'];
		var box_top		=maparea_rect.top+box_position.y-popup_rect['height'];
		var box_bottom	=box_top;
		document.getElementById("pop-up").style.left=	(box_right<=maparea_rect.right)?
															(box_left+"px"):
															(maparea_rect.right-popup_rect['width']+"px");
		
		document.getElementById("pop-up").style.top=	(box_top>=maparea_rect.top)?
															(box_top+"px"):
															(maparea_rect.top+"px");
		
		document.getElementById("pop-up").style.visibility="visible";
	});
	cy.cxtmenu( cxtmenuDefaults );
	central=cy.elements("[?is_central]")[0]
  	setLayout("cose-bilkent", cy);
	// addStyle(level_limit, central);
}

function randomColor(ele){

	color = ['red', 'blue', 'green', 'gray', 'yellow']
	randomColor = color[Math.floor(Math.random()*color.length)]
	console.log(randomColor);
	ele.style("background-color", randomColor);
}

function showText(ele){

	data = ele.data();
	origin_sent = orignalText.substring(data.i,data.j);
	document.getElementById("origin-text").innerHTML = "<h3>Origin Text for "+data.title+"</h3><br>"+origin_sent;
	ele.unselect();
	console.log(origin_sent);
}


function hide_edges(a){
	cy.nodes().forEach(function(ele,i,eles){
		var count=0;
		ele.connectedEdges().forEach(function(ele,i,eles){
			if(a.includes(ele.data("title"))|| ele.style("visibility")=="hidden"){
				count++;
			}
		});
		if(count==ele.connectedEdges().length){
			ele.style("visibility","hidden");
			ele.connectedEdges().style("visibility","hidden");
		} 
	});
	a.forEach(function(element){
		cy.edges("[title='"+element+"']").style("visibility","hidden");
	})
}
