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