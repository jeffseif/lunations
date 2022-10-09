# Python

PYTHON = $(shell which python3)
SHELL = /bin/bash
VENV_DIR = venv

.PHONY: lint
lint:
	@$(PYTHON) -m venv $(VENV_DIR)
	@$(VENV_DIR)/bin/pip install --quiet --upgrade pip
	@$(VENV_DIR)/bin/pip install --quiet pre-commit
	@$(VENV_DIR)/bin/pre-commit install
	@$(VENV_DIR)/bin/pre-commit run --all-files

.PHONY: clean
clean:
	@git clean -fdfx

# Data

.SECONDARY:

UPSTREAM_REPO_ZIP = moon-data-master.zip
RAW_DATA_CSV = lunations.csv.gz

.INTERMEDIATE: $(RAW_DATA_CSV)
$(RAW_DATA_CSV): $(UPSTREAM_REPO_ZIP)
	@echo 'timezonetz,lunar_phase' \
		| gzip \
		> $@
	@unzip -p $< moon-data-master/api/moon-phase-data/*/index.json \
		| jq --compact-output --raw-output '.[] | [.Date, .Phase] | @tsv' \
		| sed 's/\t/+00,/' \
		| sort --numeric-sort \
		| gzip \
		>> $@

.INTERMEDIATE: $(UPSTREAM_REPO_ZIP)
$(UPSTREAM_REPO_ZIP):
	@curl \
		--location \
		--output $@ \
		https://github.com/CraigChamberlain/moon-data/archive/master.zip

# Docker

MODULE_NAME = $(notdir $(shell pwd))
DOCKER_TAG = $(MODULE_NAME)

ifdef FORECAST_EPOCH_TIMESTAMP
	FORECAST_CLI_ARGS=--forecast-epoch-timestamp=$(FORECAST_EPOCH_TIMESTAMP)
endif

LIBRARY_DATA_JSON = lunations.json.gz

.PHONY: forecast
forecast:
	@$(MAKE) build
	@docker compose run --rm $(DOCKER_TAG) \
		python -m $(MODULE_NAME) forecast \
			$(FORECAST_CLI_ARGS)

.PHONY: retrain
retrain: ./dat/$(LIBRARY_DATA_JSON)

./dat/$(LIBRARY_DATA_JSON): $(RAW_DATA_CSV)
	@$(MAKE) build
	@docker compose run --rm $(DOCKER_TAG) \
		python -m $(MODULE_NAME) model \
			--path-to-csv-input=/code/$< \
			--path-to-json-output=/code/dat/$(LIBRARY_DATA_JSON)

.PHONY: build
build: $(RAW_DATA_CSV)
	@docker compose build --pull
