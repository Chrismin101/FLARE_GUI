# FLARE GUI

# Known Issues
- ~~Coordinate plotting might by flipped on the longitudinal axis, I have no idea~~ **Verified, fixed**

### Current Goals

- ~~Re-implement on-click functionality (Raph)~~
- ~~Re-implement internodal lines (Raph)~~
- ~~Re-attach NMEAFile instantiation to GUI output. Current file forces GUI to display hardcoded coordinates. Current issue is that we don't have NMEA data that is near our actual map. (Raph)~~
- ~~Refine map tiff selection (Find more appropriate scale) (Raph)~~
---

# NMEAFile Class

A class to read and process NMEA data from a CSV file.

> NOTE: When an NMEAFile object is instantiated, sentences with invalid checksums are automatically discarded from the data and placed into NMEAFile.corruptedData. 

## Attributes
- **csvFilePath** : `str`
    - The path to the CSV file containing NMEA data.
- **rawData** : `list`
    - The raw data read from the CSV file.
- **data** : `dict`
    - The processed data indexed by NMEA sentence signature.
- **corruptedData** : `list`
    - The raw data sentences that failed the checksum.

## Methods


- **getAllData()**
    - Returns the raw data read from the CSV file.
    
- **getAvailableSigs()**
    - Returns a list of available NMEA sentence signatures in the processed data.

    ## Example Usage

    ```python
    # Example usage of the NMEAFile class

    # Create an instance of NMEAFile
    nmea_file = NMEAFile('path/to/nmea_data.csv')

    # Access the processed data
    gpgga_data = nmea_file.data["$GPGGA"]

    # Print the GPGGA data
    for entry in gpgga_data:
        print(entry)
    ```

```python
class NMEAFile:
    """
    A class to read and process NMEA data from a CSV file.

    Attributes:
    -----------
    csvFilePath : str
        The path to the CSV file containing NMEA data.
    rawData : list
        The raw data read from the CSV file.
    data : dict
        The processed data indexed by NMEA sentence signature.
    corruptedData : list
        The raw data sentences that failed the checksum.


    Methods:
    --------
    getAllData():
        Returns the raw data read from the CSV file.
    
    getAvailableSigs():
        Returns a list of available NMEA sentence signatures in the processed data.
    
    _readCsv():
        Reads the CSV file and returns the data as a list of lists.
    
    _processData():
        Processes the raw data, discards rows with checksum failures, converts number strings to floats, 
        and organizes the data into a dictionary indexed by NMEA sentence signature.
    
    _is_valid_nmea_sentence(sentence):
        Validates an NMEA sentence by checking its checksum.
    """
```
