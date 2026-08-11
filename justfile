PYFILES := `echo *.py`

check:
  ruff check {{PYFILES}}
  ty check {{PYFILES}}
  vermin -vv --no-tips -i {{PYFILES}}
  md-link-checker

build:
  rm -rf dist
  uv build

upload: build
  uv-publish

doc:
  update-readme-usage -A -S "s/cdhist/cd/g"

format:
  ruff check --select I --fix {{PYFILES}} && ruff format {{PYFILES}}

clean:
  @rm -vrf uv.lock *.egg-info build/ dist/ __pycache__/
