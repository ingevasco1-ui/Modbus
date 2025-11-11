from pymodbus.client import ModbusTcpClient
import matplotlib.pyplot as plt
import time

# Configuración
ARDUINO_IP = '192.168.0.100'
PLC_IP = '192.168.0.1'
PORT = 502

plt.ion()
fig, ax = plt.subplots(figsize=(10, 5))
x_data, y_arduino, y_plc = [], [], []

print("Leyendo Arduino y PLC... Presiona 'q' para salir")

def read_device(ip, reg, slave=1):
    try:
        client = ModbusTcpClient(ip, port=PORT, timeout=2)
        if client.connect():
            rr = client.read_holding_registers(reg, 1, slave=slave)
            client.close()
            return rr.registers[0] if not rr.isError() else None
    except:
        return None

def on_key(event):
    if event.key == 'q':
        plt.close()
        exit(0)

fig.canvas.mpl_connect('key_press_event', on_key)

try:
    while plt.fignum_exists(fig.number):
        # Leer ambos dispositivos
        arduino_val = read_device(ARDUINO_IP, 0, 1)  # Arduino HR0
        plc_val = read_device(PLC_IP, 1, 1)          # PLC HR0
        
        if arduino_val is not None or plc_val is not None:
            x_data.append(time.time())
            y_arduino.append(arduino_val if arduino_val is not None else (y_arduino[-1] if y_arduino else 0))
            y_plc.append(plc_val if plc_val is not None else (y_plc[-1] if y_plc else 0))
        
        # Mantener últimos 30 puntos
        if len(x_data) > 30:
            x_data.pop(0)
            y_arduino.pop(0)
            y_plc.pop(0)
        
        # Graficar
        if len(x_data) > 1:
            x_rel = [x - x_data[0] for x in x_data]
            ax.clear()
            ax.plot(x_rel, y_arduino, 'b-', label=f'Arduino: {y_arduino[-1]}')
            ax.plot(x_rel, y_plc, 'r-', label=f'PLC: {y_plc[-1]}')
            ax.legend()
            ax.grid(True)
            plt.pause(0.3)
        
        time.sleep(0.4)

except KeyboardInterrupt:
    pass

plt.close()