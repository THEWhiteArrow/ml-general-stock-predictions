install:
	@echo "Installing dependencies..."
	cd nsp && poetry install

install-scraper:
	@echo "Installing scraper..."
	cd nsp && poetry run playwright install-deps
	cd nsp && poetry run playwright install


uninstall-scraper:
	@echo "Uninstalling scraper..."
	cd nsp && poetry run playwright uninstall

scrape:
	@echo "Scraping..."
	cd nsp && poetry run poe scrape

fmt-check:
	@echo "Checking formatting..."
	cd nsp && poetry run poe fmt-check

fmt:
	@echo "Formatting..."
	cd nsp && poetry run poe fmt

typecheck:
	@echo "Typechecking..."
	cd nsp && poetry run poe typecheck

lint:
	@echo "Linting..."
	cd nsp && poetry run poe lint