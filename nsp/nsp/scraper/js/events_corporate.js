/**
 * This script is used to collect the events for corporate and investors calendar.
 * Link : https://www.nvidia.com/en-us/events/
 * The information collected is in the format 'date,name' and is stored in a CSV file.
 *
 * RUN THIS SCRIPT IN THE BROWSER CONSOLE
 *
 * STEPS:
 * 1. Selected the entire script and copied it.
 * 2. Opened the browser console (Ctrl + Shift + J)
 * 3. Pasted the script and pressed Enter.
 * 4. The script will automatically download the CSV file with the corporate and investors events information.
 */
const events = ["start_date,end_date,name,location"];

function showAllEvents() {
	const showAllBtns = document.querySelectorAll(".sc-jTzLTM.caDwam");
	for (let btn of showAllBtns) {
		btn.click();
	}
}

function collectAllEventsInfo() {
	const eventElements = document.querySelectorAll(".sc-gZMcBi.jniRnN");

	for (let event of eventElements) {
		const event_date = event.querySelector("h2").textContent;
		const event_name = event.querySelector("h3").textContent;
		const event_location = event.querySelector("h4").textContent;

		events.push(combineEventsInfo(event_date, event_name, event_location));
	}
}

function convertDateToString(date) {
	// returns the date in the format 'YYYY-MM-DD'
	return `${date.getFullYear()}-${("0" + (date.getMonth() + 1)).slice(-2)}-${(
		"0" + date.getDate()
	).slice(-2)}`;
}

function combineEventsInfo(date, name, location) {
	name = name.replace(/,/g, "");
	location = location.replace(/,/g, "");
	date = date.replace(/,/g, "");

	let dateStart = "";
	let dateEnd = "";

	if (date.includes("-")) {
		let year = date.slice(-4);
		let dateBody = date.slice(0, -4);
		let dates = dateBody.split("-");
		let monthToUse = date.trim().slice(0, 3);

		dateStart = convertDateToString(
			new Date(Date.parse(dates[0] + " " + year))
		);

		if (dates[1].trim().length > 3) monthToUse = "";

		dateEnd = convertDateToString(
			new Date(Date.parse(monthToUse + " " + dates[1] + " " + year))
		);
	} else {
		dateStart = convertDateToString(new Date(Date.parse(date)));
	}

	const combinedInfo = `${dateStart},${dateEnd},${name},${location}`;
	return combinedInfo;
}

function downloadEventsInfo() {
	const events_info = events.join("\n");
	const blob = new Blob([events_info], { type: "text/csv" });
	const url = URL.createObjectURL(blob);

	const a = document.createElement("a");
	a.href = url;
	a.download = "events_corporate.csv";
	a.click();
}

function scrape() {
	showAllEvents();
	collectAllEventsInfo();
	downloadEventsInfo();
}

scrape();
