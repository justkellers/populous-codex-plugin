---
name: populous
description: Use when the user wants Codex to work with Populous through its MCP server, including creating populations, creating experiments, running simulations, checking results, importing shared simulations, or running autonomous research tasks.
---

# Populous

Use the Populous MCP server for customer-research and simulation workflows.

## MCP endpoint

- Server: `https://run.populous.app/mcp`
- Auth: OAuth bearer token handled by the client. Do not ask the user for raw tokens unless they are explicitly debugging auth, and never print secrets.

## Main tool groups

- Populations: `listPopulations`, `createPopulation`, `getPopulationStats`
- Experiments: `listExperiments`, `createExperiment`
- Simulations: `listSimulations`, `createSimulation`, `getSimulationStatus`, `getSimulationAnalysis`, `importSimulation`
- Autonomous tasks: `listAutonomousTasks`, `createAutonomousTask`, `addAutonomousTaskContext`, `runAutonomousTask`, `getAutonomousTaskStatus`, `getAutonomousTaskResults`

## Workflow guidance

1. For a full simulation, get or create a population first, then get or create an experiment, then call `createSimulation`.
2. Poll `getSimulationStatus` after `createSimulation`; only summarize results after `getSimulationAnalysis` returns completed analysis.
3. For website tests, keep `maxSteps` within the server cap and prefer the user's own scenario wording over invented task details.
4. For autonomous research tasks, preserve the user's stated KPI, population, context URLs, and budget constraints. Do not broaden the research question unless they ask.
5. When the user asks for business interpretation, separate what Populous returned from your own inference.

## Default framing

Populous is for pressure-testing product, positioning, pricing, feature, website, and outreach decisions with simulated target populations. It should complement real customer discovery, not replace it.
