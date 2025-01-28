import serial
import time

# Replace 'COM3' with the port your Arduino is connected to
try:
    arduino = serial.Serial(port='COM3', baudrate=9600, timeout=1)
    print("Connected to Arduino on COM3")
except serial.SerialException as e:
    print(f"Error: Could not connect to Arduino - {e}")
    exit()

# Wait for Arduino to initialize
time.sleep(2)

# Function to send H commands to Arduino
def send_head_command(angle):
    if 0 <= angle <= 180:
        command = f"H{angle}\n"  # Format the command
        arduino.write(command.encode())  # Send the command
        print(f"Sent Command: {command.strip()}")
    else:
        print("Error: Angle must be between 0 and 180")

# Test sending H commands
try:
    while True:
        for angle in range(0, 181, 30):  # Gradually increase the angle
            send_head_command(angle)
            time.sleep(1)  # Wait 1 second between commands

        for angle in range(180, -1, -30):  # Gradually decrease the angle
            send_head_command(angle)
            time.sleep(1)

except KeyboardInterrupt:
    print("Stopped by user")

# Close the serial connection
arduino.close()
print("Serial connection closed")
