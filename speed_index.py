#!/usr/bin/env python

# Copyright 2014 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Records a video and measures the 'speed index'.
See more at https://sites.google.com/a/webpagetest.org/docs/using-webpagetest/metrics/speed-index.
"""

import logging
import optparse
import os
import shlex
import subprocess
import sys
import tempfile
import time

import bitmap
import html_graph
import video


class SpeedIndex(object):
  _VIDEO_FILE_NAME = 'speed_index.mp4'
  _DEVICE_VIDEO_FILE_NAME = '/sdcard/' + _VIDEO_FILE_NAME
  _BITRATE = str(4 * 1000 * 1000)
  _WHITE = bitmap.RgbaColor(255, 255, 255)

  def __init__(self, cmd, activity_kill, wait, output):
    self._cmd = cmd
    self._activity_kill = activity_kill
    self._wait = wait
    self._video_capture_pid = None
    self._html_graph = html_graph.HTMLGraph()
    self._output = output

  def _StartVideoCapture(self):
    self._KillPending()
    subprocess.call(['adb', 'shell', 'echo 3 > '
                     '/proc/sys/vm/drop_caches'])
    video_capture = subprocess.Popen(['adb', 'shell', 'screenrecord',
                                      '--bit-rate', self._BITRATE,
                                      self._DEVICE_VIDEO_FILE_NAME])
    # Wait a bit for the screenrecord to kick in.
    time.sleep(0.5)
    video_capture = subprocess.Popen([
        'adb', 'shell', 'am', 'start', '-S',
        'com.google.android.apps.appspeedindex/.BoundingBox'])
    time.sleep(1.0)
    video_capture_pid = subprocess.check_output(['adb', 'shell', 'ps',
        'screenrecord'])
    video_capture_pid = video_capture_pid.replace('\r', '').splitlines()
    self._video_capture_pid = video_capture_pid[-1].split()[1]

  def _RunCommandAndWait(self):
    print self._cmd
    start_cmd = subprocess.Popen(shlex.split(self._cmd))
    start_cmd.wait()
    time.sleep(self._wait)

  def _StopVideoCapture(self):
    subprocess.check_output(['adb', 'shell', 'kill', '-SIGINT',
        self._video_capture_pid])
    # Wait a bit for the screenrecord to flush the file.
    time.sleep(1.0)
    subprocess.check_output(['adb', 'pull', self._DEVICE_VIDEO_FILE_NAME])
    self._KillPending()

  def _KillPending(self):
    if self._activity_kill:
      subprocess.check_output(shlex.split(self._activity_kill))
    subprocess.check_output([
        'adb', 'shell', 'am', 'force-stop',
        'com.google.android.speed_index'])

  def _Calculate(self):
    video_capture = video.Video(self._VIDEO_FILE_NAME)
    histograms = [(time, bmp.ColorHistogram(ignore_color=self._WHITE,
                                            tolerance=8))
                  for time, bmp in video_capture.GetVideoFrameIter()]

    start_histogram = histograms[0][1]
    final_histogram = histograms[-1][1]
    total_distance = start_histogram.Distance(final_histogram)

    def FrameProgress(histogram):
      if total_distance == 0:
        if histogram.Distance(final_histogram) == 0:
          return 1.0
        else:
          return 0.0
      return 1 - histogram.Distance(final_histogram) / total_distance

    time_completeness_list = [(time, FrameProgress(hist))
                              for time, hist in histograms]
    return time_completeness_list

  def Run(self):
    logging.info('Starting video capture...')
    self._StartVideoCapture()
    logging.info('Starting app...')
    self._RunCommandAndWait()
    logging.info('Downloading video...')
    self._StopVideoCapture()
    logging.info('Analyzing video...')
    data = self._Calculate()
    self._html_graph.GenerateGraph(self._output, self._cmd,
        ['Time', '%Visual Complete'], data)


def main():
  parser = optparse.OptionParser(description=__doc__,
                                 usage='speed_index')
  parser.add_option('-c', '--cmd', help='ADB Shell command to run.')
  parser.add_option('-a', '--activity', help='Activity to launch.')
  parser.add_option('-w', '--wait', help='Wait for N seconds.',
                    type='int', default=5)
  parser.add_option('-o', '--output', help='Output report',
                    default='speed_index.html')
  parser.add_option('-v', '--verbose', help='Verbose logging.',
                    action='store_true')
  (options, args) = parser.parse_args()
  if options.verbose:
    logging.getLogger().setLevel(logging.DEBUG)
  if options.cmd and options.activity:
    sys.exit('--cmd and --activity are mutually exclusive.')
  if not options.cmd and not options.activity:
    sys.exit('Specify one of --cmd or --activity.')
  cmd = options.cmd
  activity_kill = None
  if not cmd:
    cmd = 'adb shell am start -S ' + options.activity
    activity_kill = ('adb shell am force-stop ' +
        options.activity[:options.activity.index('/')])
  speed_index = SpeedIndex(cmd, activity_kill, options.wait, options.output)
  speed_index.Run()


if __name__ == '__main__':
  sys.exit(main())
