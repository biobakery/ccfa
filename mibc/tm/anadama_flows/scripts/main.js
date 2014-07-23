/*global jQuery, d3, dagreD3, DAG */

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

        getFill: function(status) {
          if (status == "WAITING") {
            return "#ADA";
          }
          else if (status == "QUEUED") {
            return "#55F";
          }
          else if (status == "RUNNING") {
            return "#5F5";
          }
          else if (status == "FAILURE") {
            return "#F55";
          }
          else if (status == "SUCCESS") {
            return "#585";
          }
          else if (status == "RUN_PREVIOUSLY") {
            return "#ADA";
          }
          else {
            return "#000";
          }
        },

        updateGraph: function(graph, task, status) {
          //var svg = d3.select("#dag > svg");
          var selection = d3.selectAll("g.node.enter");
          /*
          var index;
          for (index=0; index< selection.length; ++index) { 
                  console.log(selection[index][0]);
                  console.log(selection[index][1]);
                  console.log("space");
                  console.log(selection[index]);
          }
          */
          //#var output = selection.map(function(d) { return d.__data__;});
          selection.each(function(d, i) {
            if (d == task) {
              d3.select(this).style("fill", DAG.getFill(status));
              d3.select(this).style("stroke", DAG.getFill(status));
            }
            //console.log("d:" + d);
            //console.log("i: " + i);
          });
          //d3.selectAll("g.node.enter").attr("stroke", "blue");
        }
    };
})();

/*
 * function called automatically after page load complets;
 * sets up event listener callbacks for email text and project select boxes
 */
$(document).ready(function() {
  console.log( "JQuery welcome" );
  var ws = new WebSocket("ws://localhost:8888/websocket/");
  ws.onopen = function() {
      var obj = {'dag': 'dag'};
      var json = JSON.stringify(obj);
      ws.send(json);
  };
  ws.onmessage = function (evt) {
      var json = JSON.parse(evt.data)
      if (json.hasOwnProperty('dag')) {
        json_dag = json.dag;
        DAG.displayGraph(json.dag, jQuery('#dag-name'), jQuery('#dag > svg'));
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
          console.info(update.task + " " + update.status);
          DAG.updateGraph(json_dag, update.task, update.status);
        }
      }
  }
});

