/**
 * This script is used to collect the events and presentations information from the events and presentations page.
 * Link : https://investor.nvidia.com/events-and-presentations/events-and-presentations/default.aspx
 * The information collected is in the format 'date,name' and is stored in a CSV file.
 *
 * RUN THIS SCRIPT IN THE BROWSER CONSOLE
 *
 * STEPS:
 * 1. Selected the entire script and copied it.
 * 2. Opened the browser console (Ctrl + Shift + J)
 * 3. Pasted the script and pressed Enter.
 * 4. The script will automatically download the CSV file with the events and presentations information.
 */

const events = ["date,name"];

function getEventDate(archived_event_date) {
	// FORMAT : 'March 19, 2024'
	const date = new Date(Date.parse(archived_event_date));

	return convertDateToString(date);
}

function convertDateToString(date) {
	// returns the date in the format 'YYYY-MM-DD'
	return `${date.getFullYear()}-${("0" + (date.getMonth() + 1)).slice(-2)}-${(
		"0" + date.getDate()
	).slice(-2)}`;
}

function getEventName(archived_event_name) {
	// 'Event Name'
	return archived_event_name.replaceAll(",", " | ");
}

function awaitUpdateEvent() {
	return new Promise((resolve) => {
		const checkEventsLoaded = () => {
			const eventsArchived = document.querySelectorAll(
				".module-event-archive .module_item"
			);
			if (eventsArchived.length > 0) {
				resolve();
			} else {
				setTimeout(checkEventsLoaded, 100); // Check again after 100ms
			}
		};
		checkEventsLoaded();
	});
}

function collectArchivedEventsFromCurrentPage() {
	const eventsArchived = document.querySelectorAll(
		".module-event-archive .module_item"
	);

	console.log("Events Archived: ", eventsArchived.length);

	for (let event of eventsArchived) {
		const event_date = getEventDate(
			event.querySelector(".module_date-text").innerText
		);
		const event_name = getEventName(
			event.querySelector(".module_headline-link").innerText
		);

		events.push(`${event_date},${event_name}`);
	}

	console.log(`Successfully collected ${events.length - 1} events`);
}

async function collectArchivedEventsInfo() {
	const selectArchivedYearMenu = document.querySelector("#eventArchiveYear");
	const optionsN = selectArchivedYearMenu.options.length;

	for (let i = 0; i < optionsN; i++) {
		selectArchivedYearMenu.selectedIndex = i;
		selectArchivedYearMenu.dispatchEvent(new Event("change"));

		// Wait for the events to load
		await awaitUpdateEvent();

		// Collect the events from the current page
		collectArchivedEventsFromCurrentPage();
	}
}

function downloadEventsInfo() {
	const events_info = events.join("\n");
	const blob = new Blob([events_info], { type: "text/csv" });
	const url = URL.createObjectURL(blob);

	const a = document.createElement("a");
	a.href = url;
	a.download = "events_presentations.csv";
	a.click();
}

function collectLatestEventsInfo() {
	const eventsArchived = document.querySelectorAll(
		".module-event-latest .module_item"
	);

	console.log("Events Latest: ", eventsArchived.length);

	for (let event of eventsArchived) {
		const event_date = getEventDate(
			event.querySelector(".module_date-text").innerText
		);
		const event_name = getEventName(
			event.querySelector(".module_headline-link").innerText
		);

		events.push(`${event_date},${event_name}`);
	}

	console.log(
		`Successfully collected in overall ${events.length - 1} events`
	);
}

function removeCollectedDuplicates() {
	const uniqueEvents = Array.from(new Set(events));
	events.length = 0;
	events.push(...uniqueEvents);
}

async function scrapeEventsInfo() {
	collectLatestEventsInfo();
	await collectArchivedEventsInfo();
	removeCollectedDuplicates();
	downloadEventsInfo();
}

scrapeEventsInfo();
