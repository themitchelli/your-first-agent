#!/bin/bash
# What the scheduler runs. Cron starts with an almost empty environment:
# no project folder, no (.venv), no API key. This script sets up all three.
cd "$(dirname "$0")"
export ANTHROPIC_API_KEY="$(cat ~/.anthropic-key)"
.venv/bin/python agent.py demo "Organise any new files in this folder the same way as before." --auto-approve
