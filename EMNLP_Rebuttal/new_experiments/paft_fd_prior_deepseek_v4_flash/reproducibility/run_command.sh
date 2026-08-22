#!/usr/bin/env bash
set -euo pipefail

cd /Users/apple/PycharmProjects/tabular-synthesis/00_active/StructSynthFull
source scripts/load_api_env.sh

SYNTH_MAX_CONCURRENCY=8 SYNTH_SAMPLES_PER_CALL=20 MPLCONFIGDIR=/tmp/mpl MPLBACKEND=Agg PYTHONPATH=. venv/bin/python -u scripts/run_paft_fd_prior_full_synthesis.py   --datasets adult anxiety compas salary obesity_reg churn   --seeds 42,43,44,45,46   --n-samples-list 100,200,500,1000   --model deepseek-v4-flash   --max-concurrency 8   --samples-per-call 20   --output-root results/paft_fd_prior_llm_synthesis_deepseek_v4_flash   --skip-existing
