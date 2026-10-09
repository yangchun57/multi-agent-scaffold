<template>
  <view class="home">
    <text class="title">{{ project }}</text>
    <button @click="toLogin">去登录</button>
  </view>
</template>

<script setup lang="ts">
import { ref } from "vue";

const project = ref("{{PROJECT_NAME}}");

function toLogin() {
  uni.navigateTo({ url: "/pages/auth/login" });
}
</script>

<style scoped>
.home {
  padding: 40rpx;
}
.title {
  display: block;
  font-size: 40rpx;
  margin-bottom: 40rpx;
}
</style>
