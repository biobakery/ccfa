/*global jQuery, d3, dagreD3, DAG */
var ws;

(function () {
    'use strict';
    window.DAG = {
        displayGraph: function (graph, dagNameElem, svgElem) {
            dagNameElem.text(graph.name);
            this.renderGraph(graph, svgElem);
        },

        renderGraph: function(graph, svgParent) {
            var nodes = graph.nodes;
            var links = graph.links;

            var graphElem = svgParent.children('g').get(0);
            var svg = d3.select(graphElem);
            var renderer = new dagreD3.Renderer();
            var layout = dagreD3.layout().rankDir('LR');
            renderer.layout(layout).run(dagreD3.json.decode(nodes, links), svg.append('g'));

            // Adjust SVG height to content
            var main = svgParent.find('g > g');
            var h = main.get(0).getBoundingClientRect().height;
            var newHeight = h + 40;
            newHeight = newHeight < 80 ? 80 : newHeight;
            svgParent.height(newHeight);
            svgParent.width(768);

            // Zoom
            d3.select(svgParent.get(0)).call(d3.behavior.zoom().on('zoom', function() {
                var ev = d3.event;
                svg.select('g')
                    .attr('transform', 'translate(' + ev.translate + ') scale(' + ev.scale + ')');
            }));

            // Click
            var d3nodes = d3.selectAll("g.node.enter");
            d3nodes.on("click", DAG.click)
        },

        click: function(d) {
            console.log(d);
            window.open("http://localhost:8888/task?task=" + d);
        },

        updateGraph: function(graph, task, status) {
          var selection = d3.selectAll("g.node.enter");
          selection.each(function(d, i) {
            if (d == task) {
              d3.select(this).style("fill", getFill(status));
              d3.select(this).style("stroke", getFill(status));
            }
          });
        }
    };
})();

(function () {
    'use strict';
  window.BAR = 
  {
    displayBar: function (data, svgElem) 
    {
      var taskTickInterval = setInterval(taskTick, 1000); 
      var width = 420, barHeight = 20;
      var x = d3.scale.linear()
            .domain([0, d3.max(data.nodes)])
            .range([0, width]);

      x = 20;

      //var y = d3.scale.linear().range([height, 0]);

      //var chart = d3.select(".chart")
      //              .attr("width", width)
      //              .attr("height", height);

      var chart = d3.select(".chart")
              .attr("width", width)
              .attr("height", barHeight * data.nodes.length);

      var header = chart.selectAll("g")
         .data(data.nodes)
         .enter()
         .append("g")
         .attr("transform", function(d, i) { return "translate(0," + i * barHeight + ")"; });

      header.append("rect")
         .attr("width", 200)
         .attr("height", barHeight - 1);

      header.append("text")
         //.attr("x", function(d) { return x(d) - 3; })
         //.attr("y", barHeight / 2)
         .attr("x", 10)
         .attr("y", 10)
         .attr("dy", ".35em")
         .text(function(d) { return d.value.label; });

      // Click
      header.on("click", BAR.click)

      var chart2 = d3.select(".chart2")
              .attr("width", 600)
              .attr("height", barHeight * data.nodes.length);
      
      var bars = chart2.selectAll("g")
          .data(data.nodes);

      var existingBars = bars.enter()
         .append("g")
         .attr("transform", function(d, i) {return "translate(220, " + i * barHeight + ")"; });

      existingBars.append("rect")
         .attr("width", function(d) {
           if (!(isNaN(taskMap[d.id]))) {
              sec = Math.round(Math.max(now - taskMap[d.id], 0));
              str = convertDate(sec);
              return sec;
           }
           else {
             return 1;
           }
         })
         .attr("height", barHeight - 1);
       existingBars.append("text")
               .attr("x", 10)
               .attr("y", 10)
               .attr("dy", ".35em");


       var xAxis = d3.svg.axis();
       chart2.append("g")
               .call(xAxis);

       //existingBars.each(function(d, i) {
       //        taskMap[d] == d;
       //});

    },

    updateChart: function(graph, taskid, status, runtime) {
            console.info("Status: " + status);
          var chart = d3.select(".chart");
          var selection = chart.selectAll("g");
          selection.each(function(d, i) {
            if (d.id == taskid) {
              d3.select(this).style("fill", getFill(status));
              //d3.select(this).style("stroke", getFill(status));
            }
          });
          
          var chart2 = d3.select(".chart2");
          var rect = chart2.selectAll("rect");
          rect.each(function(d, i) {
            if (d.id == taskid) {
               d3.select(this).style("fill", getFill(status));
            }
          });
       
          /* 
          we want to set the runtime for every task here
          however, only the running tasks should be updated by a tick
          every taskMap[taskid] gets updated by a tick
          can we duplicate the update in tick here so that we can do 
          it one time for every task?
          */

          if (status == "RUNNING") {
            var now = new Date().getTime() / 1000;
            console.info("RUNNING task.id: " + taskid);
            taskMap[taskid] = now - runtime;
            /*
            var chart2 = d3.select(".chart2");
            var existingBars = chart2.selectAll("g");
            existingBars.each(function(d, i) {
               bar = d3.select(this);
               bar
               .select("text") 
               .text(function(d) { 
                 if (!(isNaN(taskMap[d.id]))) {
                   //taskMap[d.id] = this;
                   d = Math.round(Math.max(now - taskMap[d.id], 0));
                   var str = convertDate(d);
                   return str;
                 }
                 return "0";
               });
            });
            */
          }
          if (status != "RUNNING") {
            // store final number
            delete taskMap[taskid];
            console.info("taskMap delete: ");
          }
    },

    click: function(d) {
      //console.log(d);
      window.open("http://localhost:8888/task?task=" + d.id);
    }
  }
})();



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

function taskTick() {
  now = new Date().getTime() / 1000;
  chart2 = d3.select(".chart2");
  existingBars = chart2.selectAll("g");
  var xScale;

  existingBars.each(function(d, i) {
    if (!(isNaN(taskMap[d.id]))) {
      bar = d3.select(this);
      bar.select("rect")
        .attr("width", function(d) {
          times = []
          for (prop in taskTime) {
            times.push(taskTime[prop]);
          }
          console.info(times);
          xScale = d3.scale.linear()
                 .domain([0, d3.max(times) + 50])
                 .range([0, 620]);
          //console.info("d.id: " + taskMap[d.id]);
          time = now - taskMap[d.id];
          console.info("time: " + time);
          wi = xScale(time);
          console.info("wi: " + wi);
          return wi;
        });

      bar.select("text")
        .text(function(d) { 
          sec = Math.round(Math.max(now - taskMap[d.id], 0));
          // update stored time values
          taskTime[d.id] = sec;
          //console.info("sec: " + sec);
          str = convertDate(sec);
          return str;
      });
    }
  });

  var xAxis = chart2.select("xAxis")
    .scale(xScale)
    .orient("top");

  /* 
  d3.select(bar)
           .text(function(d) { 
           if (!(isNaN(taskMap[d.id]))) {
             sec = Math.round(Math.max(now - taskMap[d.id], 0));
             str = convertDate(sec);
             return str;
           }
  });
  */
  //bar.each(function(d, i) {
  /*
    existingBars.selectAll("text")
         .text(function(d) { 
           if (!(isNaN(taskMap[d.id]))) {
             sec = Math.round(Math.max(now - taskMap[d.id], 0));
             str = convertDate(sec);
             return str;
           }
           else {
             return "na";        
           }
         });
         */
  //});
};

function convertDate(totalSeconds) {
  hours = Math.floor(totalSeconds / 3600);
  totalSeconds %= 3600;
  minutes = Math.floor(totalSeconds / 60);
  seconds = totalSeconds % 60;
  return hours + ":" + minutes + ":" + seconds;
}

/*
 * function called automatically after page load complets;
 * sets up event listener callbacks for email text and project select boxes
 */
$(document).ready(function() {
  console.log( "JQuery welcome" );
  taskMap = new Object();
  taskTime = new Object();
  //taskBar = new Object();
  var bars = [];
  ws = new WebSocket("ws://localhost:8888/websocket/");
  ws.onopen = function() {
      var obj = {'dag': 'dag'};
      var json = JSON.stringify(obj);
      ws.send(json);
  };
  ws.onmessage = function (evt) {
      var json = JSON.parse(evt.data)
      if (json.hasOwnProperty('dag')) {
        var json_dag = json.dag;
        DAG.displayGraph(json.dag, jQuery('#dag-name'), jQuery('#dag > svg'));
        bars = BAR.displayBar(json.dag, jQuery('#dag > svg'));
        console.log(json.dag);
        // immediately get the status of this dag
        var obj = {'status': ""};
        var json = JSON.stringify(obj);
        ws.send(json);
      }
      else if (json.hasOwnProperty('taskUpdate')) {
        var update = json.taskUpdate;
        if (update.hasOwnProperty('task')) 
        {
          //alert(update.task);
          //console.info(update.task + " " + update.status);
          DAG.updateGraph(json_dag, update.task, update.status);
          BAR.updateChart(json_dag, update.task, update.status, update.runTime);
        }
      }
  };
  ws.oncolse = function (evt) {
    console.info("Websocket closed. " + evt.reason)
    clearInterval(taskTickInterval);
  };
});

function handleRadio(radio) {
  console.info("radio: " + radio.value)
  var obj = {'queue': radio.value};
  var json = JSON.stringify(obj);
  ws.send(json);
}