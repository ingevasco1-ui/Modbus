from pymodbus.client import ModbusTcpClient
import matplotlib.pyplot as plt
import time

PLC_IP = '192.168.0.100'
PLC_PORT = 502
SLAVE_ID = 1

plt.ion()
fig, ax = plt.subplots(figsize=(12, 6))

timestamps = []
ireg0_data, ireg1_data = [], []

print("Modbus - Input Registers - Presiona 'q' para salir...")

def on_key(event):
    if event.key == 'q':
        plt.close(fig)
        print("Saliendo...")
        exit(0)

fig.canvas.mpl_connect('key_press_event', on_key)

read_count = 0

try:
    while plt.fignum_exists(fig.number):
        try:
            client = ModbusTcpClient(PLC_IP, port=PLC_PORT)
            client.timeout = 2
            
            if not client.connect():
                print("❌ No se pudo conectar")
                time.sleep(1)
                continue
            
            # Leer Input Registers 0 y 1
            ireg_result = client.read_input_registers(address=0, count=2, slave=SLAVE_ID)
            client.close()
            
            if ireg_result.isError():
                print(f'❌ Error en lectura')
                time.sleep(0.5)
                continue
            
            # Obtener valores
            sensor_val = ireg_result.registers[0]  # Ireg0 - Sensor A1
            counter_val = ireg_result.registers[1] # Ireg1 - Contador
            
            read_count += 1
            current_time = time.time()
            
            # Agregar datos
            timestamps.append(current_time)
            ireg0_data.append(sensor_val)
            ireg1_data.append(counter_val)
            
            # Limitar datos a 40 puntos
            if len(timestamps) > 40:
                timestamps.pop(0)
                ireg0_data.pop(0)
                ireg1_data.pop(0)
            
            # Tiempo relativo
            x_relative = [t - timestamps[0] for t in timestamps]
            
            # Actualizar gráfica
            ax.clear()
            ax.plot(x_relative, ireg0_data, 'g-', linewidth=2, label=f'Sensor A1: {sensor_val}')
            ax.plot(x_relative, ireg1_data, 'r-', linewidth=2, label=f'Contador: {counter_val}')
            
            ax.set_ylabel('Valor')
            ax.set_xlabel('Tiempo (s)')
            ax.set_title(f'Input Registers - Lectura #{read_count}')
            ax.grid(True, alpha=0.3)
            ax.legend()
            
            plt.tight_layout()
            plt.pause(0.3)
            
            print(f"✅ #{read_count:3d} | Ireg0: {sensor_val:4d} | Ireg1: {counter_val:3d}")
            
        except Exception as e:
            print(f'💥 Error: {e}')
            time.sleep(1)
            
except KeyboardInterrupt:
    pass

print("Programa terminado")