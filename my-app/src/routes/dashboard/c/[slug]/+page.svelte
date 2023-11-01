<script>
  /** @type {import('./$types').PageData} */

  import * as Table from "$lib/components/ui/table";

  import { Separator } from "$lib/components/ui/separator";

  import { Input } from "$lib/components/ui/input";
  import { goto } from "$app/navigation";
  import { Button } from "$lib/components/ui/button";
  import Chart from "svelte-frappe-charts";

  export let data;

  function formatIsoDate(dateString) {
    // Create a new date object from the ISO string
    const date = new Date(dateString);

    // Define month names for formatting
    const monthNames = [
      "January",
      "February",
      "March",
      "April",
      "May",
      "June",
      "July",
      "August",
      "September",
      "October",
      "November",
      "December",
    ];

    // Get the year, month, and day
    const year = date.getFullYear();
    const month = monthNames[date.getMonth()];
    const day = date.getDate();

    // Get the hours, minutes, and seconds
    const hours = String(date.getHours()).padStart(2, "0");
    const minutes = String(date.getMinutes()).padStart(2, "0");
    const seconds = String(date.getSeconds()).padStart(2, "0");

    // Return the formatted date
    return `${month} ${day}, ${year}`;
  }
  const data_news = data.news;
  console.log(data_news);
  const publicationsPerDay = {};

  data_news.forEach((item) => {
    const date = item.for_date.split(" ")[0]; // Extract only the date portion

    if (publicationsPerDay[date]) {
      publicationsPerDay[date]["count"]++;
      publicationsPerDay[date]["score"] += item.ev_infl_combined;
    } else {
      publicationsPerDay[date] = {
        count: 1,
        score: item.ev_infl_combined,
      };
    }
  });

  for (const date in publicationsPerDay) {
    publicationsPerDay[date]["meanSentScore"] =
      publicationsPerDay[date]["score"] / publicationsPerDay[date]["count"];
  }

  const sortedDates = Object.keys(publicationsPerDay).sort(
    (a, b) => new Date(a) - new Date(b)
  );

  const sortedCounts = sortedDates.map(
    (date) => publicationsPerDay[date].count
  );
  const sortedSentScores = sortedDates.map(
    (date) => publicationsPerDay[date].meanSentScore
  );
  console.log(sortedDates); // This will give you the sorted dates
  console.log(sortedCounts); // This will give you the number of publications corresponding to those sorted dates
  console.log(sortedSentScores);

  import { onMount } from "svelte";
  let dates = sortedDates;
  let sentimentScores = sortedSentScores;
  let numberOfArticles = sortedCounts;
  let markerSizes = numberOfArticles.map((count) => count * 10);

  onMount(async () => {
    const Plotly = await import("plotly.js/dist/plotly-basic.min.js");
    let data = [
      {
        type: "scatter",
        mode: "lines+markers",
        x: dates,
        y: sentimentScores,
        line: { shape: "spline" },
        marker: {
          size: markerSizes,
          sizemode: "diameter",
        },
        name: "Sentiment Score",
      },
    ];

    let layout = {
      title: "Findex Analysis over Time",
      xaxis: {
        title: "Date",
      },
      yaxis: {
        title: "Findex Score",
      },
    };

    Plotly.newPlot("plot", data, layout);
  });
  console.log(publicationsPerDay);
</script>

<p class="mt-4 text-xl">Topics for {data.company}</p>

<div id="plot" style="width:100%; height:100%;" />

<Table.Root>
  <Table.Header>
    <Table.Row>
      <Table.Head class="w-1/5">Event</Table.Head>
      <Table.Head class="w-1/3">Summary</Table.Head>

      <Table.Head />
      <!-- <Table.Head>Tech</Table.Head>
      <Table.Head>Fin</Table.Head>
      <Table.Head>Policy</Table.Head> -->
      <Table.Head>Findex</Table.Head>
      <Table.Head class="text-right">Date</Table.Head>
    </Table.Row>
  </Table.Header>
  <Table.Body>
    {#each data.news as news, i (i)}
      <Table.Row>
        <Table.Cell class="font-medium">{news.ev_summary_short}</Table.Cell>
        <Table.Cell>{news.ev_description}</Table.Cell>

        <Table.Cell class="text-right">
          <Button variant="secondary" on:click={() => goto(`../t/${news.id}`)}>
            🔍 Dive deep</Button
          ></Table.Cell
        >
        <!-- <Table.Cell
          class={news.ev_infl_tech < 0 ? "text-red-600" : "text-green-600"}
          >{news.ev_infl_tech}</Table.Cell
        >
        <Table.Cell
          class={news.ev_infl_fin < 0 ? "text-red-600" : "text-green-600"}
          >{news.ev_infl_fin}</Table.Cell
        >
        <Table.Cell
          class={news.ev_infl_policy < 0 ? "text-red-600" : "text-green-600"}
          >{news.ev_infl_policy}</Table.Cell
        > -->
        <Table.Cell
          class={news.ev_infl_combined < 0 ? "text-red-600" : "text-green-600"}
          >{news.ev_infl_combined}</Table.Cell
        >
        <Table.Cell class="text-right"
          >{formatIsoDate(news.for_date)}</Table.Cell
        >
      </Table.Row>
    {/each}
  </Table.Body>
</Table.Root>
