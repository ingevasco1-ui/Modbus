#include <Ethernet.h>

byte mac[] = {0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED};
EthernetClient client;
uint16_t hr0;
unsigned long lastRead = 0;

void setup() {
  Serial.begin(115200);
  Ethernet.begin(mac, IPAddress(192,168,0,100));
}

bool readHR0() {
  if (!client.connect(IPAddress(192,168,0,1), 502)) return false;
  
  // Mensaje fijo para leer HR0
  static const uint8_t modbusMsg[] = {0x00,0x01,0x00,0x00,0x00,0x06,0x00,0x03,0x00,0x00,0x00,0x01};
  client.write(modbusMsg, 12);
  client.flush();
  
  delay(20); // Mínimo delay para respuesta
  
  if (client.available() >= 9) {
    while(client.available() > 9) client.read(); // Limpiar buffer
    for(byte i=0; i<7; i++) client.read(); // Saltar cabecera
    hr0 = (client.read() << 8) | client.read();
    client.stop();
    return true;
  }
  
  client.stop();
  return false;
}

void loop() {
  if (millis() - lastRead > 500) { // Lectura cada 500ms
    lastRead = millis();
    if (readHR0()) Serial.println(hr0);
  }
}
