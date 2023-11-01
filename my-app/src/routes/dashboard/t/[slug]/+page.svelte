<script>
  /** @type {import('./$types').PageData} */
  export let data;

  import { Button } from "$lib/components/ui/button";
  import { Input } from "$lib/components/ui/input";

  import * as Table from "$lib/components/ui/table";

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
</script>

<!-- <p class="text-3xl font-bold tracking-tight mt-4">{data.topic}</p>
<div>{@html data.content}</div> -->

<Table.Root>
  <Table.Header>
    <Table.Row>
      <Table.Head>Title</Table.Head>
      <Table.Head class="w-1/3">Summary</Table.Head>
      <Table.Head>Source</Table.Head>
      <Table.Head>Tech</Table.Head>
      <Table.Head>Fin</Table.Head>
      <Table.Head>Policy</Table.Head>
      <Table.Head>Date</Table.Head>
    </Table.Row>
  </Table.Header>
  <Table.Body>
    {#each data.objs as news, i (i)}
      <Table.Row>
        <Table.Cell class="font-medium">{news.title}</Table.Cell>
        <Table.Cell>{news.excerpt}</Table.Cell>
        <Table.Cell><a href={news.link}>{news.clean_url}</a></Table.Cell>

        <Table.Cell
          class={news.infl_tech < 0 ? "text-red-600" : "text-green-600"}
          >{news.infl_tech}</Table.Cell
        >
        <Table.Cell
          class={news.infl_fin < 0 ? "text-red-600" : "text-green-600"}
          >{news.infl_fin}</Table.Cell
        >
        <Table.Cell
          class={news.infl_policy < 0 ? "text-red-600" : "text-green-600"}
          >{news.infl_policy}</Table.Cell
        >
        <Table.Cell>{formatIsoDate(news.published_date)}</Table.Cell>
      </Table.Row>
    {/each}
  </Table.Body>
</Table.Root>
