PROJECT_TEST_DIR:=tests
PROJECT_NAME:=sleepcounter

.PHONY: clean
clean:
	echo "CLEANING..."
	rm -rf build dist

.PHONY: install-requirements
install-requirements:
	echo "INSTALLING REQUIREMENTS..."
	pip install -r requirements.txt

.PHONY: install
install: install-requirements
	echo "INSTALLING PYTHON MODULE..."
	pip install -e . --no-deps

.PHONY: check
check: install
	pylint $(PROJECT_NAME) --reports=y

.PHONY: test
test: install | $(PROJECT_TEST_DIR)
	echo "RUNNING PYTEST..."
	pytest -sxv --log-cli-level=INFO $(PROJECT_TEST_DIR)

.PHONY: wheel
wheel: test check
	echo "BUILDING WHEEL..."
	python setup.py bdist_wheel