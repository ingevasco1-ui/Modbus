from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.datastore import ModbusSparseDataBlock
import threading
import time
import random
from datetime import datetime

class ModbusServer:
    def __init__(self):
        self.request_count = 0
        
        # Crear un diccionario vacío para los registros
        self.registers = {}
        
        # Inicializar los primeros registros
        for i in range(100):
            self.registers[i] = 0
            
        # Usar ModbusSparseDataBlock que permite actualizaciones dinámicas
        self.store = ModbusSlaveContext(
            hr=ModbusSparseDataBlock(self.registers)
        )
        self.context = ModbusServerContext(slaves=self.store, single=True)
        
    def update_data(self):
        """Actualizar datos cada 2 segundos"""
        counter = 0
        while True:
            try:
                # ✅ Actualizar directamente el diccionario
                self.registers[0] = random.randint(100, 1000)  # HR0
                self.registers[1] = counter % 1000             # HR1
                self.registers[2] = 500 + random.randint(0, 500)  # HR2
                self.registers[3] = self.request_count         # HR3
                
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"📊 [{timestamp}] HR0={self.registers[0]}, HR1={self.registers[1]}, HR2={self.registers[2]}, HR3={self.registers[3]}")
                
                counter += 1
                time.sleep(2)
                
            except Exception as e:
                print(f"💥 Error actualizando datos: {e}")
                time.sleep(1)
    
    def start(self):
        print("=" * 60)
        print("🚀 SERVIDOR MODBUS TCP - USANDO SPARSE DATABLOCK")
        print("📍 0.0.0.0:502")
        print("📊 Registros (actualizados cada 2s):")
        print("   HR0(40001): Aleatorio (100-1000)")
        print("   HR1(40002): Contador (0-999)")
        print("   HR2(40003): Aleatorio (500-1000)")
        print("   HR3(40004): Solicitudes recibidas")
        print("👀 Esperando conexiones...")
        print("=" * 60)
        
        # Iniciar actualización de datos en hilo separado
        data_thread = threading.Thread(target=self.update_data, daemon=True)
        data_thread.start()
        
        # Iniciar servidor Modbus
        StartTcpServer(context=self.context, address=("0.0.0.0", 502))

if __name__ == "__main__":
    server = ModbusServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido")