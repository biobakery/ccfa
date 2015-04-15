/*global jQuery, jQuery UI, d3, dagreD3, DAG */
var ws;
var node_click = "LOG";

function getFill(status) {
  if (status == "WAITING") {
    return "#777";
  }
  else if (status == "QUEUED") {
    return "#44F";
  }
  else if (status == "RUNNING") {
    return "#4F4";
  }
  else if (status == "FAILURE") {
    return "#F44";
  }
  else if (status == "SUCCESS") {
    return "#484";
  }
  else if (status == "RUN_PREVIOUSLY") {
    return "#BDB";
  }
  else {
    return "#000";
  }
};

function convertDate(totalSeconds) {
  hours = Math.floor(totalSeconds / 3600);
  totalSeconds %= 3600;
  minutes = Math.floor(totalSeconds / 60);
  seconds = totalSeconds % 60;
  return hours + ":" + minutes + ":" + seconds;
}

function refresh() {
      var obj = {'short': 'short'};
      var json = JSON.stringify(obj);
      ws.send(json);
};

function setQueue(action) {
  console.log( "setQueue(" + action + ")" );
  var run = document.getElementById("run");
  var pause = document.getElementById("pause");
  var stop = document.getElementById("stop");
  if (action == "RUNNING") {
          run.checked = true;
          pause.checked = false;
          stop.checked = false;
  }
  else if (action == "PAUSED") {
          run.checked = false;
          pause.checked = true;
          stop.checked = false;
  }
  else if (action == "STOPPED") {
          run.checked = false;
          pause.checked = false;
          stop.checked = true;
  }
  var obj = {'queue': action};
  var json = JSON.stringify(obj);
  ws.send(json);
}

function refresh_input(element)
{
  if (event.keyCode == 13) {
    refresh_val = element.value;
    if (refresh_val == 0) {
      clearInterval(interval);
    }
    else {
      interval = setInterval(refresh, refresh_val * 1000);
    }
    element.value = refresh_val;
  }
}

/*
 * function called automatically after page load complets;
 * sets up event listener callbacks for email text and project select boxes
 */
$(document).ready(function() {
  console.log( "JQuery welcome" );
  taskMap = new Object();
  taskTime = new Object();
  var bars = [];
  host = document.location.host;
  console.info("host: " + host);
  ws = new WebSocket("ws://" + host + "/websocket/");
  result = {run: 'RUNNING', pause: 'PAUSED', stop: 'STOPPED', inc: 'increase', dec: 'decrease'}
  var refresh_val = 0; // start at zero - no refresh
  var interval;

  ws.onopen = function() {
      var obj = {'short': 'short'};
      var json = JSON.stringify(obj);
      ws.send(json);
  };
  ws.onmessage = function (evt) {
      var json = JSON.parse(evt.data)
      if (json.hasOwnProperty('status')) {
        var status = json.status;
        var total = document.getElementById("total");
        total.value = status.total
        var waiting = document.getElementById("waiting");
        waiting.value = status.waiting;
        var queued = document.getElementById("queued");
        queued.value = status.queued;
        var running = document.getElementById("running");
        running.value = status.running;
        var finished = document.getElementById("finished");
        finished.value = status.finished;
        var failed = document.getElementById("failed");
        failed.value = status.failed;
        var governor = document.getElementById("governor");
        governor.value = status.governor;
        var run = document.getElementById("run");
        var pause = document.getElementById("pause");
        var stop = document.getElementById("stop");
        console.log(status.queue);
        setQueue(status.queue);
      }
  };
  ws.oncolse = function (evt) {
    console.info("Websocket closed. " + evt.reason)
    clearInterval(refresh);
  };
});

