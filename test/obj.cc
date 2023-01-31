#include <stdlib.h>
#include <iostream>

struct MyObject {
  int32_t a_;
  MyObject(int32_t a) : a_(a) {
    std::cout << "constructed with value " << a_ << "\n";
  }
  ~MyObject() {
    std::cout << "destructor with value " << a_ << "\n";
  }
  int32_t mul(int32_t b) {
    return a_ * b;
  }
  int32_t sub(int32_t b) {
    return a_ - b;
  }
};

extern "C" {
  void* objconstructor(int32_t a) {
    return new MyObject(a);
  }
  void objdestructor(void* ptr) {
    delete reinterpret_cast<MyObject*>(ptr);
  }

  int32_t mul(void* ptr, int32_t b) {
    return reinterpret_cast<MyObject*>(ptr)->mul(b);
  }
  int32_t sub(void* ptr, int32_t b) {
    return reinterpret_cast<MyObject*>(ptr)->sub(b);
  }
}

