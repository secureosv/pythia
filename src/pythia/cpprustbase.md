C++ and Rust
------------
common base

TODO: do not subclass from `GoGenerator`

```python

class CppRustBase( GoGenerator ):

	def __init__(self, source=None, requirejs=False, insert_runtime=False):
		assert source
		GoGenerator.__init__(self, source=source, requirejs=False, insert_runtime=False)
		self._global_types = {
			'string' : set()
		}
		self._with_type = []
		self._switch_on_type_object = []
		self._lambda_stack = []
		self._memory = ['HEAP']  ## affects how `.` is default translated to `->` or `.`
		self._rust = True
		self._go   = False
		self._threads = []  ## c++11 threads
		self._unique_ptr = False ## TODO
		self._has_channels = False
		self._crates = {}
		self._root_classes = {}
		self._java_classpaths = []
		self._known_strings = set()
		self._force_cstr = False
		self._known_pointers = {}
		self._global_arrays  = {}
		self._global_refs    = {}
		self._typedefs       = {}
		self._in_constant    = False
		self._known_tuples   = {}
		self._global_tuples  = {}
		self.macros = {}


	def _inline_code_helper(self, s):
		return s

	def visit_Expr(self, node):
		# XXX: this is UGLY
		s = self.visit(node.value)
		if s is None:
			raise RuntimeError('error in rusttranslator.md:' +node.value.func.id)
		if s.strip() and not s.endswith(';'):
			s += ';'
		if s==';': return ''
		else: return s


	def visit_Str(self, node):
		s = node.s.replace("\\", "\\\\").replace('\n', '\\n').replace('\r', '\\r').replace('"', '\\"')
		#return '"%s"' % s
		if self._function_stack: return '"%s".to_string()' % s
		else: return '"%s"' % s

	def visit_Is(self, node):
		return '=='

	def visit_IsNot(self, node):
		return '!='

```

For Loop
-----------------
hooks into bad magic hack, 2nd pass rustc compile.

```python


	def visit_For(self, node):
		if not hasattr(node.iter, 'uid'):
			## in the first rustc pass we assume regular references using `&X`,
			## for loops over an array of Strings requires the other type using just `X` or `ref X`
			node.iter.uid = self.uid()
			node.iter.is_ref = True
			self.unodes[ node.iter.uid ] = node.iter

		target = self.visit(node.target)
		lines = []

		if isinstance(node.iter, ast.Call) and isinstance(node.iter.func, ast.Name):

			if node.iter.func.id == 'range':
				if len(node.iter.args)==1:
					iter = self.visit(node.iter.args[0])
					if self._cpp:
						lines.append('for (int %s=0; %s<%s; %s++) {' %(target, target, iter, target))
					else:
						lines.append('for %s in range(0u, %s) {' %(target, iter))
				elif len(node.iter.args)==2:
					start = self.visit(node.iter.args[0])
					iter = self.visit(node.iter.args[1])
					if self._cpp:
						lines.append('for (int %s=%s; %s<%s; %s++) {' %(target, start, target, iter, target))

					else:
						lines.append('for %s in range(%s as uint, %s as uint) {' %(target, start, iter))
				else:
					raise SyntaxError('invalid for range loop')

			elif node.iter.func.id == 'enumerate':
				iter = self.visit(node.iter.args[0])
				idx = self.visit(node.target.elts[0])
				tar = self.visit(node.target.elts[1])
				if self._cpp:
					lines.append('int %s = -1;' %idx)
					lines.append('for (auto &%s: _ref_%s) {' %(tar, iter))  ## TODO remove _ref_
				else:
					lines.append('let mut %s = -1i;' %idx)
					if node.iter.is_ref:
						lines.append('for &%s in %s.iter() { //magic:%s' %(tar, iter, node.iter.uid))
					else:
						lines.append('for %s in %s.iter() { //magic:%s' %(tar, iter, node.iter.uid))

				lines.append('  %s += 1;' %idx)

			else: ## generator function
				gfunc = node.iter.func.id
				gargs = ','.join( [self.visit(e) for e in node.iter.args] )
				lines.append('__gen%s := __new__%s(%s)' %(gfunc,gfunc, gargs))
				lines.append('for __gen%s.__done__ != 1 {' %gfunc)
				lines.append('	%s := __gen%s.next()' %(self.visit(node.target), gfunc))

		elif isinstance(node.target, ast.List) or isinstance(node.target, ast.Tuple):
			iter = self.visit( node.iter )
			if len(node.target.elts)==3 and isinstance(node.target.elts[1], ast.Name) and node.target.elts[1].id == '__as__':
				target = self.visit(node.target.elts[0])
				astype = self.visit(node.target.elts[2])
				if iter.startswith('PyObject_GetAttrString('):
					lines.append('PyObject* __pyiter__%s = PyObject_GetIter(%s);' %(target,iter))
					lines.append('while (auto _pyob_%s = PyIter_Next(__pyiter__%s)) {' %(target, target))
					if astype in 'int long i32 i64'.split():
						lines.append('	auto %s = PyInt_AS_LONG(_pyob_%s);' %(target,target))
				else:
					lines.append('for (auto &%s: *%s) {' %(target, iter))

			else:
				key = self.visit(node.target.elts[0])
				val = self.visit(node.target.elts[1])
				iname = iter.split('.')[0]
				if self._cpp:
					if iname not in self._known_maps:
						raise SyntaxError(self.format_error('for loop target tuple unpack over some unknown type, not a known map'))
					lines.append('for (auto &_pair_%s : *%s) {' %(key, iter))
					lines[-1] += '  auto %s = _pair_%s.first;' %(key, key)
					lines[-1] += '  auto %s = _pair_%s.second;' %(val, key)

				else:  ## rust
					lines.append('for (%s,&%s) in %s.iter() {' %(key,val, iter))

		else:

			iter = self.visit( node.iter )
			arrname = iter.split('.')[0]
			if node.iter.is_ref:
				if self._cpp:
					if arrname in self._known_arrays:
						if isinstance(self._known_arrays[arrname], tuple):
							lines.append('for (int __idx=0; __idx<%s; __idx++) { /*loop over fixed array*/' %self._known_arrays[arrname][1])
							lines.append(self.indent()+'%s %s = %s[__idx];' %(self._known_arrays[arrname][0], target, iter))
						elif arrname in self._known_refs:
							lines.append('for (auto &%s: %s) { /*loop over stack vector*/' %(target, iter))
						else:
							lines.append('for (auto &%s: (*%s)) { /*loop over heap vector*/' %(target, iter))
					elif arrname in self._known_maps:
						lines.append('for (auto &_pair_%s: (*%s)) {' %(target, iter))
						#lines.append('  auto %s = _pair_%s.second;' %(target, target))
						lines.append('  auto %s = _pair_%s.first;' %(target, target))
					else:
						if iter.startswith('PyObject_GetAttrString('):
							lines.append('PyObject *__pyiterator = PyObject_GetIter(%s);' %iter)
							lines.append('while (auto %s = PyIter_Next(__pyiterator)) {' %target)
						else:
							lines.append('for (auto &%s: *%s) { /*loop over unknown type*/' %(target, iter))

				else:
					lines.append('for &%s in %s.borrow_mut().iter() { //magic:%s' %(target, iter, node.iter.uid))
			else:
				lines.append('for %s in %s.borrow_mut().iter() { //magic:%s' %(target, iter, node.iter.uid))

		clean_up_scope = []
		self.push()
		for b in node.body:
			lines.append( self.indent()+self.visit(b) )
			## after `b` has been visited, if it was an assignment node,
			## it will then need to be removed from the known variables list,
			## because C++ is block scoped, and in regular python variables escape for loops.
			if hasattr(b, '_new_assignment'):
				clean_up_scope.append(b._new_assignment)

		self.pull()
		lines.append( self.indent()+'}' )  ## end of for loop

		for name in clean_up_scope:
			self._known_vars.remove(name)
			self._vars.add(name)

		return '\n'.join(lines)


```


While Loop
----------

works with rust and c++

```python

	def visit_While(self, node):
		cond = self.visit(node.test)
		if cond == 'true' or cond == '1': cond = ''
		body = []
		if not cond.strip():
			if self._cpp:
				body.append('while (true) {')
			else:
				body.append('loop {')
		else:
			if self._cpp:
				body.append('while (%s) {' %cond)
			else:
				body.append('while %s {' %cond)

		self.push()
		for line in list( map(self.visit, node.body) ):
			body.append( self.indent()+line )
		self.pull()
		body.append( self.indent() + '}' )
		return '\n'.join( body )


```


Compare `x==y`
-------------

needs to check if item is a string there is an `in` test, `if "x" in "xyz"`
so that can be translated to string.find or if it is a vector `std::find`.

```python
	def visit_Compare(self, node):
		comp = ['(']
		left = self.visit(node.left)
		if isinstance(node.left, ast.BinOp):
			comp.extend( ['(', self.visit(node.left), ')'] )
		else:
			comp.append( self.visit(node.left) )

		for i in range( len(node.ops) ):
			op = node.ops[i]
			if isinstance(op, ast.In) or isinstance(op, ast.NotIn):
				if comp[-1]==left:
					comp.pop()
				else:
					comp.append(' && ')
				rator = self.visit(node.comparators[i])
				if rator in self._known_strings:
					comp.append('(%s.find(%s) != std::string::npos)' %(rator, left))
				else:
					comp.append('(std::find(%s->begin(), %s->end(), %s) != %s->end())' %(rator, rator, left, rator))

			else:
				comp.append( self.visit(op) )

				if isinstance(node.comparators[i], ast.BinOp):
					comp.append('(')
					comp.append( self.visit(node.comparators[i]) )
					comp.append(')')
				else:
					comp.append( self.visit(node.comparators[i]) )

		comp.append( ')' )

		return ' '.join( comp )

```
If
----

TODO test `if pointer:` c++


```python

	def visit_If(self, node):
		out = []
		isinstance_test = False
		ispyinstance_test = False
		target = None
		classname = None

		if isinstance(node.test, ast.Compare) or isinstance(node.test, ast.UnaryOp) or isinstance(node.test, ast.BoolOp):
			test = self.visit(node.test)
		elif isinstance(node.test, ast.Name):
			if node.test.id in ('null', 'None', 'False'):
				test = 'false'
			elif node.test.id == 'True':
				test = 'true'
			else:
				test = '%s==true' %node.test.id
		elif isinstance(node.test, ast.Num):
			test = '%s!=0' %node.test.n
		elif isinstance(node.test, ast.Call) and isinstance(node.test.func, ast.Name) and node.test.func.id=='isinstance':
			isinstance_test = True
			target = self.visit(node.test.args[0])
			classname = self.visit(node.test.args[1])
			if self._memory[-1]=='STACK':
				test = '(%s.__class__==std::string("%s"))' %(target, classname)
			else:
				test = '(%s->__class__==std::string("%s"))' %(target, classname)

		elif isinstance(node.test, ast.Call) and isinstance(node.test.func, ast.Name) and node.test.func.id=='ispyinstance':
			ispyinstance_test = True
			target = self.visit(node.test.args[0])
			classname = self.visit(node.test.args[1])
			test = 'ispyinstance(%s, std::string("%s"))==true' %(target, classname)
			if 'ispyinstance' not in self._called_functions:
				self._called_functions['ispyinstance'] = 0
			self._called_functions['ispyinstance'] += 1

		else:
			test = '%s==true' %self.visit(node.test)

		out.append( 'if (%s) {' %test )

		self.push()
		if isinstance_test:
			assert self._cpp
			self._rename_hacks[target] = '_cast_%s' %target
			targ = target
			if '->' in target:
				targ = target.replace('->', '_')

			if self._memory[-1] == 'STACK':
				out.append(self.indent()+'auto _cast_%s = static_cast<%s>(%s);' %(targ, classname, target))
			elif self._polymorphic:
				out.append(self.indent()+'auto _cast_%s = std::dynamic_pointer_cast<%s>(%s);' %(targ, classname, target))
			else:
				out.append(self.indent()+'auto _cast_%s = std::static_pointer_cast<%s>(%s);' %(targ, classname, target))

		elif ispyinstance_test:
			assert self._cpp
			self._rename_hacks[target] = '_cast_%s' %target
			if classname in 'int i32 long i64'.split():
				out.append(self.indent()+'auto _cast_%s = PyInt_AS_LONG(%s);' %(target, target))
			elif classname in 'float f32 double f64'.split():
				out.append(self.indent()+'auto _cast_%s = PyFloat_AS_DOUBLE(%s);' %(target, target))
			elif classname in 'string str'.split():
				out.append(self.indent()+'auto _cast_%s = std::string(PyString_AS_STRING(%s));' %(target, target))
			else:
				#raise RuntimeError('TODO pytype:'+classname)
				## user class
				self._rename_hacks.pop(target)
				


		for line in list(map(self.visit, node.body)):
			if line is None: continue
			out.append( self.indent() + line )

		if isinstance_test or ispyinstance_test:
			if target in self._rename_hacks:
				self._rename_hacks.pop(target)


		orelse = []
		for line in list(map(self.visit, node.orelse)):
			orelse.append( self.indent() + line )

		self.pull()

		if orelse:
			out.append( self.indent() + '} else {')
			out.extend( orelse )

		out.append( self.indent() + '}' )

		return '\n'.join( out )


	def visit_Index(self, node):
		if isinstance(node.value, ast.Num):
			return str(node.value.n)
		else:
			return self.visit(node.value)

```
Name
-----

note: `nullptr` is c++11


```python

	def visit_Name(self, node):
		if node.id == 'None' or node.id == 'nil' or node.id == 'null':
			if self._cpp:
				return 'nullptr'
			else:
				return 'None'
		elif node.id == 'True':
			return 'true'
		elif node.id == 'False':
			return 'false'
		elif node.id in self._rename_hacks:  ## TODO make the node above on the stack is not an attribute node.
			return self._rename_hacks[ node.id ]
		elif node.id=='self' and self._class_stack and self._cpp:
			return 'this'
		elif node.id=='__finally__':
			return 'finally'
		else:
			return node.id

	def get_subclasses( self, C ):
		'''
		returns all sibling subclasses, C can be a subclass or the base class
		'''
		subclasses = set()
		self._collect_subclasses(C, subclasses)
		return subclasses

	def _collect_subclasses(self, C, subclasses):
		node = self._classes[ C ]
		if len(node._parents)==0:
			for sub in node._subclasses:
				subclasses.add( sub )
		else:
			for parent in node._parents:
				self._collect_subclasses(parent, subclasses)


	def visit_ClassDef(self, node):
		self._class_stack.append( node )
		if not hasattr(node, '_parents'):  ## only setup on the first pass
			node._parents = set()
			node._struct_def = dict()
			node._subclasses = set()  ## required for generics generator
			## subclasses must be a struct union so that Go can convert between struct types
			node._subclasses_union = dict()
			## any classes that this class contains in arrays or maps,
			## this is used by the child to create a weakref to the parent if required.
			node._contains_classes = set()
			node._weak_members = set()
			node._requires_init = False
			## subclasses need to check the parent class for methods with the same name
			## and a different signature.  These are regenerated in the subclass.
			node._methods = list()  ## nodes

		out = []
		sdef = dict()
		props = set()
		bases = set()
		base_classes = set()
		self._classes[ node.name ] = node
		self._class_props[ node.name ] = props
		if node.name not in self.method_returns_multiple_subclasses:
			self.method_returns_multiple_subclasses[ node.name ] = set()  ## tracks which methods in a class return different subclass types

		comments = []
		for b in node.body:
			if isinstance(b, ast.Expr) and isinstance(b.value, ast.Str):
				comments.append(b.value.s)

		if comments:
			out.append('/**')
			for line in comments[0].splitlines():
				out.append(' * '+line)
			out.append(' */')


		root_classes = set()  ## subsubclasses in c++ need to inherit from the roots
		cpp_bases = list()
		extern_classes = list()
		for base in node.bases:
			n = self.visit(base)
			if n == 'object':
				continue
			if n in self._root_classes:
				root_classes.add(n)

			node._parents.add( n )
			cpp_bases.append( n )
			bases.add( n )

			if n in self._class_props:
				props.update( self._class_props[n] )
				base_classes.add( self._classes[n] )

			if n not in self._classes:
				extern_classes.append(n)
			else:
				for p in self._classes[ n ]._parents:
					bases.add( p )
					props.update( self._class_props[p] )
					base_classes.add( self._classes[p] )
					if p in self._root_classes:
						root_classes.add(p)

				self._classes[ n ]._subclasses.add( node.name )

		if len(root_classes)>1 and self._cpp:
			raise RuntimeError(root_classes)

		if not len(base_classes):
			self._root_classes[ node.name ] = node

		## class decorators ##
		is_jvm_class = False
		external_header = None
		for decor in node.decorator_list:
			## __struct__ is generated in python_to_pythonjs.py
			if isinstance(decor, ast.Call) and isinstance(decor.func, ast.Name) and decor.func.id=='__struct__':
				for kw in decor.keywords:
					props.add( kw.arg )
					T = kw.value.id
					sdef[ kw.arg ] = T
			elif self._cpp:
				if isinstance(decor, ast.Name) and decor.id=='jvm':
					## subclasses from a Java class ##
					self._jvm_classes[ node.name ] = node
					is_jvm_class = True
				elif isinstance(decor, ast.Name) and decor.id in self._user_class_headers:
					external_header = self._user_class_headers[ decor.id ]
				elif isinstance(decor, ast.Call) and isinstance(decor.func, ast.Name) and decor.func.id == 'macro':
					out.append( decor.args[0].s )
				else:
					raise RuntimeError('TODO class decorator')

		init = None
		method_names = set()
		for b in node.body:
			if isinstance(b, ast.FunctionDef):
				method_names.add( b.name )
				node._methods.append( b )  ## save method node, header-signature and body.

				if b.name == '__init__':
					init = b
					node._requires_init = True

			elif isinstance(b, ast.Expr) and isinstance(b.value, ast.Dict):
				for i in range( len(b.value.keys) ):
					k = self.visit( b.value.keys[ i ] )
					if isinstance(b.value.values[i], ast.Str):
						v = b.value.values[i].s
					elif isinstance(b.value.values[i], ast.Call):
						n = b.value.values[i]
						if n.func.id in ('__go__map__', '__arg_map__'):
							if n.func.id=='__arg_map__':
								assert n.args[0].s.startswith('map[')
								key_type = n.args[0].s.split('[')[-1].split(']')[0]
								value_type = n.args[0].s.split(']')[-1]
							else:
								key_type = self.visit(n.args[0])
								value_type = self.visit(n.args[1])
							if key_type=='string': key_type = 'std::string'
							if value_type=='string': value_type = 'std::string'
							v = 'std::map<%s, %s>' %(key_type, value_type)
						elif n.func.id == '__arg_array__':
							if isinstance(n.args[0], ast.Str):
								t = n.args[0].s
							else:
								t = self.visit(n.args[0])
							dims = 0
							if t.startswith('['):
								dims = t.count('[')
								t = t.split(']')[-1]
							if t=='string':
								if self.usertypes and 'string' in self.usertypes:
									key_type = self.usertypes['string']['type']
								else:
									key_type = 'std::string'

							if not self.is_prim_type(t):
								if self.usertypes and 'shared' in self.usertypes:
									t = self.usertypes['shared']['template'] % t
								else:
									t = 'std::shared_ptr<%s>' %t

							if not dims or dims==1:
								if self.usertypes and 'vector' in self.usertypes:
									v = self.usertypes['vector']['template'] % t
								else:
									v = 'std::vector<%s>' %t
							elif dims == 2:  ## TODO clean this up, support more dims, and self.usertypes
								v = 'std::vector<std::shared_ptr<std::vector<%s>>>' %t

						else:
							raise RuntimeError('TODO', n.func.id)

					else:
						v = self.visit( b.value.values[i] )

					if v.startswith('['):  ## swap array style to C++
						x,y = v.split(']')
						v = y + x + ']'
						if self._memory[-1]=='HEAP':
							if self.is_prim_type(y):
								v = 'std::vector<%s>' %y
							else:
								v = 'std::vector<std::shared_ptr<%s>>' %y

					sdef[k] = v


		node._struct_def.update( sdef )
		unionstruct = dict()
		unionstruct.update( sdef )
		for pname in node._parents:
			if pname in self._classes:
				parent = self._classes[ pname ]
				parent._subclasses_union.update( sdef )        ## first pass
				unionstruct.update( parent._subclasses_union ) ## second pass
			else:
				pass  ## class from external c++ library


		parent_init = None
		overload_nodes = []
		overloaded  = []  ## this is just for rust
		overloaded_returns_self = []
		if base_classes:
			for bnode in base_classes:
				for b in bnode.body:
					if isinstance(b, ast.FunctionDef):
						overload_nodes.append( b )
						#if hasattr(b, 'returns_self') and b.returns_self:
						#	if b.name != '__init__' and not b.is_abstract:
						#		overloaded_returns_self.append(b)
						if b.name != '__init__' and b.name not in method_names:
							overloaded_returns_self.append(b)

						## catch_call trick is used to call methods on base classes from the subclass.
						if self._cpp:
							##self.catch_call.add( '%s->%s' %(bnode.name, b.name))
							#note: `::` is automatic now when calling classmethod/staticmethods.
							self.catch_call.add( '%s::%s' %(bnode.name, b.name))
						else:
							self.catch_call.add( '%s.%s' %(bnode.name, b.name))

						if b.name in method_names:
							b.overloaded = True
							b.classname  = bnode.name
						if b.name == '__init__':
							parent_init = {'class':bnode, 'node':b}
							node._requires_init = True


		for b in overload_nodes:
			if hasattr(b, 'overloaded'):
				original = b.name
				b.name = '__%s_%s'%(b.classname, b.name)  ## rust requires this extra hackery
				overloaded.append( self.visit(b) )
				b.name = original
			else:
				overloaded.append( self.visit(b) )

		if self._cpp:
			if cpp_bases:
				#parents = ','.join(['public %s' % rname for rname in root_classes])
				parents = ','.join(['public %s' % rname for rname in cpp_bases])
				out.append( 'class %s:  %s {' %(node.name, parents))
			else:
				#out.append( 'class %s {' %node.name)
				## shared from this is required so that `self` (this) can be passed to
				## other functions and objects that may take ownership of `self`.
				## on subclasses the base class is returned from `shared_from_this()`
				out.append( 'class %s: public std::enable_shared_from_this<%s> {' %(node.name, node.name))

			## body macros come before public ##
			for b in node.body:
				if isinstance(b, ast.Expr) and isinstance(b.value, ast.Call) and isinstance(b.value.func, ast.Name) and b.value.func.id=='macro':
					out.append(b.value.args[0].s)


			out.append( '  public:')

			#if not base_classes:
			if not cpp_bases or is_jvm_class:
				## only the base class defines `__class__`, this must be the first element
				## in the struct so that all rusthon object has the same header memory layout.
				## note if a subclass redefines `__class__` even as a string, and even as the
				## first struct item, it will still not have the same memory location as super.__class__.
				## We require the same memory location for `__class__` because the `isinstance`
				## hack requires on `__class__` always being valid to check an objects class type at runtime.
				out.append( '	std::string __class__;')
				out.append( '	bool __initialized__;')
				out.append( '	int  __classid__;')
		else:
			out.append( 'struct %s {' %node.name)
			## rust requires that a struct contains at least one item,
			## `let a = A{}` is invalid in rust, and will fail with this error
			## error: structure literal must either have at least one field or use functional structure update syntax
			## to workaround this problem in the init constructor, the A::new static method simply makes
			## the new struct passing the classname as a static string, and then calls the users __init__ method
			out.append( '	__class__ : string,')


		rust_struct_init = ['__class__:"%s"' %node.name]
		parent_attrs = {}

		if base_classes:
			for bnode in base_classes:
				if self._cpp:
					if bnode._struct_def.keys():
						out.append('//	members from class: %s  %s'  %(bnode.name, bnode._struct_def.keys()))
						## not required, the subclass should not redeclare members of parents
						#for key in bnode._struct_def:
						#	if key not in unionstruct:
						#		unionstruct[key] = bnode._struct_def[key]
						parent_attrs.update( bnode._struct_def )

				elif self._rust:
					out.append('//	members from class: %s  %s'  %(bnode.name, bnode._struct_def.keys()))
					## to be safe order should be the same?
					for key in bnode._struct_def.keys():
						if key in unionstruct:
							unionstruct.pop(key)  ## can subclass have different types in rust?
						out.append('	%s : %s,' %(key, bnode._struct_def[key]))
						rust_struct_init.append('%s:%s' %(key, default_type(bnode._struct_def[key])))

				else:
					raise RuntimeError('invalid backend')

		node._struct_init_names = []  ## save order of struct layout

		for name in unionstruct:

			if unionstruct[name]=='interface{}':
				raise SyntaxError('interface{} is just for the Go backend')

			node._struct_init_names.append( name )
			#if name=='__class__': continue

			T = unionstruct[name]
			## skip redefines of attributes in a subclass with the same type,
			## this ensures that subclasses will have the same memory layout
			## for shared attributes of the same type, and that std::static_pointer_cast also works.
			if name in parent_attrs and parent_attrs[name]==T:
				continue

			member_isprim = self.is_prim_type(T)
			if self._cpp:
				if T=='string': T = 'std::string'

				if T.endswith(']'):
					x,y = T.split('[')
					out.append('	%s  %s[%s;' %(x, name, y ))
				elif member_isprim:
					out.append('	%s  %s;' %(T, name ))
				else:
					otherclass = T.split('<')[-1].split('>')[0]

					if self.is_container_type(T):
						node._contains_classes.add( otherclass )

					weakref = False
					if otherclass in self._classes:
						if node.name in self._classes[otherclass]._contains_classes:
							#raise RuntimeError('%s contains %s' %(otherclass, node.name))
							weakref = True

					if not self._shared_pointers or self._memory[-1]=='STACK':
						out.append('	%s*  %s;' %(T, name ))
					elif self._unique_ptr:
						out.append('	std::unique_ptr<%s>  %s;' %(T, name ))
					else:

						if weakref:
							node._weak_members.add(name)
							if self.usertypes and 'weakref' in self.usertypes:
								out.append('	%s  %s;' %( self.usertypes['weakref']['template']%T, name ))
							else:
								out.append('	std::weak_ptr<%s>  %s;' %(T, name ))

						elif T.startswith('std::shared_ptr<'):  ## TODO check this
							out.append('	%s  %s;' %(T, name ))

						else:
							if self.usertypes and 'shared' in self.usertypes:
								out.append('	%s  %s;' %(self.usertypes['shared']['template']%T, name ))
							else:
								out.append('	std::shared_ptr<%s>  %s;' %(T, name ))
			else:
				rust_struct_init.append('%s:%s' %(name, default_type(T)))
				if T=='string': T = 'String'
				if member_isprim:
					out.append('	%s : %s,' %(name, T))
				else:
					out.append('	%s : Rc<RefCell<%s>>,' %(name, T))


		self._rust_trait = []
		self._cpp_class_header = []
		impl  = []
		self.push()

		## required by new style because __init__ returns this which needs to be defined for each subclass type ##
		if self._cpp and parent_init:
			if not init:
				impl.append( self.visit(parent_init['node']) )
			elif len(init.args.args) != len(parent_init['node'].args.args):
				impl.append( self.visit(parent_init['node']) )

		for b in node.body:
			if isinstance(b, ast.FunctionDef):
				impl.append( self.visit(b) )

		for b in overloaded_returns_self:
			impl.append( self.visit(b) )


		self.pull()

		if self._cpp:
			for impl_def in self._cpp_class_header:
				out.append( '\t' + impl_def )



			## c++ empty constructor with `struct-emeddding` the class name
			#out.append('	%s() : __class__(std::string("%s")) {}' %(node.name, node.name) )  ## this breaks when looping over array items
			## member initializer list `MyClass() : x(1) {}` only work when `x` is locally defined inside the class,
			## it breaks on `__class__` because that is defined in the parent class, instead `__class__` is initalized in the constructors body.
			## TODO make __class__ static const string.

			if not extern_classes:
				classid = self._classes.keys().index(node.name)
				out.append('	bool operator != (std::nullptr_t rhs) {return __initialized__;}' )
				out.append('	bool operator == (std::nullptr_t rhs) {return !__initialized__;}' )
				out.append('	%s() {__class__ = std::string("%s"); __initialized__ = true; __classid__=%s;}' %(node.name, node.name, classid) )

				## `let a:MyClass = None` is generated when in stack mode and an object is created and set to None.
				out.append('	%s(bool init) {__class__ = std::string("%s"); __initialized__ = init; __classid__=%s;}' %(node.name, node.name, classid) )

				if self._polymorphic:
					out.append('	virtual std::string getclassname() {return this->__class__;}')  ## one virtual method makes class polymorphic
				elif self._memory[-1]=='STACK':
					out.append('	std::string getclassname() {return __class__;}')
				else: #not base_classes:
					out.append('	std::string getclassname() {return this->__class__;}')

			elif is_jvm_class:
				## TODO constructor args for jvm super class and __init__ for subclass
				out.append('	%s(JavaVM* _jvm) : %s(_jvm) {__class__ = std::string("%s");}' %(node.name, extern_classes[0], node.name) )
				out.append('	std::string getclassname() {return this->__class__;}')
			else:
				pass ## some unknown external c++ class, TODO constructor.

			out.append('};')

		else: ## rust
			out.append('}')

		cpp_method_impl = []
		if self._cpp:
			for idef in impl:
				if external_header:
					cpp_method_impl.append( idef )
				else:  ## can not write c++ method implementations before other class headers
					self._cpp_class_impl.append( idef )

		else:
			## using a trait is not required, because a struct type can be directly implemented.
			## note: methods require a lambda wrapper to be passed to another function.
			#out.append('trait %s {' %node.name)
			#for trait_def in self._rust_trait: out.append( '\t'+ trait_def )
			#out.append('}')
			#out.append('impl %s for %sStruct {' %(node.name, node.name))
			#for impl_def in impl: out.append( impl_def )
			#out.append('}')

			out.append('impl %s {' %node.name)
			for impl_def in impl: out.append( impl_def )

			if overloaded:
				out.append('/*		overloaded methods		*/')
				for o in overloaded:
					out.append( o )

			if init:
				tmp = 'let mut __ref__ = %s{%s};' %(node.name, ','.join(rust_struct_init))
				tmp += '__ref__.__init__(%s);' % ','.join(init._arg_names)
				tmp += 'return __ref__;'
				out.append('/*		constructor		*/')
				out.append('	fn new( %s ) -> %s { %s }' %(init._args_signature, node.name, tmp) )
			else:
				tmp = 'let mut __ref__ = %s{%s};' %(node.name, ','.join(rust_struct_init))
				tmp += 'return __ref__;'
				out.append('/*		constructor		*/')
				out.append('	fn new() -> %s { %s }' %(node.name, tmp) )


			out.append('}')  ## end rust `impl`


		self.catch_call = set()
		self._class_stack.pop()
		if external_header:
			external_header['source'].extend( out )
			out.append( '// header saved to: %s'  % external_header['file'])
			return '\n'.join(cpp_method_impl)

		else:
			return '\n'.join(out)

```

Visit Call Special
-----------------
hack for calling base class methods.

```python

	def _visit_call_special( self, node ):
		fname = self.visit(node.func)
		assert fname in self.catch_call
		assert len(self._class_stack)
		if len(node.args):
			if isinstance(node.args[0], ast.Name) and node.args[0].id == 'self':
				node.args.remove( node.args[0] )

		if self._cpp:
			if fname.count('::') > 1: raise RuntimeError('TODO: %s'%fname)
			##classname = fname.split('->')[0]
			classname = fname.split('::')[0]
			hacked = classname + '::' + fname[len(classname)+2:]
			return self._visit_call_helper(node, force_name=hacked)
		else:
			classname = fname.split('.')[0]
			hacked = 'self.__%s_%s' %(classname, fname[len(classname)+1:])
			return self._visit_call_helper(node, force_name=hacked)

```

Subscript `a[n]`
-----------------

```python


	def visit_Subscript(self, node):
		if isinstance(node.slice, ast.Ellipsis):  ## special deference pointer syntax
			return '(*%s)' %self.visit(node.value)
		else:
			## deference pointer and then index
			if isinstance(node.slice, ast.Slice):
				if self._cpp:
					## std::valarray has a slice operator `arr[ std::slice(start,end,step) ]`
					## but std::valarray only works on numeric values, and can not grow in size.
					msg = {'value':self.visit(node.value), 'slice':node.slice, 'lower':None, 'upper':None, 'step':None}
					if node.slice.lower:
						msg['lower'] = self.visit(node.slice.lower)
					if node.slice.upper:
						msg['upper'] = self.visit(node.slice.upper)
					if node.slice.step:
						msg['step'] = self.visit(node.slice.step)

					if msg['step'] is None and (msg['value'] in self._known_strings or msg['value'] in self._global_types['string']):
						if msg['lower'] and msg['upper']:
							return '%s.substr(%s, %s)' %(msg['value'], msg['lower'], msg['upper'])
						elif msg['lower']:
							return '%s.substr(%s, %s.size()-1)' %(msg['value'], msg['lower'], msg['value'])
						else:
							return '%s.substr(0, %s)' %(msg['value'], msg['upper'])

					raise GenerateSlice( msg )

				else:
					r = '&(*%s)[%s]' % (self.visit(node.value), self.visit(node.slice))
			else:
				if self._cpp:
					## default to deference shared pointer ##
					value = self.visit(node.value)
					is_tuple_index = isinstance(node.slice, ast.Index) and isinstance(node.slice.value, ast.Set)

					if value in self._known_pointers:
						if is_tuple_index:
							r = 'std::get<%s>(*%s)' % (self.visit(node.slice.value.elts[0]), value)
						else:
							r = '(*%s)[%s]' % (value, self.visit(node.slice))
					elif self._memory[-1]=='STACK':
						if is_tuple_index:
							r = 'std::get<%s>(%s)' % (self.visit(node.slice.value.elts[0]), value)
						else:
							r = '%s[%s]' % (value, self.visit(node.slice))
					else:
						if is_tuple_index:
							r = 'std::get<%s>(*%s)' % (self.visit(node.slice.value.elts[0]), value)
						else:
							r = '(*%s)[%s]' % (value, self.visit(node.slice))

					#############################################
					if value.startswith('PyObject_GetAttrString(') and value.endswith(')'):
						r = 'PyObject_CallFunction(PyObject_GetAttrString(%s,"__getitem__"),"i", %s)' % (value, self.visit(node.slice))

					elif isinstance(node.value, ast.Name):
						target = node.value.id
						is_neg = False
						if isinstance(node.slice, ast.Index) and isinstance(node.slice.value, ast.Num) and node.slice.value.n < 0:
							is_neg = True

						if self._function_stack:
							if target in self._known_strings:
								if is_neg:
									r = '%s.substr(%s.size()%s,1)' %(target, target,self.visit(node.slice))
								else:
									r = '%s.substr(%s,1)' %(target, self.visit(node.slice))
						## need to also check if the target name is a global string ##
						if target in self._global_types['string']:
							if is_neg:
								r = '%s.substr(%s.size()%s,1)' %(target, target,self.visit(node.slice))
							else:
								r = '%s.substr(%s,1)' %(target, self.visit(node.slice))

				elif self._rust:
					r = '%s.borrow_mut()[%s]' % (self.visit(node.value), self.visit(node.slice))
				else:
					r = '(*%s)[%s]' % (self.visit(node.value), self.visit(node.slice))

			## TODO: subclass generics for arrays
			#if isinstance(node.value, ast.Name) and node.value.id in self._known_generics_arrays:
			#	target = node.value.id
			#	#value = self.visit( node.value )
			#	cname = self._known_arrays[target]
			#	#raise GenerateGenericSwitch( {'target':target, 'value':r, 'class':cname} )
			#	raise GenerateGenericSwitch( {'value':r, 'class':cname} )

			return r

```
Call Function/Method
-----------------
handles all special calls

```python

	def _visit_call_helper(self, node, force_name=None):
		fname = force_name or self.visit(node.func)
		if fname =='cdef':
			s = node.args[0].s
			varname = s.split('=')[0].split()[-1]
			if varname.startswith('*'):
				varname = varname.split('*')[-1]
			elif varname.startswith('&'):
				varname = varname.split('&')[-1]

			self._known_vars.add(varname)
			if varname in self._vars:
				self._vars.remove(varname)

			return s

		elif fname=='__array__':
			if len(node.args)==4:
				aname  = self.visit(node.args[0])
				asize  = self.visit(node.args[1])
				atype = self.visit(node.args[2])
				ainit = self.visit(node.args[3])
				self._known_arrays[aname] = (atype, asize)
				return '%s %s[%s] = %s;' %(atype, aname, asize, ainit)
			else:
				raise SyntaxError(self.format_error('invalid __array__'))

		elif self._cpp and fname=='move':
			args = ','.join([self.visit(arg) for arg in node.args])
			return 'std::move(%s)' %args

		elif self._cpp and fname=='complex':
			args = ','.join([self.visit(arg) for arg in node.args])
			return 'std::complex<double>(%s)' %args

		elif self._cpp and fname in self._typedefs:
			typedef = self._typedefs[fname]
			args = ','.join([self.visit(arg) for arg in node.args])
			if typedef.startswith('tuple('):
				if self._memory[-1]=='STACK':
					return 'std::make_tuple(%s)' %args
				else:
					return '/*typedef: %s*/[&](){auto _ = std::make_tuple(%s); return std::make_shared<decltype(_)>(_);}()' %(typedef,args)
			#elif typedef.startswith('std::shared_ptr<std::vector<') and args:
			elif typedef.startswith('std::vector<') and not args:
				if typedef=='std::vector<tuple>':
					return '/*typedef-tuple-array:%s*/%s(%s)' %(typedef, fname, args)  ## requires `new` ?
				else:
					subtype = typedef.split('<')[-1].split('>')[0]
					if subtype in self._typedefs:
						subsubtype = self._typedefs[subtype]
						if subsubtype.startswith('tuple('):
							for tsub in subsubtype[len('tuple('):-1].split(','):
								if tsub in self._typedefs:
									tsubtype = self._typedefs[tsub]
									if tsubtype.startswith('tuple('):
										raise SyntaxError(self.format_error('TRANSLATION-ERROR: an array of nested tuple of tuples, must be constructed with at least one item.'))
					return '/*typedef-array:%s*/%s(%s)' %(typedef, fname, args)  ## requires `new` ?

			elif typedef.startswith('std::vector<') and args:
				args = [self.visit(arg) for arg in node.args]
				assert args[0].startswith('new std::vector<')
				tvectype = args[0].split('{')[0][4:]
				hacked_args = []
				for arg in args:
					if arg.startswith('new '):
						arg = arg[4:]
					hacked_args.append(arg)
				return '/*typedef: %s*/std::make_shared<%s>(%s)' %(typedef, tvectype, ','.join(hacked_args))
			else:
				return '/*typedef:%s*/%s(%s)' %(typedef, fname, args)  ## requires `new` ?

		elif self._cpp and fname =='tuple->get':
			return 'std::get<%s>(*%s)' %(self.visit(node.args[1]), self.visit(node.args[0]))

		elif self._cpp and fname == 'tuple.get':
			return 'std::get<%s>(%s)' %(self.visit(node.args[1]), self.visit(node.args[0]))

		elif self._cpp and fname == 'dict->keys':
			if len(node.args) != 1:
				raise SyntaxError(self.format_error('dict.keys(mymap) requires a single argument'))

			arrname = self.visit(node.args[0])
			vectype = 'std::vector<decltype(%s)::element_type::key_type>' %arrname
			r = [
				'[&%s](){' %arrname,
				'auto __ = std::make_shared<%s>(%s());' %(vectype,vectype),
				'for (const auto &_ : *%s) {' %arrname,
				'__->push_back(_.first);',
				'}',
				'return __;}()'
			]
			return ''.join(r)

		elif self._cpp and fname == 'dict->values':
			if len(node.args) != 1:
				raise SyntaxError(self.format_error('dict.values(mymap) requires a single argument'))

			arrname = self.visit(node.args[0])
			vectype = 'std::vector<decltype(%s)::element_type::mapped_type>' %arrname
			r = [
				'[&%s](){' %arrname,
				'auto __ = std::make_shared<%s>(%s());' %(vectype,vectype),
				'for (auto &_ : *%s) {' %arrname,
				'__->push_back(_.second);',
				'}',
				'return __;}()'
			]
			return ''.join(r)

		elif fname=='future':
			if not len(self._function_stack):
				raise SyntaxError('future() call used at global level')
			elif not self._function_stack[-1].return_type.startswith('future<'):
				raise SyntaxError('expected future<T> return type, instead got: %s' %self._function_stack[-1].return_type )

			args = ','.join([self.visit(arg) for arg in node.args])
			ftemplate = self._function_stack[-1].return_type.replace('future', 'make_ready_future')
			return '%s(%s)' %(ftemplate, args)

		elif fname in self.macros:
			macro = self.macros[fname]
			if '%=' in macro:  ## advanced meta programming, captures the name of the variable the macro assigns to.
				if not self._assign_var_name:
					raise RuntimeError('the macro syntax `%=` can only be used as part of an assignment expression')
				macro = macro.replace('%=', self._assign_var_name)

			args = ','.join([self.visit(arg) for arg in node.args])
			if '"%s"' in macro:
				return macro % tuple([s.s for s in node.args])
			elif '%s' in macro:
				if macro.count('%s')>1:
					args = tuple([self.visit(s) for s in node.args])
				try:
					return macro % args
				except TypeError as err:
					raise RuntimeError('%s\nMACRO:\t%s\nARGS:\t%s' %(err[0], macro, args))

			else:
				return '%s(%s)' %(macro,args)

		if self._stack and fname in self._classes and not isinstance(self._stack, ast.Assign):
			node.is_new_class_instance = True

		is_append = False
		if fname.endswith('.append'): ## TODO - deprecate append to pushX or make `.append` method reserved by not allowing methods named `append` in visit_ClassDef?
			is_append = True
			arr = fname.split('.append')[0]

		if fname.endswith('->__exec__'):
			fname = fname.replace('->__exec__', '->exec')

		###########################################
		if fname == 'macro':
			if node.keywords:
				r = []
				for kw in node.keywords:
					r.append('#define %s %s' %(kw.arg, self.visit(kw.value)))
				return '\n'.join(r) + '//;'
			else:
				return '%s //;' %node.args[0].s
		elif fname == 'pragma':
			return '#pragma %s //;' %node.args[0].s
		elif fname == 'addr':
			return '&%s' %self.visit(node.args[0])
		elif fname.startswith('PyObject_GetAttrString') and isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id in self._known_pyobjects:
			return self.gen_cpy_call(node.func.value.id, node)  ## TODO test this
		elif fname.startswith('PyObject_GetAttrString(') and fname.endswith(')') and isinstance(node.func, ast.Attribute):
			return self.gen_cpy_call(fname, node)

		elif fname.endswith('.split') and isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id in self._known_strings:
			splitchar = 'std::string(" ")'
			if len(node.args): splitchar = self.visit(node.args[0])
			return '__split_string__( %s, %s )' %(node.func.value.id, splitchar)
		elif fname.endswith('.lower') and isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id in self._known_strings:
			return '__string_lower__(%s)' %node.func.value.id
		elif fname.endswith('.upper') and isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id in self._known_strings:
			return '__string_upper__(%s)' %node.func.value.id

		elif fname.startswith('nuitka->'):
			fname = fname.split('nuitka->')[-1]
			r = [
				'GET_STRING_DICT_VALUE(',
				' moduledict___main__,',
				'(Nuitka_StringObject *)"%s" )' %fname
			]
			return '\n'.join(r)

		elif fname.startswith('cpython->'):
			n = fname.split('cpython->')[-1]
			if n == 'initalize':
				return '__cpython_initalize__()'
			elif n == 'finalize':
				return '__cpython_finalize__(%s)' %self.visit(node.args[0])
			else:
				c = '__cpython_get__("%s")' %n
				return self.gen_cpy_call(c, node)

		elif fname.startswith('nim->'):
			if fname.endswith('main'):
				return 'PreMain(); NimMain()'
			#elif fname.endswith('unref'):  ## GC_ref is called from nim code, its not part of the NIM C API?
			#	return 'GC_unref(%s)' %self.visit(node.args[0])
			#elif fname.endswith('ref'):
			#	return 'GC_ref(%s)' %self.visit(node.args[0])
			else:
				raise RuntimeError('unknown nim api function')

		elif fname=='jvm':
			classname = node.args[0].func.id
			args = [self.visit(arg) for arg in node.args[0].args]

			## using make_shared is safer and is only a single allocation, but it crashes g++4.7
			#return 'std::make_shared<%s>(%s)'%(classname,','.join(args))

			## this is slower because it makes two allocations, and if allocation of shared_ptr
			## fails, then the object could be leaked.  using this for now because it works with g++4.7
			if classname in self._jvm_classes:
				## Rusthon class that subclass from Java classes (decorated with @jvm)
				return 'std::shared_ptr<%s>((new %s(__javavm__))->__init__(%s))'%(classname, classname,','.join(args))
			else:
				## Java class ##
				args.insert(0, '__javavm__') ## global JavaVM instance
				if len(args)>1:
					raise RuntimeError('Giws as of feb21.2015, is missing support for constructor arguments')
				return 'std::shared_ptr<%s>(new %s(%s))'%(classname, classname,','.join(args))


		elif fname=='jvm->create':  ## TODO - test multiple vms
			return '__create_javavm__();'
		elif fname=='jvm->load':
			if node.args[0].s not in self._java_classpaths:
				self._java_classpaths.append(node.args[0].s)
			return ''
		elif fname=='jvm->namespace':  ## giws squashes the name space from `org.x.y` to `org_x_y`
			s = node.args[0].s
			return 'using namespace %s;' %s.replace('.', '_')
			#ns = []
			#nspath = s.split('.')
			#for i,a in enumerate(nspath):
			#	if i==len(nspath)-1:
			#		ns.append('::'+a)
			#	else:
			#		ns.append(a+'_')
			#raise SyntaxError(ns)
		elif fname=='namespace':
			return 'using namespace %s;' %node.args[0].s
		elif fname=='weak->unwrap':
			## this is needed for cases where we do not know if its a weakptr, `self.a.b.c.parent`,
			## it is also useful for the user to simply make their code more clear.
			w = self.visit(node.args[0])
			lock_name = 'lock'
			if self.usertypes and 'weakref' in self.usertypes:
				lock_name = self.usertypes['weakref']['lock']
			if not w.endswith('.%s()'%lock_name): w += '.%s()' %lock_name
			return w

		elif fname=='weak->valid':
			## this is needed for cases where we do not know if its a weakptr, `self.a.b.c.parent`,
			## it is also useful for the user to simply make their code more clear.
			w = self.visit(node.args[0])
			if self.usertypes and 'weakref' in self.usertypes:
				return '%s.%s()' %(w,self.usertypes['weakref']['valid'])
			else:
				return '%s != nullptr' %w

		elif fname.endswith('.insert') and fname.split('.insert')[0] in self._known_arrays and len(node.args)>=2:
			arr = fname.split('.insert')[0]
			idx = self.visit(node.args[0])
			val = self.visit(node.args[1])

			if len(node.args)==2:
				#if '.' in val and arr == val.split('.')[0] and 'pop' in val:  ## TODO
				if '->' in val and arr == val.split('->')[0] and 'pop' in val:
					popidx = None
					r = []
					if val.endswith('pop_back()'):
						#popidx = '%s->size()-1' %arr
						popidx = '%s-1' %self._known_arrays[arr][1]
						r.append('auto __back__ = %s[%s];' %(arr,popidx))
						r.extend([  ## move elements forward starting from back
							self.indent()+'for (int __i=%s; __i>%s; __i--) {' %(popidx, idx),
							self.indent()+'  %s[__i] = %s[__i-1];' %(arr, arr),
							self.indent()+'}'
						])
						r.append(self.indent()+'%s[%s] = __back__;' %(arr, idx))

					else:
						popidx = val.split('(')[-1].split(')')[0].strip()
						assert popidx == '0' ## TODO other indices
						r.append('auto __front__ = %s[%s];' %(arr,popidx))
						r.extend([  ## move elements forward starting from insert idx
							self.indent()+'for (int __i=1; __i<=%s; __i++) {' %idx,
							self.indent()+'  %s[__i-1] = %s[__i];' %(arr, arr),
							self.indent()+'}'
						])
						r.append(self.indent()+'%s[%s] = __front__;' %(arr, idx))


					return '\n'.join(r)

				else:
					raise SyntaxError('fixed size stack allocated arrays can not use iterators to insert elements from another array')

			elif len(node.args)==3:
				end = self.visit(node.args[2])
				return '%s.insert(%s, %s, %s)' %(arr, idx, val, end)

			else:
				raise RuntimeError('TODO .insert(...)')


		elif fname.endswith('->insert') and fname.split('->insert')[0] in self._known_arrays and len(node.args)>=2:
			arr = fname.split('->insert')[0]
			idx = self.visit(node.args[0])
			val = self.visit(node.args[1])
			if len(node.args)==2:
				#if '->' in val and arr == val.split('->')[0] and 'pop' in val:
				#	if val.endswith('pop_back()'):
				#		popidx = '%s->size()-1' %arr
				#	else:
				#		popidx = val.split('(')[-1].split(')')[0]

				if '->begin()' in idx:
					return '%s->insert(%s, %s)' %(arr, idx, val)
				else:
					return '%s->insert(%s->begin()+%s, %s)' %(arr, arr, idx, val)
				#else:
				#	return '%s->insert(%s+%s, %s)' %(arr, arr, idx, val)
			elif len(node.args)==3:
				end = self.visit(node.args[2])
				return '%s->insert(%s, %s, %s)' %(arr, idx, val, end)

			else:
				raise RuntimeError('TODO .insert(...)')

		elif fname == 'double' and self._cpp:
			return '__double__(%s)' %self.visit(node.args[0])

		elif fname == 'clock' and len(node.args)==0:
			## note in c++ std::clock returns clock ticks, not time
			return '__clock__()'

		elif fname == '__asm__':
			ASM_WRITE_ONLY = '='  ## write constraint
			ASM_ANY_REG    = 'r'  ## register name: r, eax, ax, al,  ebx, bx, bl
			ASM_OUT_DEFAULT = ASM_WRITE_ONLY + ASM_ANY_REG

			code = []
			if self._cpp:
				code.append('asm')
			else:
				# http://doc.rust-lang.org/guide-unsafe.html#inline-assembly
				code.append('unsafe{ asm!')

			volatile = False
			alignstack = False
			outputs = []
			inputs = []
			clobber = []
			asmcode = None
			for kw in node.keywords:
				if kw.arg == 'volatile' and kw.value.id.lower()=='true':
					volatile = True
				elif kw.arg == 'alignstack' and kw.value.id.lower()=='true':
					alignstack = True
				elif kw.arg == 'outputs':
					write_mode = ASM_OUT_DEFAULT
					if isinstance(kw.value, ast.List):
						mode = kw.value.elts[0].s
						output = kw.value.elts[1].id
						outputs.append('"%s" (%s)' %(mode, output))
					else:
						outputs.append('"%s" (%s)' %(write_mode, kw.value.id))

				elif kw.arg == 'inputs':
					if isinstance(kw.value, ast.List) or isinstance(kw.value, ast.Tuple):
						for elt in kw.value.elts:
							if isinstance(elt, ast.List):
								register = elt.elts[0].s
								input = elt.elts[1].id
								inputs.append('"%s" (%s)' %(register, input))
							else:
								inputs.append('"%s" (%s)' %(ASM_ANY_REG,elt.id))
					else:
						inputs.append('"%s" (%s)' %(ASM_ANY_REG,kw.value.id))
				elif kw.arg == 'clobber':
					if isinstance(kw.value, ast.List) or isinstance(kw.value, ast.Tuple):
						clobber.extend( ['"%s"' %elt.s for elt in kw.value.elts] )
					else:
						clobber.extend(
							['"%s"'%clob for clob in kw.value.s.split(',') ]
						)

				elif kw.arg == 'code':
					asmcode = '"%s"' %kw.value.s

			if volatile:
				if self._cpp:
					code.append( 'volatile' )

			assert asmcode
			if not self._cpp:
				## rust asm uses llvm as its backend,
				## llvm asm syntax is slightly different from regular gcc,
				## input arguments in gcc are given as `%N`,
				## while in llvm they are given as `$N`
				asmcode = self._gccasm_to_llvmasm(asmcode)

			code.append( '(' )
			code.append( asmcode )
			code.append( ':' )
			if outputs:
				code.append( ','.join(outputs) )
			code.append( ':' )
			if inputs:
				code.append( ','.join(inputs) )
			code.append( ':' )
			if clobber:
				code.append( ','.join(clobber) )

			if self._cpp:
				code.append( ');')
			else:
				code.append( ':' )  ## rust options
				ropts = []
				if volatile:
					ropts.append('"volatile"')
				if alignstack:
					ropts.append('"alignstack"')

				code.append( ','.join(ropts) )
				code.append( '); } // end unsafe' )


			return ' '.join( code )

		elif fname == '__let__':
			vname = None
			infer_from = None
			if len(node.args) and isinstance(node.args[0], ast.Name):
				vname = node.args[0].id
			elif len(node.args)==2 and isinstance(node.args[0], ast.Call):
				## syntax: `let foo(bar) : SomeClass`, translates into c++11 universal constructor call
				## used when using classes from external libraries.
				assert self._cpp
				if isinstance(node.args[1], ast.Str):
					T = node.args[1].s
				else:
					T = self.visit(node.args[1])

				return '%s %s' %(T, self.visit(node.args[0]))


			elif len(node.args) and isinstance(node.args[0], ast.Attribute): ## syntax `let self.x:T = y`
				assert node.args[0].value.id == 'self'
				T = None
				if isinstance(node.args[1], ast.Str):
					T = node.args[1].s
				else:
					T = self.visit(node.args[1])

				if len(node.args)==2:
					#raise SyntaxError(','.join([self.visit(a) for a in node.args]))
					if T.startswith('['):
						if self._memory[-1]=='HEAP':
							x,y = T.split(']')
							n = x.split('[')[-1]
							return 'this->%s = std::make_shared<std::vector<%s>>(%s);' %(node.args[0].attr, y, n)

						else:
							return '/* %s : %s */' %(node.args[0].attr, T)


				value = self.visit(node.args[2])

				if isinstance(node.args[2], ast.Dict):
					assert T.startswith('__go__map__')
					d = node.args[2]
					mtypek = self.visit(node.args[1].args[0])
					mtypev = self.visit(node.args[1].args[1])
					if mtypev.startswith('{') or '{' in mtypev:
						raise RuntimeError(mtypev)
					value = '(new std::map<%s, %s>)' %(mtypek, mtypev)
					#raise SyntaxError(value)
				if self._cpp:
					return 'this->%s = %s' %(node.args[0].attr, self.visit(node.args[2]))
				else:
					return '%s = %s' %(self.visit(node.args[0]), self.visit(node.args[2]))

			else:
				assert node.keywords
				for kw in node.keywords:
					if kw.arg=='mutable': continue
					else:
						vname = kw.arg
						infer_from = kw.value  ## TODO need way to infer types for c++ backend

			if self._function_stack:
				self._known_vars.add( vname )
				if vname in self._vars:
					self._vars.remove( vname )
				V = 'let'
			else:
				V = 'static'

			mutable = False
			for kw in node.keywords:
				if kw.arg=='mutable':
					if kw.value.id.lower()=='true':
						mutable = True

			if len(node.args) == 0:
				if self._cpp:
					return 'auto %s = %s' %(vname, self.visit(infer_from))
				else:
					if mutable:
						return '%s mut %s = %s' %(V, vname, self.visit(infer_from))
					else:
						return '%s %s = %s' %(V, vname, self.visit(infer_from))

			elif len(node.args) == 1:
				return '%s %s			/* declared - rust maybe able to infer the type */' %(V, node.args[0].id)
			elif len(node.args) == 2:
				if self._cpp:
					is_array = False
					if isinstance(node.args[1], ast.Str):
						T = node.args[1].s
						if '__go__array__(' in T:
							is_array = True
							dims = T.count('__go__array__')
							atype = T.split('(')[-1]
							if not self.is_prim_type(atype):
								atype = 'std::shared_ptr<%s>' %atype

							if dims==1:
								T = 'std::vector<%s>' %atype
							else:
								raise RuntimeError(T)  ## TODO

							## note: if a shared_ptr is created on the stack without
							## std::make_shared it will print as `0`
							## and if not initalized with data, will segfault if push_back is called.
							## return '%s  %s' %(T, node.args[0].id)
							return 'auto %s = std::make_shared<%s>()' %(node.args[0].id, T)

						elif T.startswith('[') and ']' in T:
							is_array = True
							x,y = T.split(']')
							alen = x.split('[')[-1].strip()

							self._known_arrays[node.args[0].id] = (y, alen)
							if not len(self._function_stack):
								self._global_arrays[node.args[0].id] = (y, alen)

							if self._memory[-1]=='STACK':
								## note a fixed size C-array non-global `int myarr[N];` will not always
								## allocate all items to zero or null. gcc4.9 bug?
								if alen.isdigit():
									alen = int(alen)
									if y in ('int', 'uint'):
										return '%s %s%s] = {%s}' %(y, node.args[0].id, x, ','.join(['0']*alen))
									elif self.is_prim_type(y):
										return '%s %s%s] = {}' %(y, node.args[0].id, x)  ## TODO test if these are all init to null
									elif y in self._classes:
										return '%s %s%s] = {%s}' %(y, node.args[0].id, x, ','.join([y+'(false)']*alen))
									else:
										raise RuntimeError('TODO let...')

								return '%s %s%s]' %(y, node.args[0].id, x)
							else:
								if not self.is_prim_type(y):
									y = 'std::shared_ptr<%s>' %y
								return 'auto %s = std::make_shared<std::vector<%s>>(%s)' %(node.args[0].id, y, alen)


					else:
						T = node.args[1].id

					if self.is_prim_type(T) or T.endswith('*') or T.endswith('&') or self._memory[-1]=='STACK':
						return '%s  %s' %(T, node.args[0].id)
					else:
						if not self._shared_pointers:
							return '%s*  %s' %(T, node.args[0].id)
						elif self._unique_ptr:
							return 'std::unique_ptr<%s>  %s' %(T, node.args[0].id)
						else:
							return 'std::shared_ptr<%s>  %s' %(T, node.args[0].id)
				else:
					varname = node.args[0].id
					typename = None
					if isinstance(node.args[1], ast.Str):
						typename = node.args[1].s
					else:
						typename = node.args[1].id

					if mutable:
						return '%s mut %s : %s' %(V, varname, typename)
					else:
						return '%s %s : %s' %(V, varname, typename)

			elif len(node.args) == 3:
				if self._cpp:
					if isinstance(node.args[1], ast.Name):
						T = node.args[1].id
					else:
						T = node.args[1].s
					T = T.strip()
					if self.is_prim_type(T) or T.endswith('&') or isinstance(node.args[2], ast.Set):
						if T.endswith('&'):
							## http://stackoverflow.com/questions/1565600/how-come-a-non-const-reference-cannot-bind-to-a-temporary-object
							## TODO is using `const T&` safer?
							#T = 'const '+T  ## this also works
							## strip away `&`
							T = T[:-1]
						varname = node.args[0].id
						if '*' in T:
							varname += '[]' * T.count('*')
							if T=='const char*':
								self._force_cstr = True
						data = self.visit(node.args[2])
						self._force_cstr = False

						return '%s  %s = %s' %(T, varname, data)
					else:
						if self._memory[-1]=='STACK':
							value = self.visit(node.args[2])
							if value == 'nullptr' and not T.endswith('*'):
								value = T + '(false)'  ## special case, construct the class to act like `None`
							return '%s  %s = %s' %(T, node.args[0].id, value)
						elif not self._shared_pointers:
							self._known_pointers[node.args[0].id] = T
							if not len(self._function_stack):
								self._globals[node.args[0].id] = T + '*'
							return '%s*  %s = %s' %(T, node.args[0].id, self.visit(node.args[2]))
						elif self._unique_ptr:
							return 'std::unique_ptr<%s>  %s = %s' %(T, node.args[0].id, self.visit(node.args[2]))
						else:
							return 'std::shared_ptr<%s>  %s = %s' %(T, node.args[0].id, self.visit(node.args[2]))
				else:  ## rust
					if mutable:
						return '%s mut %s : %s = %s' %(V, node.args[0].id, node.args[1].s, self.visit(node.args[2]))
					else:
						return '%s %s : %s = %s' %(V, node.args[0].id, node.args[1].s, self.visit(node.args[2]))
			else:
				raise SyntaxError('TODO __let__ %s' %len(node.args))

		elif fname == '__let__' and isinstance(node.args[0], ast.Attribute):
			if isinstance(node.args[0].value, ast.Name) and node.args[0].value.id=='self':
				if self._cpp:
					if self._memory[-1]=='STACK':
						return 'this.%s = %s' %(node.args[0].attr, self.visit(node.args[-1]))
					else:
						return 'this->%s = %s' %(node.args[0].attr, self.visit(node.args[-1]))
				else:
					return 'self.%s = %s' %(node.args[0].attr, self.visit(node.args[-1]))

		elif fname=='str' and not self._cpp:
			if self._cpp:
				#return 'static_cast<std::ostringstream*>( &(std::ostringstream() << %s) )->str()' %self.visit(node.args[0])
				return 'std::to_string(%s)' %self.visit(node.args[0])  ## only works with number types
			else:
				return '%s.to_string()' %self.visit(node.args[0])

		elif fname == 'range':
			assert len(node.args)
			if self._rust:  ## TODO - some syntax for mutable/immutable range
				fname = '&mut ' + fname  ## default to mutable
				fname += str(len(node.args))
			else:
				assert self._cpp
				fname += str(len(node.args))
				if self._memory[-1]=='STACK':
					fname = '__%s__' %fname

		elif fname == 'len':
			if self._cpp:
				arg = self.visit(node.args[0])
				if arg in self._known_strings:
					if self.usertypes and 'string' in self.usertypes:
						return '%s.%s()' %(arg, self.usertypes['string']['len'])
					else:
						return '%s.size()' %arg
				elif arg.startswith('PyObject_GetAttrString(') and arg.endswith(')'):
					return '(long)PySequence_Length(%s)' %arg
				elif self._memory[-1]=='STACK':
					if arg in self._known_arrays and isinstance(self._known_arrays[arg], tuple):
						return self._known_arrays[arg][1]
					elif arg in self._known_pointers:
						return '%s->size()' %arg
					else:
						return '%s.size()' %arg
				elif self.usertypes and 'vector' in self.usertypes:
					return '%s->%s()' %(arg, self.usertypes['vector']['len'])
				else:
					return '%s->size()' %arg
			else:
				return '%s.borrow().len()' %self.visit(node.args[0])

		elif fname == 'float':
			if self._cpp or self._rust:
				return '__float__(%s)'%self.visit(node.args[0])
			else:
				raise SyntaxError("TODO float builtin")

		elif fname == '__open__':
			if self._cpp:
				if len(node.args) == 2:
					return '__open__(%s, %s)' % (self.visit(node.args[0]), self.visit(node.args[1]))
				else:
					return '__open__(%s, std::string("rb"))' % self.visit(node.args[0])

			else:
				return 'File::open_mode( &Path::new(%s.to_string()), Open, Read )' %self.visit(node.args[0])

		elif fname == '__arg_array__':
			assert len(node.args)==1
			T = self.parse_go_style_arg(node.args[0])
			if self._rust:
				if self.is_prim_type(T):
					#return '&mut Vec<%s>' %T
					return 'Rc<RefCell< Vec<%s> >>' %T
				else:
					#return '&mut Vec<&mut %s>' %T  ## old ref style
					return 'Rc<RefCell< Vec<Rc<RefCell<%s>>> >>' %T

			elif self._cpp:
				if self.is_prim_type(T):
					if not self._shared_pointers:
						return 'std::vector<%s>*' %T
					elif self._unique_ptr:
						return 'std::unique_ptr<std::vector<%s>>' %T
					else:
						return 'std::shared_ptr<std::vector<%s>>' %T
				else:
					if not self._shared_pointers:
						return 'std::vector<%s*>*' %T
					elif self._unique_ptr:
						return 'std::unique_ptr<std::vector< std::unique_ptr<%s> >>' %T
					else:
						return 'std::shared_ptr<std::vector< std::shared_ptr<%s> >>' %T
			else:
				raise RuntimeError('TODO generic arg array')

		elif fname == '__arg_map__':
			parse = node.args[0].s
			assert parse.startswith('map[')
			key_type = parse.split('[')[-1].split(']')[0]
			value_type = parse.split(']')[-1]
			if key_type=='string': key_type = 'std::string'
			if value_type=='string': value_type = 'std::string'
			return 'std::shared_ptr<std::map<%s, %s>>' %(key_type, value_type)


		if node.args:
			#args = [self.visit(e) for e in node.args]
			#args = ', '.join([e for e in args if e])
			args = []
			for e in node.args:
				if self._rust and isinstance(e, ast.Name) and e.id in self._known_arrays:
					args.append( e.id+'.clone()' )  ## automatically clone known array Rc box
				elif isinstance(e, ast.Call) and isinstance(e.func, ast.Attribute) and isinstance(e.func.value, ast.Name) and e.func.value.id in self._known_arrays and e.func.attr=='clone':
					if self._rust:
						args.append( e.func.value.id+'.clone()' )  	## user called clone()
					else:
						args.append( e.func.value.id )  			## skip clone() for c++ backend
				else:
					args.append( self.visit(e) )

			args = ', '.join(args)

		else:
			args = ''

		haskwargs = False
		if node.keywords:
			haskwargs = True
			if args: args += ','

			if self._rust:
				raise RuntimeError( self.format_error('TODO calling a function named params for rust backend') )
			elif self._cpp:
				## In the future we can easily optimize this away on plain functions,
				## because it is simple to lookup the function here, and see the order
				## of the named params, and then reorder the args here to bypass
				## creating a new `_KwArgs_` instance.
				args += '(new _KwArgs_())'
				for kw in node.keywords:
					args += '->%s(%s)' %(kw.arg,self.visit(kw.value))
			else:
				raise RuntimeError('TODO named params for some backend')

		if node.starargs:
			if args: args += ','
			if self._cpp:
				args += '(*%s)' %self.visit(node.starargs)
			else:
				args += '*%s...' %self.visit(node.starargs)


		if hasattr(node, 'is_new_class_instance') and self._rust:
			return 'Rc::new(RefCell::new( %s::new(%s) ))' % (fname, args)

		elif self._cpp and fname in self._classes:
			## create class instance - new clean style - TODO deprecate all the old _ref_hacks ##
			prefix = ''
			if self.usertypes and 'shared' in self.usertypes:
				prefix = self.usertypes['shared']['template'] % fname

			elif self._memory[-1]=='STACK':
				if self._classes[fname]._requires_init:
					return '%s().__init__(%s)' %(fname,args)
				else:
					return '%s()' %fname

			elif self._shared_pointers:
				prefix = 'std::shared_ptr<%s>' %fname
			elif self._unique_ptr:
				prefix = 'std::unique_ptr<%s>' %fname

			#########################################
			if self._classes[fname]._requires_init:
				if not isinstance(self._stack[-2], ast.Assign) and self._memory[-1]=='HEAP':
					if isinstance(self._stack[-2], ast.ListComp):
						return '%s((new %s())->__init__(%s))' %(prefix,fname,args)

					#elif self._assign_node:
					#	argname = '%s_%s' %(fname, int(id(node)))
					#	pre = 'auto %s = %s(new %s()); %s->__init__(%s);' %(argname,prefix,fname, argname,args)
					#	if not self._assign_pre:
					#		self._assign_pre.append(pre)
					#	elif pre not in self._assign_pre:
					#		self._assign_pre.append(pre)
					#	return argname
					#elif isinstance(self._stack[-2], ast.Call):
					#	print 'WARNING: object created without assignment to a variable'
					#	print fname
					#	print args
					#	return '%s((new %s())->__init__(%s))' %(prefix,fname,args)
					#elif isinstance(self._stack[-2], ast.Expr):
					#	argname = '%s_%s' %(fname, int(id(node)))
					#	pre = 'auto %s = %s(new %s()); %s->__init__(%s);' %(argname,prefix,fname, argname,args)
					#	return pre
					#elif isinstance(self._stack[-2], ast.Return):
					#	pass
					#else:
					#	raise SyntaxError(self.format_error('heap mode requires objects are assigned to variables on initialization: %s' %self._stack[-2]))

					#return '%s((new %s())->__init__(%s))' %(prefix,fname,args)

					## wrap in lambda ##
					return '[&](){auto _ = %s(new %s()); _->__init__(%s); return _;}()' %(prefix,fname,args)


				else:
					#return '%s((new %s())->__init__(%s))' %(prefix,fname,args)
					return '[&](){auto _ = %s(new %s()); _->__init__(%s); return _;}()' %(prefix,fname,args)

			else:
				return '%s(new %s())' %(prefix,fname)
		else:
			return '%s(%s)' % (fname, args)
```
BinOp
------
Extra syntax is supported by [typedpython.md](typedpython.md) using `<<` and special names as a way of encoding syntax that 
regular Python has no support for.

```python
	def visit_BinOp(self, node):
		left = self.visit(node.left)
		op = self.visit(node.op)
		try:
			right = self.visit(node.right)
		except GenerateListComp as err:
			if isinstance(node.left, ast.Call) and isinstance(node.left.func, ast.Name) and node.left.func.id=='__go__array__':
				node.right._comp_type = node.left.args[0].id
				node.right._comp_dims = 1
				raise err
			elif isinstance(node.left, ast.BinOp) and isinstance(node.left.left, ast.Name) and node.left.left.id=='__go__array__':
				node.right._comp_type = node.left.right.args[0].id
				node.right._comp_dims = 2
				raise err
			else:
				print node.left
				print node.right
				raise SyntaxError(self.format_error(err))

		if op == '>>' and left == '__new__':
			if self._cpp:
				if isinstance(node.right, ast.Call) and isinstance(node.right.func, ast.Name):
					classname = node.right.func.id
					if classname in self._classes:
						if node.right.args:
							args = ','.join([self.visit(arg) for arg in node.right.args])
							return '(new %s)->__init__(%s)' %(classname, args)
						else:
							return '(new %s)->__init__()' %classname
					else:
						if node.right.args:
							args = ','.join([self.visit(arg) for arg in node.right.args])
							return '(new %s(%s))' %(classname, args)
						else:
							return '(new %s)' %classname

				else:
					#raise SyntaxError(self.format_error(self.visit(node.right)))
					return '(new %s)' %self.visit(node.right)

			else:
				return ' new %s' %right

		elif op == '<<':
			go_hacks = ('__go__array__', '__go__arrayfixed__', '__go__map__', '__go__func__')

			if isinstance(node.left, ast.Attribute) and node.left.attr=='__doubledot__':  ## this style is deprecated
				if isinstance(node.right, ast.Call):
					return self.gen_cpy_call(self.visit(node.left.value), node.right)
					r = [
						'PyObject_Call(',
						'	PyObject_GetAttrString(%s,"%s"),' %(self.visit(node.left.value), node.right.func.id),
						'	Py_BuildValue("()"),',
						'	NULL',
						')'
					]
					return '\n'.join(r)

				elif isinstance(node.right, ast.Name):
					return 'PyObject_GetAttrString(%s,"%s")' %(self.visit(node.left.value), node.right.id)
				elif isinstance(node.right, ast.Attribute) and node.right.attr=='__doubledot__':
					return 'PyObject_GetAttrString(%s,"%s")' %(self.visit(node.left.value), self.visit(node.right.value))
				else:
					raise SyntaxError(self.format_error('bad use of ->'))

			elif left in ('__go__receive__', '__go__send__'):
				self._has_channels = True
				if self._cpp:
					## cpp-channel API
					return '%s.recv()' %right
				elif self._rust:
					return '%s.recv().unwrap()' %right

			elif isinstance(node.left, ast.Call) and isinstance(node.left.func, ast.Name) and node.left.func.id in go_hacks:
				if node.left.func.id == '__go__func__':
					raise SyntaxError('TODO - go.func')
				elif node.left.func.id == '__go__map__':
					key_type = self.visit(node.left.args[0])
					value_type = self.visit(node.left.args[1])
					value_vec  = None
					if isinstance(node.left.args[0], ast.Str):
						key_type = node.left.args[0].s
						if key_type.startswith('['):
							raise SyntaxError(self.format_error('dictionary keys can not be a vector type'))

					if isinstance(node.left.args[1], ast.Str):
						value_type = node.left.args[1].s
						if value_type.startswith('[]'):
							value_vec = value_type.split(']')[-1]
							value_type = 'std::vector<%s>*' % value_vec
					elif isinstance(node.left.args[1], ast.Tuple):
						tupletype = []
						for telt in node.left.args[1].elts:
							if isinstance(telt, ast.Str):
								v = telt.s
								if v.startswith('"') and v.endswith('"'):
									v = v[1:-1]
							else:
								v = self.visit(telt)
							if v.startswith('[]'):
								t  = v.split(']')[-1]
								if self._memory[-1]=='STACK':
									v = 'std::vector<%s>' %t
								else:
									v = 'std::vector<%s>*' %t

							tupletype.append(v)
						if self._memory[-1]=='STACK':
							value_type = 'std::tuple<%s>' %','.join(tupletype)
						else:
							value_type = 'std::shared_ptr<std::tuple<%s>>' %','.join(tupletype)
						#raise RuntimeError(value_type)

					#########################
					if key_type == 'string':
						key_type = 'std::string'

					if isinstance(node.right, ast.Dict):
						items = []
						for i in range( len(node.right.keys) ):
							k = self.visit(node.right.keys[i])
							v = self.visit(node.right.values[i])
							if v.startswith('[') and v.endswith(']'):
								v = ('new std::vector<%s>{'%value_vec) + v[1:-1] + '}'
							elif isinstance(node.right.values[i], ast.Tuple): #elif v.startswith('{') and v.endswith('}'):
								targs = []
								tuptargs = []
								for ti,te in enumerate(node.right.values[i].elts):
									tt = tupletype[ti]
									tv = self.visit(te)
									if tv.startswith('[') and tv.endswith(']'):
										assert tt.startswith('std::vector')
										if tt.endswith('*'):
											tv = '(new %s{%s})' %(tt[:-1], tv[1:-1])
										else:
											tv = '%s{%s}' %(tt, tv[1:-1])
									targs.append(tv)

								if self._memory[-1]=='STACK':
									v = 'std::make_tuple(%s)' %','.join(targs)
								else:
									v = 'std::make_shared<std::tuple<%s>>(std::make_tuple(%s))' %(','.join(tupletype), ','.join(targs))

							items.append('{%s, %s}' %(k,v))

						right = '{%s}' %'\n,'.join(items)

					if self._memory[-1]=='STACK':
						return 'std::map<%s, %s>%s' %(key_type, value_type, right)
					else:
						map_type = 'std::map<%s,%s>' %(key_type, value_type)
						return 'std::shared_ptr<%s>(new %s%s)' %(map_type, map_type, right)
				else:
					if isinstance(node.right, ast.Name):
						raise SyntaxError(node.right.id)

					right = []
					for elt in node.right.elts:
						if isinstance(elt, ast.Num) and self._rust:
							right.append( str(elt.n)+'i64' )
						else:
							right.append( self.visit(elt) )

					rargs = right[:]

					if self._rust:
						right = '(%s)' %','.join(right)
					elif self._cpp:
						right = '{%s}' %','.join(right)

					if node.left.func.id == '__go__array__':
						T = self.visit(node.left.args[0])
						if self._cpp:
							return ('std::vector<%s>'%T, rargs)   ## note special case, returns a tuple.

						elif self._rust:
							#return '&mut vec!%s' %right
							return 'Rc::new(RefCell::new(vec!%s))' %right

						else:
							raise RuntimeError('invalid backend')

					elif node.left.func.id == '__go__arrayfixed__':
						asize = self.visit(node.left.args[0])
						atype = self.visit(node.left.args[1])
						isprim = self.is_prim_type(atype)
						if self._cpp:
							return ('std::vector<%s>'%atype, asize, rargs) ## note special case, returns a tuple.
						elif self._rust:
							#return '&vec!%s' %right
							return 'Rc::new(RefCell::new(vec!%s))' %right
						else:
							raise RuntimeError('invalid backend')


			elif isinstance(node.left, ast.Name) and node.left.id=='__go__array__':
				if self._rust:
					raise RuntimeError('TODO array pointer')
					return '&mut Vec<%s>' %self.visit(node.right)  ## TODO - test this
				elif self._cpp:
					if not isinstance(node.right,ast.Call):
						raise RuntimeError('TODO mdarrays')

					mdtype = self.visit(node.right.args[0])
					if not self._shared_pointers:
						return 'std::vector<std::vector<%s>*>*'%mdtype
					elif self._unique_ptr:
						return 'std::unique_ptr<std::vector< std::unique_ptr<std::vector<%s>> >>'%mdtype
					else:
						return 'std::shared_ptr<std::vector< std::shared_ptr<std::vector<%s>> >>'%mdtype
				else:
					raise RuntimeError('invalid backend')

			elif isinstance(node.right, ast.Name) and node.right.id=='__as__':
				if self._cpp:
					return self.visit(node.left)
				else:
					return '%s as ' %self.visit(node.left)

			elif isinstance(node.left, ast.BinOp) and isinstance(node.left.right, ast.Name) and node.left.right.id=='__as__':
				#cast_to = right
				cast_to = self.visit(node.right)
				if isinstance(node.right, ast.Str):
					cast_to = node.right.s

				if self._rust:
					return '%s %s' %(self.visit(node.left), cast_to)
				else:
					ptr = self.visit(node.left.left)
					if cast_to in 'pystring pystr pyint pyi32 pylong pyi64 pyfloat pydouble pyf32 pyf64 pybool'.split():
						if cast_to=='pystring' or cast_to=='pystr':
							return 'PyString_FromString(%s.c_str())' %ptr
						elif cast_to in 'pyint pyi32 pylong pyi64'.split():
							return 'PyInt_FromLong(%s)' %ptr
						elif cast_to in 'pyfloat pyf32'.split():
							return 'PyFloat_FromDouble(%s)' %ptr
						else:
							raise RuntimeError('TODO as type: %s'%cast_to)

					elif self.is_prim_type(cast_to):
						if type(ptr) is tuple: ## this is probably a bug
							ptr = ptr[0]
						if ptr.startswith('PyObject_GetAttrString') or ptr.startswith('PyObject_Call'):
							if cast_to == 'int':
								return 'static_cast<%s>(PyInt_AS_LONG(%s))' %(cast_to, ptr)
							elif cast_to in ('float','f32'):
								return 'static_cast<%s>(PyFloat_AsDouble(%s))' %(cast_to, ptr)
							elif cast_to in ('double','f64'):
								return 'PyFloat_AsDouble(%s)' %ptr
							elif cast_to == 'string':
								return 'std::string(PyString_AS_STRING(%s))' %ptr
							elif cast_to == 'bool':
								return '(%s==Py_True)' %ptr
							else:
								raise RuntimeError('TODO other cast to types for cpython')
						else:
							return 'static_cast<%s>(%s)' %(cast_to, self.visit(node.left.left))
					elif self._memory[-1]=='STACK':
						cast_from = self.visit(node.left.left)
						if isinstance(node.left.left, ast.Str):  ## allow quoted cast to with `as`
							cast_from = node.left.left.s

						if cast_from in self._known_refs:
							raise RuntimeError(cast_from)
						if self._function_stack:
							fnode = self._function_stack[-1]
							if fnode.return_type==cast_to:  ## TODO check is node above is ast.Return
								return 'static_cast<%s>(%s)' %(cast_to, cast_from)

						return 'static_cast<%s>(%s)' %(cast_to, self.visit(node.left.left))

					elif self._polymorphic:
						return 'std::dynamic_pointer_cast<%s>(%s)' %(cast_to, self.visit(node.left.left))
					else:
						return 'std::static_pointer_cast<%s>(%s)' %(cast_to, self.visit(node.left.left))

			elif isinstance(node.left, ast.Call) and isinstance(node.left.func, ast.Name) and node.left.func.id=='inline':
				return '%s%s' %(node.left.args[0].s, right)
			else:
				## TODO this is hackish
				if type(left) is tuple:
					raise RuntimeError(left)
				atype = left.split('<')[-1].split('>')[0]
				if isinstance(node.right, ast.Tuple):
					r = ['new std::vector<%s> %s' %(atype, self.visit(elt)) for elt in node.right.elts]
					right = '{%s}' %','.join(r)
				return (left, right)  ## special case for new arrays


		if left in self._typed_vars and self._typed_vars[left] == 'numpy.float32':  ## deprecated
			left += '[_id_]'
		if right in self._typed_vars and self._typed_vars[right] == 'numpy.float32':  ## deprecated
			right += '[_id_]'

		#if op=='<<':
		#	#raise SyntaxError(type(node.left))
		#	raise SyntaxError(left+right)
		if left in self._known_instances:
			left = '*'+left

		return '(%s %s %s)' % (left, op, right)

	def visit_ListComp(self, node):
		#raise RuntimeError('list comps are only generated from the parent node')
		raise GenerateListComp(node)

```
Return
-------

TODO remove GenerateTypeAssert, go leftover.
TODO tuple return for c++

```python

	#def visit_Num(self, node):
	#	return node.n

	def visit_Raise(self, node):
		if self._rust:
			return 'panic!("%s");'  % self.visit(node.type)
		elif self._cpp:
			if isinstance(node.type, ast.Call) and node.type.keywords:
				self._has_rebuild = True
				args = []
				for k in node.type.keywords:
					args.append( self.visit(k.value) + ' /*%s*/'%k.arg )
				return '__request_rebuild( %s );' %','.join(args)
			else:
				T = self.visit(node.type)
				return 'throw %s;' % T
		else:
			raise RuntimeError('unknown backend')


	def visit_Return(self, node):
		assert not self._cpp  ## cpptranslator.md overrides this
		if isinstance(node.value, ast.Tuple):
			return 'return %s;' % ', '.join(map(self.visit, node.value.elts))
		elif node.value:
			v = self.visit(node.value)
			return 'return %s;' % v
		return 'return;'
```

Lambda Functions
----------------
rust lambda
c++11 lambda

Lambda functions have a different type syntax from normal functions and methods.
Regular functions and methods type their arguments with Python3 annotation syntax,
`def f( a:int ):`

Lambda functions type their arguments using the keyword default value,
`lambda a=int:`


```python

	def visit_Lambda(self, node):
		args = [self.visit(a) for a in node.args.args]
		if args and args[0]=='__INLINE_FUNCTION__':
			raise SyntaxError('TODO inline lambda/function hack')
		elif self._cpp:
			assert len(node.args.args)==len(node.args.defaults)
			args = []
			for i,a in enumerate(node.args.args):
				T = node.args.defaults[i].s
				if not self.is_prim_type(T): T = 'std::shared_ptr<%s>' %T
				s = '%s  %s' %(T, self.visit(a))
				args.append( s )
			## TODO support multiline lambda, and return the last line
			return '[&](%s){ return %s; }' %(','.join(args), self.visit(node.body))
		else:
			return '|%s| %s ' %(','.join(args), self.visit(node.body))

```

Function/Method
---------------
note: functions defined in `with extern(abi="C"):` are `declare_only` their bodies are skipped.
operator overloading is implemented here for c++
TODO clean up go stuff.

```python

	def _visit_function(self, node):
		func_pre = []
		out = []

		is_declare = hasattr(node, 'declare_only') and node.declare_only  ## see pythonjs.py visit_With
		is_closure = False
		node.is_abstract = False
		node.func_header = None
		node.func_args = []
		node.func_body = []

		if not hasattr(node, '_return_nodes'):
			node._return_nodes = set()

		if self._function_stack[0] is node:
			self._global_functions[node.name] = node
			self._vars = set()
			self._known_vars = set()
			self._known_instances = dict()
			self._known_arrays    = dict()
			self._known_arrays.update( self._global_arrays )
			self._known_strings   = set()
			self._known_pyobjects = dict()
			self._known_refs      = dict()
			self._known_refs.update( self._global_refs )
			self._known_pointers  = dict()
			self._known_tuples    = dict()
			self._known_tuples.update( self._global_tuples )

		elif len(self._function_stack) > 1:
			## do not clear self._known_* inside of closures ##
			is_closure = True

		comments = []
		for b in node.body:
			if isinstance(b, ast.Expr) and isinstance(b.value, ast.Str):
				comments.append( b.value.s )
		if comments:
			out.append('/**')
			for line in comments[0].splitlines():
				out.append(' * '+line)
			out.append(' */')


		args_typedefs = {}
		chan_args_typedefs = {}
		generics = set()
		args_generics = dict()
		args_super_classes = {}
		func_pointers = set()
		arrays = dict()
		operator = None
		if node.name in ('__getitem__', '__setitem__'):  ## TODO support setitem, return a proxy with `=` overloaded?
			operator = '[]'
		elif node.name == '__unwrap__':
			operator = '->'
		elif node.name == '__copy__':
			operator = '='
		elif node.name == '__call__':
			operator = '()'
		elif node.name == '__add__':
			operator = '+'
		elif node.name == '__iadd__':
			operator = '+='
		elif node.name == '__sub__':
			operator = '-'
		elif node.name == '__isub__':
			operator = '-='
		elif node.name == '__mul__':
			operator = '*'
		elif node.name == '__imul__':
			operator = '*='
		elif node.name == '__div__':
			operator = '/'
		elif node.name == '__idiv__':
			operator = '/='


		options = {'getter':False, 'setter':False, 'returns':None, 'returns_self':False, 'generic_base_class':None, 'classmethod':False}

		virtualoverride = False
		extern = False

		for decor in node.decorator_list:
			self._visit_decorator(
				decor,
				node=node,
				options=options,
				args_typedefs=args_typedefs,
				chan_args_typedefs=chan_args_typedefs,
				generics=generics,
				args_generics=args_generics,
				func_pointers=func_pointers,
				arrays = arrays,
				args_super_classes=args_super_classes,
			)

			if isinstance(decor, ast.Call) and isinstance(decor.func, ast.Name) and decor.func.id == 'expression':
				assert len(decor.args)==1
				node.name = self.visit(decor.args[0])
			elif isinstance(decor, ast.Name) and decor.id=='jvm':
				raise RuntimeError('TODO @jvm for function')
			elif isinstance(decor, ast.Name) and decor.id=='virtualoverride':
				virtualoverride = True
			elif isinstance(decor, ast.Name) and decor.id=='extern':
				extern = True
			elif isinstance(decor, ast.Call) and isinstance(decor.func, ast.Name) and decor.func.id == 'macro':
				#out.append(decor.args[0].s)
				if self._cpp:
					self._cpp_class_header.append(decor.args[0].s)
			elif isinstance(decor, ast.Name) and decor.id=='abstractmethod':
				## TODO: virtual function c++
				assert self._cpp
				out.append('/* abstractmethod: %s */' %node.name)
				node.is_abstract = True
			elif isinstance(decor, ast.Attribute) and decor.attr=='safe':  ## GCC STM
				func_pre.append('__attribute__((transaction_safe))')
			elif isinstance(decor, ast.Attribute) and decor.attr=='pure':  ## GCC STM
				func_pre.append('__attribute__((transaction_pure))')

		for name in arrays:
			arrtype = args_typedefs[name]#arrays[ name ]
			if '[' in arrtype:
				# C-style
				if arrtype.endswith(']'):
					raise RuntimeError(arrtype)
				else:
					raise RuntimeError(arrtype+'!!!')

			self._known_arrays[ name ] = arrtype

		for name in args_typedefs:
			if args_typedefs[name]=='string':
				self._known_strings.add(name)
			elif args_typedefs[name].endswith('&'):
				self._known_refs[name] = args_typedefs[name]
			elif args_typedefs[name].endswith('*'):
				self._known_instances[name]= args_typedefs[name]
				self._known_pointers[name] = args_typedefs[name]


		node.returns_self = returns_self = options['returns_self']
		return_type = options['returns']
		generic_base_class = options['generic_base_class']
		#if self._cpp and return_type and return_type.startswith('tuple('):
		#	raise RuntimeError(return_type)

		if returns_self and self._cpp:
			return_type = self._class_stack[-1].name

		## picked up from first pass
		if hasattr(node, 'return_type') and node.return_type and not return_type:
			return_type = node.return_type

		if not len(node._return_nodes) and not return_type:
			return_type = 'void'
		## used after first pass
		node.func_returns = return_type

		is_delete = node.name == '__del__'
		is_init = node.name == '__init__'
		is_main = node.name == 'main'
		if is_main and self._cpp:  ## g++ requires main returns an integer
			return_type = 'int'
		elif is_init and self._cpp:
			if self._memory[-1]=='STACK':
				return_type = '%s' %self._class_stack[-1].name
			else:
				return_type = '%s*' %self._class_stack[-1].name

		elif return_type and not self.is_prim_type(return_type):
			if self._cpp:
				if 'returns_array' in options and options['returns_array']:
					pass
				else:
					if return_type.endswith('&') or return_type.endswith('*') or return_type.endswith('>') or self._memory[-1]=='STACK':
						pass
					elif self.usertypes and 'shared' in self.usertypes:
						return_type = self.usertypes['shared']['template'] % return_type
					elif not self._shared_pointers:
						return_type = '%s*' %return_type
						#return_type = '%s' %return_type  ## return copy of object

					elif self._unique_ptr:
						return_type = 'std::unique_ptr<%s>' %return_type
					else:
						return_type = 'std::shared_ptr<%s>' %return_type
			else:
				if return_type == 'self':  ## Rust 1.2 can not return keyword `self`
					return_type = self._class_stack[-1].name

				return_type = 'Rc<RefCell<%s>>' %return_type

		if return_type == 'string':
			if self._cpp:
				if self.usertypes and 'string' in self.usertypes:
					return_type = self.usertypes['string']['type']
				else:
					return_type = 'std::string'
			elif self._rust:
				return_type = 'String'

		node.return_type = return_type
		node._arg_names = args_names = []
		args = []
		oargs = []
		offset = len(node.args.args) - len(node.args.defaults)
		varargs = False
		varargs_name = None
		is_method = False
		args_gens_indices = []
		closures = []
		alt_versions = []  ## list of ([args], [body])
		if args_super_classes:
			alt_versions.append( ([],[]) )

		has_stdmove = False
		stdmoveargs  =[]

		for i, arg in enumerate(node.args.args):
			arg_name = arg.id
			dindex = i - offset
			stdmove = False

			if arg_name not in args_typedefs.keys()+chan_args_typedefs.keys():
				if arg_name=='self':
					assert i==0
					is_method = True
					continue
				elif dindex >= 0 and node.args.defaults and self.visit(node.args.defaults[dindex]).startswith('move('):
					stdmove = True
					has_stdmove = True
					#fails in c++11#a = 'auto %s = std::%s' %(arg_name, self.visit(node.args.defaults[dindex]))
					a = '%s = std::%s' %(arg_name, self.visit(node.args.defaults[dindex]))
				elif self._cpp:
					args_typedefs[arg_name]='auto'  ## c++14
				else:
					err =[
						'- - - - - - - - - - - - - - - - - -',
						'error in function: %s' %node.name,
						'missing typedef: %s' %arg.id,
						'- - - - - - - - - - - - - - - - - -',
					]
					raise SyntaxError( self.format_error('\n'.join(err)) )

			if arg_name in args_typedefs:
				arg_type = args_typedefs[arg_name]
				if self._cpp:
					if args_super_classes:
						altargs, altbody = alt_versions[0]
						if arg_name in args_super_classes:
							if is_method:  ## inlined wrapper methods
								altargs.append(
									'std::shared_ptr<%s> %s' %(args_super_classes[arg_name][0], arg_name)
								)
								altbody.append('std::static_pointer_cast<%s>(%s),' %(arg_type.split('<')[-1].split('>')[0], arg_name))
							else:  ## fully regenerated function
								altargs.append(
									'std::shared_ptr<%s> __%s' %(args_super_classes[arg_name][0], arg_name)
								)
								altbody.append('auto %s = std::static_pointer_cast<%s>(__%s);' %(arg_name, arg_type.split('<')[-1].split('>')[0], arg_name))
						else:
							altargs.append('%s %s' %(arg_type, arg_name))
							altbody.append(arg_name+',')

					## TODO better way to guess if an untyped param is a pointer
					#if arg_type=='auto':
					#	self._known_instances[arg_name]='auto'

					## rule above assumes anything marked with `auto` should not used __shared__ wrapper and directly use `a->b`
					if arg_type in ('string', 'string*', 'string&', 'string&&'):
						if self.usertypes and 'string' in self.usertypes:
							if arg_type.endswith('&&'):
								arg_type = self.usertypes['string']['type'] + '&&'
							elif arg_type.endswith('&'):
								arg_type = self.usertypes['string']['type'] + '&'
							elif arg_type.endswith('*'):
								arg_type = self.usertypes['string']['type'] + '*'
							else:
								arg_type = self.usertypes['string']['type']
						else:
							## standard string type in c++ std::string
							arg_type = arg_type.replace('string', 'std::string')

					if 'std::' in arg_type and arg_type.endswith('>') and ('shared_ptr' in arg_type or 'unique_ptr' in arg_type):
						if arg_name in self._known_instances:
							print 'nested lambda?'
						self._known_instances[arg_name] = arg_type


					if arg_name in func_pointers:
						## note C has funky function pointer syntax, where the arg name is in the middle
						## of the type, the arg name gets put there when parsing above.
						a = arg_type
					elif arg_type.endswith(']'):
						atype,alen = arg_type.split('[')
						self._known_arrays[arg_name] = (atype, alen[:-1])
						a = '%s %s[%s' %(atype, arg_name, alen)
					else:
						a = '%s %s' %(arg_type, arg_name)

					if generics and arg_name in args_generics.keys():
						args_gens_indices.append(i)

					if arg_type.endswith('*'):
						self._known_pointers[arg_name] = arg_type  ## TODO, strip star?

				elif self._rust:  ## standard string type in rust `String`
					if arg_type == 'string': arg_type = 'String'  
					if '|' in arg_type:
						x,y,z = arg_type.split('|')
						arg_type = '__functype__%s'%len(closures)
						closures.append('%s:Fn(%s) %s' %('__functype__%s'%len(closures), y,z))

					a = '%s:%s' %(arg_name, arg_type)


			elif arg_name in chan_args_typedefs:
				arg_type = chan_args_typedefs[arg_name]
				is_sender = False
				is_recver = False
				if arg_type.startswith('Sender<'):
					arg_type = arg_type[ len('Sender<') : -1 ]
					is_sender = True
				elif arg_type.startswith('Receiver<'):
					arg_type = arg_type[ len('Receiver<') : -1 ]
					is_recver = True


				if self._cpp:
					## cpp-channel API is both input and output like Go.
					if self.is_prim_type(arg_type):
						a = 'cpp::channel<%s>  %s' %(arg_type, arg_name)
					else:
						a = 'cpp::channel<%s*>  %s' %(arg_type, arg_name)
				elif self._rust:
					## allow go-style `chan` keyword with Rust backend,
					## defaults to Sender<T>, because its assumed that sending channels
					## will be the ones most often passed around.
					## the user can use rust style typing `def f(x:X<t>):` in function defs
					## to type a function argument as `Reveiver<t>`

					if is_recver:
						a = '%s : Receiver<%s>' %(arg_name, arg_type)
					else:
						a = '%s : Sender<%s>' %(arg_name, arg_type)

				else:
					raise RuntimeError('TODO chan for backend')


			if dindex >= 0 and node.args.defaults and not stdmove:
				default_value = self.visit( node.args.defaults[dindex] )
				## because _KwArgs_ class has argument types that refer to user defined
				## classes (that are forward declared), only pointers or std::shared_ptr
				## can be used as their type, otherwise g++ will fail with this error:
				## error: ‘MyClass’ has incomplete type
				if not self.is_prim_type(arg_type):
					if not arg_type.endswith('*') and not arg_type.endswith('&') and not arg_type.endswith('>') and not arg_type.startswith('std::'):
						assert self._memory[-1]=='STACK'
						arg_type += '*'
						args_typedefs[arg_name] = arg_type

				self._kwargs_type_[ arg_name ] = arg_type
				oargs.append( (arg_name, default_value) )
			elif stdmove:
				stdmoveargs.append(a)
			else:
				args.append( a )
				node._arg_names.append( arg_name )

		##############################################
		if args_super_classes:
			if is_method:
				altargs, altbody = alt_versions[0]
				altbody.insert(0,'{ return %s('%node.name)
				if altbody[-1][-1]==',':
					altbody[-1] = altbody[-1][:-1]
				altbody[-1] += ');}'
			else:
				## there is a bug in gcc4.9 where a static_pointer_cast of a shared pointer
				## can cause a segfault in the generated wrapper functions.
				## note: the wrappers work with methods, see above.
				altbody.insert(0,'{')

				for b in node.body:
					altbody.append(self.indent()+self.visit(b))
				altbody.append('}')

		if oargs:
			node._arg_names.append( '__kwargs' )
			if self._cpp:
				args.append( '_KwArgs_*  __kwargs')
			elif self._rust:
				raise SyntaxError( self.format_error('TODO named keyword parameters') )
			else:
				raise SyntaxError('TODO kwargs for some backend')

		starargs = None
		if node.args.vararg:
			if self._cpp: raise RuntimeError('TODO *args for c++')
			starargs = node.args.vararg
			assert starargs in args_typedefs
			args.append( '__vargs__ : Vec<%s>' %args_typedefs[starargs])
			node._arg_names.append( starargs )

		#prefix = '__attribute__((visibility("default"))) '  ## this fails to force functions to be available to ctypes in CPython.
		prefix = ''
		if func_pre:
			prefix +=  ' '.join(func_pre) + ' '

		if options['classmethod']:
			prefix += 'static '
			if args and 'object ' in args[0]:  ## classmethods output from java2python produces `cls:object`
				args = args[1:]
		if extern:
			prefix += 'extern '
			is_declare = True

		if virtualoverride:
			is_method = True

		fname = node.name
		if operator:
			fname = 'operator ' + operator

		#if self._cpp:
		#	for arg in args:
		#		if arg.startswith('string '):
		#			raise RuntimeError(args)  ## should never happen

		node._args_signature = ','.join(args)
		####
		if is_method:
			assert self._class_stack
			method = '(self *%s)  ' %self._class_stack[-1].name
		else:
			method = ''

		clonames = ','.join(['__functype__%s'%ci for ci in range(len(closures))])


		if is_closure:
			if self._rust and closures:
				raise SyntaxError('TODO: rust syntax for a lambda function that takes function pointers as arguments')

			if return_type:
				if self._rust:
					out.append( 'let %s = |%s| -> %s {\n' % (node.name, ', '.join(args), return_type) )
				elif self._cpp:
					if has_stdmove:
						out.append( 'auto %s = [%s](%s) -> %s {\n' % (node.name, ', '.join(stdmoveargs), ', '.join(args), return_type) )
					else:
						out.append( 'auto %s = [&](%s) -> %s {\n' % (node.name, ', '.join(args), return_type) )
			else:
				if self._rust:
					out.append( 'let %s = |%s| {\n' % (node.name, ', '.join(args)) )
				elif self._cpp:
					if has_stdmove:
						out.append( 'auto %s = [%s](%s) {\n' % (node.name,', '.join(stdmoveargs), ', '.join(args)) )
					else:
						out.append( 'auto %s = [&](%s) {\n' % (node.name, ', '.join(args)) )

		else:
			if return_type:
				if self._cpp: ## c++ ##
					if is_method or options['classmethod']:
						classname = self._class_stack[-1].name
						sig = '%s %s::%s(%s)' % (return_type, classname, fname, ', '.join(args))

						if self._noexcept:
							out.append( self.indent() + '%s noexcept {\n' % sig )
							sig = '%s%s %s(%s)' % (prefix,return_type, fname, ', '.join(args))
							self._cpp_class_header.append(sig + ' noexcept;')
						else:
							out.append( self.indent() + '%s {\n' % sig )
							sig = '%s%s %s(%s)' % (prefix,return_type, fname, ', '.join(args))

							if virtualoverride:
								sig = 'virtual %s override' %sig

							self._cpp_class_header.append(sig + ';')

							if alt_versions:
								assert args_super_classes
								for av in alt_versions:
									altargs, altbody = av
									asig = 'inline %s %s(%s)' % (return_type, fname, ', '.join(altargs))
									self._cpp_class_header.append( asig + '\n'.join(altbody))

							if node.args.defaults:
								if len(args)==1:  ## all args have defaults, generate plain version with no defaults ##
									okwargs = ['(new _KwArgs_)']
									args = []
									for oarg in oargs:
										oname = oarg[0]
										T = args_typedefs[oname]
										if T=='string':
											T = 'std::string'
										args.append('%s %s' %(T, oname))
										okwargs.append('%s(%s)' %(oname,oname))

									okwargs = '->'.join(okwargs)
									osig = '%s%s %s(%s) { return this->%s(%s); }' % (prefix,return_type, fname, ','.join(args), fname, okwargs)
									self._cpp_class_header.append(osig)

					else:  ## regular function
						if self._noexcept:
							sig = '%s%s %s(%s)' % (prefix,return_type, fname, ', '.join(args))
							out.append( self.indent() + '%s noexcept {\n' % sig )
							if not is_main: self._cheader.append( sig + ' noexcept;' )
						else:
							sig = '%s%s %s(%s)' % (prefix,return_type, fname, ', '.join(args))
							out.append( self.indent() + '%s {\n' % sig )
							if not is_main:
								self._cheader.append( sig + ';' )
								if alt_versions:
									assert args_super_classes
									for av in alt_versions:
										altargs, altbody = av
										asig = '%s %s(%s)' % (return_type, fname, ', '.join(altargs))
										out.insert(0, asig + '\n'.join(altbody))

				else:  ## rust ##
					if is_method:
						self._rust_trait.append('fn %s(&mut self, %s) -> %s;' %(node.name, ', '.join(args), return_type) )
						if closures:
							out.append( self.indent() + 'fn %s<%s>(&mut self, %s) -> %s' % (node.name, clonames, ', '.join(args), return_type) )
							out.append( self.indent() + '	where')
							self.push()
							for clo in closures:
								out.append( self.indent() + '	%s,' %clo)
							self.pull()
							out.append( self.indent() + '{')

						else:
							out.append( self.indent() + 'fn %s(&mut self, %s) -> %s {' % (node.name, ', '.join(args), return_type) )

					else:
						if closures:
							out.append( self.indent() + 'fn %s<%s>(%s) -> %s' % (node.name, clonames, ', '.join(args), return_type) )
							out.append( self.indent() + '	where')
							self.push()
							for clo in closures:
								out.append( self.indent() + '	%s,' %clo)
							self.pull()
							out.append( self.indent() + '{')
						else:
							out.append( self.indent() + 'fn %s(%s) -> %s {' % (node.name, ', '.join(args), return_type) )

			else:  ## function with no return type, `auto` can be used in c++14 to find the return type.

				if self._cpp: ## c++ ##
					if is_method or options['classmethod']:
						classname = self._class_stack[-1].name
						if is_delete:
							sig = '%s::~%s()' %(classname, classname)
							if self._noexcept:
								out.append( self.indent() + '%s noexcept {\n' % sig  )
								sig = '~%s()' %classname
								self._cpp_class_header.append(sig + ';')
							else:
								out.append( self.indent() + '%s {\n' % sig  )
								sig = '~%s()' %classname
								self._cpp_class_header.append(sig + ';')

						else:
							sig = 'auto %s::%s(%s)' %(classname, fname, ', '.join(args))
							if self._noexcept:
								out.append( self.indent() + '%s noexcept {\n' % sig  )
								sig = '%sauto %s(%s)' % (prefix,fname, ', '.join(args))
								self._cpp_class_header.append(sig + ' noexcept;')
							else:
								out.append( self.indent() + '%s {\n' % sig  )
								sig = '%sauto %s(%s)' % (prefix,fname, ', '.join(args))

								if virtualoverride:
									sig = 'virtual %s override' %sig

								self._cpp_class_header.append(sig + ';')
					else:
						if self._noexcept:
							sig = '%sauto %s(%s)' %(prefix, fname, ', '.join(args))
							out.append( self.indent() + '%s noexcept {\n' % sig  )
							if not is_main: self._cheader.append( sig + ' noexcept;' )
						else:
							sig = '%sauto %s(%s)' %(prefix, fname, ', '.join(args))
							out.append( self.indent() + '%s {\n' % sig  )
							if not is_main: self._cheader.append( sig + ';' )

				else:         ## rust ##
					if is_method:
						self._rust_trait.append('fn %s(&mut self, %s);' %(node.name, ', '.join(args)) )
						if closures:
							out.append( self.indent() + 'fn %s<%s>(&mut self, %s) ' % (node.name, clonames, ', '.join(args)) )
							out.append( self.indent() + '	where')
							self.push()
							for clo in closures:
								out.append( self.indent() + '	%s,' %clo)
							self.pull()
							out.append( self.indent() + '{')
						else:
							out.append( self.indent() + 'fn %s(&mut self, %s) {' % (node.name, ', '.join(args)) )

					else:
						if closures:
							out.append( self.indent() + 'fn %s<%s>(%s)' % (node.name, clonames, ', '.join(args)) )
							out.append( self.indent() + '	where')
							self.push()
							for clo in closures:
								out.append( self.indent() + '	%s,' %clo)
							self.pull()
							out.append( self.indent() + '{')
						else:
							out.append( self.indent() + 'fn %s(%s) {' % (node.name, ', '.join(args)) )

		self.push()

		if oargs:
			for n,v in oargs:
				if self._cpp:
					T = args_typedefs[n]
					if T=='string':
						T = 'std::string'
					## in stack mode the user must explicitly pass a pointer
					## when using keyword arguments and object instances.
					## (in heap mode this is not required)
					if n in self._kwargs_type_ and self._memory[-1]=='STACK':
						T = self._kwargs_type_[n]

					out.append(self.indent() + '%s  %s = %s;' %(T,n,v))
					out.append(self.indent() + 'if (__kwargs->__use__%s == true) {' %n )
					out.append(self.indent() +  '  %s = __kwargs->_%s_;' %(n,n))
					out.append(self.indent() + '}')

				else:
					out.append(self.indent() + 'let mut %s = %s;' %(n,v))
					out.append(self.indent() + 'if (__kwargs.__use__%s == true) {' %n )
					out.append(self.indent() +  '  %s = __kwargs.%s;' %(n,n))
					out.append(self.indent() + '}')

			if self._cpp:
				## TODO free __kwargs
				pass

		if starargs:
			out.append(self.indent() + 'let %s = &__vargs__;' %starargs)

		if self._cpp:
			for b in node.body:
				out.append(self.indent()+self.visit(b))

		else:  ## the rust backend requires this?
			body = node.body[:]
			body.reverse()
			self.generate_generic_branches( body, out, self._vars, self._known_vars )


		self._scope_stack = []

		if self._threads:
			assert self._cpp
			while self._threads:
				threadname = self._threads.pop()
				out.append(self.indent()+'if (%s.joinable()) %s.join();' %(threadname,threadname))

		if is_main and self._cpp:
			if self._has_jvm:
				out.append('std::cout << "program exit - DestroyJavaVM" <<std::endl;')
				out.append(self.indent()+'__javavm__->DestroyJavaVM();')
				out.append('std::cout << "JavaVM shutdown ok." <<std::endl;')  ## jvm crashes here TODO fixme.
				#out.append('delete __javavm__;')  ## invalid pointer - segfault.
			out.append( self.indent() + 'return 0;' )
		if is_init and self._cpp:
			if self._memory[-1]=='STACK':
				out.append( self.indent() + 'return *this;' )
			else:
				out.append( self.indent() + 'return this;' )

			#if not self._shared_pointers:
			#	out.append( self.indent() + 'return this;' )
			#else:
			#	#out.append( self.indent() + 'return std::make_shared<%s>(this);' %self._class_stack[-1].name )  ## crashes GCC
			#	out.append( self.indent() + 'return nullptr;' )  ## the exe with PGO will crash if nothing returns

		if len(self._known_arrays.keys()):
			out.append( self.indent()+'/* arrays:')
			for arrname in self._known_arrays:
				arrtype = self._known_arrays[arrname]
				out.append(self.indent()+'	%s : %s' %(arrname, arrtype))
			out.append('*/')

		self.pull()
		if (self._rust or self._cpp) and is_closure:
			out.append( self.indent()+'};' )
		else:
			if is_declare:
				return out[0].replace('{', ';')
			else:
				out.append( self.indent()+'}' )

		node.func_body = out[:]

		if generics and self._cpp:
			overloads = []
			gclasses = set(args_generics.values())
			for gclass in gclasses:

				for subclass in generics:
					for i,line in enumerate(out):
						if i==0: line = line.replace('<%s>'%gclass, '<%s>'%subclass)
						overloads.append(line)

				if len(args_generics.keys()) > 1:
					len_gargs = len(args_generics.keys())
					len_gsubs = len(generics)
					gsigs = []

					p = list(generics)
					p.append( generic_base_class )
					while len(p) < len_gargs:
						p.append( generic_base_class )
					gcombos = set( itertools.permutations(p) )
					if len(gcombos) < 16:  ## TODO fix bug that makes this explode
						for combo in gcombos:
							combo = list(combo)
							combo.reverse()
							gargs = []
							for idx, arg in enumerate(args):
								if idx in args_gens_indices:
									gargs.append(
										arg.replace('<%s>'%gclass, '<%s>'%combo.pop())
									)
								else:
									gargs.append( arg )

						sig = '%s %s(%s)' % (return_type, node.name, ', '.join(gargs))
						gsigs.append( sig )

					for sig in gsigs:
						overloads.append('%s {' %sig)
						for line in out[1:]:
							overloads.append(line)


			out.extend(overloads)

		return '\n'.join(out)

	def _hack_return(self, v, return_type, gname, gt, node):
		## TODO - fix - this breaks easily
		raise RuntimeError('hack return deprecated')
		if v.strip().startswith('return ') and '*'+gt != return_type:
			if gname in v and v.strip() != 'return self':
				if '(' not in v:
					v += '.(%s)' %return_type
					v = v.replace(gname, '__gen__')
					self.method_returns_multiple_subclasses[ self._class_stack[-1].name ].add(node.name)
		return v

```

generate_generic_branches
-------------------------
TODO, this is a left over from the Go backend,
it is a nice hack that generates a branch in the caller for methods that return different types,
this could also come in handy with the rust and c++ backends.


```python

	def generate_generic_branches(self, body, out, force_vars, force_used_vars):
		#out.append('/* GenerateGeneric */')
		#out.append('/*vars: %s*/' %self._vars)
		#out.append('/*used: %s*/' %self._known_vars)

		#force_vars, force_used_vars = self._scope_stack[-1]
		self._vars = set(force_vars)
		self._known_vars = set(force_used_vars)

		#out.append('/*force vars: %s*/' %force_vars)
		#out.append('/*force used: %s*/' %force_used_vars)

		prev_vars = None
		prev_used = None
		vars = None
		used = None

		vars = set(self._vars)
		used = set(self._known_vars)

		#out.append('/*Sstack len: %s*/' %len(self._scope_stack))
		#if self._scope_stack:
		#	out.append('/*stack: %s - %s*/' %self._scope_stack[-1])
		#	out.append('/*STAK: %s */' %self._scope_stack)


		while len(body):
			prev_vars = vars
			prev_used = used

			b = body.pop()
			if isinstance(b, ast.Expr) and isinstance(b.value, ast.Str):  ## skip doc strings here
				continue

			try:
				v = self.visit(b)
				if v: out.append( self.indent() + v )
			except GenerateGenericSwitch as err:
				self._scope_stack.append( (set(self._vars), set(self._known_vars)))

				#out.append('/* 		GenerateGenericSwitch */')
				#out.append('/*	vars: %s*/' %self._vars)
				#out.append('/*	used: %s*/' %self._known_vars)
				#out.append('/*	prev vars: %s*/' %prev_vars)
				#out.append('/*	prev used: %s*/' %prev_used)
				#out.append('/*	stack: %s - %s*/' %self._scope_stack[-1])
				#out.append('/*	stack len: %s*/' %len(self._scope_stack))
				#out.append('/*	stack: %s*/' %self._scope_stack)

				G = err[0]
				if 'target' not in G:
					if isinstance(b, ast.Assign):
						G['target'] = self.visit(b.targets[0])
					else:
						raise SyntaxError('no target to generate generic switch')


				out.append(self.indent()+'__subclass__ := %s' %G['value'])
				out.append(self.indent()+'switch __subclass__.__class__ {')
				self.push()

				subclasses = self.get_subclasses( G['class'] )
				for sub in subclasses:
					out.append(self.indent()+'case "%s":' %sub)
					self.push()
					#out.append(self.indent()+'%s := __subclass__.(*%s)' %(G['target'], sub)) ## error not an interface
					#out.append(self.indent()+'%s := %s(*__subclass__)' %(G['target'], sub))
					out.append(self.indent()+'__addr := %s(*__subclass__)' %sub)
					out.append(self.indent()+'%s := &__addr' %G['target'])

					pv, pu = self._scope_stack[-1]
					self.generate_generic_branches( body[:], out, pv, pu )

					self.pull()
				self._scope_stack.pop()

				self.pull()
				out.append(self.indent()+'}')
				return


	def _visit_call_helper_var(self, node):
		args = [ self.visit(a) for a in node.args ]
		#if args:
		#	out.append( 'var ' + ','.join(args) )
		if node.keywords:
			for key in node.keywords:
				args.append( key.arg )

		for name in args:
			if name not in self._vars:
				self._vars.add( name )

		#out = []
		#for v in args:
		#	out.append( self.indent() + 'var ' + v + ' int')

		#return '\n'.join(out)
		return ''



	def visit_Break(self, node):
		if len(self._match_stack) and not self._cpp:
			return ''
		else:
			return 'break;'

```

Augmented Assignment `+=`
-----------------------


```python

	def visit_AugAssign(self, node):
		## n++ and n-- are slightly faster than n+=1 and n-=1
		target = self.visit(node.target)
		op = self.visit(node.op)
		value = self.visit(node.value)

		if target in self._known_instances:
			target = '*'+target

		if isinstance(node.target, ast.Name) and op=='+' and node.target.id in self._known_strings and not self._cpp:
			return '%s.push_str(%s.as_slice());' %(target, value)

		if self._cpp and op=='+' and isinstance(node.value, ast.Num) and node.value.n == 1:
			a = '%s ++;' %target
		elif self._cpp and op=='-' and isinstance(node.value, ast.Num) and node.value.n == 1:
			a = '%s --;' %target
		else:
			a = '%s %s= %s;' %(target, op, value)
		return a

```

Attribute `.`
---------
TODO deprecate `->` or use for something else.
Also swaps `.` for c++ namespace `::` by checking if the value is a Name and the name is one of the known classes.

```python

	def visit_Attribute(self, node):
		parent_node = self._stack[-2]
		name = self.visit(node.value)
		fname = None
		if isinstance(node.value, ast.Call):
			fname = self.visit(node.value.func)

		attr = node.attr
		if attr=='__finally__':
			attr = 'finally'
		#############################
		if attr == '__doublecolon__':
			return '%s::' %name
		elif attr == '__right_arrow__':
			return '%s->' %name
		elif attr == '__doubledot__':
			return 'PyObject_GetAttrString(%s,' %name
		elif name.endswith('->') or name.endswith('::'):
			return '%s%s' %(name,attr)
		elif name in ('self','this') and self._cpp and self._class_stack:
			if attr in self._class_stack[-1]._weak_members:
				if len(self._stack)>2:
					assert self._stack[-1] is node
					if isinstance(self._stack[-2], ast.Assign):
						for target in self._stack[-2].targets:
							if target is node:
								return 'this->%s' %attr
				if self.usertypes and 'weakref' in self.usertypes:
					return 'this->%s.%s()' %(attr, self.usertypes['weakref']['lock'])
				else:
					return 'this->%s.lock()' %attr
			elif self._memory[-1]=='STACK':
				#return 'this.%s' %attr  ## will not work
				#return '%s' %attr  ## compiles but, but has invalid addresses at runtime
				return '(*this).%s' %attr ## deref each time

			else:
				return 'this->%s' %attr

		elif name in self._rename_hacks and not isinstance(parent_node, ast.Attribute):
			if self._memory[-1]=='STACK':
				return '_cast_%s.%s' %(name.replace('->', '_'), attr)
			else:
				return '_cast_%s->%s' %(name.replace('->', '_'), attr)

		elif name.startswith('nuitka->') and not isinstance(parent_node, ast.Attribute):
			assert attr in ('module', 'moduledict')
			raise RuntimeError('TODO')

		elif name.startswith('cpython->') and not isinstance(parent_node, ast.Attribute):
			raise RuntimeError(attr)

		elif self._cpp and (name in self._known_pyobjects) and not isinstance(parent_node, ast.Attribute):
			return 'PyObject_GetAttrString(%s,"%s")' %(name, attr)

		elif self._cpp and name in self._globals and self._globals[name].endswith('*'):
			return '%s->%s' %(name, attr)

		elif self._cpp and name in self._known_pointers:
			if name in self._known_arrays and attr=='append':
				return '%s->push_back' %name
			else:
				return '%s->%s' %(name, attr)

		elif (name in self._known_instances or name in self._known_arrays) and not isinstance(parent_node, ast.Attribute):
			if self._cpp:
				## TODO - attribute lookup stack to make this safe for `a.x.y`
				## from the known instance need to check its class type, for any
				## subobjects and deference pointers as required. `a->x->y`
				## TODO - the user still needs a syntax to use `->` for working with
				## external C++ libraries where the variable may or may not be a pointer.
				## note: `arr.insert(index,value)` is implemented in visit_call_helper
				if attr=='append' and name in self._known_arrays:
					if self.usertypes and 'vector' in self.usertypes:
						return '%s->%s' %(name, self.usertypes['vector']['append'])
					elif name in self._known_pointers:
						return '%s->push_back' %name
					elif self._memory[-1]=='STACK':
						return '%s.push_back' %name
					else:
						return '%s->push_back' %name
				elif attr=='pop' and name in self._known_arrays:
					## pop_back in c++ returns void, so this only works when `arr.pop()` is not used,
					## in the case where the return is assigned `a=arr.pop()`, the workaround is done in visit_Assign, TODO `f(arr.pop())`
					if self.usertypes and 'vector' in self.usertypes:
						return '%s->%s' %(name, self.usertypes['vector']['pop'])
					else:
						return '%s->pop_back' %name

				elif self._memory[-1]=='STACK':  ## TODO self._instances_on_stack
					return '%s.%s' % (name, attr)
				else:
					return '%s->%s' % (name, attr)
					#return 'pointer(%s)->%s' % (name, attr)

			else:  ## rust
				## note: this conflicts with the new Rust unstable API,
				## where the `append` method acts like Pythons `extend` (but moves the contents)
				## depending on how the Rust API develops, this may have to be deprecated,
				## or a user option to control if known arrays that call `append` should be
				## translated into `push`.
				## note: as a workaround known arrays could have special method `merge`,
				## that would be translated into `append`, while this would be more python,
				## it breaks human readablity of the translation, and makes debugging harder,
				## because the user has to be aware of this special case.
				if attr=='append' and name in self._known_arrays:
					attr = 'push'

				return '%s.borrow_mut().%s' % (name, attr)

		elif (name in self._known_strings) and not isinstance(parent_node, ast.Attribute):
			## allows direct use of c++ std::string properties and methods like: at, erase, replace, swap, pop_back, etc..
			return '%s.%s' %(name,attr)
		elif isinstance(node.value, ast.Str):
			return '%s.%s' %(name,attr)
		elif self._cpp:
			if name in self._classes and not isinstance(parent_node, ast.Attribute):
				return '%s::%s' % (name, attr)
			elif name.endswith(',') and name.startswith('PyObject_GetAttrString('):
				return '%s"%s")' %(name, attr)
			else:
				if name in 'jvm nim cpython nuitka weak'.split():
					return '%s->%s' % (name, attr)
				elif name in self._known_refs or self._memory[-1]=='STACK':
					return '%s.%s' % (name, attr)
				elif name in self._known_instances:  ## user can use std::move to capture these in lambdas for STACK memory mode.
					return '%s->%s' % (name, attr)
				elif fname in self._global_functions and fname not in self._known_vars:
					return '%s.%s' % (name, attr)
				#elif self._shared_pointers:
				#	return '__shared__(%s)->%s' % (name, attr)
				#else:
				#	return '__pointer__(%s)->%s' % (name, attr)
				else:
					return '%s->%s' % (name, attr)

		else:
			return '%s.%s' % (name, attr)
```

List Comp
---------
```python

	def _listcomp_helper(self, node, target=None, type=None, size=None, dimensions=1):
		if not target: target = node._comp_type
		assert target
		assert type
		isprim = self.is_prim_type(type)
		slice_hack = False
		self._known_arrays[target] = type

		gen = node.generators[0]
		try:
			a = self.visit(node.elt)
		except GenerateSlice as error:  ## special c++ case for slice syntax
			assert self._cpp
			msg = error[0]
			a = '_slice_'
			slice_hack = self._gen_slice(
				a,
				value=msg['value'],
				lower=msg['lower'],
				upper=msg['upper'],
				step =msg['step'],
			)



		b = self.visit(gen.target)
		c = self.visit(gen.iter)
		range_n = []
		if isinstance(gen.iter, ast.Call) and isinstance(gen.iter.func, ast.Name):
			if gen.iter.func.id == 'range':
				if len(gen.iter.args) == 1:
					range_n.append( self.visit(gen.iter.args[0]) )
				elif len(gen.iter.args) == 2:
					range_n.append( self.visit(gen.iter.args[0]) )
					range_n.append( self.visit(gen.iter.args[1]) )
				elif len(gen.iter.args) == 3:
					range_n.append( self.visit(gen.iter.args[0]) )
					range_n.append( self.visit(gen.iter.args[1]) )
					range_n.append( self.visit(gen.iter.args[2]) )

		out = []
		compname = target
		if self._memory[-1]=='HEAP':
			compname = '_comp_%s' %target

		if self._rust:
			if range_n:
				if len(range_n)==1:
					#c = 'range(0u,%su)' %range_n[0]
					c = '0u32..%su32' %range_n[0]
				elif len(range_n)==2:
					#c = 'range(%su,%su)' %( range_n[0], range_n[1] )
					c = '%su32..%su32' %( range_n[0], range_n[1] )
				else:
					raise SyntaxError('TODO list comp range(low,high,step)')

			mutref = False
			if isprim:
				out.append('let mut %s : Vec<%s> = Vec::new();' %(compname,type))
			else:
				mutref = True
				#out.append('let mut %s : Vec<&mut %s> = Vec::new();' %(compname,type))  ## ref style
				out.append('let mut %s : Vec< Rc<RefCell<%s>> > = Vec::new();' %(compname,type))

			if range_n:
				## in rust the range builtin returns ...
				out.append('for %s in %s {' %(b, c))
				out.append('	%s.push(%s as %s);' %(compname, a, type))
			else:
				out.append('for &%s in %s.iter() {' %(b, c))
				if mutref:
					#out.append('	%s.push(&mut %s);' %(compname, a))
					out.append('	%s.push(%s);' %(compname, a))
				else:
					out.append('	%s.push(%s);' %(compname, a))

			out.append('}')

			#out.append('let mut %s = &%s;' %(target, compname))
			if mutref:
				out.append('let %s : Rc<RefCell< Vec<Rc<RefCell<%s>>> >> = Rc::new(RefCell::new(%s));' %(target, type, compname))
			else:
				out.append('let %s : Rc<RefCell< Vec<%s> >> = Rc::new(RefCell::new(%s));' %(target, type, compname))

			self._known_arrays[target] = type
			#out.append('drop(%s);' %compname)  ## release from scope, not required because the Rc/RefCell moves it.


		elif self._cpp:
			vectype    = None
			subvectype = None
			if isprim:
				subvectype = 'std::vector<%s>' %type
				#out.append('std::vector<%s> %s;' %(type,compname))
			else:
				if self._memory[-1]=='STACK':
					subvectype = 'std::vector<%s>' %type
				elif not self._shared_pointers:
					subvectype = 'std::vector<%s*>' %type
				elif self._unique_ptr:
					subvectype = 'std::vector<std::unique_ptr<%s>>' %type
				else:
					subvectype = 'std::vector<std::shared_ptr<%s>>' %type

			if dimensions == 1:
				vectype = subvectype
			elif dimensions == 2:
				if self._memory[-1]=='STACK':
					vectype = 'std::vector<%s>' %subvectype
				elif not self._shared_pointers:
					vectype = 'std::vector<%s*>' %subvectype
				elif self._unique_ptr:
					vectype = 'std::vector<std::unique_ptr< %s >>' %subvectype
				else:
					vectype = 'std::vector<std::shared_ptr< %s >>' %subvectype
			else:
				raise SyntaxError('TODO other dimensions')

			out.append('%s %s; /*comprehension*/' %(vectype,compname))


			if range_n:
				if len(range_n)==1:
					out.append(self.indent()+'for (int %s=0; %s<%s; %s++) {' %(b, b, range_n[0], b))

				elif len(range_n)==2:
					out.append(self.indent()+'for (int %s=%s; %s<%s; %s++) {' %(b, range_n[0], b, range_n[1], b))

			else:
				out.append(self.indent()+'for (auto &%s: %s) {' %(b, c))

			if slice_hack:
				out.append( slice_hack )

			if isprim:
				out.append(self.indent()+'	%s.push_back(%s);' %(compname, a))
			else:
				assert type in self._classes
				if False:
					tmp = '_tmp_'
					constructor_args = a.strip()[ len(type)+1 :-1] ## strip to just args
					r = '%s  _ref_%s = %s{};' %(type, tmp, type)
					if constructor_args:
						r += '_ref_%s.__init__(%s);\n' %(tmp, constructor_args)

					if not self._shared_pointers:
						r += '%s* %s = &_ref_%s;' %(type, tmp, tmp)
					elif self._unique_ptr:
						r += 'std::unique_ptr<%s> %s = std::make_unique<%s>(_ref_%s);' %(type, tmp, type, tmp)
					else:
						r += 'std::shared_ptr<%s> %s = std::make_shared<%s>(_ref_%s);' %(type, tmp, type, tmp)
					out.append( r )
					out.append('	%s.push_back(%s);' %(compname, tmp))

				out.append(self.indent()+'	%s.push_back(%s);' %(compname, a))


			out.append(self.indent()+'}')  ## end comp for loop


			## TODO vector.resize if size is given
			if self._memory[-1]=='STACK':
				#out.append(self.indent()+'auto %s = %s;' %(target, compname))
				pass
			elif not self._shared_pointers:
				out.append(self.indent()+'auto %s = &%s;' %(target, compname))
			elif self._unique_ptr:
				out.append(self.indent()+'auto %s = std::make_unique<%s>(%s);' %(target, vectype, compname))
			else:
				out.append(self.indent()+'auto %s = std::make_shared<%s>(%s);' %(target, vectype, compname))

		else:
			raise RuntimeError('TODO list comp for some backend')

		return '\n'.join(out)

```

Assignment
----------

implemented for rust and c++

Assignment to some variable, tracks assignments to local variables for arrays, objects, and strings,
because they need some special handling in other places.


```python


	def visit_Assign(self, node):
		self._catch_assignment = False
		self._assign_node = node
		self._assign_pre  = []
		res = self._visit_assign(node)
		self._assign_node = None
		if self._assign_pre:
			self._assign_pre.append(res)
			res = '\n'.join(self._assign_pre) 
			self._assign_pre  = []
		return res

	def _visit_assign(self, node):
		result = []  ## for arrays of arrays with list comps
		value  = None
		comptarget = None  ## if there was a comp, then use result and comptarget

		if isinstance(node.targets[0], ast.Name) and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id=='range':
			self._known_arrays[node.targets[0].id] = 'int'
			#if len(node.value.args)==1:
			#	alen = self.visit(node.value.args[0])
			#	self._known_arrays[node.targets[0].id] = ('int', alen)
			#	if not len(self._function_stack):
			#		self._global_arrays[node.targets[0].id] = ('int', alen)
			if not len(self._function_stack):
				self._global_arrays[node.targets[0].id] = 'int'
				if self._memory[-1]=='STACK':
					## note: __range#__ returns a copy of std::vector<T>
					## TODO `range(start,stop,step, fixed=True/False)
					self._global_refs[node.targets[0].id] = 'std::vector<int>'

		#######################
		if isinstance(node.targets[0], ast.Tuple):
			if len(node.targets) > 1: raise NotImplementedError('TODO')
			elts = [self.visit(e) for e in node.targets[0].elts]
			target = '(%s)' % ','.join(elts)  ## this works in rust, not c++
			assert not self._cpp
		elif isinstance(node.targets[0], ast.Name) and node.targets[0].id in self._known_arrays and isinstance(self._known_arrays[node.targets[0].id], tuple):
			target = self.visit(node.targets[0])
			value = None
			if isinstance(node.value, ast.Subscript):
				if isinstance(node.value.slice, ast.Slice):
					if not node.value.slice.lower and not node.value.slice.upper and not node.value.slice.step:
						value = self.visit(node.value.value)
					else:
						raise SyntaxError(self.format_error('invalid slice assignment to a fixed size array'))
				else:
					raise SyntaxError(self.format_error('invalid assignment to a fixed size array'))

			if value is None:
				value = self.visit(node.value)

			atype, fixed_size = self._known_arrays[target]

			if '(' in value and ')' in value:  ## do not unroll from a function call
				if not self._function_stack:  ## global
					self._globals[ target ] = (atype, fixed_size)
					return 'auto %s = %s; /*global fixed size array: %s[%s]*/' % (target, value, atype, fixed_size)

				elif target in self._vars:
					## first assignment of a known variable, this requires 'auto' in c++11
					self._vars.remove( target )
					self._known_vars.add( target )
					return 'auto %s = %s; /*assignment to fixed size array: %s[%s]*/' % (target, value, atype, fixed_size)
				else:
					return '%s = %s; /*reassignment to fixed size array: %s[%s]*/' % (target, value, atype, fixed_size)

			elif fixed_size.isdigit() and int(fixed_size)<512:  ## or in self._macro_constants: TODO
				fixed_size = int(fixed_size)
				r = []
				for i in range(fixed_size):
					r.append('%s[%s] = %s[%s];' %(target,i, value,i))
				return ' '.join(r)
			else:
				r = [
					'for (int __i=0; __i<%s; __i++) {' %fixed_size,
					self.indent()+'  %s[__i] = %s[__i];' %(target, value),
					self.indent()+'}',
				]
				return '\n'.join(r)

		elif isinstance(node.targets[0], ast.Subscript) and isinstance(node.targets[0].slice, ast.Slice):
			## slice assignment, the place sliced away is replaced with the assignment value, this happens inplace.
			## `arr1[ :n ]=arr2` slices away all items before n, and inserts arr2 in its place.
			## if `n` is greater than the length of the array, then the array is cleared first.
			target = self.visit(node.targets[0].value)
			slice = node.targets[0].slice
			value = self.visit(node.value)
			if not slice.lower and not slice.upper and not slice.step:  ## slice copy: `myarr[:]=other` ##
				if self._memory[-1]=='STACK':
					if target in self._known_arrays and isinstance(self._known_arrays[target], tuple):
						atype, fixed_size = self._known_arrays[target]
						## unroll loop if possible ##
						if fixed_size.isdigit() and int(fixed_size)<512:  ## or in self._macro_constants: TODO
							fixed_size = int(fixed_size)
							r = []
							for i in range(fixed_size):
								r.append('%s[%s] = %s[%s];' %(target,i, value,i))
							return '\n'.join(r)
						else:
							r = [
								'for (int __i=0; __i<%s; __i++) {' %fixed_size,
								self.indent()+'  %s[__i] = %s[__i];' %(target, value),
								self.indent()+'}',
							]
							return '\n'.join(r)

					elif value in self._known_arrays and isinstance(self._known_arrays[value], tuple):
						atype, fixed_size = self._known_arrays[value]
						## unroll loop if possible ##
						if fixed_size.isdigit() and int(fixed_size)<512:  ## or in self._macro_constants: TODO
							fixed_size = int(fixed_size)
							r = []
							for i in range(fixed_size):
								r.append('%s[%s] = %s[%s];' %(target,i, value,i))
							return '\n'.join(r)
						else:
							r = [
								'for (int __i=0; __i<%s; __i++) {' %fixed_size,
								self.indent()+'  %s[__i] = %s[__i];' %(target, value),
								self.indent()+'}',
							]
							return '\n'.join(r)
					else:
						raise RuntimeError( self.format_error('can not determine the fixed array size from either the target or source: %s=%s'%(target,value) ))
				else:
					raise RuntimeError('TODO array slice assign `arr[:]=other`')

			elif not slice.lower and slice.upper:
				s = self.visit(slice.upper)
				if self._memory[-1]=='STACK':
					if target in self._known_arrays and isinstance(self._known_arrays[target], tuple):
						atype, fixed_size = self._known_arrays[target]
						## TODO assert fixed_size < slice.upper

					r = [
						'for (int __i=0; __i<%s; __i++) {' %self.visit(slice.upper),
						self.indent()+'  %s[__i] = %s[__i];' %(target, value),
						self.indent()+'}',
					]
					return '\n'.join(r)

					#if target in self._known_arrays and isinstance(self._known_arrays[target], tuple):
					#	atype, fixed_size = self._known_arrays[target]
					#	r = [
					#		'for (int __i=0; __i<%s; __i++) {' %self.visit(slice.upper),
					#		self.indent()+'  %s[__i] = %s[__i];' %(target, value),
					#		self.indent()+'}',
					#	]
					#	return '\n'.join(r)
					#else:
					#	r = [
					#		'if (%s >= %s.size()) { %s.erase(%s.begin(), %s.end());' %(s,target, target,target,target),
					#		'} else { %s.erase(%s.begin(), %s.begin()+%s); }' %(target,target,target, self.visit(slice.upper)),
					#		'%s.insert(%s.begin(), %s.begin(), %s.end());' %(target, target, value,value)
					#	]
					#return '\n'.join(r)
				else:
					r = [
						'if (%s >= %s->size()) { %s->erase(%s->begin(), %s->end());' %(s,target, target,target,target),
						'} else { %s->erase(%s->begin(), %s->begin()+%s); }' %(target,target,target, self.visit(slice.upper)),
						'%s->insert(%s->begin(), %s->begin(), %s->end());' %(target, target, value,value)
					]
					return '\n'.join(r)
			elif slice.lower and not slice.upper:
				if self._memory[-1]=='STACK':
					if target in self._known_arrays and isinstance(self._known_arrays[target], tuple):
						fixed_size = self._known_arrays[target][1]
						r = [
							self.indent()+'int __L = 0;',
							self.indent()+'for (int __i=%s; __i<%s; __i++) {' %(self.visit(slice.lower), fixed_size),
							self.indent()+'  %s[__i] = %s[__L];' %(target, value),
							self.indent()+'  __L ++;',
							self.indent()+'}',
						]
						return '\n'.join(r)
					else:
						r = [
							'%s.erase(%s.begin()+%s, %s.end());' %(target,target,self.visit(slice.lower), target),
							'%s.insert(%s.end(), %s.begin(), %s.end());' %(target, target, value,value)
						]
						return '\n'.join(r)
				else:
					r = [
						'%s->erase(%s->begin()+%s, %s->end());' %(target,target,self.visit(slice.lower), target),
						'%s->insert(%s->end(), %s->begin(), %s->end());' %(target, target, value,value)
					]
					return '\n'.join(r)

			else:
				raise RuntimeError('TODO slice assignment lower and upper limits')

		else:
			target = self.visit( node.targets[0] )
			self._assign_var_name = target
			if target.startswith('std::get<'):
				## note: there is no `std::set` because tuples can not change once constructed.
				#return 'std::set' + target[ len('std::set') : -1 ] + ',' + self.visit(node.value) + ');'
				raise SyntaxError(self.format_error('tuple items can not be reassigned'))
		#######################

		if self._cpp and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute) and node.value.func.attr in ('pop', 'insert'):
			arrname = self.visit(node.value.func.value)
			if arrname in self._known_arrays:
				if node.value.func.attr=='insert':
					raise RuntimeError('invalid assignment, array.insert returns nothing.')

				elif node.value.func.attr=='pop':
					popindex = None
					if node.value.args: popindex = self.visit(node.value.args[0])
					######################
					if popindex == '0':
						if self._memory[-1]=='STACK':
							result.append('auto %s = %s[0];' %(target, arrname))
							result.append('%s.erase(%s.begin(),%s.begin()+1);' %(arrname,arrname,arrname))
						else:
							result.append('auto %s = (*%s)[0];' %(target, arrname))
							result.append('%s->erase(%s->begin(),%s->begin()+1);' %(arrname,arrname,arrname))
					elif popindex==None or popindex == '-1':
						if self._memory[-1]=='STACK':
							result.append('auto %s = %s[ %s.size()-1 ];' %(target, arrname, arrname))
							result.append('%s.pop_back();' %arrname)
						else:
							result.append('auto %s = (*%s)[ %s->size()-1 ];' %(target, arrname, arrname))
							result.append('%s->pop_back();' %arrname)
					else:
						raise SyntaxError('TODO array.pop(n)', popindex)
	
				return '\n'.join(result)

			else:
				## do nothing because we are not sure if this is an array
				pass


		#######################
		if isinstance(node.value, ast.BinOp) and self.visit(node.value.op)=='<<' and isinstance(node.value.left, ast.Name) and node.value.left.id=='__go__send__':
			value = self.visit(node.value.right)
			self._has_channels = True
			if self._cpp:
				## cpp-channel API
				return '%s.send(%s);' % (target, value)
			elif self._rust:
				return '%s.send(%s).unwrap();' % (target, value)  ## Rust1.2 API, must call unwrap after send.
			else: ## Go
				return '%s <- %s;' % (target, value)

		elif isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id=='__go__':
			thread = target
			spawn_func = self.visit(node.value.args[0])
			if isinstance(node.value.args[0], ast.Name):
				spawn_func += '()'

			#closure_wrapper = '[&]{%s;}'%spawn_func  ## do not capture loop variants
			closure_wrapper = '[=]{%s;}'%spawn_func

			if self._memory[-1]=='STACK':
				return 'std::thread %s( %s );' %(thread, closure_wrapper)
			else:
				return 'auto %s = std::shared_ptr<std::thread>( new std::thread(%s) );' %(thread, closure_wrapper)

		elif not self._function_stack:  ## global level
			value = self.visit(node.value)
			if isinstance(value, tuple):
				assert self._cpp
				if len(value)==2:
					if self._memory[-1]=='STACK':
						return '%s %s%s;' %(value[0], target, value[1] )
					else:
						return 'auto %s = std::make_shared<%s>(%s);' %(target, value[0], ','.join(value[1]) )
				elif len(value)==3:
					arrtype, arrsize, arrcon = value
					return 'auto %s = std::make_shared<%s>(%s);' %(target, arrtype, arrsize)

				else:
					raise RuntimeError(value)



			if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id in self._classes:
				if self._rust:
					value = '__new__' + value
					return 'let %s *%s = %s;' % (target, node.value.func.id, value)  ## rust, TODO can c++ construct globals on the heap outside of function?
				else:
					return 'auto %s = %s;' %(target, value)
			else:
				guesstype = 'auto'
				if isinstance(node.value, ast.Num):
					guesstype = 'int'
				elif isinstance(node.value, ast.Str):
					guesstype = 'string'
				elif self._rust:
					if isinstance(node.value, ast.Name) and node.value.id=='None':
						raise SyntaxError( self.format_error('untyped global set to None'))
					else:
						raise SyntaxError( self.format_error('untyped global'))

				## save info about globals ##
				if isinstance(node.targets[0], ast.Name):
					self._globals[ node.targets[0].id ] = guesstype
				if guesstype not in self._global_types:
					self._global_types[guesstype] = set()
				self._global_types[guesstype].add( target )

				## we need a syntax for static/const ##
				isprim = self.is_prim_type(guesstype)
				if self._cpp:
					if guesstype=='string':
						#return 'const std::string %s = %s;' % (target, value)
						return 'std::string %s = %s;' % (target, value)
					elif isprim or guesstype=='auto':
						return '%s %s = %s;' % (guesstype, target, value)
					else:
						if not self._shared_pointers:
							return '%s* %s = %s;' % (guesstype, target, value)
						elif self._unique_ptr:
							return 'std::unique_ptr<%s> %s = %s;' % (guesstype, target, value)
						else:
							return 'std::shared_ptr<%s> %s = %s;' % (guesstype, target, value)

				else:
					return 'static %s : %s = %s;' % (target, guesstype, value)

		elif isinstance(node.targets[0], ast.Name) and node.targets[0].id in self._vars:
			## first assignment of a known variable, this requires 'auto' in c++, or `let` in rust.
			## note that the first pass of translation picks up all local variables traversing into
			## all nested structures and loops (not block scoped)
			self._vars.remove( target )
			self._known_vars.add( target )
			node._new_assignment = target

			#if len(self._stack)>=2 and isinstance(self._stack[-2], ast.For):
			#	raise RuntimeError(self._stack)

			if isinstance(node.value, ast.Str):  ## catch strings for `+=` hack
				self._known_strings.add( target )

			try:
				value = self.visit(node.value)

			except GenerateListComp as error:  ## new style to generate list comprehensions
				compnode = error[0]

				if not isinstance(node.value, ast.BinOp):
					## try to guess type of list comprehension ##
					if isinstance(compnode.elt, ast.Call) and isinstance(compnode.elt.func, ast.Name) and compnode.elt.func.id in self._classes:
						return self._listcomp_helper(
							compnode,
							target=target,
							type=compnode.elt.func.id
						)

					raise SyntaxError( self.format_error('untyped list comprehension') )

				comptarget = None
				comptype = None
				arrtype  = None

				if isinstance(node.value.left, ast.Call):
					assert node.value.left.func.id in ('__go__array__', '__go__arrayfixed__')
					comptype = node.value.left.func.id
					if comptype == '__go__array__':
						comptarget = target
						comptype = node.value.left.func.id
						arrtype  = self.visit(node.value.left.args[0])

						return self._listcomp_helper(
							compnode,
							target=comptarget,
							type=arrtype
						)
					else:

						return self._listcomp_helper(
							compnode,
							target=target,
							type=self.visit(node.value.left.args[1]),
							size=self.visit(node.value.left.args[0]),
						)

				elif isinstance(node.value.left, ast.BinOp):
					## This happens when the constructor contains a list of items,
					## and one of the items is an list comp, `result` gets shoved
					## into one of the slots in the constuctor.
					## This can also happens when a 1/2D array contains just a single
					## list comp, `arr = [][]int((1,2,3) for i in range(4))`,
					## creates a 4x3 2D array, in this case the list comp needs
					## to be regenerated as 2D below.
					comptype = node.value.left.left.id=='__go__array__'
					if (node.value.left.left, ast.Name) and node.value.left.left.id=='__go__array__':
						arrtype = node.value.left.right.args[0].id
						comptarget = '_subcomp_'+target
						result.append(
							self._listcomp_helper(
								compnode,
								target=comptarget,
								type=arrtype
							)
						)

					else:
						raise RuntimeError('TODO mdarray subtype')
				else:
					raise RuntimeError(node.value.left)


			except GenerateSlice as error:  ## special c++ case for slice syntax
				assert self._cpp
				msg = error[0]
				slice_type = None  ## slice on an unknown type is broken and will segfault - TODO fix this
				result_size = None
				if msg['value'] in self._known_arrays:
					slice_type = self._known_arrays[msg['value']]

					## stack allocated array ##
					if isinstance(self._known_arrays[msg['value']], tuple):
						new_type   = list(slice_type)
						if msg['lower'] and not msg['upper']:
							if new_type[1].isdigit() and msg['lower'].isdigit():
								result_size = int(new_type[1]) - int(msg['lower'])
								new_type[1] = str(result_size)
							else:
								new_type[1] += '-%s' %msg['lower']
						elif not msg['lower'] and msg['upper']:
							if new_type[1].isdigit() and msg['upper'].isdigit():
								result_size = int(new_type[1]) - int(msg['upper'])
								new_type[1] = str(result_size-1)
							else:
								new_type[1] += '-%s' %msg['upper']
						elif not msg['lower'] and not msg['upper']:
							## slice copy, same size
							if slice_type[1].isdigit():
								result_size = int(slice_type[1])
							else:
								result_size = slice_type[1]

						else:
							new_type[1]= None
						self._known_arrays[target] = tuple(new_type)

					else:
						self._known_arrays[target] = slice_type

				return self._gen_slice(
					target,
					value=msg['value'],
					lower=msg['lower'],
					upper=msg['upper'],
					step =msg['step'],
					type=slice_type,
					result_size = result_size
				)


			if isinstance(node.value, ast.Num):
				if type(node.value.n) is int:
					if self._cpp:
						pass
					else:
						value += 'i64'

			if value=='None':
				if self._cpp:
					raise RuntimeError('invalid in c++ mode')  ## is this possible in c++14?
				else:  ## TODO, this is a bad idea?  letting rust infer the type should have its own syntax like `let x;`
					return 'let mut %s;  /* let rust infer type */' %target



			if not self._cpp and isinstance(node.value, ast.BinOp) and self.visit(node.value.op)=='<<' and isinstance(node.value.left, ast.Call) and isinstance(node.value.left.func, ast.Name) and node.value.left.func.id=='__go__map__':
				key_type = self.visit(node.value.left.args[0])
				value_type = self.visit(node.value.left.args[1])

				if isinstance(node.value.left.args[0], ast.Str):
					raise RuntimeError(node.value.left.args[0])

				if isinstance(node.value.left.args[1], ast.Str):
					raise RuntimeError(node.value.left.args[1])

				if key_type=='string': key_type = 'String'
				if value_type=='string': value_type = 'String'
				self._known_maps[ target ] = (key_type, value_type)

				a = []
				for i in range( len(node.value.right.keys) ):
					k = self.visit( node.value.right.keys[ i ] )
					v = self.visit( node.value.right.values[i] )
					a.append( '_ref_%s.insert(%s,%s);'%(target,k,v) )
				v = '\n'.join( a )
				r  = 'let mut _ref_%s = HashMap::<%s, %s>::new();\n%s\n' %(target, key_type, value_type, v)
				r += 'let mut %s = &_ref_%s;' %(target, target)
				return r

			elif self._cpp and isinstance(node.value, ast.BinOp) and self.visit(node.value.op)=='<<':

				if isinstance(node.value.left, ast.BinOp) and isinstance(node.value.op, ast.LShift):  ## 2D Array
					## c++ vector of vectors ##
					## std::shared_ptr< std::vector<std::shared_ptr<std::vector<T>>> >

					if isinstance(node.value.left.left, ast.Name) and node.value.left.left.id=='__go__array__':

						T = self.visit(node.value.left.right.args[0])
						if T=='string': T = 'std::string'
						self._known_arrays[ target ] = T
						if not self.is_prim_type(T):
							T = 'std::shared_ptr<%s>' %T

						subvectype = 'std::vector<%s>' %T
						if self._memory[-1]=='STACK':
							vectype = 'std::vector<%s>' %subvectype
						elif not self._shared_pointers:
							vectype = 'std::vector<%s*>' %subvectype
						elif self._unique_ptr:
							vectype = 'std::vector<std::unique_ptr<%s>>' %subvectype
						else:
							vectype = 'std::vector<std::shared_ptr<%s>>' %subvectype


						if isinstance(node.value.right, ast.Tuple):
							r = ['/* %s = vector of vectors to: %s */' %(target,T)]
							args = []
							for i,elt in enumerate(node.value.right.elts):
								if isinstance(elt, ast.Tuple):
									subname = '_sub%s_%s' %(i, target)
									args.append( subname )
									sharedptr = False
									for sarg in elt.elts:
										if isinstance(sarg, ast.Name) and sarg.id in self._known_instances:
											sharedptr = True
											if self._memory[-1]=='STACK':
												subvectype = 'std::vector<%s>' %T
												vectype = 'std::vector<%s>' %subvectype

											elif not self._shared_pointers:
												subvectype = 'std::vector<%s*>' %T
												vectype = 'std::vector<%s*>' %subvectype
											elif self._unique_ptr:
												subvectype = 'std::vector<  std::unique_ptr<%s>  >' %T
												vectype = 'std::vector< std::unique_ptr<%s> >' %subvectype
											else:
												subvectype = 'std::vector<  std::shared_ptr<%s>  >' %T
												vectype = 'std::vector< std::shared_ptr<%s> >' %subvectype


									subargs = [self.visit(sarg) for sarg in elt.elts]
									if self._memory[-1]=='STACK':
										r.append('%s %s = {%s};' %(subvectype, subname, ','.join(subargs)))  ## direct ref
									else:
										r.append(self.indent()+'%s _r_%s = {%s};' %(subvectype, subname, ','.join(subargs)))

										if not self._shared_pointers:
											r.append(
												self.indent()+'%s* %s = &_r_%s;' %(subvectype, subname, subname)
											)

										elif self._unique_ptr:
											r.append(
												self.indent()+'std::unique_ptr<%s> %s = _make_unique<%s>(_r_%s);' %(subvectype, subname, subvectype, subname)
											)

										else:
											r.append(
												self.indent()+'std::shared_ptr<%s> %s = std::make_shared<%s>(_r_%s);' %(subvectype, subname, subvectype, subname)
											)

								elif isinstance(elt, ast.ListComp):
									r.extend(result)
									args.append('_subcomp_%s'%target)  ## already a shared_ptr

								else:
									args.append( self.visit(elt) )

							if self._memory[-1]=='STACK':
								r.append(self.indent()+'%s %s = {%s};' %(vectype, target, ','.join(args)))

							else:
								#r.append(self.indent()+'%s _ref_%s = {%s};' %(vectype, target, ','.join(args)))
								heapargs = []
								for arg in args:
									if arg.startswith('new std::vector'):
										vtype = arg[ len('new ') : ].split('{')[0]
										arg = 'std::shared_ptr<%s>(%s)' %(vtype, arg)
									heapargs.append( self.indent() + '\t' + arg )

								if not self._shared_pointers:
									r.append(
										self.indent()+'%s* %s = {%s};' %(vectype, target, ','.join(args))
									)

								elif self._unique_ptr:  ## TODO test and fixme
									r.append(
										self.indent()+'std::unique_ptr<%s> %s = _make_unique<%s>(_ref_%s);' %(vectype, target, vectype, target)
									)
								else:
									r.append(
										self.indent()+'auto %s = std::make_shared<%s>(%s{%s});' %(target, vectype, vectype, ',\n'.join(heapargs))
									)

							return (self.indent()+'\n').join(r)

						elif isinstance(node.value.right, ast.ListComp):
							compnode = node.value.right
							return self._listcomp_helper(
								compnode,
								target=target,
								type=T,
								dimensions=2
							)

					elif isinstance(node.value.left.right, ast.Name) and node.value.left.right.id=='__as__':
						return self.indent()+'auto %s = %s;' %(target, value)

					else:
						raise RuntimeError('TODO other md-array types', node.value)


				elif isinstance(node.value.left, ast.Call) and isinstance(node.value.left.func, ast.Name) and node.value.left.func.id in COLLECTION_TYPES:
					S = node.value.left.func.id
					if S == '__go__map__':
						key_type = self.visit(node.value.left.args[0])
						value_type = self.visit(node.value.left.args[1])
						value_vec  = None
						if not self.is_prim_type(value_type):
							value_type = 'std::shared_ptr<%s>' %value_type

						if isinstance(node.value.left.args[0], ast.Str):
							raise RuntimeError('TODO dict key type from string: %s' %value_type)

						if isinstance(node.value.left.args[1], ast.Str):
							value_type = node.value.left.args[1].s
							value_vec  = value_type.split(']')[-1]
							if self._memory[-1]=='STACK':
								value_type = 'std::vector<%s>' %value_vec
							else:
								value_type = 'std::vector<%s>*' %value_vec
						elif isinstance(node.value.left.args[1], ast.Tuple):
							raise RuntimeError('TODO map and tuple')
						elif value_type.startswith('{') and value_type.endswith('}'):
							raise RuntimeError(self.format_error('invalid value_type: %s' %value_type))
						elif '{' in value_type:
							raise RuntimeError('TODO { in value_type')

						#####################
						if key_type=='string':
							if self.usertypes and 'string' in self.usertypes:
								key_type = self.usertypes['string']['type']
							else:
								key_type = 'std::string'


						if value_type=='string':
							if self.usertypes and 'string' in self.usertypes:
								value_type = self.usertypes['string']['type']
							else:
								value_type = 'std::string'

						self._known_maps[ target ] = (key_type, value_type)

						#keyvalues = []
						a = []
						for i in range( len(node.value.right.keys) ):
							k = self.visit( node.value.right.keys[ i ] )
							v = self.visit( node.value.right.values[i] )
							if v.startswith('[') and v.endswith(']'):
								if self._memory[-1]=='STACK':
									v = ('std::vector<%s>{'%value_vec) + v[1:-1] + '}'
								else:
									v = ('new std::vector<%s>{'%value_vec) + v[1:-1] + '}'
							a.append( '{%s,%s}'%(k,v) )
						#	keyvalues.append( (k,v) )
						#v = ', '.join( a )
						initlist = '{%s}' %'\n,'.join(a)
						map_type = 'std::map<%s,%s>' %(key_type, value_type)
						if self._memory[-1]=='STACK':
							return 'auto %s = %s%s;' %(target, map_type, initlist)

						else:
							return 'auto %s = std::shared_ptr<%s>(new %s%s);' %(target, map_type, map_type, initlist)


						## DEPRECATED c++11 shared pointer
						if self.usertypes and 'map' in self.usertypes:
							maptype = self.usertypes['map']['template'] % (key_type, value_type)
							st = self.usertypes['shared']['template']
							r = ['%s _ref_%s();' %(maptype, target)]
							if keyvalues:
								for key,val in keyvalues:
									r.append('_ref_%s[%s] = %s;' %(target,key,val))
							r.append('%s %s(&_ref_%s);' %(st%maptype, target, target))
							return '\n'.join(r)

						elif self._shared_pointers:
							maptype = 'std::map<%s, %s>' %(key_type, value_type)
							r = '%s _ref_%s = {%s};' %(maptype, target, v)
							if self._unique_ptr:
								r += 'std::unique_ptr<%s> %s = _make_unique<%s>(_ref_%s);' %(maptype, target, maptype, target)
							else:
								r += 'std::shared_ptr<%s> %s = std::make_shared<%s>(_ref_%s);' %(maptype, target, maptype, target)
							return r
						else:  ## raw pointer
							return 'std::map<%s, %s> _ref_%s = {%s}; auto %s = &_ref_%s;' %(key_type, value_type, target, v, target, target)

					elif 'array' in S:
						args = []
						for elt in node.value.right.elts:
							#if isinstance(elt, ast.Num):
							args.append( self.visit(elt) )

						if S=='__go__array__':
							T = self.visit(node.value.left.args[0])
							if T in self.macros:
								T = self.macros[T]
							isprim = self.is_prim_type(T)
							if T=='string':
								if self.usertypes and 'string' in self.usertypes:
									T = self.usertypes['string']['type']
								else:
									T = 'std::string'
							self._known_arrays[ target ] = T
							if T=='tuple':
								tupleargs = []
								for elt in node.value.right.elts:
									#raise RuntimeError(elt.func.id)
									tupleargs.append( self.visit(elt) )

								#for arg in args:
								#	if arg.startswith('[]')
								#	args.append( self.visit(elt) )

								#return 'std::shared_ptr<std::vector<std::tuple<%s>>> %s;' %(','.join(tupleargs), target)
								if self._memory[-1]=='STACK':
									tuplevec = 'std::vector<std::tuple<%s>>' %','.join(tupleargs)
									self._known_refs[target] = tuplevec
									return 'auto %s = %s();' %(target, tuplevec)
								else:
									tuplevec = 'std::vector< std::shared_ptr<std::tuple<%s>> >' %','.join(tupleargs)
									return 'auto %s = std::make_shared<%s>(%s());' %(target, tuplevec, tuplevec)

							if self.usertypes and 'vector' in self.usertypes:
								vtemplate = self.usertypes['vector']['template']
								stemplate = 'std::shared_ptr<%s>'
								if 'shared' in self.usertypes:
									stemplate = self.usertypes['shared']['template']
								if isprim:
									vectype = vtemplate%T
								else:
									vectype = vtemplate % stemplate % T
								return '%s %s = {%s};' %(vectype, target, ','.join(args))

							elif self._shared_pointers:
								if isprim or self._memory[-1]=='STACK':
									vectype = 'std::vector<%s>' %T
									constuct = '(new std::vector<%s>({%s}))' %(T, ','.join(args))
								else:
									if self._unique_ptr:
										vectype = 'std::vector<std::unique_ptr<%s>>' %T
									else:
										vectype = 'std::vector<std::shared_ptr<%s>>' %T
										#constuct = '( new std::vector<std::shared_ptr<%s>>(new std::shared_ptr<%s>(%s)) )' %(T,T, ','.join(args))
										constuct = '( new std::vector<std::shared_ptr<%s>>({%s}) )' %(T, ','.join(args))

								## old style using std::make_shared
								#r = '%s _ref_%s = {%s};' %(vectype, target, ','.join(args))
								#if self._unique_ptr:
								#	r += 'std::unique_ptr<%s> %s = _make_unique<%s>(_ref_%s); /* 1D Array */' %(vectype, target, vectype, target)
								#else:
								#	r += 'std::shared_ptr<%s> %s = std::make_shared<%s>(_ref_%s); /* 1D Array */' %(vectype, target, vectype, target)
								#return r

								## new style
								if self._memory[-1]=='STACK':
									self._known_pointers[target] = vectype
									return '%s* %s = %s; /* 1D Array */' %(vectype, target, constuct )
								elif self._unique_ptr:
									r += 'std::unique_ptr<%s> %s = _make_unique<%s>(_ref_%s); /* 1D Array */' %(vectype, target, vectype, target)
								else:
									#return 'std::shared_ptr<%s> %s = std::shared_ptr<%s>( new %s(%s) ); /* 1D Array */' %(vectype, target,vectype, vectype, ','.join(args) )
									return 'std::shared_ptr<%s> %s( %s ); /* 1D Array */' %(vectype, target,constuct )

							else:  ## raw pointer
								if isprim:
									return 'std::vector<%s>  _ref_%s = {%s}; auto %s = &_ref_%s;' %(T, target, ','.join(args), target, target)
								else:
									return 'std::vector<%s*>  _ref_%s = {%s}; auto %s = &_ref_%s;' %(T, target, ','.join(args), target, target)

						elif S=='__go__arrayfixed__':
							asize = self.visit(node.value.left.args[0])
							atype = self.visit(node.value.left.args[1])
							self._known_arrays[ target ] = (atype,asize)
							if self._memory[-1]=='STACK':
								return '%s %s[%s] = {%s};' %(atype, target, asize, ','.join(args))

							elif self._shared_pointers:
								#vectype = 'std::array<%s, %sul>' %(atype, asize)  ## what api or syntax should we use for fixed size arrays?
								if self.is_prim_type(atype):
									vectype = 'std::vector<%s>' %atype
								else:
									vectype = 'std::vector<std::shared_ptr<%s>>' %atype

								r = '%s _ref_%s = {%s};' %(vectype, target, ','.join(args))
								r += '_ref_%s.resize(%s);' %(target, asize)
								if self._unique_ptr:
									r += 'std::unique_ptr<%s> %s = _make_unique<%s>(_ref_%s);' %(vectype, target, vectype, target)
								else:
									r += 'std::shared_ptr<%s> %s = std::make_shared<%s>(_ref_%s);' %(vectype, target, vectype, target)
								return r
							else:
								## note: the inner braces are due to the nature of initializer lists, one per template param.
								#return 'std::array<%s, %s>  %s = {{%s}};' %(atype, asize, target, ','.join(args))
								## TODO which is correct? above with double braces, or below with none?
								return 'std::array<%s, %sul>  _ref_%s  {%s}; auto %s = &_ref_%s;' %(atype, asize, target, ','.join(args), target, target)

				elif isinstance(node.value.left, ast.Name) and node.value.left.id=='__go__receive__':
					if target in self._known_vars:
						return 'auto %s = %s;' %(target, self.visit(node.value))  ## TODO check this is this a bug? should not be `auto`
					else:
						return 'auto %s = %s;' %(target, self.visit(node.value))

				elif isinstance(node.value.left, ast.Attribute) and node.value.left.attr=='__doubledot__':
					pyob = self.visit(node.value.left.value)
					if isinstance(node.value.right, ast.Name):
						attr = node.value.right.id
						return 'auto %s = %s;' %(target, self.gen_cpy_get(pyob, attr))
					elif isinstance(node.value.right, ast.Call):
						return 'auto %s = %s;' %(target, self.gen_cpy_call(pyob, node.value.right))
					else:
						raise RuntimeError('TODO x=y->?')

				else:
					#raise SyntaxError(('invalid << hack', node.value.left.attr))
					#raise SyntaxError(('invalid << hack', self.visit(node.value.right)))
					raise SyntaxError(('invalid << hack', node.value.right))

			if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute) and isinstance(node.value.func.value, ast.Name):
				varname = node.value.func.value.id
				info = varname + '  '

				if varname in self._known_vars and varname in self._known_instances and self._go:  ## TODO, c++ backend
					## generics generator ##
					#raise SyntaxError(varname + ' is known class::' + self._known_instances[varname] + '%s(%s)' % (fname, args))
					cname = self._known_instances[varname]
					info += 'class: ' + cname
					if node.value.func.attr in self.method_returns_multiple_subclasses[ cname ]:
						self._known_instances[target] = cname
						raise GenerateGenericSwitch( {'target':target, 'value':value, 'class':cname, 'method':node.value.func.attr} )

				if self._cpp:
					#if value.startswith('__cpython_call__'):  ## logic no longer requires _known_pyobjects
					#	self._known_pyobjects[ target ] = varname
					return 'auto %s = %s;			/* %s */' % (target, value, info)
				else:
					if '.borrow_mut()' in value:
						return 'let mut %s = %s;			/* %s */' % (target, value, info)
					else:
						return 'let %s = %s;			/* %s */' % (target, value, info)


			elif isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name):

				## creation of a new class instance and assignment to a local variable
				if node.value.func.id=='new' and isinstance(node.value.args[0],ast.Call) and isinstance(node.value.args[0].func, ast.Name) and not node.value.args[0].func.id.startswith('_'):
					classname = node.value.args[0].func.id
					value = self.visit(node.value.args[0])
					self._known_instances[ target ] = classname

					if self._cpp:
						if classname in self._classes:
							if self._memory[-1]=='HEAP':
								return 'auto %s = %s; // heap-object' %(target, value)
							else:
								return 'auto %s = %s; // stack-object' %(target, value)
						else:
							if self._memory[-1]=='HEAP':
								return 'auto %s = new %s; // heap-xobject' %(target, value)
							else:
								return 'auto %s = %s; // stack-xobject' %(target, value)

						if self._unique_ptr:
							## TODO fix everywhere, check visit_binop
							## raise RuntimeError(self.visit(node.value))
							if 'std::shared_ptr' in value:
								value = value.replace('shared_ptr', 'make_unique')  ## c++14
								vh,vt = value.split('->__init__')
								value = vh.split('((')[0] + '()->__init__' + vt[:-1]

						elif self._memory[-1]=='HEAP':
							if value.count('->__init__(') > 1:
								print 'WARNING: in heap mode with shared pointers,'
								print 'objects should be assigned to a variable before'
								print 'passing them to the constructor of another object'
								print 'target=', target
								print 'pre-value=', value
								x = value[  : value.index('->__init__(') ] + ')'
								y = value[ value.index('->__init__(') : ][:-1]
								value = x+y
								print 'post-value=', value
							elif '->__init__(' in value:
								vh,vt = value.split('->__init__')
								if is_new:
									value = '%s); %s->__init__%s' %(vh, target, vt[:-1])
								else:
									value = '%s); %s->__init__%s' %(vh, target, vt[:-1])

							return 'auto %s = %s; // heap-object' %(target, value)

						elif is_new:
							return 'auto %s = new %s; // new-object' %(target, value)
						else:
							return 'auto %s = %s; // stack-object' %(target, value)

					else:  ## rust
						self._construct_rust_structs_directly = False

						if self._construct_rust_structs_directly:  ## NOT DEFAULT
							## this is option is only useful when nothing is happening
							## in __init__ other than assignment of fields, rust enforces that
							## values for all struct field types are given, and this can not
							## map to __init__ logic where some arguments have defaults.

							## convert args into struct constructor style `name:value`
							args = []
							for i,arg in enumerate(node.value.args):
								args.append( '%s:%s' %(self._classes[classname]._struct_init_names[i], self.visit(arg)))
							if node.value.keywords:
								for kw in node.value.keywords:
									args.append( '%s:%s' %(kw.arg, self.visit(kw.value)))

							return 'let %s = &mut %s{ %s };' %(target, classname, ','.join(args))  ## directly construct struct, this requires all arguments are given.

						else:
							## RUST DEFAULT create new class instance
							## by calling user constructor __init__
							## SomeClass::new(init-args) takes care of making the struct with
							## default null/empty/zeroed values.

							## note: methods are always defined with `&mut self`, this requires that
							## a mutable reference is taken so that methods can be called on the instance.

							## old ref style
							#value = self._visit_call_helper(node.value, force_name=classname+'::new')
							#return 'let %s = &mut %s;' %(target, value)

							## new reference counted mutable style
							value = self._visit_call_helper(node.value)
							return 'let %s : Rc<RefCell<%s>> = %s;' %(target, classname, value)
				else:
					if self._cpp:
						if isinstance(node.value, ast.Expr) and isinstance(node.value.value, ast.BinOp) and self.visit(node.value.value.op)=='<<':
							raise SyntaxError(node.value.value.left)
						elif isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id=='new':
							V = self.visit(node.value.args[0])
							if isinstance(V, tuple):
								vType, vInit = V
								if isinstance(vInit, list):
									return 'auto %s = new %s({%s});' %(target, vType, ','.join(vInit))
								else:
									if vType.endswith('*'):
										vType = vType[:-1]
										return 'auto %s = new %s%s;' %(target, vType, vInit)
									else:
										raise RuntimeError('not a pointer?')
										return '%s %s %s;' %(vType, target, vInit)

							else:
								return 'auto %s = %s;			/* new variable*/' % (target, value)
						else:
							return 'auto %s = %s;			/* new variable*/' % (target, value)
					else:
						return 'let %s = %s;			/* new variable */' % (target, value)

			else:
				if self._cpp:
					#raise RuntimeError((node.value.left, node.value.right, node.value.op))
					if comptarget:
						result.append('auto %s = %s;  /* list comprehension */' % (target, comptarget))
						return '\n'.join(result)
					elif isinstance(node.value, ast.BinOp) and isinstance(node.value.op, ast.RShift) and isinstance(node.value.left, ast.Name) and node.value.left.id=='__new__':
						self._known_instances[target] = self.visit(node.value.right)
						return 'auto %s = %s;  /* new object */' % (target, value)
					elif isinstance(node.value, ast.Tuple):

						tupletype = []
						for telt in node.value.elts:
							if isinstance(telt, ast.Str):  ## TODO test tuple with strings
								v = telt.s
								if v.startswith('"') and v.endswith('"'):  ## TODO this looks like a bug
									v = v[1:-1]
							elif isinstance(telt, ast.List): #v.startswith('[') and v.endswith(']'):
								tsubvec = None
								for st in telt.elts:
									if isinstance(st, ast.Num):
										tsubvec = 'float64'
										break
								assert tsubvec is not None
								v = 'std::vector<%s>' %tsubvec


							elif isinstance(telt, ast.Num):
								v = 'float64'
							elif isinstance(telt, ast.Name):
								v = 'decltype(%s)' % self.visit(telt)
							else:
								v = self.visit(telt)

							if v.startswith('[]'):
								t  = v.split(']')[-1]
								if self._memory[-1]=='STACK':
									v = 'std::vector<%s>' %t
								else:
									v = 'std::vector<%s>*' %t

							tupletype.append(v)


						targs = []
						for ti,te in enumerate(node.value.elts):
							tt = tupletype[ti]
							tv = self.visit(te)
							if tv.startswith('[') and tv.endswith(']'):
								assert tt.startswith('std::vector')
								if tt.endswith('*'):
									tv = '(new %s{%s})' %(tt[:-1], tv[1:-1])
								else:
									tv = '%s{%s}' %(tt, tv[1:-1])
							#elif tv.startswith('std::vector'):  ## never happens?
							#	raise RuntimeError(tv)

							if tt.startswith('std::vector') and self._memory[-1]=='HEAP':
								tupletype[ti] = 'std::shared_ptr<%s>' %tt
								if not tv.startswith('new '):
									raise RuntimeError(self.format_error(tv))
									tv = 'std::shared_ptr<%s>(new %s)' %(tt, tv)
								else:
									tv = 'std::shared_ptr<%s>(%s)' %(tt, tv)

							targs.append(tv)

						if self._memory[-1]=='STACK':
							self._known_refs[target] = 'tuple<%s>' % ','.join(targs)
							return 'auto %s = std::make_tuple(%s); /*new-tuple*/' %(target, ','.join(targs))
						else:
							return 'auto %s = std::make_shared<std::tuple<%s>>(std::make_tuple(%s)); /*new-tuple*/' %(target, ','.join(tupletype), ','.join(targs))
					else:
						return 'auto %s = %s;  /* auto-fallback %s */' % (target, value, node.value)
				else:
					if value.startswith('Rc::new(RefCell::new('):
						#return 'let _RC_%s = %s; let mut %s = _RC_%s.borrow_mut();	/* new array */' % (target, value, target, target)
						self._known_arrays[ target ] = 'XXX'  ## TODO get class name
						return 'let %s = %s;	/* new array */' % (target, value)
					else:
						return 'let mut %s = %s;			/* new muatble */' % (target, value)

		else:
			## the variable has already be used, and is getting reassigned,
			## or its a destructured assignment, or assignment to an attribute, TODO break this apart.

			is_attr = False
			is_tuple = False
			if target not in self._known_vars:
				if isinstance(node.targets[0], ast.Attribute):
					is_attr = True
				elif isinstance(node.targets[0], ast.Tuple):
					is_tuple = True
				elif isinstance(node.targets[0], ast.Name):
					##assert node.targets[0].id in self._globals
					pass
				elif isinstance(node.targets[0], ast.Subscript):
					pass
				else:
					raise SyntaxError( self.format_error(node.targets[0]))

			out = []
			try:
				value = self.visit(node.value)
			except GenerateSlice as error:  ## special c++ case for slice syntax
				assert self._cpp
				msg = error[0]
				slice_type = None  ## slice on an unknown type is broken and will segfault - TODO fix this
				if msg['value'] in self._known_arrays:
					slice_type = self._known_arrays[msg['value']]
					self._known_arrays[target] = slice_type

				slice = self._gen_slice(
					target,
					value=msg['value'],
					lower=msg['lower'],
					upper=msg['upper'],
					step =msg['step'],
					type=slice_type,
				)
				return slice

			isclass = False
			isglobal = target in self._globals
			if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id in self._classes:
				isclass = True

			if self._cpp:
				if isclass:
					classname = node.value.func.id
					self._known_instances[ target ] = classname

					return '%s = %s;' %(target, value)
					## TODO remove below
					#constructor_args = value.strip()[ len(classname)+1 :-1] ## strip to just args
					#r = ''
					#if isglobal:
					#	r += '/* global : %s, type:%s */\n' %(target, classname)
					#r += '%s  _ref_%s = %s{};' %(classname, target, classname)
					#if constructor_args:
					#	r += '_ref_%s.__init__(%s);' %(target, constructor_args)
					#if not self._shared_pointers:
					#	r += '\n%s = &_ref_%s;' %(target, target)
					#elif self._unique_ptr:
					#	r += '\n%s = std::make_unique<%s>(_ref_%s);' %(target, classname, target)
					#else:
					#	r += '\n%s = std::make_shared<%s>(_ref_%s);' %(target, classname, target)
					#return r

				elif is_attr and target.startswith('PyObject_GetAttrString(') and target.endswith(')'):
					pyob = self.visit(node.targets[0].value.value)
					attr = node.targets[0].attr
					if isinstance(node.value, ast.Num):
						if str(node.value.n).isdigit():
							return 'PyObject_SetAttrString(%s, "%s", PyInt_FromLong(%s));'%(pyob,attr, value)

						else:
							return 'PyObject_SetAttrString(%s, "%s", PyFloat_FromDouble(%s));'%(pyob,attr, value)

					elif isinstance(node.value, ast.Str):
						raise RuntimeError('TODO assign str to pyobject')
					else:
						return 'PyObject_SetAttrString(%s, "%s", %s);'%(pyob,attr, value)

				elif target.startswith('PyObject_CallFunction(') and target.endswith(')'):
					## hackish way to support `pyob->somearray[n]
					hack = target.replace(
						'"__getitem__"),"i",',
						'"__setitem__"),"iO",'
					)
					return '%s, %s);' %( hack[:-1], value )

				elif isinstance(value, tuple):
					assert isinstance(node.value, ast.BinOp)
					assert isinstance(node.value.left, ast.Call)
					assert node.value.left.func.id=='__go__array__'
					#raise RuntimeError(value)
					#raise RuntimeError(node.value.left.args[0].id)
					#assert node.value.left.args[0].id=='tuple'
					if target in self._vars:
						self._vars.remove( target )
						self._known_vars.add( target )
						return 'auto %s = %s{%s}; /*somearray*/' %(target, value[0], ','.join(value[1]))
					else:
						return '%s = %s{%s}; /*somearray*/' %(target, value[0], ','.join(value[1]))
				else:
					if value in self._known_arrays and isinstance(self._known_arrays[value], tuple) and self._memory[-1]=='STACK':
						atype, fixed_size = self._known_arrays[value]

						## unroll loop if possible ##
						if '(' in value and ')' in value:  ## do not unroll from a function call
							if target in self._vars:
								## first assignment of a known variable, this requires 'auto' in c++11
								self._vars.remove( target )
								self._known_vars.add( target )
								return 'auto %s = %s; /*Assignment to fixed size array: %s[%s]*/' % (target, value, atype, fixed_size)
							else:
								return '%s = %s; /*Reassignment to fixed size array: %s[%s]*/' % (target, value, atype, fixed_size)

						elif fixed_size.isdigit() and int(fixed_size)<512:  ## or in self._macro_constants: TODO
							fixed_size = int(fixed_size)
							r = []
							for i in range(fixed_size):
								r.append('%s[%s] = %s[%s];' %(target,i, value,i))
							return ' '.join(r)
						else:
							r = [
								'for (int __i=0; __i<%s; __i++) {' %fixed_size,
								self.indent()+'  %s[__i] = %s[__i];' %(target, value),
								self.indent()+'}',
							]
							return '\n'.join(r)

					else:
						return '%s = %s;' % (target, value)

			else:
				assert self._rust
				## destructured assignments also fallback here.
				## fallback to mutable by default? `let mut (x,y) = z` breaks rustc
				if isclass:
					raise RuntimeError('TODO')
				if is_attr:
					return '%s = %s;' % (target, value)
				else:
					return 'let %s = %s;' % (target, value)

```
