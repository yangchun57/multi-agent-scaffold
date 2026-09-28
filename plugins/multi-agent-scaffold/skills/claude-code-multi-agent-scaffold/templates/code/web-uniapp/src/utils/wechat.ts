/** 微信浏览器判定（UA 检测抽为工具函数，避免页面内重复实现） */
export function isWechatBrowser(): boolean {
  if (typeof navigator === "undefined") return false;
  return /MicroMessenger/i.test(navigator.userAgent);
}

/** H5 hash 模式下从 URL 解析租户标识（勿依赖 onLoad，query 在 # 后取不到） */
export function parseUrlTenant(): string {
  if (typeof location === "undefined") return "";
  const match = location.href.match(/[?&]tenant=([^&]+)/);
  return match ? decodeURIComponent(match[1]) : "";
}
