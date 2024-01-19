#include <WiFi.h>
#include <HTTPClient.h>
#include <TinyGPS++.h>

const char* ssid = "Totalplay9EA3";
const char* password = "9EA3D244jSKwwzmz";

TinyGPSPlus gps;
HardwareSerial SerialGPS(1);

// Configura los pines RX y TX para el GPS
const int RXPin = 16;
const int TXPin = 17;
const int GPSBaud = 9600;

// URL del servidor Flask en la Raspberry Pi
const char* serverName = "http://192.168.100.96:5000/agregar_punto_ruta";

void setup() {
  Serial.begin(9600);
  SerialGPS.begin(GPSBaud, SERIAL_8N1, RXPin, TXPin);
  
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("Conectando a WiFi...");
  }
  Serial.println("Conectado a WiFi");
}

void loop() {
  while (SerialGPS.available() > 0) {
    if (gps.encode(SerialGPS.read())) {
      if (gps.location.isValid()) {
        float latitud = gps.location.lat();
        float longitud = gps.location.lng();

        // Enviar los datos al servidor Flask
        if (WiFi.status() == WL_CONNECTED) {
          HTTPClient http;
          http.begin(serverName);
          http.addHeader("Content-Type", "application/json");
          
          String httpRequestData = "{\"latitud\":" + String(latitud, 6) + ",\"longitud\":" + String(longitud, 6) + "}";
          int httpResponseCode = http.POST(httpRequestData);

          if (httpResponseCode > 0) {
            String response = http.getString();
            Serial.println(response);
          }
          else {
            Serial.print("Error en el código de respuesta HTTP: ");
            Serial.println(httpResponseCode);
          }
          http.end();
        }
        delay(10000); // Espera 10 segundos antes de enviar la próxima ubicación
      }
    }
  }
}

