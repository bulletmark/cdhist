PYFILES := `echo *.py`

check:
  ruff check {{PYFILES}}
  ty check {{PYFILES}}
  md-link-checker

build:
  rm -rf dist
  uv build

upload: build
  uv-publish

doc:
  update-readme-usage -r cd

format:
  ruff check --select I --fix {{PYFILES}} && ruff format {{PYFILES}}

clean:
  @rm -vrf uv.lock *.egg-info build/ dist/ __pycache__/
