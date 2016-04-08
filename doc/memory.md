Pythia script translated into C++14 will allocate objects on the heap, 
and use standard reference counted garbage collection by default.

Each of these object types will be wrapped by `std::shared_ptr<T>`:
* `myclass()` objects are initialized as `std::shared_ptr<myclass>`
* `[]` lists become `std::shared_ptr<std::vector<T>>`
* `{}` dicts become `std::shared_ptr<std::map<K,V>>`

Note in stack memory mode, objects are not wrapped by `std::shared_ptr<T>`,
and memory is automatically freed when it falls out of scope.

create an object on the stack
-----------------------------
```python
with stack:
	a = MyClass()
```

create an array on the stack
-----------------------------
```python
with stack:
	a = [1,2,3]
```

cyclic data structures
----------------------

Wrapping objects with `std::shared_ptr` requires using `std::weak_ptr` to break cyclic references.
The translator will detect simple cases where a child class has a reference to a class that contains 
a list of itself, when this is found the parent will be wrapped with `std::weak_ptr` instead of `std::shared_ptr`

The child can then access its parent with some additional logic,
getting a reference to the parent must be done by wrapping it with
`p = weakref.unwrap( self.myparent )`
and then checking if `p` is None.
`if p is None: print "parent has been freed"`
then if the parent is not None, it can be used normally, because `weakref.unwrap()` will convert the `std::weak_ref` to a `std::shared_ptr`.
