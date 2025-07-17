OVERVIEW-----------------------
These files comprise the software that interfaces with the wearable plant health monitoring sensors, "PlantPulse Patches". This software receives BLE packets (19 bytes expected) from BT devices, logs data to a csv file, then trends data from the csv file onto a web-based
dashboard.

HOW-TO USE (very basic)--------
- Connect to BT devices
    Run 'ble_receiver.py' from command line or by executing code
    The program will print if the software (un)successfully connected to "APCH" prefix devices, and will begin printing BLE transmitted data.  If connection doesn't occur, you can try resetting the device (at least on the eval. board)

- Start streamlit dashboard
    Run 'dashboard.py' from command line with the command "streamlit run dashboard.py"
    The dashboard should launch in a new window. 
