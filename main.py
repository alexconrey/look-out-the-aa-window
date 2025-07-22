import requests
import curses
import time
import datetime

from typing import Any, NoReturn, List, Dict

def knots_to_mph(knots):
  """
  Converts a speed from knots to miles per hour (mph).

  Args:
    knots: The speed in knots (float or int).

  Returns:
    The speed in miles per hour (float).
  """
  conversion_factor = 1.15078
  mph = knots * conversion_factor
  return int(mph)

def get_service_data():
	return requests.get("https://www.aainflight.com/api/v1/connectivity/viasat/services").json()

def get_flight_data():
	return requests.get("https://www.aainflight.com/api/v1/connectivity/viasat/flight").json()

def format_data() -> List[str]:
	"""
	Formats flight and service data into a list of formatted strings.

	Returns:
		List[str]: Formatted strings containing flight and service information
	"""
	formatted_data: List[str] = []
	service_data: Dict[str, Any] = get_service_data()
	flight_data: Dict[str, Any] = get_flight_data()

    # Format WiFi service information
	for service in service_data['serviceList']:
		if service['serviceName'] != 'satelliteNetwork':
			continue
		
		details = service['details']
		formatted_data.extend([
			f"WiFi Status:        {details['serviceState']}",
			f"Frequency Band:     {details['frequencyBand']}"
		])
		
		if details['returnToCoverageTime'] != 0:
			formatted_data.append(
				f"WiFi Resume ETA:      {details['returnToCoverageTime']}"
			)

    # Format basic flight information
	formatted_data.extend([
		f"Plane Registration: {flight_data['vehicleId']}",
		f"Flight Number:      {flight_data['flightNumber']}",
		f"Origin:             {flight_data['origin']}",
		f"Destination:        {flight_data['destination']}"
	])

	def format_minutes_to_time(minutes: int) -> str:
		"""Convert minutes to HH:MM format."""
		return datetime.time(
			hour=int(minutes / 60),
			minute=int(minutes % 60)
		).strftime("%H:%M")

	flight_duration_str = format_minutes_to_time(flight_data['flightDuration'])
	time_flown_str = format_minutes_to_time(
		flight_data['flightDuration'] - flight_data['timeToGo']
	)
	time_remaining_str = format_minutes_to_time(flight_data['timeToGo'])

	# Format flight status information
	formatted_data.extend([
		f"\n",
		f"Flight Phase:        {flight_data['flightPhase']}",
		f"Current Altitude:    {flight_data['altitude']}",
	])

	# Format speed information
	groundspeed_knots: float = flight_data['groundspeed']
	groundspeed_mph: float = knots_to_mph(groundspeed_knots)
	formatted_data.extend([
		f"Groundspeed (knots): {groundspeed_knots}",
		f"Groundspeed (MPH):   {groundspeed_mph}"
		f"\n"
	])

	formatted_data.extend([
		f"Total time:          {flight_duration_str}",
		f"Time Flown:          {time_flown_str}",
		f"Time Remaining:      {time_remaining_str}",
		"\n"
	])

	return formatted_data

def main(stdscr: Any) -> NoReturn:
	"""
	Main application loop for the curses-based interface.

	Args:
		stdscr: The main curses window object
	"""
	# Initialize curses settings
	curses.curs_set(0)  # Hide the cursor
	curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_GREEN)
	stdscr.clear()      # Clear the screen initially
	rows, cols = stdscr.getmaxyx()

	# Calculate the y-coordinate for the last line (0-indexed)
	last_line_y = rows - 1
	stdscr.nodelay(True)  # Make getch() non-blocking

	try:
		while True:
			refresh_timestamp: datetime = datetime.datetime.now()
			refresh_timestamp_str: str = refresh_timestamp.strftime("%Y-%m-%d %H:%M:%S")
			
			# Format and display data
			formatted_data: str = "\n".join(format_data())
			stdscr.addstr(0, 0, formatted_data)
			stdscr.addstr(last_line_y-2, 0, f"Last reloaded: {refresh_timestamp_str}", curses.color_pair(1))
			stdscr.addstr(last_line_y, 0, "Press 'q' to quit.")
			stdscr.refresh()

			# Check for quit command
			if stdscr.getch() == ord('q'):
				break

			# Wait and refresh
			time.sleep(5)  # 5 second delay
			stdscr.clear()
            
	except KeyboardInterrupt:
		# Handle clean exit on Ctrl+C
		pass
	finally:
		# Cleanup curses
		curses.endwin()

if __name__ == '__main__':
	curses.wrapper(main)
