<template>
  <view class="login-page">
    <input v-model="form.tenantCode" class="input" placeholder="租户编码" />
    <input v-model="form.username" class="input" placeholder="用户名" />
    <input v-model="form.password" class="input" password placeholder="密码" />
    <button class="btn" :loading="loading" @click="onLogin">登录</button>
  </view>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import { useUserStore } from "../../stores/user";
import { parseUrlTenant } from "../../utils/wechat";

const userStore = useUserStore();
const loading = ref(false);
const form = reactive({
  tenantCode: parseUrlTenant(),
  username: "",
  password: "",
});

async function onLogin() {
  loading.value = true;
  try {
    await userStore.usernameLogin(form.username, form.password, form.tenantCode);
    uni.switchTab({ url: "/pages/home/index" });
  } catch {
    // 错误已由 request 拦截器统一 toast，此处不重复提示
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #1890ff, #096dd9);
  padding: 120rpx 32rpx 0;
}
.input {
  background: #f5f7fa;
  border-radius: 8rpx;
  padding: 20rpx 24rpx;
  margin-bottom: 24rpx;
}
.btn {
  margin-top: 24rpx;
  background: #fff;
  color: #1890ff;
}
</style>
