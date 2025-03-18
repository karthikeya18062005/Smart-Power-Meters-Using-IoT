import machine
import time
import network
import urequests

# Configure Wi-Fi
ssid = 'DE-LAB'
password = ''

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

while not wlan.isconnected():
    pass

print('Connected to Wi-Fi')

# Setup ADC
adc = machine.ADC(26)

server_ip = '10.10.27.248'  # Replace with the server Pico's IP address
server_port = 8080

def read_gas_sensor():
    a=adc.read_u16()
    print(a)
    return a
id="client1"
while True:
    gas_value = read_gas_sensor()
    url = f'http://{server_ip}:{server_port}/update?sensor={id}&value={gas_value}'
    try:
        response = urequests.get(url)
        print(response.text)
    except Exception as e:
        print(e)
    time.sleep(1)
