# soorma-dev

Tooling for working by soorma.ai's development methodology.

> **Status: pre-release.** One plugin so far, [`soorma-review`](plugins/soorma-review/README.md), with
> one skill for reviewing working sessions. Names and behaviour may change until a first release.

## What this is

soorma.ai builds software with a methodology in two parts: AI-PRD, which turns intent into
approved requirements and a backlog, and AI-DLC, which turns approved requirements into a
reviewed implementation. Both are defined as rules that an AI coding agent follows, with a human
approving at every gate that matters: merges, tags, repository settings, legal text, and
decisions.

`soorma-dev` packages procedures for working that way as [Claude Code](https://docs.claude.com/en/docs/claude-code)
plugins. A plugin here carries a procedure, and points at the methodology's rules rather than
restating them.

## Plugins

| Plugin | What it does |
|---|---|
| [`soorma-review`](plugins/soorma-review/README.md) | Review an AI agent's working session as its reviewer: verify its claims against git, GitHub and CI, merge with the human approver, and hand back paste-ready instructions |

This repository is a Claude Code plugin marketplace:

```sh
claude plugin marketplace add soorma-ai/soorma-dev
claude plugin install soorma-review@soorma-dev
```

How to run a review session with it, and how to try it from a local checkout: see
[Using it](plugins/soorma-review/README.md#using-it) and
[Install](plugins/soorma-review/README.md#install) in the plugin's README.

## What this is not, yet

- **Not the methodology's rules.** They are maintained separately; plugins here link to them at
  pinned versions.
- **Not an agent harness.** Running a generating agent and a reviewing agent as a pair, with
  instructions passed between them as messages, is the long-term direction. Today a human passes
  them.
- **Not stable.** Names, layout, and behaviour may change until a first release is tagged.

## Licence

**Source-available, not open source.** `soorma-dev` is licensed under [FSL-1.1-ALv2](LICENSE):
you may do anything with it except offer a commercial product or service that competes with
soorma.ai. Internal use at any scale, research, and education are all permitted.

**Each release becomes Apache 2.0 two years after it ships**, automatically, and not revocably by
soorma.ai.

[`LICENSE`](LICENSE) is authoritative; the above is a summary.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). Contributions require a signed Contributor License
Agreement: [`CLA.md`](CLA.md) for individuals, [`CCLA.md`](CCLA.md) for organizations.

For anything security-sensitive, email founders@soorma.ai rather than opening a public issue.
