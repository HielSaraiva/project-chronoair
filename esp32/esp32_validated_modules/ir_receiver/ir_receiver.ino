#include <IRremote.h>
#include <Arduino.h>

// Variáveis Globais
#define RAW_LENGTH_RECEIVED_MIN 100  // Tamanho mínmo do código raw a ser recebido

// Definindo os GPIOs usados
#define IR_RECEIVE 13  // Pino (D13) conectado ao LED IR Receptor VS1838B
#define LED_RED 16     // Pino (RX2) conectado ao LED vermelho

void setup() {
  Serial.begin(115200);  // Inicializando o monitor serial
  while (!Serial)
    ;  // Espera o serial ficar disponível

  Serial.println(F("START " __FILE__ " from " __DATE__ "\r\nUsing library version " VERSION_IRREMOTE));  // Apenas para saber qual programa esta rodando

  IrReceiver.begin(IR_RECEIVE, ENABLE_LED_FEEDBACK);  // Inicializando o receptor IR com o pino padrao

  pinMode(LED_RED, OUTPUT);  // Configura o pino do LED_RED como saída

  Serial.print(F("Pronto para receber sinais IR: "));
}

void loop() {
  if (IrReceiver.decode() && IrReceiver.decodedIRData.rawlen >= RAW_LENGTH_RECEIVED_MIN) {  // Se um sinal IR foi recebido E tiver um tamanho maior do que o mínmo esperado

    Serial.print(F("Código RAW recebido: "));
    // IrReceiver.printIRResultRawFormatted(&Serial, true);  // Printa os tempos do código RAW formatado
    Serial.println(IrReceiver.decodedIRData.decodedRawData, HEX);  // Exibe o código RAW recebido em HEXA

    IrReceiver.printIRResultShort(&Serial);  // Exibe o Protocolo, o código RAW em HEXA e o tamanho dos dados recebidos

    // LED de confirmacao (Sinal foi recebido)
    digitalWrite(LED_RED, HIGH);  // Acende o LED
    delay(200);                   // Mantém o LED aceso por 200ms
    digitalWrite(LED_RED, LOW);   // Apaga o LED

    Serial.println();
    IrReceiver.resume();  // Prepara para o próximo sinal
  }
}
