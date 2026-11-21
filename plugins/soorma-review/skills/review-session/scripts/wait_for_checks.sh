#!/usr/bin/env bash
# SPDX-License-Identifier: FSL-1.1-ALv2
#
# Wait for a pull request's checks to finish, then print each one.
#
#   bash wait_for_checks.sh OWNER/REPO PR [EXPECTED_HEAD_SHA] [TIMEOUT_SECONDS]
#
# With EXPECTED_HEAD_SHA, it first waits until the PR's head is that commit, so
# results from an older head are never read as current. Runs under bash on
# purpose: zsh doesn't word-split, and macOS bash 3 lacks associative arrays,
# so values are read with `read -r`. Uses gh's built-in --jq; no jq needed.
#
# Exit status: 0 when every check passed or was skipped, 1 when any failed,
# 2 on timeout.

set -u

repo=${1:?usage: wait_for_checks.sh OWNER/REPO PR [EXPECTED_HEAD_SHA] [TIMEOUT_SECONDS]}
pr=${2:?usage: wait_for_checks.sh OWNER/REPO PR [EXPECTED_HEAD_SHA] [TIMEOUT_SECONDS]}
expected=${3:-}
timeout=${4:-1800}
interval=15
waited=0

summary_jq='[
  .headRefOid[0:12],
  (.statusCheckRollup | length),
  ([.statusCheckRollup[] | select((.status // "COMPLETED") != "COMPLETED" or (.state // "") == "PENDING" or (.state // "") == "EXPECTED")] | length)
] | @tsv'

while :; do
  line=$(gh pr view "${pr}" --repo "${repo}" --json headRefOid,statusCheckRollup --jq "${summary_jq}") || exit 1
  read -r head total pending <<< "${line}"
  if [ -n "${expected}" ] && [ "${head}" != "${expected:0:12}" ]; then
    state="head ${head}, waiting for ${expected:0:12}"
  elif [ "${total}" -gt 0 ] && [ "${pending}" -eq 0 ]; then
    break
  else
    state="head ${head}: ${pending} of ${total} checks pending"
  fi
  if [ "${waited}" -ge "${timeout}" ]; then
    echo "timed out after ${waited}s (${state})" >&2
    exit 2
  fi
  sleep "${interval}"
  waited=$((waited + interval))
done

echo "head ${head}: ${total} checks finished after ${waited}s"
gh pr view "${pr}" --repo "${repo}" --json statusCheckRollup --jq \
  '.statusCheckRollup[] | [(.name // .context), (.conclusion // .state), (.workflowName // ""), (.detailsUrl // .targetUrl // "")] | @tsv'

failed=$(gh pr view "${pr}" --repo "${repo}" --json statusCheckRollup --jq \
  '[.statusCheckRollup[] | (.conclusion // .state) | select(. != "SUCCESS" and . != "SKIPPED" and . != "NEUTRAL")] | length')
[ "${failed}" -eq 0 ]
