serial:
    baudrate: 9600
    port: /dev/ttyUSB0
    parity: N
    stopbits: 1
opc:
    endpoint: "opc.tcp://127.0.0.1:4840/instrument/"
    uri: "http://test.server"
    mapping:
        name: GET_FLOWRATE
            method: set_flowrate
        name: GET_FLOWRATE
            method: get_flowrate
