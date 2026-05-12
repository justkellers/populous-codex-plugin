# Populous Codex Plugin Marketplace

This repository is a GitHub-backed Codex plugin marketplace for Populous. It exposes one installable plugin, `populous`, which connects Codex to the Populous MCP server:

```text
https://run.populous.app/mcp
```

Use it when Codex should help create target populations, configure experiments, run simulations, inspect simulation analysis, import shared simulations, or run autonomous research tasks in Populous.

## Install

Add this marketplace to Codex:

```bash
codex plugin marketplace add justkellers/populous-codex-plugin
```

Restart Codex after adding the marketplace. Populous should appear as an installable plugin and prompt for authentication when the MCP server requires it.

Self-serve publishing to the official Codex Plugin Directory is not assumed here; this repo is intended for GitHub-backed marketplace installation.

## Repository layout

- `.agents/plugins/marketplace.json` registers the Populous plugin for Codex marketplace installation.
- `plugins/populous/.codex-plugin/plugin.json` defines the plugin metadata.
- `plugins/populous/.mcp.json` registers the Populous MCP server.
- `plugins/populous/skills/populous/SKILL.md` gives Codex Populous-specific workflow guidance.
- `plugins/populous/scripts/validate_plugin.py` validates the marketplace, plugin manifest, and MCP config.
- `plugins/populous/scripts/check_mcp_health.sh` checks whether the MCP endpoint is reachable.

## Validation

Run the package checks:

```bash
python3 plugins/populous/scripts/validate_plugin.py
jq empty .agents/plugins/marketplace.json plugins/populous/.codex-plugin/plugin.json plugins/populous/.mcp.json
```

Check remote MCP reachability:

```bash
plugins/populous/scripts/check_mcp_health.sh
```

For an authenticated smoke test, set `POPULOUS_ACCESS_TOKEN` in your shell and rerun the health check. Do not commit tokens or paste them into docs.

## MCP-only fallback

If you only need the MCP server and not the full plugin metadata or skill guidance, add this to `~/.codex/config.toml` and restart Codex:

```toml
[mcp_servers.populous]
url = "https://run.populous.app/mcp"
```

The marketplace install path is preferred because it carries the Populous workflow guidance in `plugins/populous/skills/populous/SKILL.md`.
