# coding=utf-8
"""
AgentBrowser 封装 - 使用 agent-browser CLI 进行浏览器自动化

基于 https://github.com/vercel-labs/agent-browser
使用语义化定位器 (Accessibility Tree) 替代脆弱的 CSS/XPath 选择器
"""

import json
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class AgentBrowserError(Exception):
    """AgentBrowser 异常基类"""
    pass


class AgentBrowser:
    """
    agent-browser CLI 封装类

    功能：
    - 会话管理（支持多会话并行）
    - 快照获取（获取页面 Accessibility Tree）
    - 语义化操作（点击、输入、导航等）
    - 元素引用（@e1, @e2 等持久化引用）
    - 自动等待和重试机制

    使用示例：
        browser = AgentBrowser(session_name="tender_shandong", headless=True)
        browser.goto("http://ggzy.shandong.gov.cn/")

        # 获取快照
        snapshot = browser.snapshot(interactive_only=True)

        # 语义化操作
        browser.fill("@e5", "软件开发")  # 通过元素引用填充
        browser.click(placeholder="请选择采购类型")  # 通过语义定位器点击
        browser.press("Enter")

        # 等待和提取
        browser.wait(2000)
        content = browser.get_content()
    """

    def __init__(
        self,
        session_name: str = "default",
        headless: bool = True,
        timeout: int = 30000,
        viewport_width: int = 1280,
        viewport_height: int = 720,
    ):
        """
        初始化 AgentBrowser

        Args:
            session_name: 会话名称（用于多会话管理）
            headless: 是否无头模式
            timeout: 默认超时时间（毫秒）
            viewport_width: 视口宽度
            viewport_height: 视口高度
        """
        self.session_name = session_name
        self.headless = headless
        self.timeout = timeout
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height

        # 构建基础命令
        # 格式: agent-browser [options] <command> [args]
        self._base_cmd = ["agent-browser"]

        # 添加会话选项
        if session_name and session_name != "default":
            self._base_cmd.extend(["--session", session_name])

        # 无头模式：agent-browser 默认就是无头的，不需要额外参数

        self._last_snapshot: Optional[Dict] = None
        self._element_refs: Dict[str, str] = {}  # ref_id -> description

    def _run(self, *args, input_data: Optional[str] = None, capture_output: bool = True, options: Optional[list] = None) -> subprocess.CompletedProcess:
        """
        执行 agent-browser 命令

        Args:
            *args: 命令和命令参数
            input_data: 标准输入数据
            capture_output: 是否捕获输出
            options: 命令特定选项（在命令名称之后）

        Returns:
            subprocess.CompletedProcess 对象

        Raises:
            AgentBrowserError: 命令执行失败
        """
        # 构建完整命令: agent-browser [global-options] <command> [command-options] [args]
        cmd = self._base_cmd.copy()

        # 添加命令和参数
        cmd.extend(args)

        # 添加命令特定选项（在命令之后）
        if options:
            cmd.extend(options)

        try:
            result = subprocess.run(
                cmd,
                input=input_data,
                text=True,
                capture_output=capture_output,
                timeout=self.timeout / 1000,  # 转换为秒
            )

            if result.returncode != 0:
                raise AgentBrowserError(
                    f"agent-browser 命令失败: {' '.join(cmd)}\n"
                    f"返回码: {result.returncode}\n"
                    f"错误输出: {result.stderr}"
                )

            return result

        except subprocess.TimeoutExpired:
            raise AgentBrowserError(f"agent-browser 命令超时: {' '.join(cmd)}")
        except FileNotFoundError:
            raise AgentBrowserError("agent-browser 未安装或不在 PATH 中")
        except Exception as e:
            raise AgentBrowserError(f"agent-browser 命令异常: {e}")

    def snapshot(self, interactive_only: bool = True, save_to: Optional[str] = None) -> Dict:
        """
        获取页面快照（Accessibility Tree）

        Args:
            interactive_only: 是否只返回可交互元素（-i 参数）
            save_to: 可选，保存快照到文件路径

        Returns:
            快照 JSON 字典，包含 elements 列表

        示例返回:
            {
                "elements": [
                    {
                        "ref": "@e1",
                        "role": "textbox",
                        "name": "关键词搜索",
                        "placeholder": "请输入关键词",
                        "visible": true
                    },
                    ...
                ]
            }
        """
        # 命令特定选项
        options = []
        if interactive_only:
            options.append("-i")
        options.append("--json")

        result = self._run("snapshot", options=options)
        response = json.loads(result.stdout)

        # agent-browser 返回格式: {"success": true, "data": {"refs": {...}, "snapshot": "..."}}
        if not response.get("success"):
            error = response.get("error", "Unknown error")
            raise AgentBrowserError(f"Snapshot failed: {error}")

        # 转换为标准格式
        refs_dict = response.get("data", {}).get("refs", {})
        elements = []

        for ref_id, elem_data in refs_dict.items():
            elements.append({
                "ref": f"@{ref_id}",  # 添加 @ 前缀
                "role": elem_data.get("role", ""),
                "name": elem_data.get("name", ""),
                "placeholder": elem_data.get("placeholder", ""),
                "visible": True,  # agent-browser 默认只返回可见元素
            })

        snapshot = {"elements": elements}
        self._last_snapshot = snapshot

        # 更新元素引用映射
        for elem in elements:
            ref = elem.get("ref")
            if ref:
                name = elem.get("name") or elem.get("placeholder") or elem.get("role")
                self._element_refs[ref] = name

        # 保存快照到文件
        if save_to:
            Path(save_to).parent.mkdir(parents=True, exist_ok=True)
            with open(save_to, "w", encoding="utf-8") as f:
                json.dump(snapshot, f, ensure_ascii=False, indent=2)

        return snapshot

    def goto(self, url: str, wait_until: str = "networkidle") -> None:
        """
        导航到 URL

        Args:
            url: 目标 URL
            wait_until: 等待条件（load | domcontentloaded | networkidle）
        """
        # agent-browser 使用 "open" 命令
        self._run("open", url)

    def click(
        self,
        ref: Optional[str] = None,
        role: Optional[str] = None,
        name: Optional[str] = None,
        placeholder: Optional[str] = None,
        text: Optional[str] = None,
        wait_ms: int = 500
    ) -> None:
        """
        点击元素（支持多种定位方式）

        Args:
            ref: 元素引用（如 @e1）
            role: ARIA 角色（如 button, link）
            name: 可访问名称（如按钮文本）
            placeholder: 占位符文本
            text: 元素文本内容
            wait_ms: 点击后等待时间（毫秒）

        示例:
            browser.click(ref="@e5")
            browser.click(role="button", name="查询")
            browser.click(placeholder="请输入关键词")
        """
        locator = self._build_locator(ref, role, name, placeholder, text)
        self._run("click", locator)
        if wait_ms > 0:
            time.sleep(wait_ms / 1000)

    def fill(
        self,
        ref: Optional[str] = None,
        placeholder: Optional[str] = None,
        value: str = "",
        wait_ms: int = 300
    ) -> None:
        """
        填充输入框

        Args:
            ref: 元素引用（如 @e1）
            placeholder: 占位符文本
            value: 要填充的值
            wait_ms: 填充后等待时间（毫秒）
        """
        locator = self._build_locator(ref=ref, placeholder=placeholder)
        # agent-browser fill 命令: fill <selector> <text>
        self._run("fill", locator, value)
        if wait_ms > 0:
            time.sleep(wait_ms / 1000)

    def press(self, key: str, wait_ms: int = 500) -> None:
        """
        按下键盘按键

        Args:
            key: 按键名称（Enter, Escape, Tab, ArrowDown 等）
            wait_ms: 按键后等待时间（毫秒）
        """
        self._run("press", key)
        if wait_ms > 0:
            time.sleep(wait_ms / 1000)

    def wait(self, ms: int) -> None:
        """
        等待指定时间

        Args:
            ms: 等待时间（毫秒）
        """
        time.sleep(ms / 1000)

    def get_content(self) -> str:
        """
        获取页面内容（HTML）

        Returns:
            页面 HTML 内容
        """
        # agent-browser 使用 eval 执行 JavaScript
        result = self._run("eval", "document.documentElement.outerHTML")
        return result.stdout

    def screenshot(self, save_to: str, fullpage: bool = False) -> None:
        """
        截图

        Args:
            save_to: 保存路径（PNG 格式）
            fullpage: 是否全页截图
        """
        options = []
        if fullpage:
            options.append("--full")

        Path(save_to).parent.mkdir(parents=True, exist_ok=True)
        self._run("screenshot", save_to, options=options)

    def close(self) -> None:
        """
        关闭浏览器会话
        """
        try:
            self._run("close")
        except AgentBrowserError:
            pass  # 会话可能已关闭

    def _build_locator(
        self,
        ref: Optional[str] = None,
        role: Optional[str] = None,
        name: Optional[str] = None,
        placeholder: Optional[str] = None,
        text: Optional[str] = None,
    ) -> str:
        """
        构建语义化定位器

        优先级：ref > placeholder > name > role+name > text

        Returns:
            定位器字符串

        示例:
            @e5
            placeholder="请输入关键词"
            role="button" name="查询"
            text="查看详情"
        """
        if ref:
            return ref

        if placeholder:
            return f'placeholder="{placeholder}"'

        if name:
            if role:
                return f'role="{role}" name="{name}"'
            return f'name="{name}"'

        if text:
            return f'text="{text}"'

        if role:
            return f'role="{role}"'

        raise AgentBrowserError("必须提供至少一个定位参数")

    def find_element_by_text(self, text: str, role: Optional[str] = None) -> Optional[Dict]:
        """
        通过文本查找元素（从最后一次快照）

        Args:
            text: 文本内容（支持模糊匹配）
            role: 可选，限定角色类型

        Returns:
            元素字典，如果未找到返回 None
        """
        if not self._last_snapshot:
            return None

        text_lower = text.lower()

        for elem in self._last_snapshot.get("elements", []):
            # 检查角色匹配
            if role and elem.get("role") != role:
                continue

            # 检查文本匹配
            name = elem.get("name", "").lower()
            placeholder = elem.get("placeholder", "").lower()

            if text_lower in name or text_lower in placeholder:
                return elem

        return None

    def extract_table_data(self, snapshot: Optional[Dict] = None) -> List[Dict[str, str]]:
        """
        从快照中提取表格数据

        Args:
            snapshot: 快照字典，如果为 None 则使用最后一次快照

        Returns:
            表格行列表，每行是一个字典

        示例返回:
            [
                {"ref": "@e10", "title": "软件开发项目", "date": "2024-01-15"},
                {"ref": "@e11", "title": "系统集成服务", "date": "2024-01-16"},
            ]
        """
        if snapshot is None:
            snapshot = self._last_snapshot

        if not snapshot:
            return []

        # 查找表格相关元素
        table_rows = []
        current_row = {}

        for elem in snapshot.get("elements", []):
            role = elem.get("role", "")
            name = elem.get("name", "")
            ref = elem.get("ref", "")

            # 识别表格行（row, gridcell 等）
            if role in ["row", "gridcell", "cell"]:
                if name:
                    current_row[role] = name
                    current_row["ref"] = ref

            # 识别链接（可能是标题）
            if role == "link" and name:
                if current_row:
                    current_row["title"] = name
                    current_row["ref"] = ref
                else:
                    current_row = {"title": name, "ref": ref}

            # 识别完整的行（当遇到新行或特定分隔符）
            if current_row and len(current_row) >= 2:
                table_rows.append(current_row.copy())
                current_row = {}

        return table_rows

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.close()

    def __repr__(self):
        return f"AgentBrowser(session='{self.session_name}', headless={self.headless})"
