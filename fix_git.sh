#!/bin/bash
cd /data/.openclaw/workspace/ai-website
git rebase --abort || true
git fetch origin
git reset --hard origin/main
python3 build_index.py
git add .
git commit -m 'Auto-publish Copilot Katsaus'
git push
