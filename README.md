"""
This repository is based on chrome's speed index:
https://code.google.com/p/chromium/codesearch#chromium/src/tools/perf/metrics/speedindex.py

For more details, see:
https://sites.google.com/a/webpagetest.org/docs/using-webpagetest/metrics/speed-index

However, instead of measuring web pages, it calculates the "visual completeness"
for android apps.
This can be specially useful for black-box testing of apps startup.
It doesn't need any special instrumentation on the application under test.
As such, it provides fairly coarse grained information, but that can still
be useful as a first approach to measure startup performance.
"""

# 1) Build the "BoundingBox" helper app.
sdk/tools/android update project --name BoundingBox -p . --target android-19
ant clean debug
ant debug install

# 2) Build the "bitmap" python module:
g++ bitmaptools.cc -o bitmaptools
