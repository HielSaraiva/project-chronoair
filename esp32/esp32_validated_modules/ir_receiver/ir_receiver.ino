#include <IRremote.h>
#include <Arduino.h>

// Variáveis Globais
#define RAW_LENGTH_RECEIVED_MIN 100  // Tamanho mínmo do código raw a ser recebido

// Definindo os GPIOs usados
#define IR_RECEIVE_PIN 13  // Pino conectado ao VS1838B
#define LED_RED 16         // Pino conectado ao LED vermelho


void setup() {
  Serial.begin(115200);  // Inicializando o monitor serial
  while (!Serial)
    ;  // Espera o serial ficar disponível

  Serial.println(F("START " __FILE__ " from " __DATE__ "\r\nUsing library version " VERSION_IRREMOTE));  // Apenas para saber qual programa esta rodando

  IrReceiver.begin(IR_RECEIVE_PIN, ENABLE_LED_FEEDBACK);  // Inicializando o receptor IR
  pinMode(LED_RED, OUTPUT);                               // Configura o pino do LED_RED como saída

  Serial.print(F("Pronto para receber sinais IR: "));
}

void loop() {
  if (IrReceiver.decode() && IrReceiver.decodedIRData.rawlen >= RAW_LENGTH_RECEIVED_MIN) {  // Se um sinal IR foi recebido E tiver um tamanho maior do que o mínmo esperado

    Serial.println(F("Código RAW recebido: "));
    IrReceiver.printIRResultRawFormatted(&Serial, true);  // Printa o código raw formatado

    // for (int i = 0; i < IrReceiver.decodedIRData.rawlen; i++) {            // Exibe o conteúdo do array de dados RAW
    //   Serial.print(IrReceiver.decodedIRData.decodedRawDataArray[i], DEC);  // Imprime o valor em decimal
    //   Serial.print(" ");                                                   // Espaço entre os valores
    // }

    IrReceiver.printIRResultShort(&Serial);  // Printa o Protocolo e o tamanho dos dados recebidos

    digitalWrite(LED_RED, HIGH);  // Acende o LED
    delay(200);                   // Mantém o LED aceso por 200ms
    digitalWrite(LED_RED, LOW);   // Apaga o LED

    Serial.println();
    IrReceiver.resume();  // Prepara para o próximo sinal
  }
}
