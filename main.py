from inputs import get_gamepad
import telnetlib
import threading
import time
import datetime

# Open the Telnet connection to the Duet controller
duet_telnet = telnetlib.Telnet()
duet_telnet.open("cnc")

# Dictionary to track button states
button_states = {}
lock = threading.Lock()

# Function to continuously monitor button state and update the dictionary
def button_monitor():
    while True:
        events = get_gamepad()

        for event in events:
            print(event.code, event.state)
            if not event.code.startswith("SYN_REPORT"):
                with lock:
                    # Update button state
                    button_states[event.code] = event.state
                    # print(button_states)

# Function to send commands based on button states
def send_commands():
    while True:
        with lock:
            gcode = "G91 G1"


            # D-PAD UP AND DOWN (1mm Z movement)
            dpad_up = button_states.get("ABS_HAT0Y", 0)
            dpad_down = button_states.get("ABS_HAT0Y", 0)

            if dpad_up == -1:
                print("Z axis UP 1mm (D-PAD up)")
                gcode += "Z1"

            if dpad_down == 1:
                print("Z axis DOWN 1mm (D-PAD down)")
                gcode += "Z-1"


            # D-PAD LEFT AND RIGHT (1mm X movement)
            dpad_left = button_states.get("ABS_HAT0X", 0)
            dpad_right = button_states.get("ABS_HAT0X", 0)

            if dpad_left == -1:
                print("X axis LEFT 1mm (D-PAD left)")
                gcode += "X-1"

            if dpad_right == 1:
                print("X axis RIGHT 1mm (D-PAD right)")
                gcode += "X1"


            # X and B buttons (fine movement on Z axis)
            x_button = button_states.get("BTN_NORTH", 0)
            b_button = button_states.get("BTN_SOUTH", 0)

            if x_button == 1:
                print("Z axis UP 0.25mm (X button)")
                gcode += "Z0.25"

            if b_button == 1:
                print("Z axis DOWN 0.25mm (B button)")
                gcode += "Z-0.25"


            # Y and A buttons (fine movement on X axis)
            y_button = button_states.get("BTN_WEST", 0)
            a_button = button_states.get("BTN_EAST", 0)

            if y_button == 1:
                print("X axis LEFT 0.25mm (Y button)")
                # duet_telnet.write("G91 G1 X-0.5".encode('utf-8') + b'\n')
                gcode += "X-0.5"

            if a_button == 1:
                print("X axis RIGHT 0.25mm (A button)")
                # duet_telnet.write("G91 G1 X0.5".encode('utf-8') + b'\n')
                gcode += "X0.5"

            duet_telnet.write(gcode.encode('utf-8') + b'\n')

            # BTN_TR (Homing All Axes)
            btn_tr = button_states.get("BTN_TR", 0)
            if btn_tr == 1:
                last_btn_tr_press_time = datetime.datetime.now()
                duet_telnet.write("G91\n".encode('utf-8'))
                duet_telnet.write("G21\n".encode('utf-8'))
                duet_telnet.write("G1 H1 Z94 F900\n".encode('utf-8'))
                duet_telnet.write("G1 Z-3 F2400\n".encode('utf-8'))
                duet_telnet.write("G1 H1 Z94 F300\n".encode('utf-8'))
                duet_telnet.write("G1 H1 X1500 Y1500 F2400\n".encode('utf-8'))
                duet_telnet.write("G92 X800 Y1270 Z94\n".encode('utf-8'))
                duet_telnet.write("G1 X-3 Y-3 F2400\n".encode('utf-8'))
                duet_telnet.write("G1 H1 X1500 Y1500 F300\n".encode('utf-8'))
                duet_telnet.write("G92 X800 Y1270 Z94\n".encode('utf-8'))
                duet_telnet.write("G90\n".encode('utf-8'))

        # Add a short delay to control the frequency of command sending
        time.sleep(0.15)  # Adjust the sleep interval as needed

# Create and start the button monitoring thread
monitor_thread = threading.Thread(target=button_monitor)
monitor_thread.start()

# Call the function to send commands in the main thread
send_commands()

# Wait for the monitoring thread to finish (which happens when the program is manually terminated)
monitor_thread.join()

# Close the Telnet connection when done
duet_telnet.close()