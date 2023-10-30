<script>
  import Plotly from 'plotly.js-dist';
  import { onMount } from 'svelte';
  
  let plotData;
  let layout;

  onMount(async () => {
    const res = await fetch('http://localhost:1234/getfakedata');
    const { traces, layout: layoutConfig } = await res.json();
    plotData = traces;
    layout = layoutConfig;
    Plotly.newPlot('myDiv', plotData, layout);
  });
</script>

<div id="myDiv"></div>
