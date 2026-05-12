# Publishing Notes

This repo is structured as a Codex marketplace. The marketplace entry lives in `.agents/plugins/marketplace.json`; the Populous plugin package lives in `plugins/populous`.

## Before sharing broadly

1. Confirm `license: "Proprietary"` is still the intended public metadata.
2. Decide whether `plugins/populous/assets/app-icon.png` is the final public icon.
3. Add screenshots under `plugins/populous/assets/` and reference them from `plugins/populous/.codex-plugin/plugin.json` if marketplace screenshots become required.
4. Run:

```bash
python3 plugins/populous/scripts/validate_plugin.py
plugins/populous/scripts/check_mcp_health.sh
```

5. Install from a clean Codex profile or machine, enable the plugin, and confirm authentication, MCP tool discovery, and one read-only Populous tool call.

## Marketplace install

Use this GitHub-backed marketplace source:

```bash
codex plugin marketplace add justkellers/populous-codex-plugin
```

If `codex` is not on PATH, use the bundled Codex app binary:

```bash
/Applications/Codex.app/Contents/Resources/codex plugin marketplace add justkellers/populous-codex-plugin
```

Do not add bearer tokens, API keys, or private endpoints to marketplace files, `.mcp.json`, docs, or examples.
