"""MkDocs hook: re-parse the documentation and regenerate the wiki pages before every build.

This is what makes `npm run dev` pick up edits to Documentation/*.txt and tools/*.py automatically.
Set RRSS_SKIP_GENERATE=1 to build the pages exactly as they are on disk.
"""
import logging
import os
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
log = logging.getLogger("mkdocs.hooks.rrss")


def on_pre_build(config, **kwargs):
    if os.environ.get("RRSS_SKIP_GENERATE"):
        return
    for script in ("parse_docs.py", "generate_site.py"):
        result = subprocess.run([sys.executable, "-I", str(TOOLS / script)], capture_output=True, text=True)
        tail = (result.stdout.strip().splitlines() or [""])[-1]
        log.info("%s: %s", script, tail)
        for line in result.stderr.strip().splitlines():
            log.warning("%s: %s", script, line)
        if result.returncode != 0:
            raise RuntimeError(f"{script} failed (exit code {result.returncode})")
