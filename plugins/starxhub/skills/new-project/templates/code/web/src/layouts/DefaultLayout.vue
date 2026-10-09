<template>
  <el-container class="layout">
    <el-aside width="200px" class="aside">
      <div class="logo">{{PROJECT_NAME}}</div>
      <el-menu
        :default-active="$route.path"
        router
        class="menu"
      >
        <el-menu-item index="/dashboard">
          <span>首页看板</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <span>{{ $route.meta.title ?? '' }}</span>
      </el-header>

      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
// 布局组件：侧边栏 + 顶栏 + 主内容区
</script>

<style scoped>
.layout {
  height: 100vh;
}
.aside {
  background: #001529;
}
.logo {
  height: 60px;
  line-height: 60px;
  text-align: center;
  color: #fff;
  font-size: 18px;
  font-weight: 600;
}
.menu {
  border-right: none;
}
.header {
  display: flex;
  align-items: center;
  border-bottom: 1px solid #eee;
  font-weight: 500;
}
.main {
  background: #f5f5f5;
}
</style>
