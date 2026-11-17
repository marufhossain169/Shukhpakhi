import sys
print("Python:", sys.version)
try:
    import scipy
    print("scipy:", scipy.__version__)
except ImportError:
    print("scipy: NOT FOUND")
try:
    import numpy
    print("numpy:", numpy.__version__)
except ImportError:
    print("numpy: NOT FOUND")
print("Module search paths:")
for p in sys.path[:6]:
    print(" ", p)
