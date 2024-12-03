#include <IRremote.h>
#include <Arduino.h>

// Definindo os GPIOs usados
#define IR_SENDER 18  // Pino (D18) conectado ao LED IR Emissor
#define LED_WHITE 17  // Pino (TX2) conectado ao LED branco

void setup() {
  Serial.begin(115200);  // Inicializando o monitor serial
  while (!Serial)
    ;  // Espera o serial ficar disponível

  Serial.println(F("START " __FILE__ " from " __DATE__ "\r\nUsing library version " VERSION_IRREMOTE));  // Apenas para saber qual programa esta rodando

  IrSender.begin(IR_SENDER);  // Inicializando o emissor IR com o pino padrao
  disableLEDFeedback();       // Desabilita o feedback do LED no pino padrao

  pinMode(LED_WHITE, OUTPUT);  // Configura o pino do LED_WHITE como saída

  Serial.print(F("Pronto para enviar sinais IR: "));
}

const uint16_t rawData[] = { -3173800
 +4400,-4400
 + 550,-1600 + 550,- 500 + 550,-1650 + 500,-1650
 + 500,- 550 + 550,- 500 + 550,-1600 + 550,- 550
 + 550,- 500 + 550,-1600 + 550,- 550 + 550,- 500
 + 550,-1600 + 550,-1600 + 550,- 550 + 550,-1600
 + 550,- 500 + 550,-1600 + 550,-1600 + 550,-1600
 + 550,-1600 + 550,- 550 + 550,-1600 + 550,-1600
 + 550,-1600 + 550,- 500 + 550,- 550 + 550,- 500
 + 550,- 550 + 550,-1600 + 550,- 500 + 550,- 550
 + 550,-1600 + 550,-1600 + 550,-1600 + 550,- 500
 + 600,- 500 + 550,- 500 + 600,- 500 + 550,- 500
 + 600,- 500 + 550,- 500 + 550,- 550 + 550,-1600
 + 550,-1600 + 550,-1600 + 550,-1600 + 550,-1600
 + 550,-5200 +4400,-4400 + 550,-1600 + 550,- 550
 + 500,-1650 + 500,-1650 + 500,- 550 + 550,- 550
 + 500,-1650 + 500,- 550 + 550,- 550 + 500,-1650
 + 500,- 550 + 550,- 550 + 500,-1650 + 500,-1650
 + 500,- 550 + 550,-1600 + 550,- 550 + 500,-1650
 + 500,-1650 + 500,-1650 + 500,-1650 + 500,- 550
 + 550,-1600 + 550,-1600 + 550,-1600 + 550,- 550
 + 500,- 550 + 550,- 550 + 500,- 550 + 550,-1600
 + 550,- 550 + 500,- 550 + 550,-1650 + 500,-1650
 + 500,-1650 + 500,- 550 + 500,- 550 + 550,- 550
 + 500,- 550 + 550,- 550 + 500,- 550 + 550,- 550
 + 500,- 550 + 550,-1650 + 500,-1650 + 500,-1650
 + 500,-1650 + 500,-1650 + 500};

void loop() {
  // Printando os dados do sinal RAW a ser enviado
  Serial.println();
  Serial.print(F("Enviando sinal RAW"));
  Serial.println();
  Serial.flush();

  IrSender.sendRaw(rawData, sizeof(rawData) / sizeof(rawData[0]), NEC_KHZ);  // Enviando o sinal RAW

  // LED de confirmacao (Sinal foi enviado)
  digitalWrite(LED_WHITE, HIGH);  // Acende o LED
  delay(100);                     // Mantém o LED aceso por 100ms
  digitalWrite(LED_WHITE, LOW);   // Apaga o LED

  delay(1000);  // o atraso deve ser maior que 5 ms, caso contrário o receptor o verá como um sinal longo
}
