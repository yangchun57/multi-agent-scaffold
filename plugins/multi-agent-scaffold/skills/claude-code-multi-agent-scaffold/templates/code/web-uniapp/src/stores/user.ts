import { defineStore } from "pinia";
import { ref } from "vue";
import { usernameLogin as loginApi, type LoginResponse, type UserInfo } from "../api/auth";

export const useUserStore = defineStore("user", () => {
  const token = ref<string>("");
  const userInfo = ref<UserInfo | null>(null);

  function setLoginResult(result: LoginResponse) {
    token.value = result.accessToken;
    userInfo.value = result.user;
    uni.setStorageSync("access_token", result.accessToken);
    uni.setStorageSync("refresh_token", result.refreshToken);
    uni.setStorageSync("user_info", JSON.stringify(result.user));
    uni.setStorageSync("tenant_id", result.user.tenantId);
  }

  async function usernameLogin(username: string, password: string, tenantCode: string) {
    const res = await loginApi(username, password, tenantCode);
    setLoginResult(res);
    return res;
  }

  function logout() {
    token.value = "";
    userInfo.value = null;
    uni.removeStorageSync("access_token");
    uni.removeStorageSync("refresh_token");
    uni.removeStorageSync("user_info");
  }

  function isLoggedIn() {
    return !!token.value && !!userInfo.value;
  }

  return { token, userInfo, usernameLogin, setLoginResult, logout, isLoggedIn };
});
