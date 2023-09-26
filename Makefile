.PHONY: all clean dist test docs linter coverage exe

EGG_INFO_FILE := src/stmpro.egg-info
VERSION_FILE := src/stmpro/_version.py

ifeq ($(OS),Windows_NT)
	PYTHON_COMMAND := python
else
	PYTHON_COMMAND := python3
endif


all: dist coverage linter docs

clean:
	-rm -rf dist .coverage $(EGG_INFO_FILE) $(VERSION_FILE)
	@$(MAKE) -C docs clean

dist:
	@echo "Building package"
	$(PYTHON_COMMAND) -m build
	@echo ""

test:
	@echo "Running tests"
	PYTHONPATH=$(PWD)/src python3 -m unittest -v
	@echo ""

docs: dist
	@echo "Generating documentation"
	@$(MAKE) -C docs html
	@echo ""

linter:
	@echo "Running Pylint for code quality checks"
	pylint src --exit-zero
	@echo ""

coverage:
	@echo "Running code coverage tests and report"
	coverage run
	coverage report
	coverage xml
	@echo ""

exe: dist
	@echo "Generating exe file"
	$(PYTHON_COMMAND) -m spec_file_generator
	pyinstaller stmpro.spec
	@echo ""