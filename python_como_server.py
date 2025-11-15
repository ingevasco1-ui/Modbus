from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
import threading
import time

# Datastore con valores iniciales
store = ModbusSlaveContext(hr=ModbusSequentialDataBlock(0, [1000, 2000]))
context = ModbusServerContext(slaves=store, single=True)

def actualizar_registros():
    """Actualiza los registros cada 3 segundos"""
    contador = 0
    while True:
        nuevo_valor1 = 1000 + contador
        nuevo_valor2 = 2000 + (contador * 2)
        
        store.setValues(3, 0, [nuevo_valor1, nuevo_valor2])
        print(f"📤 Enviando - Reg0: {nuevo_valor1}, Reg1: {nuevo_valor2}")
        
        contador += 1
        time.sleep(1)

# Iniciar hilo de actualización
threading.Thread(target=actualizar_registros, daemon=True).start()

print("✅ Servidor Modbus activo: 127.0.0.1:502")
print("🔧 Configura Modbus Poll: Address=0, Length=2")
print("📊 Los valores cambiarán cada 3 segundos")

StartTcpServer(context=context, address=("0.0.0.0", 502))