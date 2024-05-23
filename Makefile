install:
	@echo "Installing dependencies..."
	cd gsp && poetry install

scrape:
	@echo "Scraping..."
	cd gsp && poetry run poe scrape

fmt-check:
	@echo "Checking formatting..."
	cd gsp && poetry run poe fmt-check

fmt:
	@echo "Formatting..."
	cd gsp && poetry run poe fmt

typecheck:
	@echo "Typechecking..."
	cd gsp && poetry run poe typecheck

lint:
	@echo "Linting..."
	cd gsp && poetry run poe lint

test:
	@echo "Testing..."
	cd gsp && poetry run poe test

test-dev:
	@echo "Testing marker 'dev'..."
	cd gsp && poetry run poe test-dev

test-coverage:
	@echo "Testing with coverage..."
	cd gsp && poetry run poe test-cov

convert:
	@echo "Converting notebooks..."
	cd gsp && poetry run poe convert


pipeline:
	@echo "Running pipeline..."
	cd gsp && poetry run poe pipeline 
