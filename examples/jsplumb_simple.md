html
----

requires jsPlumb 2.0.7
```bash
cd
git clone https://github.com/sporritt/jsPlumb.git
```


```html
<html>
<head>
<script src="~/jsPlumb/dist/js/jsPlumb-2.0.7-min.js" git="https://github.com/sporritt/jsPlumb.git"></script>

<link href="~/bootstrap-3.3.5-dist/css/bootstrap.min.css" rel="stylesheet">
<link href="//netdna.bootstrapcdn.com/font-awesome/4.0.3/css/font-awesome.css" rel="stylesheet">
<link href="//fonts.googleapis.com/css?family=Lato:400,700" rel="stylesheet">

<link rel="stylesheet" href="~/jsPlumb/dist/css/jsPlumbToolkit-defaults.css">
<link rel="stylesheet" href="~/jsPlumb/dist/css/main.css">
<link rel="stylesheet" href="~/jsPlumb/dist/css/jsPlumbToolkit-demo.css">

<!-- support lib for bezier stuff -->
<script src="~/jsPlumb/lib/jsBezier-0.7.js"></script>
<script src="~/jsPlumb/lib/mottle-0.7.1.js"></script>
<script src="~/jsPlumb/lib/biltong-0.2.js"></script>
<script src="~/jsPlumb/lib/katavorio-0.13.0.js"></script>

<style>
.flowchart-demo .window {
	border: 1px solid #346789;
	box-shadow: 2px 2px 19px #aaa;
	-webkit-box-shadow: 2px 2px 19px #aaa;
	border-radius: 0.5em;
	opacity: 0.8;
	width: 80px;
	height: 80px;
	line-height: 80px;
	cursor: pointer;
	text-align: center;
	z-index: 20;
	position: absolute;
	background-color: #eeeeef;
	color: black;
	font-family: helvetica, sans-serif;
	padding: 0.5em;
	font-size: 0.9em;
	-webkit-transition: -webkit-box-shadow 0.15s ease-in;
	transition: box-shadow 0.15s ease-in;
}

.flowchart-demo .window:hover {
	box-shadow: 2px 2px 19px #444;
	-webkit-box-shadow: 2px 2px 19px #444;
	opacity: 0.6;
}

.flowchart-demo .active {
	border: 1px dotted green;
}

.flowchart-demo .hover {
	border: 1px dotted red;
}

#flowchartWindow1 {
	top: 34em;
	left: 5em;
}

#flowchartWindow2 {
	top: 7em;
	left: 36em;
}

#flowchartWindow3 {
	top: 27em;
	left: 48em;
}

#flowchartWindow4 {
	top: 23em;
	left: 22em;
}

.flowchart-demo .jsplumb-connector {
	z-index: 4;
}

.flowchart-demo .jsplumb-endpoint, .endpointTargetLabel, .endpointSourceLabel {
	z-index: 21;
	cursor: pointer;
}

.flowchart-demo .aLabel {
	background-color: white;
	padding: 0.4em;
	font: 12px sans-serif;
	color: #444;
	z-index: 21;
	border: 1px dotted gray;
	opacity: 0.8;
	cursor: pointer;
}

.flowchart-demo .aLabel.jsplumb-hover {
	background-color: #5C96BC;
	color: white;
	border: 1px solid white;
}

.window.jsplumb-connected {
	border: 2px solid green;
}

.jsplumb-drag {
	outline: 4px solid pink !important;
}

path, .jsplumb-endpoint {
	cursor: pointer;
}

.jsplumb-overlay {
	background-color:transparent;
}
</style>

<!myscript>
<@myscript>


</head>
<body>
<div class="jtk-demo-main">
	<div class="jtk-demo-canvas canvas-wide flowchart-demo jtk-surface jtk-surface-nopan" id="canvas">
	</div>
</div>
</body>
</html>
```

@myscript
```pythia
#backend:javascript
from runtime import *


// this is the paint style for the connecting lines..
connectorPaintStyle = {
	lineWidth: 4,
	strokeStyle: "#61B7CF",
	joinstyle: "round",
	outlineColor: "white",
	outlineWidth: 2
}
# .. and this is the hover style.
connectorHoverStyle = {
	lineWidth: 4,
	strokeStyle: "#216477",
	outlineWidth: 2,
	outlineColor: "white"
}
endpointHoverStyle = {
	fillStyle: "#216477",
	strokeStyle: "#216477"
}
# the definition of source endpoints (the small blue ones)
sourceEndpoint = {
	endpoint: "Dot",
	paintStyle: {
		strokeStyle: "#7AB02C",
		fillStyle: "transparent",
		radius: 7,
		lineWidth: 3
	},
	isSource: true,
	connector: [ "Flowchart", { stub: [40, 60], gap: 10, cornerRadius: 5, alwaysRespectStubs: true } ],
	connectorStyle: connectorPaintStyle,
	hoverPaintStyle: endpointHoverStyle,
	connectorHoverStyle: connectorHoverStyle,
	dragOptions: {},
	overlays: [
		[ "Label", {
			location: [0.5, 1.5],
			label: "Drag",
			cssClass: "endpointSourceLabel",
			visible:false
		} ]
	]
}
# the definition of target endpoints (will appear when the user drags a connection)
targetEndpoint = {
	endpoint: "Dot",
	paintStyle: { fillStyle: "#7AB02C", radius: 11 },
	hoverPaintStyle: endpointHoverStyle,
	maxConnections: -1,
	dropOptions: { hoverClass: "hover", activeClass: "active" },
	isTarget: true,
	overlays: [
		[ "Label", { location: [0.5, -0.5], label: "Drop", cssClass: "endpointTargetLabel", visible:false } ]
	]
}


def on_plumb_ready():
	instance = window.jsp = jsPlumb.getInstance({
		# default drag options
		DragOptions: { cursor: 'pointer', zIndex: 2000 },
		# the overlays to decorate each connection with.  note that the label overlay uses a function to generate the label text; in this
		# case it returns the 'labelText' member that we set on each connection in the 'init' method below.
		ConnectionOverlays: [
			[ "Arrow", {
				location: 1,
				visible:true,
				id:"ARROW",
				events:{
					click: lambda: alert("you clicked on the arrow overlay")
				}
			} ],
			[ "Label", {
				location: 0.1,
				id: "label",
				cssClass: "aLabel",
				events:{
					tap: lambda: alert("clicked on alabel")
				}
			}]
		],
		Container: "canvas"
	})

	basicType = {
		connector: "StateMachine",
		paintStyle: { strokeStyle: "red", lineWidth: 4 },
		hoverPaintStyle: { strokeStyle: "blue" },
		overlays: [
			"Arrow"
		]
	}
	instance.registerConnectionType("basic", basicType)



	def init(connection):
		connection.getOverlay("label").setLabel(connection.sourceId + "-" + connection.targetId);


	def on_batch():
		nodes = {}
		for i in range(4):
			elt = document->('i')
			elt->('hello world')
			name = 'my-window'+str(i)
			node = add_flowchart_node(name, elt)
			nodes[name]=node
			node.style.top = (i+10) + 'em'
			node.style.left = (i*20) + 'em'

		for name in nodes:
			for oname in nodes:
				if oname != name:
					instance.addEndpoint(
						name, sourceEndpoint,
						{ anchor: "TopCenter", uuid: name+"TopCenter" }
					)
					instance.addEndpoint(
						name, targetEndpoint,
						{ anchor: "BottomCenter", uuid: oname+"BottomCenter" }
					)

		# listen for new connections; initialise them the same way we initialise the connections at startup.
		instance.bind(
			"connection", 
			lambda connInfo, originalEvent: init(connInfo.connection)
		)


		for name in nodes:
			for oname in nodes:
				if oname != name:
					spoint = name+"TopCenter"
					tpoint = oname+"BottomCenter"
					instance.connect(uuids=[spoint, tpoint], editable=True)

		# listen for clicks on connections, and offer to delete connections on click.
		instance.bind(
			"click", 
			lambda conn, originalEvent: conn.toggleType("basic")
		)

		instance.bind(
			"connectionDrag", 
			lambda connection: console.log("connection " + connection.id + " is being dragged. suspendedElement is ", connection.suspendedElement, " of type ", connection.suspendedElementType)
		)

		instance.bind(
			"connectionDragStop", 
			lambda connection: console.log("connection " + connection.id + " was dragged")
		)

		instance.bind(
			"connectionMoved", 
			lambda params: console.log("connection " + params.connection.id + " was moved")
		)

		view_thy_self( instance )

		# make all the window divs draggable
		instance.draggable(jsPlumb.getSelector(".flowchart-demo .window"), { grid: [20, 20] })


	# suspend drawing and initialise.
	instance.batch(on_batch)

	jsPlumb.fire("jsPlumbDemoLoaded", instance);


jsPlumb.ready(on_plumb_ready)


def add_flowchart_node(name, child):
	div = document->('div')->(id=name)
	div.setAttribute('class','window jtk-node')
	document->('#canvas')->(div)
	div->(child)
	return div


def view_thy_self(instance):
	lines = document->('#myscript').firstChild.nodeValue.splitlines()
	funcs = {}
	current_func = None
	for line in lines:
		if line.startswith('def '):
			print 'got func'
			fname = line[4:].split(':')[0]
			current_func = fname
			funcs[fname] = []
		elif '(' in line and ')' in line and current_func in funcs:
			funcs[current_func].append(line)

	x = 20
	y = 30
	for fname in funcs:
		body = funcs[fname]
		elt = document->('div')
		elt->( document->('h5')->(fname) )
		pre = document->('pre')
		elt->(pre)
		div = add_flowchart_node(fname, elt)
		div.style.top = y + 'em'
		div.style.left = x + 'em'
		div.style.width = '200px'
		div.style.height = (len(body)*20)+10
		y += 2
		x += 10
		for ln in body:
			pre->(ln)

		instance.addEndpoint(
			fname, sourceEndpoint,
			{ anchor: "TopCenter", uuid: fname+"TopCenter" }
		)
		instance.addEndpoint(
			fname, targetEndpoint,
			{ anchor: "RightMiddle", uuid: fname+"RightMiddle" }
		)


```