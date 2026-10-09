import { isWechatBrowser } from "../utils/wechat";

/** ApiResult 信封（后端统一返回结构；Python 后端裸对象场景见 README 注意点） */
export interface ApiResult<T> {
  code: number;
  message: string;
  data: T;
}

interface RequestOptions {
  url: string;
  method: "GET" | "POST" | "PUT" | "DELETE";
  data?: unknown;
  needAuth?: boolean;
}

/** H5 开发环境直连后端（绕过 uni-app vite 插件对 proxy 的干扰）；生产走相对路径 */
const BASE_URL = (() => {
  if (typeof location !== "undefined" && location.hostname === "localhost") {
    return "{{BACKEND_ORIGIN}}/api";
  }
  return "/api";
})();

function currentQuery(): string {
  if (typeof location === "undefined") return "";
  return location.hash.includes("?")
    ? location.hash.substring(location.hash.indexOf("?"))
    : location.search || "";
}

/** 认证方式按环境分流：微信浏览器走 OAuth，非微信 H5 跳本地登录页并保留 query，小程序走回调页 */
export function redirectToLogin(): void {
  // #ifdef H5
  if (isWechatBrowser()) {
    const tenantId = uni.getStorageSync("tenant_id") || "default";
    location.href =
      "/api/auth/wechat-h5-login?redirect=" +
      encodeURIComponent(location.href) +
      "&tenant=" +
      tenantId;
  } else {
    uni.reLaunch({ url: "/pages/auth/login" + currentQuery() });
  }
  // #endif
  // #ifndef H5
  uni.reLaunch({ url: "/pages/auth/login" });
  // #endif
}

async function request<T>(options: RequestOptions): Promise<T> {
  const { url, method, data, needAuth = true } = options;
  const token: string = uni.getStorageSync("access_token") || "";

  if (needAuth && !token) {
    redirectToLogin();
    throw new Error("未登录");
  }

  const header: Record<string, string> = { "Content-Type": "application/json" };
  if (token) header.Authorization = "Bearer " + token;

  const res = await uni.request({
    url: BASE_URL + url,
    method,
    data: data as never,
    header,
  });
  const status = res.statusCode;
  const body = res.data as ApiResult<T>;

  if (status === 401) {
    uni.removeStorageSync("access_token");
    uni.removeStorageSync("refresh_token");
    uni.removeStorageSync("user_info");
    redirectToLogin();
    throw new Error("登录已过期");
  }
  if (status >= 400) {
    const msg = (body && (body as ApiResult<T>).message) || "请求失败(" + status + ")";
    uni.showToast({ title: msg, icon: "none" });
    throw new Error(msg);
  }
  // 成功：解包并返回 data（调用方拿到的就是 T，不再访问 code/data）
  return (body && "data" in body ? body.data : (body as unknown as T));
}

export function get<T>(url: string, options?: { needAuth?: boolean }) {
  return request<T>({ url, method: "GET", needAuth: options?.needAuth });
}
export function post<T>(url: string, data?: unknown, options?: { needAuth?: boolean }) {
  return request<T>({ url, method: "POST", data, needAuth: options?.needAuth });
}
export function put<T>(url: string, data?: unknown, options?: { needAuth?: boolean }) {
  return request<T>({ url, method: "PUT", data, needAuth: options?.needAuth });
}
export function del<T>(url: string, options?: { needAuth?: boolean }) {
  return request<T>({ url, method: "DELETE", needAuth: options?.needAuth });
}
