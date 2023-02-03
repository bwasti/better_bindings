import better_bindings as bb
import time

m = bb.bind("fn.so", {
  "foo": ([bb.int32, bb.int32], bb.float),
  "bar": ([bb.int32, bb.float], bb.int32)
})

for _ in range(10):
    t0 = time.time()
    for i in range(100000):
        _ = m.foo(4, 4)
    t1 = time.time()
    print((t1 - t0) * 1e6 / 100000, "us per call")

