<script lang="ts" context="module">
  import * as Avatar from "$lib/components/ui/avatar";
  const defaultLinks = [
    { titleId: "Dashboard", href: "/dashboard", icon: "dashboard" },
    { titleId: "API-Keys", href: "/dashboard/api-keys", icon: "key" },
    {
      titleId: "Account",
      href: "/dashboard/account",
      icon: "user",
      disabled: false,
    },
  ];
</script>

<script lang="ts">
  import Link from "$lib/Link.svelte";

  import { buttonVariants } from "$lib/components/ui/button";
  import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuGroup,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
  } from "$lib/components/ui/dropdown-menu";

  import { cn } from "$lib/components/utils";
  import { Icons } from "$lib/icons";

  export let showName = false;
  export let hideTheme = false;
  export let links = defaultLinks;
</script>

<DropdownMenu {...$$restProps}>
  <DropdownMenuTrigger
    class={cn(
      buttonVariants({ variant: "ghost" }),
      "relative",
      !showName
        ? "h-8 w-8 rounded.full"
        : "pl-0 [&>svg]:aria-expanded:rotate-180"
    )}
  >
    <Avatar.Root>
      <Avatar.Image src="https://github.com/shadcn.png" alt="@shadcn" />
      <Avatar.Fallback>CN</Avatar.Fallback>
    </Avatar.Root>
    {#if showName}
      <span class="ml-2"> Rick </span>

      <Icons.chevronDown
        class="ml-2 h-4 w-4 transition-transform"
        aria-hidden="true"
      />
    {/if}
  </DropdownMenuTrigger>

  <DropdownMenuContent class="w-56">
    <DropdownMenuLabel class="font-normal flex items-center">
      <div class="flex flex-col space-y-1">
        <p class="text-sm font-medium leading-none">Rick</p>

        <p class="text-xs leading-none text-muted-foreground">rick@mor.ty</p>
      </div>
    </DropdownMenuLabel>
    <DropdownMenuSeparator />
    <DropdownMenuGroup>
      {#each links as link}
        {@const Icon = link.icon && Icons[link.icon]}
        <DropdownMenuItem asChild disabled={link.disabled}>
          <Link
            href={link.href}
            class={cn(
              buttonVariants({ variant: "ghost" }),
              "px-2 py-1.5 w-full justify-start text-primary"
            )}
          >
            {#if link.icon}
              <Icon class="mr-2 h-4 w-4" aria-hidden="true" />
            {/if}
            {link.titleId}
          </Link>
        </DropdownMenuItem>
      {/each}
    </DropdownMenuGroup>

    <DropdownMenuSeparator />

    <DropdownMenuItem asChild>
      <Link
        href="/auth/sign-out"
        class={cn(
          buttonVariants({ variant: "ghost" }),
          "px-2 py-1.5 w-full justify-start text-primary"
        )}
      >
        <Icons.logout class="mr-2 h-4 w-4" aria-hidden="true" />
        Sign Out
      </Link>
    </DropdownMenuItem>
  </DropdownMenuContent>
</DropdownMenu>
