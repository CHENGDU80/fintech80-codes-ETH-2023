<script>
  import { base } from "$app/paths";

  export let href = "";
  export let external = false;

  console.log(base);
</script>

<a
  href={external ? href : `${href}`}
  target={external ? "_blank" : undefined}
  rel={external ? "noreferrer" : undefined}
  {...$$restProps}
>
  <slot />
</a>
