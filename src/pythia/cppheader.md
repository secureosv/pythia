C++ Header
----------

notes: new in c++11: algorithm, functional, thread, and chrono.
includes typedefs for the standard types, like `f32`.

note: OSX requires cmath, because std::pow and std::round is used in the builtins.

```python

CPP_HEADER = """
#include <memory>
#include <vector>
#include <array>
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <map>
#include <algorithm>
#include <functional>
#include <thread>
#include <chrono>
#include <cmath>
#include <complex>

typedef long   i64;
typedef int    i32;
typedef double f64;
typedef double float64;
typedef float  f32;
typedef float  float32;
typedef const char*  cstring;

"""

```