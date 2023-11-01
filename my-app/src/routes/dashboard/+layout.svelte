<script lang="ts" context="module">
  const userNavLinks = [
    { titleId: "Homepage", href: "/home", icon: "link" },
    {
      titleId: "Billing",
      href: "/dashboard/settings/billing",
      icon: "billing",
    },
    { titleId: "Settings", href: "/dashboard/settings", icon: "settings" },
  ];

  const sidebarNav = [
    {
      titleId: "Electric Vehicles",
      href: "/dashboard/electric-vehicles",
      icon: "dashboard",
    },

    {
      titleId: "Create New Board",
      href: "/dashboard/api-keys",
      icon: "key",
      bottom: true,
    },
  ];
</script>

<script>
  import Link from "$lib/Link.svelte";
  import { Button } from "$lib/components/ui/button";
  import { Separator } from "$lib/components/ui/separator";
  import SidebarNav from "$lib/layout/sidebar-nav.svelte";
  import UserMenu from "$lib/layout/user-menu.svelte";
  import * as Popover from "$lib/components/ui/popover";
  import { useChat } from "ai/svelte";
  import Input from "$lib/components/ui/input/input.svelte";

  const { input, handleSubmit, messages } = useChat();
</script>

<div>
  <div class="hidden lg:fixed lg:inset-y-0 lg:z-50 lg:flex lg:w-72 lg:flex-col">
    <div class="flex grow flex-col gap-y-5 overflow-y-auto px-6 pb-4 border-r">
      <div class="flex h-16 shrink-0 items-center">
        <Link
          href="/dashboard/electric-vehicles"
          class="flex items-center space-x-2 mr-auto"
        >
          <img src="/logo.svg" alt="finsight" class="h-16 w-auto" />
          <!-- <span class="hidden font-bold sm:inline-block"> finsight </span> -->
        </Link>
      </div>

      <SidebarNav items={sidebarNav} />
    </div>
  </div>

  <div class="lg:pl-72">
    <div
      class="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-4 border-b px-4 shadow-sm sm:gap-x-6 sm:px-6 lg:px-8 justify-end bg-background/20 backdrop-blur-sm"
    >
      <div class="flex h-full justify-center items-center py-2 gap-2">
        <Popover.Root>
          <Popover.Trigger
            ><Button variant="outline" size="sm">Chat</Button></Popover.Trigger
          >
          <Popover.Content
            ><section>
              <p>finsight chat</p>
              <Separator />
              <ul>
                {#each $messages as message}
                  <li>{message.role}: {message.content}</li>
                {/each}
              </ul>
              <form on:submit={handleSubmit}>
                <Input class="mt-4" bind:value={$input} />
                <Button class="mt-4" size="sm" type="submit">Send</Button>
              </form>
            </section></Popover.Content
          >
        </Popover.Root>
        <Button variant="outline" size="sm">Feedback</Button>
        <Separator orientation="vertical" class="h-full" />
        <UserMenu showName links={userNavLinks} />
      </div>
    </div>

    <main>
      <div class="px-4 sm:px-6 lg:px-8">
        <slot />
      </div>
    </main>
  </div>
</div>
