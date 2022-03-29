.PHONY: install docs

DOCS_TARGET := ./docs/api-reference/packages

install:
	poetry install

docs:
	mkdir -p $(DOCS_TARGET)/core
	mkdir -p $(DOCS_TARGET)/plugins

	$(MAKE) --directory=packages/core/minos-microservice-aggregate install docs
	cp -R packages/core/minos-microservice-aggregate/docs/_build/html $(DOCS_TARGET)/core/minos-microservice-aggregate

	$(MAKE) --directory=packages/core/minos-microservice-common install docs
	cp -R packages/core/minos-microservice-common/docs/_build/html $(DOCS_TARGET)/core/minos-microservice-common

	$(MAKE) --directory=packages/core/minos-microservice-cqrs install docs
	cp -R packages/core/minos-microservice-cqrs/docs/_build/html $(DOCS_TARGET)/core/minos-microservice-cqrs

	$(MAKE) --directory=packages/core/minos-microservice-networks install docs
	cp -R packages/core/minos-microservice-networks/docs/_build/html $(DOCS_TARGET)/core/minos-microservice-networks

	$(MAKE) --directory=packages/core/minos-microservice-saga install docs
	cp -R packages/core/minos-microservice-saga/docs/_build/html $(DOCS_TARGET)/core/minos-microservice-saga

	$(MAKE) --directory=packages/plugins/minos-broker-kafka install docs
	cp -R packages/plugins/minos-broker-kafka/docs/_build/html $(DOCS_TARGET)/plugins/minos-broker-kafka

	$(MAKE) --directory=packages/plugins/minos-broker-rabbitmq install docs
	cp -R packages/plugins/minos-broker-rabbitmq/docs/_build/html $(DOCS_TARGET)/plugins/minos-broker-rabbitmq

	$(MAKE) --directory=packages/plugins/minos-discovery-minos install docs
	cp -R packages/plugins/minos-discovery-minos/docs/_build/html $(DOCS_TARGET)/plugins/minos-discovery-minos

	$(MAKE) --directory=packages/plugins/minos-http-aiohttp install docs
	cp -R packages/plugins/minos-http-aiohttp/docs/_build/html $(DOCS_TARGET)/plugins/minos-http-aiohttp

	$(MAKE) --directory=packages/plugins/minos-router-graphql install docs
	cp -R packages/plugins/minos-router-graphql/docs/_build/html $(DOCS_TARGET)/plugins/minos-router-graphql


	poetry run $(MAKE) --directory=docs html
