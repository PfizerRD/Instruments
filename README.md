# serial-instrument-server
Docker containers to provide various multiple protocol interfaces to
communicate to serial enabled instruments (e.g. Mettler Toledo balances. IKA
stirrers, Julabo chillers, Cole Parmer Pumps, ...etc.)

## Example
Clone this program on a computer that is attached to a serial equipment and an
ethernet connection.  Power on the serial equipment. Upon power up of the
microcomputer and serial instrument, the microcomputer will read all available
instrument parameters (i.e. set points, values, ...) and publish them to the
MQTT broker as well as provide an interface to aquire them using HTTP or OPC
UA.  Sending instrument commands is done by sending the following JSON schema
as a MQTT payload, or as the body of an HTTP PUT, or writing OPC UA tag.
`
    {
        "user": user_name,
        "password": password,
        "command":
        {
            "command_name", command_name,
            "parameters": parameters"
        }
    }
`

The services running on the microcomputer provide some additional benefits,
such as queuing commands, rate limiting the serial command rate to avoid
serial timing issues, buffering instrument data, "locking" an instrument with
a username and password.

## How it works
- The code runs on a computer that is connected serially to an instrument (e.g. Dsub-9/RS-232) and
  an Ethernet connection.
- The code defines a set of Docker services that belong to the same Docker network.
  - One service starts a Python service that creates a pySerial interface to the instrument
    and listens on a socket interface. This serial-socket service accepts client connections
    and translates any commands received on the socket interface and format and forwards the
    command on the serial interface.
- Additional services are started that translate between other common TCP/IP protocols, such
  as MQTT, OPC UA, and HTTP.
- The selection of the serial instrument type, and parameters required to define the
  other protocol parameters (e.g. MQTT broker IP, OPC UA remote server, port numbers, serial
  port position, ...etc) are defined in a *.env* file that docker-compose uses to start
  the services.

## Get started
1. Clone the serial instrument repository on a computer attached to the serial equipment
and to an Ethernet connection
2. Edit the *.env* file and define the desired instrument services.
For example,
`
HOST=computerName             # The name of the computer attached to the serial device.
SERIAL_PORT="/dev/ttyUSB0"    # The port name of the device location (see udev rules).
SOCKET_HOST=ika               # The name of the service for the instrument type (e.g. Ika, Julabo, ...etc.).
SOCKET_PORT=54132             # The port number to bind the socket.
MQTT_BROKER=192.168.1.3       # The IP address of the remote MQTT broker
GROUP_ID=DPD                  # The group ID of the MQTT device (see MQTT Sparkplug specifications)
DEVICE_ID=DLC                 # The device ID of the MQTT device (see MQTT Sparkplug specifications)
`
**Note that the device name must also be entered into the docker-compose file under the *instrument* service,
as parameter substitution does not appear to work on the device mapping.**
4. Plug the computer into the serial instrument.
5. Power on the device.
5. Start the services `docker-compose up --build -d`
6. Send commands to the device using one of the protocols started. The general format of a command is
`
              {
                  "user": user_name,
                  "password": password,
                  "command":
                  {
                      "command_name": command_name,
                      "parameters": {"param_1": value_1, "param_2": value_2, ...}
                  }
              }
`
The *user_name* and *password* are not set by default, so can be set to any
non-None value. The values can be set by using the *login* command, to "lock"
the instrument to a specific user, if desired (see documentation).

The *command_name* and *parameters* are instrument specific. However, several
generic commands are provided for all instruments, such as *get_about* (returns
information about the attached device) and *get_data* (returns the most recent
data abou the device). For example, to get information about the serial device:
`
              {
                  "user": "anyone",
                  "password": "anything",
                  "command":
                  {
                      "command_name": "get_about",
                      "parameters": None
                  }
              }
`
Details on other instrument specific commands are provided in the
documentation.
6. Additional tools from `https://github.com/brentjm/iot-docker-services.git`
   can be used to create database dashboards (*Grafana*), automate data flows
   and calculations (*Node-RED*), and other advanced features, such as creating
   "digital-twins" from custom made interfaces.
   
## Author
   Brent Maranzano

## License
   MIT
