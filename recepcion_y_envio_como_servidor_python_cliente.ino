#include <Ethernet.h>
#include <Modbus.h>
#include <ModbusIP.h>

byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
IPAddress ip(192, 168, 0, 100);
ModbusIP mb;

unsigned long ts = 0;
int i = 0;

void setup() {
  Serial.begin(115200);
  Ethernet.begin(mac, ip);
  
  // Inicializar con valores por defecto Y delays
  delay(100);
  mb.addHreg(0, 0);
  delay(100);
  mb.addHreg(1, 0);
  delay(100); 
  mb.addIreg(0, 0);
  delay(100);
  mb.addIreg(1, 0);
  delay(100);
  
  ts = millis(); 
  Serial.println("Modbus Listo - Inicializado con delays");
}

void loop() {
  mb.task();
  
  int sensorValue = analogRead(A1);
  
  if (millis() - ts >= 300) {   
    ts = millis();
    i++;
    if (i > 100) i = 0;
  }
  
  // Actualizar registros con pequeño delay
  mb.Ireg(0, sensorValue);
  delay(5);
  mb.Ireg(1, i);
  
  // Debug reducido para mejor performance
  if (millis() % 1000 < 100) { // Solo imprimir cada ~1 segundo
    Serial.print("IREG: ");
    Serial.print(sensorValue);
    Serial.print(", ");
    Serial.println(i);
  }
  
  delay(50); // Delay reducido
}
