#!/usr/bin/env python

# Copyright 2014 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import logging
import optparse
import bisect
import os
import json
import sys

import html_graph

class JSONCombiner(object):
  def __init__(self, output, json_list):
    self._data = {}
    self._output = output
    self._json_list = json_list

  def _GetClosest(self, key, timestamp):
    if timestamp in self._data[key]:
      return self._data[key][timestamp]
    sorted_ts = sorted(self._data[key].keys())
    closest = bisect.bisect_right(sorted_ts, timestamp)
    if closest:
      return self._data[key][sorted_ts[closest - 1]]
    return self.data[key][sorted_ts[-1]]

  def Generate(self):
    all_timestamps = set()
    for json_name in self._json_list:
      with file(json_name) as f:
        data = json.loads(f.read())
      for d in data:
        all_timestamps.add(d[0])
        if json_name not in self._data:
          self._data[json_name] = {}
        self._data[json_name][d[0]] = d[1]

    all_timestamps = sorted(all_timestamps)
    headers = ['Time']
    for k in sorted(self._data.keys()):
      headers += ['%s (%%Visual Complete)' %
                  os.path.basename(os.path.splitext(k)[0])]

    time_series = []
    for ts in all_timestamps:
      time_series += [[ts]]
      for k in sorted(self._data.keys()):
        time_series[-1] += [self._GetClosest(k, ts)]

    g = html_graph.HTMLGraph()
    g.GenerateGraph(self._output, 'Combined', headers, time_series)


def main():
  parser = optparse.OptionParser(description=__doc__,
                                 usage='json_combiner')
  parser.add_option('-o', '--output', help='Output report',
                    default='speed_index.html')
  (options, args) = parser.parse_args()
  combiner = JSONCombiner(options.output, args)
  combiner.Generate()


if __name__ == '__main__':
  sys.exit(main())
