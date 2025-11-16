<template>
  <a-config-provider :locale="locale">
    <router-view />
  </a-config-provider>
</template>

<script setup>
import zhCN from 'ant-design-vue/es/locale/zh_CN'
import { ref } from 'vue'

const locale = ref(zhCN)
</script>

<style scoped>
</style>



