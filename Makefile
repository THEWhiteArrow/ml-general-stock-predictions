install:
	@echo "Installing dependencies..."
	cd gsp && poetry install

install-scraper:
	@echo "Installing scraper..."
	cd gsp && poetry run playwright install-deps
	cd gsp && poetry run playwright install


uninstall-scraper:
	@echo "Uninstalling scraper..."
	cd gsp && poetry run playwright uninstall

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