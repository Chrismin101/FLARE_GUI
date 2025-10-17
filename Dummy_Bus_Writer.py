import csv
import serial
import time

PORT = 'COM3'
BaudRate = 9600

# Path to the real CAN telemetry dataset captured on 2-16-2025
DATA_FILE = "Data/2-16-2025 - CAN Data Test - 2-16-2025 - CAN Data Test.csv"


def write_uart():
    """Stream each row of the CAN test data over a serial link.

    The original implementation split the output of a single CSV row across
    multiple serial lines.  This caused important fields such as latitude and
    longitude to appear on different lines from the timestamp and altitude,
    making it difficult for the receiver to associate a complete coordinate
    set with the correct point in time.

    Each row is now transmitted as a single line that contains every field in
    the CSV.  The timestamp, latitude, longitude and altitude are placed at the
    start of the line so they can be parsed together.  Remaining fields follow
    in the same "key: value" format used previously.
    """

    with open(DATA_FILE, newline='') as csvfile, serial.Serial(PORT, BaudRate) as ser:
        print(f"Connected to {PORT} at {BaudRate} baud.")
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Build a single line containing every column from the CSV.
            parts = [
                f"Time: {row['Time (s)']}",
                f"Latitude: {row['Latitude (deg)']}",
                f"Longitude: {row['Longitude (deg)']}",
                f"Altitude: {row['Altitude (m)']}m",
                f"Velocity: {row['Total Velocity (m/s)']}m/s",
                f"Accel: {row['Total Acceleration (m/s^2)']}m/s^2",
                f"AngleOfAttack: {row['Angle of Attack (deg)']}deg",
                f"RollRate: {row['Roll Rate (r/s)']}r/s",
                f"PitchRate: {row['Pitch Rate (r/s)']}r/s",
                f"YawRate: {row['Yaw Rate (r/s)']}r/s",
                f"Mass: {row['Mass (g)']}g",
                f"AirTemp: {row['Air Temperature (Celsius)']}C",
                f"AirPressure: {row['Air Pressure (mbar)']}mbar",
            ]

            packet = " ".join(parts) + "\n"

            ser.write(packet.encode('utf-8'))

            print(f"Sent packet:\n{packet}")
            time.sleep(0.1)


if __name__ == '__main__':
    write_uart()
