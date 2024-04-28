install:
	@echo "Installing dependencies..."
	poetry install

install-scraper:
	@echo "Installing scraper..."
	poetry run playwright install-deps
	poetry run playwright install


uninstall-scraper:
	@echo "Uninstalling scraper..."
	poetry run playwright uninstall

scrape:
	@echo "Scraping..."
	poetry run poe scrape