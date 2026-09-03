# 0002: Routers and setup skills are user-invoked; discipline skills are model-invoked

Date: 2026-09-02

## Context

A skill the model can invoke on its own costs context on every turn through its description and fires on loosely matching requests. A skill only the user can invoke costs nothing until called, but the agent cannot reach it when the task needs it.

## Decision

Skills that orchestrate or need a human in the loop (router, setup, connect, grill, and-now) set `disable-model-invocation: true` and `policy.allow_implicit_invocation: false`. Skills that hold reusable discipline (tech-audit, gsc-review, content, review, diagnose, links, distribution) are model-invoked with a description that names one trigger per branch.

## Consequences

A new skill is user-invoked unless the agent must reach it on its own; the description of a model-invoked skill is the contract and is edited with the same care as the steps.
