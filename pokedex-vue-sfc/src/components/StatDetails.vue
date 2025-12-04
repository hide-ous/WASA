<template>
  <div class="flex justify-between bg-gray-100 p-2 rounded">
    <span>{{ stat.stat.name }}</span>
    <strong>{{ stat.base_stat }}</strong>
  </div>
</template>

<script>
export default {
  name: "StatDetails",
  props: { stat: Object }
}
</script>
