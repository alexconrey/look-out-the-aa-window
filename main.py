import requests
import curses
import time

def get_service_data():
	return requests.get("https://www.aainflight.com/api/v1/connectivity/viasat/services").json()

def get_flight_data():
	return requests.get("https://www.aainflight.com/api/v1/connectivity/viasat/flight").json()

def format_data():
	formatted_data = []
	service_data = get_service_data()
	flight_data = get_flight_data()
	for service in service_data['serviceList']:
		if service['serviceName'] != 'satelliteNetwork':
			continue
		details = service['details']
		formatted_data.append("WiFi Status: {}".format(details['serviceState']))
		formatted_data.append("Frequency Band: {}".format(details['frequencyBand']))
		
		if details['returnToCoverageTime'] != 0:
			formatted_data.append("ETA for WiFi coverage resume: {}".format(details['returnToCoverageTime']))

	formatted_data.append("Plane Registration: {}".format(flight_data['vehicleId']))
	formatted_data.append("Flight Number: {}".format(flight_data['flightNumber']))
	formatted_data.append("Origin: {}".format(flight_data['origin']))
	formatted_data.append("Destination: {}".format(flight_data['destination']))
	formatted_data.append("Total time: {}".format(flight_data['flightDuration']))

	time_flown = flight_data['flightDuration'] - flight_data['timeToGo']
	formatted_data.append("Time Flown: {}".format(time_flown))
	formatted_data.append("Time Remaining: {}".format(flight_data['timeToGo']))

	formatted_data.append("\n")
	formatted_data.append("Flight Phase: {}".format(flight_data['flightPhase']))
	formatted_data.append("Current Altitude: {}".format(flight_data['altitude']))
	formatted_data.append("Current Groundspeed: {}".format(flight_data['groundspeed']))
	formatted_data.append("Remaining Miles: {}".format(flight_data['distanceToGo']))
	return formatted_data




def main(stdscr):
    # # Initialize curses settings
	curses.curs_set(0) # Hide the cursor
	stdscr.clear()     # Clear the screen initially
	stdscr.nodelay(True)  # Make getch() non-blocking

	counter = 0
	while True:
		formatted_data = "\n".join(format_data())
		stdscr.addstr(0, 0, formatted_data)
		# stdscr.addstr(0, 0, f"Screen updated {counter} times.")
		stdscr.addstr(20, 0, "Press 'q' to quit.")
		stdscr.refresh()

		key = stdscr.getch()
		if key == ord('q'):
			break

		time.sleep(15)  # Wait for 15 seconds
		stdscr.clear()  # Clear the entire screen
		counter += 1

if __name__ == '__main__':
	curses.wrapper(main)
