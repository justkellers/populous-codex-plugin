#!/usr/bin/env python3
"""Validate the Populous Codex marketplace package."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
PLUGIN_JSON = PLUGIN_ROOT / ".codex-plugin" / "plugin.json"
MCP_JSON = PLUGIN_ROOT / ".mcp.json"
MARKETPLACE_JSON = REPO_ROOT / ".agents" / "plugins" / "marketplace.json"
EXPECTED_MCP_URL = "https://run.populous.app/mcp"
EXPECTED_REPOSITORY = "https://github.com/justkellers/populous-codex-plugin"


errors: list[str] = []
warnings: list[str] = []


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def load_json_text(text: str, source: str) -> dict[str, Any]:
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        errors.append(f"Invalid JSON in {source}: {exc}")
        return {}

    if not isinstance(data, dict):
        errors.append(f"{source} must contain a JSON object")
        return {}
    return data


def load_marketplace_json() -> dict[str, Any]:
    if MARKETPLACE_JSON.exists():
        return load_json(MARKETPLACE_JSON)

    try:
        result = subprocess.run(
            ["git", "show", ":.agents/plugins/marketplace.json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        fallback = REPO_ROOT / "marketplace.example.json"
        warnings.append("Using marketplace.example.json because .agents is unavailable in this local sandbox")
        return load_json(fallback)

    return load_json_text(result.stdout, ".agents/plugins/marketplace.json from git index")


def load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError:
        errors.append(f"Missing required file: {rel(path)}")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(f"Invalid JSON in {rel(path)}: {exc}")
        return {}

    if not isinstance(data, dict):
        errors.append(f"{rel(path)} must contain a JSON object")
        return {}
    return data


def require_string(obj: dict[str, Any], key: str, context: str) -> str:
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{context}.{key} must be a non-empty string")
        return ""
    return value


def require_path(root: Path, path_value: str, context: str, expect_dir: bool = False) -> None:
    if not path_value.startswith("./"):
        errors.append(f"{context} should be a relative path beginning with ./")
        return

    target = root / path_value[2:]
    if expect_dir and not target.is_dir():
        errors.append(f"{context} points to a missing directory: {path_value}")
    elif not expect_dir and not target.is_file():
        errors.append(f"{context} points to a missing file: {path_value}")


def reject_todos(value: Any, context: str) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            reject_todos(child, f"{context}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            reject_todos(child, f"{context}[{index}]")
    elif isinstance(value, str) and "TODO" in value:
        errors.append(f"{context} contains a TODO placeholder")


def validate_plugin_json(plugin: dict[str, Any]) -> None:
    required_top_level = [
        "name",
        "version",
        "description",
        "homepage",
        "repository",
        "license",
        "skills",
        "mcpServers",
    ]
    for key in required_top_level:
        require_string(plugin, key, "plugin")

    if plugin.get("name") != "populous":
        errors.append('plugin.name must be "populous"')
    if plugin.get("repository") != EXPECTED_REPOSITORY:
        errors.append(f'plugin.repository must be "{EXPECTED_REPOSITORY}"')

    require_path(PLUGIN_ROOT, str(plugin.get("skills", "")), "plugin.skills", expect_dir=True)
    require_path(PLUGIN_ROOT, str(plugin.get("mcpServers", "")), "plugin.mcpServers")

    author = plugin.get("author")
    if not isinstance(author, dict):
        errors.append("plugin.author must be an object")
    else:
        for key in ["name", "email", "url"]:
            require_string(author, key, "plugin.author")

    interface = plugin.get("interface")
    if not isinstance(interface, dict):
        errors.append("plugin.interface must be an object")
        return

    for key in [
        "displayName",
        "shortDescription",
        "longDescription",
        "developerName",
        "category",
        "websiteURL",
        "privacyPolicyURL",
        "termsOfServiceURL",
        "brandColor",
        "composerIcon",
        "logo",
    ]:
        require_string(interface, key, "plugin.interface")

    require_path(PLUGIN_ROOT, str(interface.get("composerIcon", "")), "plugin.interface.composerIcon")
    require_path(PLUGIN_ROOT, str(interface.get("logo", "")), "plugin.interface.logo")

    capabilities = interface.get("capabilities")
    if not isinstance(capabilities, list) or not all(isinstance(item, str) for item in capabilities):
        errors.append("plugin.interface.capabilities must be a list of strings")

    prompts = interface.get("defaultPrompt")
    if not isinstance(prompts, list) or not all(isinstance(item, str) for item in prompts):
        errors.append("plugin.interface.defaultPrompt must be a list of strings")
    else:
        if len(prompts) > 3:
            errors.append("plugin.interface.defaultPrompt must contain at most 3 prompts")
        for index, prompt in enumerate(prompts, start=1):
            if len(prompt) > 128:
                errors.append(f"plugin.interface.defaultPrompt[{index}] is longer than 128 characters")

    screenshots = interface.get("screenshots")
    if not isinstance(screenshots, list):
        errors.append("plugin.interface.screenshots must be a list")
    else:
        for screenshot in screenshots:
            if not isinstance(screenshot, str):
                errors.append("plugin.interface.screenshots must contain only strings")
                continue
            require_path(PLUGIN_ROOT, screenshot, f"plugin.interface.screenshots entry {screenshot}")


def validate_mcp_json(mcp: dict[str, Any]) -> None:
    server = mcp.get("populous")
    if not isinstance(server, dict):
        errors.append(".mcp.json must contain a populous server object")
        return

    url = server.get("url")
    if url != EXPECTED_MCP_URL:
        errors.append(f'mcpServers.populous.url must be "{EXPECTED_MCP_URL}"')

    if "headers" in server:
        warnings.append(".mcp.json contains headers; do not commit bearer tokens or secrets")


def validate_marketplace_json(marketplace: dict[str, Any]) -> None:
    if marketplace.get("name") != "populous-marketplace":
        errors.append('marketplace.name must be "populous-marketplace"')

    interface = marketplace.get("interface")
    if not isinstance(interface, dict) or interface.get("displayName") != "Populous":
        errors.append('marketplace.interface.displayName must be "Populous"')

    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list) or len(plugins) != 1:
        errors.append("marketplace.plugins must contain exactly one plugin")
        return

    entry = plugins[0]
    if not isinstance(entry, dict):
        errors.append("marketplace.plugins[0] must be an object")
        return

    if entry.get("name") != "populous":
        errors.append('marketplace plugin name must be "populous"')

    source = entry.get("source")
    if not isinstance(source, dict):
        errors.append("marketplace plugin source must be an object")
    else:
        if source.get("source") != "local":
            errors.append('marketplace plugin source.source must be "local"')
        if source.get("path") != "./plugins/populous":
            errors.append('marketplace plugin source.path must be "./plugins/populous"')
        require_path(REPO_ROOT, str(source.get("path", "")), "marketplace plugin source.path", expect_dir=True)

    policy = entry.get("policy")
    if not isinstance(policy, dict):
        errors.append("marketplace plugin policy must be an object")
    else:
        if policy.get("installation") != "AVAILABLE":
            errors.append('marketplace policy.installation must be "AVAILABLE"')
        if policy.get("authentication") != "ON_USE":
            errors.append('marketplace policy.authentication must be "ON_USE"')

    if entry.get("category") != "Productivity":
        errors.append('marketplace category must be "Productivity"')


def main() -> int:
    plugin = load_json(PLUGIN_JSON)
    mcp = load_json(MCP_JSON)
    marketplace = load_marketplace_json()

    reject_todos(plugin, "plugin")
    reject_todos(mcp, "mcp")
    reject_todos(marketplace, "marketplace")

    validate_plugin_json(plugin)
    validate_mcp_json(mcp)
    validate_marketplace_json(marketplace)

    if errors:
        print("Validation failed:")
        for item in errors:
            print(f"- {item}")
        return 1

    print("Validation passed for marketplace.json, plugin.json, and .mcp.json.")
    if warnings:
        print("Warnings:")
        for item in warnings:
            print(f"- {item}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
