.SECONDARY:
MODULE_NAME = $(notdir $(shell pwd))
DOCKER_TAG = $(MODULE_NAME)
GIT_SHA=$(shell git rev-parse HEAD)

ifndef VERBOSE
	DOCKER_BUILD_ARGS=--quiet
endif

UPSTREAM_REPO_ZIP = moon-data-master.zip
RAW_DATA_CSV = lunations.csv.gz
LIBRARY_DATA_JSON = lunations.json.gz


$(LIBRARY_DATA_JSON): run $(RAW_DATA_CSV)
	@docker cp \
		$(RAW_DATA_CSV) \
		$(DOCKER_TAG):/code/
	@docker exec \
		$(DOCKER_TAG) \
		/code/venv/bin/python -m $(MODULE_NAME) \
		--path-to-csv-input=/code/$(RAW_DATA_CSV) \
		--path-to-json-output=/code/$(LIBRARY_DATA_JSON)
	@docker cp \
		$(DOCKER_TAG):/code/$(LIBRARY_DATA_JSON) \
		$@


.PHONY: run
run: build stop
	# Run a fresh container
	@docker run \
		--detach \
		--interactive \
		--name=$(DOCKER_TAG) \
		--tty \
		$(DOCKER_TAG)


.PHONY: build
build: Dockerfile requirements-minimal.txt $(shell find $(DOCKER_TAG) -type f)
	# Build a fresh image
	@docker build \
		$(DOCKER_BUILD_ARGS) \
		--build-arg=GIT_SHA=$(GIT_SHA) \
		--tag $(DOCKER_TAG) \
		.

.PHONY: stop
stop:
	# Stop and remove container
	@docker container stop \
		--time=1 \
		$(DOCKER_TAG) \
		2>&1 > /dev/null || true
	@docker container rm \
		$(DOCKER_TAG) \
		2>&1 > /dev/null || true


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
