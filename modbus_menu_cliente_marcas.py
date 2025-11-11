from pymodbus.client import ModbusTcpClient
import time

# --- CONFIGURACIÓN ---
PLC_IP = '192.168.0.1'
PLC_PORT = 502
SLAVE_ID = 2 # Usando el ID que especificaste.

# ======================================================================
# == FUNCIONES AUXILIARES CON DIAGNÓSTICO DETALLADO INTEGRADO         ==
# ======================================================================
def write_single_bit_in_register(client, bit_address, new_value):
    """
    Implementa R-M-W con impresiones de diagnóstico detalladas.
    """
    register_address = bit_address // 16
    bit_position = bit_address % 16
    
    # 1. LEER
    print(f"  -> [Paso 1: LEER] Leyendo Holding Register en la dirección Modbus {register_address}...")
    read_result = client.read_holding_registers(address=register_address, count=1, slave=SLAVE_ID)
    if read_result.isError():
        print(f"  -> ERROR: No se pudo leer el registro {register_address} antes de modificar.")
        return False
        
    current_value = read_result.registers[0]
    print(f"  -> Valor decimal actual leído: {current_value} (binario: {current_value:016b})")

    # 2. MODIFICAR
    print(f"  -> [Paso 2: MODIFICAR] Cambiando bit {bit_position} a '{new_value}'...")
    if new_value:
        new_register_value = current_value | (1 << bit_position)
    else:
        new_register_value = current_value & ~(1 << bit_position)
    
    print(f"  -> Nuevo valor decimal a escribir: {new_register_value} (binario: {new_register_value:016b})")
    
    # 3. ESCRIBIR
    print(f"  -> [Paso 3: ESCRIBIR] Enviando nuevo valor al Holding Register {register_address}...")
    write_result = client.write_register(address=register_address, value=new_register_value, slave=SLAVE_ID)
    if write_result.isError():
        print(f"  -> ERROR: La escritura falló. Respuesta del PLC: {write_result}")
        return False
        
    print(f"  -> ¡ÉXITO! El PLC aceptó la escritura.")
    return True

def read_single_bit_from_register(client, bit_address):
    """
    Lee un solo bit y muestra el valor del registro contenedor.
    """
    register_address = bit_address // 16
    bit_position = bit_address % 16
    
    print(f"  -> Leyendo Holding Register en la dirección Modbus {register_address} para extraer el bit {bit_position}...")
    result = client.read_holding_registers(address=register_address, count=1, slave=SLAVE_ID)
    if result.isError():
        print(f"  -> Error leyendo el registro {register_address}. Respuesta del PLC: {result}")
        return None
    
    register_value = result.registers[0]
    print(f"  -> Valor decimal del registro leído: {register_value} (binario: {register_value:016b})")
    
    bit_value = bool((register_value >> bit_position) & 1)
    return bit_value

# ======================================================================
# ==                      MENÚ Y LÓGICA PRINCIPAL                     ==
# ======================================================================
def print_menu():
    # ... (sin cambios)
    print("\n" + "="*50)
    print(f"      MENÚ DE CONTROL MODBUS TCP (Slave ID: {SLAVE_ID})")
    print("="*50)
    print("--- FUNCIONES MODBUS ESTÁNDAR ---")
    print("  1. Leer Coils (FC01)")
    print("  2. Leer Entradas Discretas (FC02)")
    print("  3. Leer Holding Registers (FC03)")
    print("  4. Activar un Coil (FC05 - ON)")
    print("  5. Desactivar un Coil (FC05 - OFF)")
    print("  6. Escribir un Holding Register (FC06)")
    print("  7. Escribir Múltiples Coils (FC15)")
    print("  8. Escribir Múltiples Holding Registers (FC16)")
    print("\n--- MANEJO DE MARCAS (vía Registros) ---")
    print("  9. Leer estado de una Marca (bit en un registro)")
    print("  10. Cambiar estado de una Marca (bit en un registro)")
    print("\n--- SALIR ---")
    print("  q. Salir del programa")
    print("="*50)

client = ModbusTcpClient(PLC_IP, port=PLC_PORT)

try:
    print(f"Intentando conectar con el PLC en {PLC_IP}...")
    client.connect()
    if not client.is_socket_open():
        raise ConnectionError(f"No se pudo establecer la conexión con {PLC_IP}")
    print("¡Conexión exitosa!")
    
    while True:
        print_menu()
        choice = input("Elige una opción y presiona Enter: ")

        # Opciones 1-8 se mantienen igual
        if choice == '1':
            result = client.read_coils(address=0, count=16, slave=SLAVE_ID)
            if not result.isError(): print("  Estado de Coils (0-15):", result.bits)
            else: print("  Error:", result)
        elif choice == '2':
            result = client.read_discrete_inputs(address=0, count=16, slave=SLAVE_ID)
            if not result.isError(): print("  Estado de Entradas (0-15):", result.bits)
            else: print("  Error:", result)
        elif choice == '3':
            # Nota: Asegúrate de que tu puntero en el PLC cubra 10 registros.
            # Si tu puntero es WORD 3, cambia count=3 para evitar el error IllegalAddress.
            result = client.read_holding_registers(address=0, count=3, slave=SLAVE_ID)
            if not result.isError(): print("  Valores de Registros (0-9):", result.registers)
            else: print("  Error:", result)
        elif choice == '4' or choice == '5':
            try:
                addr = int(input("  Introduce la dirección del Coil: "))
                value_to_write = (choice == '4')
                result = client.write_coil(address=addr, value=value_to_write, slave=SLAVE_ID)
                if not result.isError(): print("  ¡Escritura exitosa!")
                else: print("  Error:", result)
            except ValueError: print("  Error: Debes introducir un número entero.")
        elif choice == '6':
            try:
                addr = int(input("  Introduce la dirección del Holding Register: "))
                value = int(input(f"  Introduce el valor a escribir: "))
                result = client.write_register(address=addr, value=value, slave=SLAVE_ID)
                if not result.isError(): print("  ¡Escritura exitosa!")
                else: print("  Error:", result)
            except ValueError: print("  Error: Debes introducir números enteros.")
        elif choice == '7':
            try:
                addr = int(input("  Introduce la dirección de inicio para los Coils: "))
                values_str = input("  Introduce los valores (1/0) separados por comas: ")
                values_list = [bool(int(v.strip())) for v in values_str.split(',')]
                result = client.write_coils(address=addr, values=values_list, slave=SLAVE_ID)
                if not result.isError(): print("  ¡Comando enviado!")
                else: print("  Error:", result)
            except (ValueError, IndexError): print("  Error: Formato de entrada incorrecto.")
        elif choice == '8':
            try:
                addr = int(input("  Introduce la dirección de inicio para los Registros: "))
                values_str = input("  Introduce los valores numéricos separados por comas: ")
                values_list = [int(v.strip()) for v in values_str.split(',')]
                result = client.write_registers(address=addr, values=values_list, slave=SLAVE_ID)
                if not result.isError(): print("  ¡Escritura múltiple de Registros exitosa!")
                else: print("  Error:", result)
            except (ValueError, IndexError): print("  Error: Formato de entrada incorrecto.")
        
        # --- OPCIONES 9 Y 10 CON LÓGICA DE DIAGNÓSTICO ---
        elif choice == '9': # Leer estado de una Marca
            try:
                addr = int(input("  Introduce la dirección del bit a leer (ej: 160): "))
                print(f"\n-> Leyendo estado del bit {addr}...")
                estado_bit = read_single_bit_from_register(client, bit_address=addr)
                if estado_bit is not None:
                    print(f"  => El estado final del bit {addr} es: {estado_bit}")
            except ValueError:
                print("  Error: Debes introducir un número entero.")
                
        elif choice == '10': # Cambiar estado de una Marca
            try:
                addr = int(input("  Introduce la dirección del bit a cambiar (ej: 168): "))
                new_state_str = input("  Introduce el nuevo estado (1 para ON, 0 para OFF): ")
                new_state = bool(int(new_state_str))
                print(f"\n-> Intentando escribir en bit {addr} el valor {new_state}...")
                success = write_single_bit_in_register(client, bit_address=addr, new_value=new_state)
                if success:
                    print("  => ¡Comando de escritura completado!")
                else:
                    print("  => Fallo en el proceso de escritura.")
            except (ValueError, IndexError):
                print("  Error: Entrada no válida.")

        elif choice.lower() == 'q':
            print("Terminando programa...")
            break
        else:
            print("Opción no válida. Por favor, intenta de nuevo.")
        
        time.sleep(0.5)

except ConnectionError as e:
    print(f"Error de Conexión: {e}")
except Exception as e:
    print(f"Ha ocurrido un error inesperado: {e}")
finally:
    if client.is_socket_open():
        client.close()
        print("\nConexión cerrada.")