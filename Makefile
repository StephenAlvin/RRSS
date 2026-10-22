# Same commands as package.json, for people without Node.
.PHONY: setup dev build generate data clean

setup:
	python3 -m venv venv && venv/bin/pip install --upgrade pip && venv/bin/pip install -r requirements.txt

dev:
	SITE_URL=http://127.0.0.1:8000/ DISABLE_MKDOCS_2_WARNING=true venv/bin/mkdocs serve --dirty

build:
	DISABLE_MKDOCS_2_WARNING=true venv/bin/mkdocs build --strict

generate:
	venv/bin/python -I tools/build.py --skip-fetch --skip-sprites

data:
	venv/bin/python -I tools/build.py

clean:
	rm -rf site
