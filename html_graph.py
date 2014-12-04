# Copyright 2014 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import json
from string import Template


class HTMLGraph(object):
  _HTML_TEMPLATE = """<!DOCTYPE html>
<script src="https://www.google.com/jsapi"></script>
<script>
var all_data = $ALL_DATA;
google.load('visualization', '1', {packages:['corechart', 'table']});
google.setOnLoadCallback(drawChart);
function drawChart() {
  var data = google.visualization.arrayToDataTable(all_data);
  var charOptions = {
    title: 'Speed Index',
    hAxis: {title: 'Time',  titleTextStyle: {color: 'red'}},
  };
  var chart = new google.visualization.AreaChart(
      document.getElementById('chart_div'));
  chart.draw(data, charOptions);
  var table = new google.visualization.Table(
      document.getElementById('table_div'));
  table.draw(data);
}
</script>
Speed Index for $COMMAND
<div id="chart_div" style="width: 1024px; height: 640px;"></div>
<div id="table_div" style="width: 1024px; height: 640px;"></div>
"""

  def GenerateGraph(self, output, command, headers, all_data):
    html_report = Template(self._HTML_TEMPLATE).safe_substitute(
        {
          'COMMAND': command,
          'ALL_DATA': json.dumps([headers] + all_data)
        })
    with file(output + '.html', 'w') as w:
      w.write(html_report)
    with file(output + '.json', 'w') as w:
      w.write(json.dumps(all_data))
