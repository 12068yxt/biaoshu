#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块

Rule 1：所有可变参数放入 YAML 配置文件，配置变更热重载，禁止代码硬编码
Rule 2：多模型后端兼容（OpenRouter / 阿里云百炼 / OpenAI）
Rule 3：提示词文件化，system/user/examples 分离，Jinja2 变量渲染

职责：
- YAML 配置加载与热重载（检查文件 mtime）
- 多模型后端配置解析（backend: openrouter|dashscope|openai）
- API Key 从环境变量读取，禁止硬编码
- 提示词文件（system.txt/user.txt/examples.txt）读取与拼接
- 提示词模板变量渲染（Jinja2）
"""

import os
import yaml
from typing import Any, Dict, Optional, Tuple
from jinja2 import Template, Environment, BaseLoader


class ConfigManager:
    """
    配置管理器

    支持：
    - YAML 配置热重载（文件 mtime 变更自动重载）
    - 多后端 LLM 配置（openrouter / dashscope / openai）
    - API Key 优先从环境变量读取
    - 提示词文件路径配置与动态加载
    - Jinja2 模板变量渲染

    Attributes:
        config_path: YAML 配置文件路径（相对于工作目录）
        config_data: 解析后的完整配置字典
        _file_mtimes: 各配置文件的最后修改时间（用于热重载检测）
        _jinja_env: Jinja2 环境
    """

    def __init__(self, config_path: str = "config/standard.yaml") -> None:
        """
        初始化配置管理器并立即加载配置

        Args:
            config_path: YAML 配置文件路径

        Raises:
            FileNotFoundError: 配置文件不存在
            yaml.YAMLError: YAML 语法错误
        """
        self.config_path: str = config_path
        self.config_data: Dict[str, Any] = {}
        self._file_mtimes: Dict[str, float] = {}
        self._jinja_env = Environment(loader=BaseLoader())
        self._load_config()

    # ------------------------------------------------------------------
    # 配置加载与热重载
    # ------------------------------------------------------------------

    def _load_config(self) -> None:
        """
        加载 YAML 主配置文件，并记录所有相关文件的 mtime

        同时预读取提示词文件的 mtime，以便热重载时检测变化。
        """
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as f:
            self.config_data = yaml.safe_load(f)

        # 记录主配置文件 mtime
        self._file_mtimes[self.config_path] = os.path.getmtime(self.config_path)

        # 记录提示词文件的 mtime（用于热重载检测）
        prompts_cfg = self.config_data.get("prompts", {})
        for key in ("system_file", "user_file", "examples_file"):
            fp = prompts_cfg.get(key)
            if fp and os.path.exists(fp):
                self._file_mtimes[fp] = os.path.getmtime(fp)

    def reload_if_changed(self) -> bool:
        """
        检查所有被追踪文件是否发生变化，若有则重新加载

        支持热重载：配置文件或提示词文件修改后无需重启

        Returns:
            True 表示执行了重新加载，False 表示无变化
        """
        needs_reload = any(
            os.path.exists(fp) and os.path.getmtime(fp) > mtime
            for fp, mtime in self._file_mtimes.items()
        )
        if needs_reload:
            self._load_config()
            return True
        return False

    # ------------------------------------------------------------------
    # 配置获取
    # ------------------------------------------------------------------

    def get_style_config(self) -> Dict[str, Any]:
        """
        获取 SVG 视觉风格配置

        Returns:
            样式配置字典，包含 bg_color / text_color / font / colors 等
        """
        return self.config_data.get("style", {})

    def get_output_config(self) -> Dict[str, Any]:
        """
        获取输出路径配置

        Returns:
            输出配置字典，包含 svg_dir / report_file / mermaid_file 等
        """
        return self.config_data.get("output", {})

    def get_llm_config(self) -> Dict[str, Any]:
        """
        获取当前激活后端的 LLM 配置（Rule 2：多模型后端兼容）

        读取逻辑：
        1. 读取 llm.backend 字段确定后端类型（openrouter/dashscope/openai）
        2. 读取对应后端子配置（base_url、model、temperature、max_tokens）
        3. API Key 从环境变量读取（api_key_env 字段指定环境变量名）
        4. 通用重试参数从 llm 根级读取

        Returns:
            包含 base_url / api_key / model / temperature / max_tokens /
            retry_times / retry_base_delay 的扁平化配置字典
        """
        llm_root = self.config_data.get("llm", {})
        backend = llm_root.get("backend", "dashscope")

        # 取对应后端子配置
        backend_cfg: Dict[str, Any] = llm_root.get(backend, {})

        # 从环境变量读取 API Key（禁止硬编码）
        env_var: str = backend_cfg.get("api_key_env", "")
        api_key: str = os.environ.get(env_var, "")

        return {
            "backend": backend,
            "base_url": backend_cfg.get("base_url", ""),
            "api_key": api_key,
            "model": backend_cfg.get("model", "qwen-max"),
            "temperature": backend_cfg.get("temperature", 0.3),
            "max_tokens": backend_cfg.get("max_tokens", 4096),
            # 通用重试参数
            "retry_times": llm_root.get("retry_times", 2),
            "retry_base_delay": llm_root.get("retry_base_delay", 1.0),
        }

    # ------------------------------------------------------------------
    # 提示词加载与渲染（Rule 3）
    # ------------------------------------------------------------------

    def load_prompts(self) -> Tuple[str, str]:
        """
        加载并组合原始提示词（未渲染变量）

        加载逻辑：
        1. 从 standard.yaml 读取 prompts.system_file / user_file / examples_file
        2. 读取 system.txt 内容
        3. 读取 user.txt 内容
        4. 若 examples.txt 存在且非空，拼接到 system：
           system + "\n\n## 示例\n" + examples
        5. 返回 (system, user) 元组（未渲染变量）

        Returns:
            (system_prompt_template, user_prompt_template) 元组

        Raises:
            FileNotFoundError: system.txt 或 user.txt 不存在
        """
        prompts_cfg = self.config_data.get("prompts", {})
        system_file: str = prompts_cfg.get("system_file", "prompts/system.txt")
        user_file: str = prompts_cfg.get("user_file", "prompts/user.txt")
        examples_file: str = prompts_cfg.get("examples_file", "prompts/examples.txt")

        # 读取 system 提示词
        if not os.path.exists(system_file):
            raise FileNotFoundError(f"系统提示词文件不存在: {system_file}")
        with open(system_file, "r", encoding="utf-8") as f:
            system_prompt = f.read()

        # 读取 user 提示词模板
        if not os.path.exists(user_file):
            raise FileNotFoundError(f"用户提示词文件不存在: {user_file}")
        with open(user_file, "r", encoding="utf-8") as f:
            user_prompt = f.read()

        # 读取 examples 并拼接（可选）
        if os.path.exists(examples_file):
            with open(examples_file, "r", encoding="utf-8") as f:
                examples_content = f.read()
            if examples_content.strip():
                system_prompt = f"{system_prompt}\n\n## 示例\n{examples_content}"

        return system_prompt, user_prompt

    def render_prompts(
        self,
        title: str,
        content: str,
        hierarchy_path: str,
        **extra_vars: Any,
    ) -> Tuple[str, str]:
        """
        渲染提示词模板，填充章节变量和风格变量

        变量清单：
        - title：章节标题
        - content：章节正文（完整传递，不截断）
        - hierarchy_path：层级路径
        - bg_color / text_color / font：来自 style 配置
        - primary / secondary / accent / bg_light 等：来自 style.colors 配置
        - **extra_vars：调用方传入的额外变量

        Args:
            title: 章节标题
            content: 章节正文（完整，不截断）
            hierarchy_path: 上级标题路径
            **extra_vars: 额外模板变量

        Returns:
            (rendered_system, rendered_user) 渲染后的提示词元组
        """
        # 检查配置是否有变更（热重载）
        self.reload_if_changed()

        style = self.get_style_config()
        colors: Dict[str, str] = style.get("colors", {})

        # 构建模板变量字典（扁平化 colors 子键，方便 {{ primary }} 等直接引用）
        template_vars: Dict[str, Any] = {
            "title": title,
            "content": content,
            "hierarchy_path": hierarchy_path,
            "bg_color": style.get("bg_color", "#FFFFFF"),
            "text_color": style.get("text_color", "#1A2B4C"),
            "font": style.get("font", "Microsoft YaHei, Arial, sans-serif"),
            # 展开 colors 子键
            **colors,
            # 调用方额外变量（优先级最高，可覆盖上方）
            **extra_vars,
        }

        # 加载原始模板
        system_template, user_template = self.load_prompts()

        # 使用 Jinja2 渲染
        system_prompt = self._jinja_env.from_string(system_template).render(template_vars)
        user_prompt = self._jinja_env.from_string(user_template).render(template_vars)

        return system_prompt, user_prompt
