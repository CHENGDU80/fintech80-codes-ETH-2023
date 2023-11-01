<script lang="ts">
  import { page } from "$app/stores";
  import Link from "$lib/Link.svelte";
  import { cn, getPathNameWithoutLocale } from "$lib/components/utils";

  export let items: any = [];
</script>

{#if items.length}
  <div class="grid grid-flow-row auto-rows-max text-md">
    {#each items as item, index (index)}
      {#if item.href}
        <Link href={item.href} external={item.external}>
          <span
            class={cn(
              "group flex w-full items-center rounded-md border border-transparent px-2 py-1 hover:bg-muted hover:text-foreground",
              getPathNameWithoutLocale($page.url) === item.href
                ? "bg-muted font-medium text-foreground"
                : "text-muted-foreground",
              item.disabled && "pointer-events-none opacity-60"
            )}
          >
            <span>{item.titleId}</span>
          </span>
        </Link>
      {:else}
        <span
          class="flex w-full cursor-not-allowed items-center rounded-md p-2 text-muted-foreground hover:underline"
        >
          {item.titleId}
        </span>
      {/if}
    {/each}
  </div>
{/if}
