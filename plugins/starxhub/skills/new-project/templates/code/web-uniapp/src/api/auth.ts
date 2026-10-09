import { post } from "./request";

export interface UserInfo {
  id: string;
  username: string;
  nickname?: string;
  role: string;
  tenantId: number;
}

export interface LoginResponse {
  accessToken: string;
  refreshToken: string;
  user: UserInfo;
}

/** 登录接口无需 token，显式传 needAuth:false（否则无 token 时拦截器直接跳走） */
export function usernameLogin(username: string, password: string, tenantCode: string) {
  return post<LoginResponse>("/auth/login", { username, password, tenantCode }, { needAuth: false });
}
