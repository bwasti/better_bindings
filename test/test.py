import better_bindings as bb

m = bb.bind("fn.so", {
  "foo": ([bb.int32, bb.int32], bb.float),
  "bar": ([bb.int32, bb.float], bb.int32)
})

print(m.foo(5, 5))
print(m.bar(8, 5))

import time

t0 = time.time()
for i in range(100000):
    _ = m.foo(4, 4)
t1 = time.time()
print((t1 - t0) * 1e6 / 100000, "us per call")

MyObject = bb.object(
    "obj.so",
    {
        "__init__": ("objconstructor", [bb.int32], bb.ptr),
        "__del__": ("objdestructor", [bb.ptr], bb.void),
        "mul": ([bb.ptr, bb.int32], bb.int32),
        "sub": ([bb.ptr, bb.int32], bb.int32),
    },
)

obj = MyObject(8)
print(obj.mul(4))
print(obj.sub(3))
