# device specific port where arduino is connected
SERIAL_PORT = 'COM3'
# match arduino, 9600 is standard
BAUD_RATE = 9600

# --- Serial Communication Setup ---
ser = None # Initialize serial port object as None
try:
    # Attempt to open the serial port
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
    print(f"Successfully connected to serial port {SERIAL_PORT}")
except serial.SerialException as e:
    # If connection fails, print an error and disable serial functionality
    print(f"Could not open serial port {SERIAL_PORT}: {e}")
    print("Please check if the Arduino is connected and the port name is correct.")
    print("You can continue playing, but buzzer functionality will be disabled.")