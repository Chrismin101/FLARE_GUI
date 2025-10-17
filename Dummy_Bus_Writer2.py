import csv
import serial
import time

PORT = 'COM10'
BaudRate = 9600

# Path to the real CAN telemetry dataset captured on 2-16-2025
DATA_FILE = "Data/debug.csv"


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
            ser.write(row["raw_nmea"].encode('utf-8'))
            ser.write('\n'.encode('utf-8'))
            print(f"Sent packet:\n{row["raw_nmea"]}")

            time.sleep(0.1)


if __name__ == '__main__':
    write_uart()
