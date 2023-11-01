<script>
  import { onMount } from "svelte";

  onMount(async () => {
    const Plotly = await import("plotly.js/dist/plotly-basic.min.js");
    var trace1 = {
      x: ["BMW", "BYD", "Copper", "Litheum"],
      y: [0.2, 0.6, 0.1, -0.4],
      name: "Tech Innovation",
      type: "bar",
    };

    var trace2 = {
      x: ["BMW", "BYD", "Copper", "Litheum"],
      y: [0.1, 0.9, 0.2, 0.3],
      name: "Finance",
      type: "bar",
    };

    var trace3 = {
      x: ["BMW", "BYD", "Copper", "Litheum"],
      y: [0.6, 0.8, 0.4, 0.4],
      name: "Politics",
      type: "bar",
    };

    var data = [trace1, trace2, trace3];

    var layout = {
      xaxis: { title: "Indicators" },
      yaxis: { title: "Findex" },
      barmode: "relative",
      title: "Event Impact across entities",
    };

    Plotly.newPlot("plot", data, layout);
  });
</script>

<div id="plot" style="width:100%; height:100%;" />
