<script lang="ts">
  import { Input } from "$lib/components/ui/input";
  import { Button } from "$lib/components/ui/button";
  import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
  } from "$lib/components/ui/card";
  import { Label } from "$lib/components/ui/label";
  import Link from "$lib/Link.svelte";
  import { goto } from "$app/navigation";
</script>

<main class="w-screen h-screen max-h-screen">
  <div class="container max-w-lg p-0 lg:p-0 max-h-full">
    <div
      class="container flex h-screen w-full max-w-full flex-col justify-center"
    >
      <Card>
        <CardHeader class="space-y-1 text-center">
          <img
            src="/path/to/your/logo.png"
            alt="Company Logo"
            class="mx-auto w-32 h-32"
          />
          <CardTitle class="text-2xl">Sign into your Account</CardTitle>
          <CardDescription
            >Choose your preferred sign in method.</CardDescription
          >
        </CardHeader>
        <CardContent class="grid gap-4">
          <div class="grid gap-2">
            <div class="grid gap-1">
              <Label class="sr-only" for="email">Email</Label>
              <Input
                id="email"
                name="email"
                placeholder="name@example.com"
                type="email"
                required
                autocapitalize="none"
                autocomplete="email"
                autocorrect="off"
              />
            </div>
            <div class="grid gap-1">
              <Label class="sr-only" for="email">Password</Label>
              <Input
                id="password"
                name="password"
                placeholder="Password"
                type="password"
                required
                autocapitalize="none"
                autocorrect="off"
              />
            </div>
            <Button>Sign In</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  </div>
</main>
