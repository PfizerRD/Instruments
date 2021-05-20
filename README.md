# Instruments
This repository provides Python a package that can provide OPC UA and MQTT
interfaces to common laboratory equipment. Thus, standalone equipment can be


## How it works
- The package runs on a computer that is connected to an instrument (serially
  or socket) that provides an API.
- The package provides services that monitor various protocols (OPC UA, MQTT,
  HTTP).
- When one of the services observes a command request, the request is forwarded
  to the attached instrument to be executed and a callback is provided.
- Upon execution, the callback is executed, which provides custom handling of
  instrument responses.


## Get started
1. Clone the repository on an instrument attached to a device that provides either
a serial or BSD socket API.
2. Configure the desired lisening services in the YAML configuration.
3. Define the handling of incoming command requests and instrument responses.
3. Start the services using docker-compose.
   
## Author
   Giuseppe Cogoni<br/>
   Brent Maranzano<br/>
   John Pfisterer

## License
   MIT
