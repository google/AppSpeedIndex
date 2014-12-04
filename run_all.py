#!/usr/bin/env python

import optparse
import os
import subprocess
import sys

ACTIVITIES = {
  'calculator':
      'com.android.calculator2/.Calculator',
  'clock':
      'com.google.android.deskclock/com.android.deskclock.DeskClock',
}

def main():
  parser = optparse.OptionParser(description=__doc__,
                                 usage='run_all')
  parser.add_option('-f', '--filter',
      action='append', choices=sorted(ACTIVITIES.keys()))
  parser.add_option('-a', '--activity',
      action='append', default=[])
  (options, args) = parser.parse_args()
  ran = []
  for name in sorted(ACTIVITIES.keys()):
    activity = ACTIVITIES[name]
    if options.filter and name not in options.filter:
      print 'Skipping ', name
      continue
    print 'Launching ', name
    ran += [name]
    subprocess.check_output(['python', 'speed_index.py', '-v', '-a', activity,
                             '-o', os.path.join('/tmp', name)])
  for activity in sorted(options.activity):
    name = activity.split('/')[0].split('.')[-1]
    print 'Launching ', name
    ran += [name]
    subprocess.check_output(['python', 'speed_index.py', '-v', '-a', activity,
                             '-o', os.path.join('/tmp', name)])
  combined = [os.path.join('/tmp', a) + '.json' for a in ran]
  print 'Combining...'
  subprocess.check_output(['python', 'json_combiner.py',
                           '-o', '/tmp/combined'] + combined)

if __name__ == '__main__':
  sys.exit(main())
