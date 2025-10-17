import re
import csv
import numpy as np
import sys

def calculate_checksum(nmea_sentence):
    checksum = 0
    for char in nmea_sentence:
        checksum ^= ord(char)
    return f"{checksum:02X}"

if len(sys.argv) == 3 and sys.argv[1] == '--checksum-file':
        input_path = sys.argv[2]
        output_path = input_path.rsplit('.', 1)[0] + '_checksummed.csv'
        with open(input_path, 'r') as infile, open(output_path, 'w') as outfile:
            for line in infile:
                line = line.strip()
                if line.startswith('$'):
                    sentence = line[1:]
                    if '*' in sentence:
                        sentence = sentence.split('*')[0]
                    checksum = calculate_checksum(sentence)
                    outfile.write(f"{line.split('*')[0]}*{checksum}\n")
                else:
                    outfile.write(line + '\n')
        sys.exit(0)

# If called with an argument, return the checksum of the supplied NMEA sentence
if len(sys.argv) > 1:
    print(sys.argv[1])
    sentence = sys.argv[1]
    # Remove leading '$' and anything after '*'
    if sentence.startswith('$'):
        sentence = sentence[1:]
    if '*' in sentence:
        sentence = sentence.split('*')[0]
    print(calculate_checksum(sentence))
    sys.exit(0)

    # If called with the '--checksum-file' flag, process the specified file



# Load the NMEA data from the CSV file
nmea_data = ""
with open("Data/eggfinder_simulated_nmea.csv", mode='r') as file:
    csvReader = csv.reader(file)
    for row in csvReader:
        nmea_data += ",".join(row) + "\n"

# Extract latitudes and longitudes
latitudes = re.findall(r'(\d{4,5}\.\d+),[NS]', nmea_data)
longitudes = re.findall(r'(\d+\.\d+),[WE]', nmea_data)

# Convert latitudes and longitudes to decimal degrees
latitudes_dec = [(int(lat[:2]) + float(lat[2:]) / 60) for lat in latitudes]
longitudes_dec = [-(int(lon[:3]) + float(lon[3:]) / 60) for lon in longitudes]

# Compute the translation offsets
original_first_lat = latitudes_dec[0]
original_first_lon = longitudes_dec[0]

target_first_lat = 47.98699567925023
target_first_lon = -81.84837953976061

lat_offset = target_first_lat - original_first_lat
lon_offset = target_first_lon - original_first_lon

# Apply the translation
adjusted_latitudes_dec = [lat + lat_offset for lat in latitudes_dec]
adjusted_longitudes_dec = [lon + lon_offset for lon in longitudes_dec]

# Display the adjusted coordinates
adjusted_nmea_data = nmea_data
for original_lat, adjusted_lat in zip(latitudes, adjusted_latitudes_dec):
    adjusted_lat_str = str(np.round(adjusted_lat*100,4))
    adjusted_nmea_data = adjusted_nmea_data.replace(original_lat, adjusted_lat_str)

for original_lon, adjusted_lon in zip(longitudes, adjusted_longitudes_dec):
    adjusted_lon_str = str(np.round(adjusted_lon*100,4))
    adjusted_nmea_data = adjusted_nmea_data.replace(original_lon, adjusted_lon_str)

# Save the adjusted NMEA data to a new CSV file
with open("Rocket_URDF/NMEAData_Examples/HomeTest_adjusted.csv", mode='w') as file:
    # Split the adjusted NMEA data into lines
    adjusted_nmea_lines = adjusted_nmea_data.splitlines()

    # Update the checksum for each NMEA sentence
    for i, line in enumerate(adjusted_nmea_lines):
        if line.startswith('$') and '*' in line:
            sentence, checksum = line.rsplit('*', 1)
            original_sentence = nmea_data.splitlines()[i]
            original_sentence, original_checksum = original_sentence.rsplit('*', 1)
            if calculate_checksum(original_sentence[1:]) == original_checksum:
                new_checksum = calculate_checksum(sentence[1:])
                adjusted_nmea_lines[i] = f"\"{sentence}*{new_checksum}\""

    # Join the lines back into a single string
    adjusted_nmea_data_with_checksum = "\n".join(adjusted_nmea_lines)

    file.write(adjusted_nmea_data_with_checksum)
