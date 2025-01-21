#include <IRremote.h>
#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// Definindo os GPIOs usados
#define LED_RGB_RED 4     // Pino (D4) conectado ao pino VERMELHO do led RGB
#define LED_RGB_GREEN 16  // Pino (RX2) conectado ao pino VERDE do led RGB
#define LED_RGB_BLUE 17   // Pino (TX2) conectado ao pino AZUL do led RGB

void setup() {
  Serial.begin(115200);  // Inicializando o monitor serial
  while (!Serial)
    ;  // Espera o serial ficar disponível

  Serial.println(F("START " __FILE__ " from " __DATE__ "\r\nUsing library version " VERSION_IRREMOTE));  // Apenas para saber qual programa esta rodando

  // Configurando LED RGB
  pinMode(LED_RGB_BLUE, OUTPUT);
  pinMode(LED_RGB_GREEN, OUTPUT);
  pinMode(LED_RGB_RED, OUTPUT);
}

void loop() {
  analogWrite(LED_RGB_BLUE, 0);
  analogWrite(LED_RGB_GREEN, 0);
  analogWrite(LED_RGB_RED, 255);
  delay(500);
  // Indicação luminosa (Sinal Recebido)
  analogWrite(LED_RGB_BLUE, 0);
  analogWrite(LED_RGB_GREEN, 0);
  analogWrite(LED_RGB_RED, 0);
  delay(500);
  analogWrite(LED_RGB_BLUE, 0);
  analogWrite(LED_RGB_GREEN, 255);
  analogWrite(LED_RGB_RED, 0);
  delay(500);
  analogWrite(LED_RGB_BLUE, 0);
  analogWrite(LED_RGB_GREEN, 0);
  analogWrite(LED_RGB_RED, 0);
  delay(500);
  analogWrite(LED_RGB_BLUE, 255);
  analogWrite(LED_RGB_GREEN, 0);
  analogWrite(LED_RGB_RED, 0);
  delay(500);
  analogWrite(LED_RGB_BLUE, 0);
  analogWrite(LED_RGB_GREEN, 0);
  analogWrite(LED_RGB_RED, 0);
  delay(500);
}