Vis.js Example
--------------
http://visjs.org/network_examples.html

@index.html
```html
<html>
<head>
<title>Network | Groups</title>

<style>
body {
	color: #d3d3d3;
	font: 12pt arial;
	background-color: #ffffff;
}

#mynetwork {
	width: 100%;
	height: 100%;
	border: 1px solid #444444;
	background-color: #dddddd;
}
</style>

<script src="~/vis/dist/vis.js"></script>
<link href="~/vis/dist/vis.css" rel="stylesheet" type="text/css"/>
<!myapp>
<@myapp>
</head>

<body onload="main()">
<div id="mynetwork"></div>
</body>
</html>
```

@myapp
```pythia
#backend:javascript
from runtime import *

def make_nodes(funcs):
	nodes = []
	for fname in funcs:
		fnode = {id:fname, label:fname, group:fname, shape:'ellipse'}
		nodes.append(fnode)
		for i,v in enumerate(funcs[fname].vars):
			vnode = {id:fname+'VAR'+i, label:v, group:fname+'VAR', font:{size:20}}
			nodes.append(vnode)

		for i,v in enumerate(funcs[fname].loops):
			vnode = {id:fname+'LOOP'+i, label:v, group:fname+'LOOP', shape:'box', font:{size:15}}
			nodes.append(vnode)

	return nodes

def make_edges(funcs):
	edges = []
	for fname in funcs:
		for i,v in enumerate(funcs[fname].vars):
			edge = {'from':fname, 'to':fname+'VAR'+i}
			edges.append(edge)

		for i,v in enumerate(funcs[fname].loops):
			edge = {'from':fname, 'to':fname+'LOOP'+i, 'width':10, 'length':100}
			edges.append(edge)

	return edges

def main():
	lines = document->('#myapp').firstChild.nodeValue.splitlines()
	funcs = {}
	fname = None
	for ln in lines:
		if ln.startswith('def '):
			fname = ln[4:]
			funcs[fname] = {vars:[], loops:[]}
		elif '=' in ln:
			vname = ln.split('=')[0].strip()
			if vname not in funcs[fname].vars:
				funcs[fname].vars.append(vname)
		elif ln.strip().startswith('for '):
			funcs[fname].loops.append(ln.strip())

	nodes = make_nodes(funcs)
	edges = make_edges(funcs)

	# create a network
	container = document.getElementById('mynetwork')
	data = {
		nodes: nodes,
		edges: edges
	}
	options = {
		nodes: {
			shape: 'dot',
			size: 30,
			font: {
				size: 32
			},
			borderWidth: 2,
			shadow:true
		},
		edges: {
			width: 2,
			shadow:true
		}
	}
	network = new vis.Network(container, data, options)


```