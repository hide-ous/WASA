<template>
  <div class="text-center mb-6">
    <h2 class="text-2xl font-bold capitalize">
      {{ pokemon.name }} (#{{ pokemon.id }})
    </h2>
    <img :src="pokemon.sprites.front_default" class="mx-auto my-4" />
  </div>
</template>

<script>
export default {
  name: "PokemonSummary",
  props: { pokemon: Object }
}
</script>
