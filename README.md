# Better Bindings

<img width="1486" alt="Screenshot 2023-02-01 at 4 52 47 PM" src="https://user-images.githubusercontent.com/4842908/216171788-9443aa70-da90-4655-aa42-ede92eeb82a6.png">



This project will attempt to accomplishes 2 things:

1. Easiest to implement bindings (using a standard C ABI) - ✅
2. Fastest bindings (using something like `compile`) - 🚧

### Easy to use

Simple functions are trivial:

```python
import better_bindings as bb

module = bb.bind('mylib.dylib', {
  'fn': ([bb.int32, bb.int32], bb.float),
  'renamed': ('orig_name', [bb.int32], bb.void)
})

out = module.fn(4, 4)
print(out)
```

Objects are also straightforward:

```python
import better_bindings as bb

MyObj = bb.object('mylib.dylib', {
  '__init__': ('makeObj', [bb.int32, bb.int32], bb.ptr),
  '__del__': ('destroyObj', [bb.ptr], bb.void),
  'foo': ('foo', [bb.ptr, bb.int32], bb.int32)
})

obj = MyObj(8, 4)
out = obj.foo(3)
print(out)
```


### Fast bindings (work in progress)

Currently, bindings are compiled on the fly with the system's C compiler

```python
module = bb.bind('mylib.dylib', binding_map) # calls clang/gcc!
```

**In the future,** I hope to expose `compile()`.
New code is generated and the bytecode is hotswapped (ala torchdynamo):

```python
module = bb.bind('mylib.dylib', binding_map) 

def bar(a, b):
  c = module.foo(a, 3)
  d = module.foo(c, b)
  return d

bar = bb.compile(bar) # the two calls to `foo` are merged and compiled together
```

This is particularly useful for ref counting

```python
MyObj = bb.object('mylib.dylib', binding_map) 

def bar(a, b):
  obja = MyObj(a, 4)
  objb = MyObj(b, 4)
  objc = obja + objb
  return objc

bar = bb.compile(bar) # the intermediate obja and objb are not materialized in Python, no refcounts are bumped!
```


