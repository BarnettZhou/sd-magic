<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import { ElMenu, ElMenuItem } from 'element-plus'
</script>

<template>
  <el-container>
    <el-header>
      <el-menu mode="horizontal" router>
        <el-menu-item index="/prompts">提示词管理</el-menu-item>
        <el-menu-item index="/templates">方案管理</el-menu-item>
      </el-menu>
    </el-header>
    <el-main>
      <router-view></router-view>
    </el-main>
  </el-container>
</template>

<style scoped>
.el-container {
  height: 100vh;
  width: 100%;
}

.el-header {
  padding: 0;
  border-bottom: 1px solid #dcdfe6;
}
</style>
