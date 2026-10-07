#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目技术栈探测与目录结构分析脚本。

输出结构化 JSON，包含：
- 技术栈识别（语言/框架/ORM/数据库）
- 代码目录定位（是否在标准位置）
- 文档文件扫描与分类
- 引用扫描（需更新的旧路径）
- 匹配度评估（Level 1/2/3）

用法：
    python detect_stack.py <project-root>

输出：
    JSON 格式探测结果（stdout）
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Any


class ProjectDetector:
    """项目探测器：只读分析项目结构"""

    def __init__(self, root: str):
        self.root = Path(root).resolve()
        self.result: dict[str, Any] = {
            "root": str(self.root),
            "stack": {},
            "code_locations": {},
            "doc_locations": [],
            "references_to_update": [],
            "stack_match": {"level": 3, "backend": {}, "frontend": {}},
        }

    def detect(self) -> dict[str, Any]:
        """执行完整探测流程"""
        self._detect_backend()
        self._detect_frontend()
        self._scan_documents()
        self._scan_references()
        self._assess_match_level()
        return self.result

    def _detect_backend(self) -> None:
        """检测后端技术栈"""
        # Python + FastAPI
        if (self.root / "requirements.txt").exists():
            content = (self.root / "requirements.txt").read_text(encoding="utf-8", errors="ignore")
            if "fastapi" in content.lower():
                self.result["stack"]["backend"] = {
                    "language": "python",
                    "framework": "fastapi",
                    "orm": "sqlalchemy" if "sqlalchemy" in content.lower() else None,
                }
                self._locate_python_backend()
                return

        # Python + Django
        if (self.root / "manage.py").exists() or (self.root / "requirements.txt").exists():
            content = ""
            if (self.root / "requirements.txt").exists():
                content = (self.root / "requirements.txt").read_text(encoding="utf-8", errors="ignore")
            if "django" in content.lower():
                self.result["stack"]["backend"] = {
                    "language": "python",
                    "framework": "django",
                    "orm": "django-orm",
                }
                return

        # .NET
        csproj_files = list(self.root.rglob("*.csproj"))
        if csproj_files:
            self.result["stack"]["backend"] = {
                "language": "dotnet",
                "framework": "aspnet-core",
                "orm": "sqlsugar",  # 默认假设，可进一步检测
            }
            self._locate_dotnet_backend(csproj_files)
            return

        # Go
        if (self.root / "go.mod").exists():
            content = (self.root / "go.mod").read_text(encoding="utf-8", errors="ignore")
            framework = "gin" if "gin-gonic" in content else "echo" if "labstack/echo" in content else "unknown"
            self.result["stack"]["backend"] = {
                "language": "go",
                "framework": framework,
                "orm": "gorm" if "gorm.io" in content else None,
            }
            return

        # Node.js + Express/NestJS
        if (self.root / "package.json").exists():
            content = (self.root / "package.json").read_text(encoding="utf-8", errors="ignore")
            if '"express"' in content:
                self.result["stack"]["backend"] = {
                    "language": "nodejs",
                    "framework": "express",
                    "orm": None,
                }
            elif '"@nestjs/core"' in content:
                self.result["stack"]["backend"] = {
                    "language": "nodejs",
                    "framework": "nestjs",
                    "orm": None,
                }

    def _detect_frontend(self) -> None:
        """检测前端技术栈"""
        pkg_json = self.root / "package.json"
        if not pkg_json.exists():
            # 可能在子目录
            for candidate in [self.root / "frontend", self.root / "web", self.root / "src" / "web"]:
                if (candidate / "package.json").exists():
                    pkg_json = candidate / "package.json"
                    break
            else:
                return

        content = pkg_json.read_text(encoding="utf-8", errors="ignore")

        # Vue 3
        if '"vue"' in content and '"version": "3' in content:
            ui_lib = "element-plus" if '"element-plus"' in content else "ant-design-vue" if '"ant-design-vue"' in content else None
            self.result["stack"]["frontend"] = {
                "framework": "vue3",
                "ui_lib": ui_lib,
                "build_tool": "vite" if '"vite"' in content else "webpack",
            }
            self._locate_frontend(pkg_json.parent)
            return

        # React
        if '"react"' in content:
            if '"next"' in content:
                self.result["stack"]["frontend"] = {"framework": "nextjs", "ui_lib": None, "build_tool": "next"}
            else:
                self.result["stack"]["frontend"] = {"framework": "react", "ui_lib": None, "build_tool": "webpack"}
            return

        # uni-app
        if '"@dcloudio/uni-app"' in content:
            self.result["stack"]["frontend"] = {"framework": "uniapp", "ui_lib": None, "build_tool": "vite"}
            return

    def _locate_python_backend(self) -> None:
        """定位 Python 后端代码目录"""
        candidates = [
            self.root / "src" / "backend" / "api",
            self.root / "backend" / "api",
            self.root / "app",
            self.root / "api",
        ]
        for candidate in candidates:
            if candidate.exists() and (candidate / "main.py").exists():
                self.result["code_locations"]["backend"] = {
                    "path": str(candidate.relative_to(self.root)),
                    "type": "python-fastapi",
                    "in_standard": candidate == self.root / "src" / "backend" / "api",
                    "target": "src/backend/api" if not (candidate == self.root / "src" / "backend" / "api") else None,
                }
                return

    def _locate_dotnet_backend(self, csproj_files: list[Path]) -> None:
        """定位 .NET 后端代码目录"""
        # 找包含 .Api.csproj 的目录
        for csproj in csproj_files:
            if ".Api.csproj" in csproj.name:
                api_dir = csproj.parent
                in_standard = api_dir == self.root / "src" / "backend" / "api"
                self.result["code_locations"]["backend"] = {
                    "path": str(api_dir.relative_to(self.root)),
                    "type": "dotnet-aspnet",
                    "in_standard": in_standard,
                    "target": "src/backend/api" if not in_standard else None,
                }
                return

    def _locate_frontend(self, pkg_dir: Path) -> None:
        """定位前端代码目录"""
        in_standard = pkg_dir == self.root / "src" / "web"
        self.result["code_locations"]["frontend"] = {
            "path": str(pkg_dir.relative_to(self.root)),
            "type": self.result["stack"]["frontend"]["framework"],
            "in_standard": in_standard,
            "target": "src/web" if not in_standard else None,
        }

    def _scan_documents(self) -> None:
        """扫描文档文件并分类"""
        doc_patterns = {
            "技术规范": ["architecture.md", "design.md", "tech-spec.md", "api-spec.md"],
            "用户文档": ["user-guide.md", "manual.md", "README.md"],
            "变更记录": ["CHANGELOG.md", "HISTORY.md"],
        }

        # 扫描根目录
        for md_file in self.root.glob("*.md"):
            if md_file.name == "README.md":
                self.result["doc_locations"].append({
                    "path": "README.md",
                    "category": "项目说明",
                    "keep_root": True,
                })
            elif md_file.name in ["CHANGELOG.md", "HISTORY.md"]:
                self.result["doc_locations"].append({
                    "path": md_file.name,
                    "category": "变更记录",
                    "target": f"docs/01-技术规范/{md_file.name}",
                })

        # 扫描 docs/ 目录
        docs_dir = self.root / "docs"
        if docs_dir.exists():
            for md_file in docs_dir.rglob("*.md"):
                rel_path = md_file.relative_to(self.root)
                # 判断是否在标准位置
                if str(rel_path).startswith("docs/00-项目文档/") or str(rel_path).startswith("docs/01-技术规范/"):
                    continue  # 已在标准位置
                self.result["doc_locations"].append({
                    "path": str(rel_path),
                    "category": "技术规范" if "arch" in md_file.name.lower() or "design" in md_file.name.lower() else "其他",
                    "target": f"docs/01-技术规范/{md_file.name}",
                })

        # 扫描 wiki/ 目录
        wiki_dir = self.root / "wiki"
        if wiki_dir.exists():
            for md_file in wiki_dir.rglob("*.md"):
                rel_path = md_file.relative_to(self.root)
                self.result["doc_locations"].append({
                    "path": str(rel_path),
                    "category": "用户文档",
                    "target": f"docs/02-用户文档/{md_file.name}",
                })

    def _scan_references(self) -> None:
        """扫描需更新的引用（旧路径）"""
        # 检查 CI 配置
        ci_files = [
            self.root / ".github" / "workflows" / "ci.yml",
            self.root / ".gitlab-ci.yml",
            self.root / "Jenkinsfile",
        ]
        for ci_file in ci_files:
            if ci_file.exists():
                content = ci_file.read_text(encoding="utf-8", errors="ignore")
                # 查找前端路径引用
                if "frontend" in content and self.result["code_locations"].get("frontend", {}).get("target"):
                    self.result["references_to_update"].append({
                        "file": str(ci_file.relative_to(self.root)),
                        "pattern": "frontend",
                        "replacement": "src/web",
                    })

        # 检查 Docker 配置
        docker_files = [self.root / "Dockerfile", self.root / "docker-compose.yml"]
        for docker_file in docker_files:
            if docker_file.exists():
                content = docker_file.read_text(encoding="utf-8", errors="ignore")
                if "frontend" in content and self.result["code_locations"].get("frontend", {}).get("target"):
                    self.result["references_to_update"].append({
                        "file": docker_file.name,
                        "pattern": "frontend",
                        "replacement": "src/web",
                    })

    def _assess_match_level(self) -> None:
        """评估技术栈匹配度"""
        backend = self.result["stack"].get("backend", {})
        frontend = self.result["stack"].get("frontend", {})

        # Level 1: 完全匹配（已知技术栈）
        if backend.get("language") in ["python", "dotnet"] and frontend.get("framework") in ["vue3", "uniapp"]:
            self.result["stack_match"]["level"] = 1
        # Level 2: 部分匹配（能识别分层，但技术栈不在预定义内）
        elif backend.get("language") or frontend.get("framework"):
            self.result["stack_match"]["level"] = 2
        # Level 3: 不匹配
        else:
            self.result["stack_match"]["level"] = 3

        self.result["stack_match"]["backend"] = {
            "detected": f"{backend.get('language', 'unknown')}-{backend.get('framework', 'unknown')}",
            "supported": backend.get("language") in ["python", "dotnet"],
        }
        self.result["stack_match"]["frontend"] = {
            "detected": frontend.get("framework", "unknown"),
            "supported": frontend.get("framework") in ["vue3", "uniapp"],
        }


def main():
    if len(sys.argv) < 2:
        print("用法: python detect_stack.py <project-root>", file=sys.stderr)
        sys.exit(1)

    project_root = sys.argv[1]
    if not os.path.isdir(project_root):
        print(f"错误: {project_root} 不是有效目录", file=sys.stderr)
        sys.exit(1)

    detector = ProjectDetector(project_root)
    result = detector.detect()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
