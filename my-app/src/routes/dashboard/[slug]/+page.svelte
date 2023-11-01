<script lang="ts">
  import * as Tabs from "$lib/components/ui/tabs";
  import * as Card from "$lib/components/ui/card";
  import { Button } from "$lib/components/ui/button";
  import { Input } from "$lib/components/ui/input";
  import { Label } from "$lib/components/ui/label";
  import * as AlertDialog from "$lib/components/ui/alert-dialog";
  import * as Alert from "$lib/components/ui/alert";
  import * as Avatar from "$lib/components/ui/avatar";
  import { companies } from "$lib/config/companies";
  import CardContent from "$lib/components/ui/card/card-content.svelte";
  import * as Table from "$lib/components/ui/table";
  import { goto } from "$app/navigation";
  import { onMount } from "svelte";

  /** @type {import('./$types').PageData} */
  export let data;

  let tabValue = "today";

  console.log(data.companies);

  let currentNews = data.news.daily;
  $: {
    console.log(tabValue);
    if (tabValue === "today") {
      currentNews = data.news.daily;
    } else if (tabValue === "week") {
      currentNews = data.news.weekly;
    }
    console.log(currentNews);
  }
</script>

<p class="mt-4 text-2xl">👋🏾 Welcome back to application</p>

<div class="mt-4">
  <Alert.Root>
    <Alert.Title>A summary of what the move was today</Alert.Title>
    <Alert.Description>
      😿 Sorry, ChatGPT is not working for at the moment. Please read the lorem.
      Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy
      eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam
      voluptua. At vero eos et accusam et.
    </Alert.Description>
  </Alert.Root>
</div>

<div class="flex flex-col sm:flex-row space-y-8 sm:space-y-0 sm:space-x-8 mt-6">
  <Card.Root class="md:w-3/4 w-[350px]">
    <Card.Header>
      <Card.Title>Recent Events</Card.Title>
    </Card.Header>
    <Tabs.Root bind:value={tabValue}>
      <Tabs.List class="grid w-full grid-cols-2">
        <Tabs.Trigger value="today">Today</Tabs.Trigger>
        <Tabs.Trigger value="week">1 Week</Tabs.Trigger>
      </Tabs.List>

      <Card.Content>
        {#if currentNews.length > 0}
          <Table.Root class="overflow-y-scroll">
            <Table.Header>
              <Table.Row>
                <Table.Head class="w-3/4">Events</Table.Head>
                <Table.Head>Score</Table.Head>

                <Table.Head class="text-right" />
              </Table.Row>
            </Table.Header>
            <Table.Body>
              {#each currentNews as news, i (i)}
                <Table.Row>
                  <Table.Cell
                    ><a href="a">{news.ev_summary_short} </a></Table.Cell
                  >

                  <Table.Cell
                    ><a
                      href="t/{news.id}"
                      class={news.ev_infl_combined < 0
                        ? "text-red-600"
                        : "text-green-600"}>{news.ev_infl_combined}</a
                    ></Table.Cell
                  >

                  <Table.Cell class="text-right">
                    <Button
                      variant="secondary"
                      on:click={() => goto(`t/${news.id}`)}
                    >
                      🔍 Dive deep</Button
                    ></Table.Cell
                  >
                </Table.Row>
              {/each}
            </Table.Body>
          </Table.Root>
        {:else}
          <p class="mt-6 text-center font-bold text-xl">No news :(</p>
        {/if}
      </Card.Content>
    </Tabs.Root>
  </Card.Root>
  <div class="w-[350px]">
    <Card.Root>
      <Card.Header>
        <Card.Title>Your company of Interest</Card.Title>
        <Card.Description
          >We keep an eye on your companies and also possible other interesting
          ones.</Card.Description
        >
      </Card.Header>
      <CardContent>
        <div class="space-y-8">
          {#if companies.logos.length}
            {#each companies.logos as item, index (index)}
              <div class="flex items-center">
                <a href="c/{item.symbol}">
                  <Avatar.Root class="w-10 h-auto">
                    <Avatar.Image src="/logos/{item.logo}.png" alt="Avatar" />
                    <Avatar.Fallback>OM</Avatar.Fallback>
                  </Avatar.Root>
                </a>
                <div class="ml-4 space-y-1">
                  <a
                    class="text-sm font-medium leading-none"
                    href="c/{item.symbol}">{item.name}</a
                  >
                </div>
                <div class="ml-auto font-medium">
                  <a
                    class="text-sm font-medium leading-none"
                    href="c/{item.symbol}"
                  >
                    <div class="font-bold">
                      {data.companies.score[item.symbol]}
                    </div>
                  </a>
                </div>
              </div>
            {/each}
          {/if}
        </div>
      </CardContent>
    </Card.Root>
  </div>
</div>
