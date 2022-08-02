.SECONDARY:
MODULE_NAME = $(notdir $(shell pwd))
DOCKER_TAG = $(MODULE_NAME)
GIT_SHA=$(shell git rev-parse HEAD)

ifdef FORECAST_EPOCH_TIMESTAMP
	FORECAST_CLI_ARGS=--forecast-epoch-timestamp=$(FORECAST_EPOCH_TIMESTAMP)
endif

UPSTREAM_REPO_ZIP = moon-data-master.zip
RAW_DATA_CSV = lunations.csv.gz
LIBRARY_DATA_JSON = lunations.json.gz


.PHONY: forecast
forecast:
	@docker compose up --detach
	@docker compose exec \
		$(DOCKER_TAG) \
		/code/venv/bin/python -m $(MODULE_NAME) forecast \
		$(FORECAST_CLI_ARGS)
	@docker compose down


.PHONY: retrain
retrain: ./dat/$(LIBRARY_DATA_JSON)


./dat/$(LIBRARY_DATA_JSON): $(RAW_DATA_CSV)
	@docker compose up --detach
	@docker compose cp \
		$< \
		$(DOCKER_TAG):/code/
	@docker compose exec \
		$(DOCKER_TAG) \
		/code/venv/bin/python -m $(MODULE_NAME) model \
		--path-to-csv-input=/code/$< \
		--path-to-json-output=/code/$(LIBRARY_DATA_JSON)
	@docker compose cp \
		$(DOCKER_TAG):/code/$(LIBRARY_DATA_JSON) \
		$@
	@docker compose down


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
		--remote-name \
		https://github.com/CraigChamberlain/moon-data/archive/master.zip
