import network
import socket
import time
import ujson as json  # Use MicroPython's ujson

# Configure Wi-Fi
ssid = 'DE-LAB'
password = ''

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

while not wlan.isconnected():
    time.sleep(1)

# Get and print the IP address of the Pico
ip_address = wlan.ifconfig()[0]
print('Connected to Wi-Fi')
print(f'IP Address: {ip_address}')

# Store sensor values
sensor_values = {}

# Setup server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('', 8080))
server_socket.listen(2)
server_socket.settimeout(5)  # Set a timeout for accepting connections

def update_sensor_values(query):
    params = query.split('&')
    sensor_id = None
    sensor_value = None
    for param in params:
        key, value = param.split('=')
        if key == 'sensor':
            sensor_id = value
        elif key == 'value':
            sensor_value = int(value)
    if sensor_id and sensor_value is not None:
        sensor_values[sensor_id] = sensor_value
        print(sensor_values)

def generate_html():
    with open('index.html', 'r') as file:
        html = file.read()
    return html

def generate_json():
    return json.dumps(sensor_values)

while True:
    try:
        client_socket, client_address = server_socket.accept()
        try:
            request = client_socket.recv(1024)
            request_str = request.decode('utf-8')
            print(f"Request: {request_str}")  # Debugging: Log the request
            if 'GET /update' in request_str:
                query = request_str.split(' ')[1].split('?')[1]
                update_sensor_values(query)
                response = 'HTTP/1.1 200 OK\n\nUpdated'
            elif 'GET /data' in request_str:
                json_data = generate_json()
                response = f'HTTP/1.1 200 OK\nContent-Type: application/json\n\n{json_data}'
            else:
                html = generate_html()
                response = f'HTTP/1.1 200 OK\nContent-Type: text/html\n\n{html}'
            client_socket.sendall(response.encode('utf-8'))
        except Exception as e:
            print(f'Error handling request: {e}')
        finally:
            client_socket.close()
    except OSError as e:
        if e.errno == 110:  # ETIMEDOUT (timeout error)
            continue
        elif e.errno == 103:  # ECONNABORTED (connection aborted)
            print(f'Connection aborted: {e}')
            continue
        else:
            print(f'Error accepting connection: {e}')
