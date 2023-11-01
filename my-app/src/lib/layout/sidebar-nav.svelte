<script lang="ts">
  import Link from "$lib/Link.svelte";
  import { Separator } from "$lib/components/ui/separator";

  import { cn } from "$lib/components/utils";

  import SidebarNavItems from "./sidebar-nav-items.svelte";

  export let items: SidebarNavItem[] = [];
</script>

<div class="flex h-full w-full overflow-auto">
  {#if items.length}
    <div class="flex flex-col w-full min-h-full py-6 pr-4 space-y-2">
      {#each items as item, index (index)}
        {#if item.bottom}
          <div class="flex-grow" />
          <Separator />
        {/if}
        {#if item.items}
          <div class={cn("pb-4 space-y-2")}>
            {#if item.href}
              <Link href={item.href}>
                <h4 class="mb-1 rounded-md px-2 py-1 text-sm font-semibold">
                  {item.titleId}
                </h4>
              </Link>
            {:else}
              <h4 class="mb-1 rounded-md px-2 py-1 text-sm font-semibold">
                {item.titleId}
              </h4>
            {/if}

            {#if item?.items}
              {#if item?.items?.length}
                <SidebarNavItems items={item.items} />
              {/if}
            {/if}
          </div>
        {:else}
          <SidebarNavItems items={[item]} />
        {/if}
      {/each}
    </div>
  {/if}
</div>
