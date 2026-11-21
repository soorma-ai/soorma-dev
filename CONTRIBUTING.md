# Contributing to Soorma Dev

Thanks for your interest in the project. `soorma-dev` is tooling for working by
soorma.ai's development methodology: Claude Code plugins and skills that carry
the methodology's procedures. It is source-available under
[FSL-1.1-ALv2](LICENSE), with each release converting to Apache 2.0 two years
after it ships.

**Before anything else:** this repository is at its start. Its first
deliverable is a single plugin, and its scope will grow deliberately. Until it
has settled, the most useful contributions are questions and discussion in
issues rather than pull requests.

## Before you start

### Contributor License Agreement

All contributors must sign a Contributor License Agreement before their first
contribution can be merged. There are two routes:

- **Contributing on your own behalf** — sign [`CLA.md`](CLA.md). When you open a
  pull request a bot will comment with instructions; signing is a single comment
  on the pull request and is only required once.
- **Contributing on behalf of your employer**, or where your employer holds
  rights in work you do — your company signs [`CCLA.md`](CCLA.md) instead. This
  one cannot be signed by comment: it needs signature by someone authorised to
  bind the company. Email founders@soorma.ai to start that, and list the
  employees who will be contributing so their pull requests are recognised as
  covered.

If you are employed and unsure which applies, check with your employer before
signing the individual agreement — many employment contracts assign copyright in
work related to the employer's business.

The CLA lets the project license future versions under different terms. It does
**not** let us withdraw your contribution from the licence it was submitted
under: work contributed while `soorma-dev` is under FSL-1.1-ALv2 stays
available under FSL-1.1-ALv2 permanently, including that licence's automatic
conversion to Apache 2.0. See [`CLA.md`](CLA.md) for the reasoning.

### Third-party material

If a contribution contains anything you did not write yourself — vendored code,
a snippet from another project, generated output carrying its own terms — say so
in the pull request description and identify the source and its licence, and
mark it in the source file itself.

Material under terms that cannot be redistributed under this project's outbound
licensing cannot be accepted. Note that the bar here is **stricter than a
permissive project's**: because `soorma-dev` is source-available rather than
open source, some material that would be unproblematic in an MIT or Apache
project cannot be taken in — copyleft code in particular. If you are unsure
whether something qualifies, ask in the pull request rather than omitting it; a
disclosed dependency is a conversation, an undisclosed one is a licensing defect
that is expensive to unwind later.

This is the process referred to by the Contributor License Agreement, which asks
you to confirm you own the copyright in what you submit.

### What belongs in `soorma-dev`

- **Procedures, not the methodology itself.** The methodology is defined in
  soorma.ai's rule repositories. A skill here points at the rules it applies, at
  a pinned commit, rather than restating them.
- **Generic first, specifics apart.** A skill's procedure is written so that any
  team could follow it. What is particular to soorma.ai's repositories (their
  names, branch flow, required checks) lives in the plugin's `references/`.
- **Nothing private.** This repository is public. No email addresses beyond the
  project contact, tokens, passwords, internal hostnames, local paths, or
  excerpts of working-session transcripts. Lessons are paraphrased.

## Getting set up

You need [Claude Code](https://docs.claude.com/en/docs/claude-code) to try a
plugin, and Python 3 to run the repository checks.

## Making a change

1. **Open an issue first** for anything beyond a small fix.
2. **Branch from `dev`.** Pull requests target `dev`, not `main`.
3. **Run the checks** before you push: `python3 -I tools/validate.py`, which is
   what CI's `Validate` job runs.
4. **Update the docs** that your change makes wrong.

## Reporting bugs

Open an issue with the version, what you expected, what happened, and the
smallest reproduction you can manage. For anything security-sensitive, do not
open a public issue — email founders@soorma.ai instead.
