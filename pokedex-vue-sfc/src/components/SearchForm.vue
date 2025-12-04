<template>
  <div class="flex space-x-2 mb-4">
    <input type="number" v-model.number="localId" class="border p-2 rounded" />
    <button @click="emitSearch" class="bg-indigo-600 text-white px-4 py-2 rounded">
      Cerca
    </button>
  </div>
</template>

<script>
export default {
  name: "SearchForm",
  props: { initialId: { type: Number, default: 1 } },
  data() {
    return { localId: this.initialId }
  },
  methods: {
    emitSearch() {
      this.$emit("search", this.localId)
    }
  }
}
</script>
