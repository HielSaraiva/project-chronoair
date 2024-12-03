#include <IRremote.h>
#include <Arduino.h>

// Constantes
#define RAW_LENGTH_RECEIVED_MIN 100  // Tamanho mínimo do código raw a ser recebido
#define RAW_BUFFER_LENGTH 750        // For air condition remotes it requires 750. Default is 200.

// Definindo os GPIOs usados
#define IR_RECEIVE 13  // Pino (D13) conectado ao LED IR Receptor VS1838B
#define LED_RED 16     // Pino (RX2) conectado ao LED vermelho
#define IR_SENDER 18   // Pino (D18) conectado ao LED IR Emissor
#define LED_WHITE 17   // Pino (TX2) conectado ao LED branco

// Variáveis Globais
int DELAY_BETWEEN_REPEAT = 50;
bool sinalRecebido = false;

// Storage for the recorded code
struct storedIRDataStruct {
  IRData receivedIRData;
  // extensions for sendRaw
  uint8_t rawCode[RAW_BUFFER_LENGTH];  // The durations if raw
  uint8_t rawCodeLength;               // The length of the code
} sStoredIRData;

// Protótipos de Funcoes
void storeCode();
void sendCode(storedIRDataStruct *aIRDataToSend);

void setup() {
  Serial.begin(115200);  // Inicializando o monitor serial
  while (!Serial)
    ;  // Espera o serial ficar disponível

  Serial.println(F("START " __FILE__ " from " __DATE__ "\r\nUsing library version " VERSION_IRREMOTE));  // Apenas para saber qual programa esta rodando

  IrReceiver.begin(IR_RECEIVE, ENABLE_LED_FEEDBACK);  // Inicializando o receptor IR com o pino padrao
  pinMode(LED_RED, OUTPUT);                           // Configura o pino do LED_RED como saída

  IrSender.begin(IR_SENDER);   // Inicializando o emissor IR com o pino padrao
  disableLEDFeedback();        // Desabilita o feedback do LED no pino padrao
  pinMode(LED_WHITE, OUTPUT);  // Configura o pino do LED_WHITE como saída
}

void loop() {
  if (IrReceiver.decode() && IrReceiver.decodedIRData.rawlen >= RAW_LENGTH_RECEIVED_MIN) {  // Se um sinal IR foi recebido E tiver um tamanho maior do que o mínmo esperado
    sinalRecebido = true;
    Serial.println(F("Código RAW recebido"));
    // IrReceiver.printIRResultRawFormatted(&Serial, true);  // Printa os tempos do código RAW formatado
    // Serial.println(IrReceiver.decodedIRData.decodedRawData, HEX);  // Exibe o código RAW recebido em HEXA

    // IrReceiver.printIRResultShort(&Serial);  // Exibe o Protocolo, o código RAW em HEXA e o tamanho dos dados recebidos

    // LED de confirmacao (Sinal foi recebido)
    digitalWrite(LED_RED, HIGH);  // Acende o LED
    delay(200);                   // Mantém o LED aceso por 200ms
    digitalWrite(LED_RED, LOW);   // Apaga o LED

    storeCode();
  }
  IrReceiver.resume();  // Prepara para o próximo sinal

  if (sinalRecebido) {
    Serial.flush();
    sendCode(&sStoredIRData);
    delay(DELAY_BETWEEN_REPEAT);

    // LED de confirmacao (Sinal foi enviado)
    digitalWrite(LED_WHITE, HIGH);    // Acende o LED
    delay(100);                       // Mantém o LED aceso por 100ms
    digitalWrite(LED_WHITE, LOW);     // Apaga o LED
  }

  delay(100);
}

void storeCode() {
  sStoredIRData.receivedIRData = IrReceiver.decodedIRData;

  Serial.print(F("Sinal recebido e armazenado"));
  IrReceiver.printIRResultRawFormatted(&Serial, true);  // Output the results in RAW format
  IrReceiver.printIRResultShort(&Serial);               // Exibe o Protocolo, o código RAW em HEXA e o tamanho dos dados recebidos
  sStoredIRData.rawCodeLength = IrReceiver.decodedIRData.rawDataPtr->rawlen - 1;
  /*
         * Store the current raw data in a dedicated array for later usage
         */
  IrReceiver.compensateAndStoreIRResultInArray(sStoredIRData.rawCode);
}

void sendCode(storedIRDataStruct *aIRDataToSend) {
  // Assume 38 KHz
  IrSender.sendRaw(aIRDataToSend->rawCode, aIRDataToSend->rawCodeLength, 38);
  Serial.println(F("Código enviado"));
}
