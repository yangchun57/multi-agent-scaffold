<script setup lang="ts">
import { onLaunch } from "@dcloudio/uni-app";

onLaunch(() => {
  // 应用启动：可从本地恢复 token（request.ts 每次读取 storage）
  console.log("app launch");
});
</script>

<style>
/* 全局样式仅放必要的 reset；页面样式在各 .vue 内 scoped */
page {
  background-color: #f7f8fa;
}
</style>
