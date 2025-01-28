#include <IRremote.h>
#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// Constantes
#define RAW_LENGTH_RECEIVED_MIN 50  // Tamanho mínimo do código raw a ser recebido
#define RAW_BUFFER_LENGTH 750       // For air condition remotes it requires 750. Default is 200.
#define IR_FREQUENCY 38             // Frequência do sinal IR
#define MSG_BUFFER_SIZE (500)       // Define o tamanho do buffer

// Definindo os GPIOs usados
#define IR_RECEIVE 13          // Pino (D13) conectado ao LED IR Receptor VS1838B
#define IR_SENDER 18           // Pino (D18) conectado ao LED IR Emissor
#define LED_RGB_RED 4          // Pino (D4) conectado ao pino VERMELHO do led RGB
#define LED_RGB_GREEN 16       // Pino (RX2) conectado ao pino VERDE do led RGB
#define LED_RGB_BLUE 17        // Pino (TX2) conectado ao pino AZUL do led RGB
#define RECEIVE_BUTTON_OFF 19  // Pino (D23) conectado ao botão de receber IR (Desligar)
#define EMITTER_BUTTON_OFF 22  // Pino (D22) conectado ao botão de emitir IR (Desligar)
#define RECEIVE_BUTTON_ON 21   // Pino (D21) conectado ao botão de receber IR (Ligar)
#define EMITTER_BUTTON_ON 23   // Pino (D19) conectado ao botão de emitir IR (Ligar)


// Variáveis Globais

// Sinal IR
bool sinalRecebido = false;

// Variáveis do botão:
int lastStateReceiverOff = HIGH;  // O último estado do pino de input receiver (Desligar)
int lastStateEmitterOff = HIGH;   // O último estado do pino de input emitter (Desligar)
int currentStateReceiverOff;      // O estado atual do receiver (Desligar)
int currentStateEmitterOff;       // O estado atual do emitter (Desligar)
int lastStateReceiverOn = HIGH;   // O último estado do pino de input receiver (Ligar)
int lastStateEmitterOn = HIGH;    // O último estado do pino de input emitter (Ligar)
int currentStateReceiverOn;       // O estado atual do receiver (Ligar)
int currentStateEmitterOn;        // O estado atual do emitter (Ligar)

// Configuração Wi-Fi
const char* ssid = "brisa-4160473";
const char* password = "nsexdx3q";
// const char* ssid = "IFCE";
// const char* password = "ifcewifi";

// Configurações do broker MQTT
const char* mqtt_server = "70c7294fcccf4b729c7c25b7ce3006fb.s1.eu.hivemq.cloud";
const int mqtt_port = 8883;  // Porta segura para TLS
const char* mqtt_user = "esp32_ir";
const char* mqtt_password = "Hiel1234";

// Configuração do Cliente
WiFiClientSecure espClient;
PubSubClient client(espClient);
// unsigned long lastMsg = 0;
char msg[MSG_BUFFER_SIZE];
// int value = 0;

// Certificado de Criptografia HiveMQ Cloud (hardcoded)
static const char* root_ca PROGMEM = R"EOF(
-----BEGIN CERTIFICATE-----
MIIFazCCA1OgAwIBAgIRAIIQz7DSQONZRGPgu2OCiwAwDQYJKoZIhvcNAQELBQAw
TzELMAkGA1UEBhMCVVMxKTAnBgNVBAoTIEludGVybmV0IFNlY3VyaXR5IFJlc2Vh
cmNoIEdyb3VwMRUwEwYDVQQDEwxJU1JHIFJvb3QgWDEwHhcNMTUwNjA0MTEwNDM4
WhcNMzUwNjA0MTEwNDM4WjBPMQswCQYDVQQGEwJVUzEpMCcGA1UEChMgSW50ZXJu
ZXQgU2VjdXJpdHkgUmVzZWFyY2ggR3JvdXAxFTATBgNVBAMTDElTUkcgUm9vdCBY
MTCCAiIwDQYJKoZIhvcNAQEBBQADggIPADCCAgoCggIBAK3oJHP0FDfzm54rVygc
h77ct984kIxuPOZXoHj3dcKi/vVqbvYATyjb3miGbESTtrFj/RQSa78f0uoxmyF+
0TM8ukj13Xnfs7j/EvEhmkvBioZxaUpmZmyPfjxwv60pIgbz5MDmgK7iS4+3mX6U
A5/TR5d8mUgjU+g4rk8Kb4Mu0UlXjIB0ttov0DiNewNwIRt18jA8+o+u3dpjq+sW
T8KOEUt+zwvo/7V3LvSye0rgTBIlDHCNAymg4VMk7BPZ7hm/ELNKjD+Jo2FR3qyH
B5T0Y3HsLuJvW5iB4YlcNHlsdu87kGJ55tukmi8mxdAQ4Q7e2RCOFvu396j3x+UC
B5iPNgiV5+I3lg02dZ77DnKxHZu8A/lJBdiB3QW0KtZB6awBdpUKD9jf1b0SHzUv
KBds0pjBqAlkd25HN7rOrFleaJ1/ctaJxQZBKT5ZPt0m9STJEadao0xAH0ahmbWn
OlFuhjuefXKnEgV4We0+UXgVCwOPjdAvBbI+e0ocS3MFEvzG6uBQE3xDk3SzynTn
jh8BCNAw1FtxNrQHusEwMFxIt4I7mKZ9YIqioymCzLq9gwQbooMDQaHWBfEbwrbw
qHyGO0aoSCqI3Haadr8faqU9GY/rOPNk3sgrDQoo//fb4hVC1CLQJ13hef4Y53CI
rU7m2Ys6xt0nUW7/vGT1M0NPAgMBAAGjQjBAMA4GA1UdDwEB/wQEAwIBBjAPBgNV
HRMBAf8EBTADAQH/MB0GA1UdDgQWBBR5tFnme7bl5AFzgAiIyBpY9umbbjANBgkq
hkiG9w0BAQsFAAOCAgEAVR9YqbyyqFDQDLHYGmkgJykIrGF1XIpu+ILlaS/V9lZL
ubhzEFnTIZd+50xx+7LSYK05qAvqFyFWhfFQDlnrzuBZ6brJFe+GnY+EgPbk6ZGQ
3BebYhtF8GaV0nxvwuo77x/Py9auJ/GpsMiu/X1+mvoiBOv/2X/qkSsisRcOj/KK
NFtY2PwByVS5uCbMiogziUwthDyC3+6WVwW6LLv3xLfHTjuCvjHIInNzktHCgKQ5
ORAzI4JMPJ+GslWYHb4phowim57iaztXOoJwTdwJx4nLCgdNbOhdjsnvzqvHu7Ur
TkXWStAmzOVyyghqpZXjFaH3pO3JLF+l+/+sKAIuvtd7u+Nxe5AW0wdeRlN8NwdC
jNPElpzVmbUq4JUagEiuTDkHzsxHpFKVK7q4+63SM1N95R1NbdWhscdCb+ZAJzVc
oyi3B43njTOQ5yOf+1CceWxG1bQVs5ZufpsMljq4Ui0/1lvh+wjChP4kqKOJ2qxq
4RgqsahDYVvTH9w7jXbyLeiNdd8XM2w9U/t7y0Ff/9yi0GE44Za4rF2LN9d11TPA
mRGunUHBcnWEvgJBQl9nJEiU0Zsnvgc/ubhPgXRR4Xq37Z0j4r7g1SgEEzwxA57d
emyPxgcYxn/eR44/KJ4EBs+lVDR3veyJm+kXQ99b21/+jh5Xos1AnX5iItreGCc=
-----END CERTIFICATE-----
)EOF";

// Storage for the recorded code
struct storedIRDataStruct {
  IRData receivedIRData;
  // extensions for sendRaw
  uint8_t rawCode[RAW_BUFFER_LENGTH];  // The durations if raw
  uint8_t rawCodeLength;               // The length of the code
} aStoredIRDataOff, aStoredIRDataOn;

// Protótipos de Funcoes
void storeCodeOff();
void storeCodeOn();
void sendCode(storedIRDataStruct* aIRDataToSend);
void setup_wifi();
void callback(char* topic, byte* payload, unsigned int length);
void reconnect();

void setup() {
  Serial.begin(115200);  // Inicializando o monitor serial
  while (!Serial)
    ;  // Espera o serial ficar disponível

  Serial.println(F("START " __FILE__ " from " __DATE__ "\r\nUsing library version " VERSION_IRREMOTE));  // Apenas para saber qual programa esta rodando

  IrReceiver.begin(IR_RECEIVE, ENABLE_LED_FEEDBACK);  // Inicializando o receptor IR com o pino padrao

  IrSender.begin(IR_SENDER);  // Inicializando o emissor IR com o pino padrao
  disableLEDFeedback();       // Desabilita o feedback do LED no pino padrao

  // Configurando LED RGB
  pinMode(LED_RGB_BLUE, OUTPUT);
  pinMode(LED_RGB_GREEN, OUTPUT);
  pinMode(LED_RGB_RED, OUTPUT);

  // Configurando BUTTONS
  pinMode(RECEIVE_BUTTON_OFF, INPUT_PULLUP);  // ativa o resistor pull-up interno
  pinMode(EMITTER_BUTTON_OFF, INPUT_PULLUP);  // ativa o resistor pull-up interno
  pinMode(RECEIVE_BUTTON_ON, INPUT_PULLUP);   // ativa o resistor pull-up interno
  pinMode(EMITTER_BUTTON_ON, INPUT_PULLUP);   // ativa o resistor pull-up interno

  setup_wifi();  // Conecta à rede WiFi

  // Setando as informações para o objeto "cliente"
  espClient.setCACert(root_ca);
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);  //Passando função como argumento
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    setup_wifi();
  }

  if (!client.connected()) {
    reconnect();
  }

  client.loop();

  currentStateReceiverOff = digitalRead(RECEIVE_BUTTON_OFF);
  currentStateEmitterOff = digitalRead(EMITTER_BUTTON_OFF);
  currentStateReceiverOn = digitalRead(RECEIVE_BUTTON_ON);
  currentStateEmitterOn = digitalRead(EMITTER_BUTTON_ON);

  // Verificar botão de RECEBER IR Off
  if (lastStateReceiverOff == LOW && currentStateReceiverOff == HIGH) {  // Botão pressionado (pino em LOW)
    Serial.println("Botão RECEBER IR pressionado!");
    unsigned long startRecording = millis();
    unsigned long timeout = 10000;
    bool sinalDetectado = false;

    memset(&aStoredIRDataOff, 0, sizeof(aStoredIRDataOff));  // Limpa o buffer de dados armazenados
    Serial.println("Pronto para receber sinal IR de DESLIGAR...");
    analogWrite(LED_RGB_BLUE, 0);
    analogWrite(LED_RGB_GREEN, 0);
    analogWrite(LED_RGB_RED, 255);

    while (millis() - startRecording < timeout) {
      if (IrReceiver.decode()) {
        Serial.println("Sinal IR detectado!");
        if (IrReceiver.decodedIRData.rawlen >= RAW_LENGTH_RECEIVED_MIN) {
          sinalDetectado = true;

          // Indicação luminosa (Sinal Recebido)
          analogWrite(LED_RGB_BLUE, 0);
          analogWrite(LED_RGB_GREEN, 0);
          analogWrite(LED_RGB_RED, 0);
          delay(200);
          analogWrite(LED_RGB_BLUE, 0);
          analogWrite(LED_RGB_GREEN, 255);
          analogWrite(LED_RGB_RED, 0);
          delay(200);
          analogWrite(LED_RGB_BLUE, 0);
          analogWrite(LED_RGB_GREEN, 0);
          analogWrite(LED_RGB_RED, 0);

          break;
        } else {
          Serial.println("Sinal IR muito curto, ignorando...");
        }
        IrReceiver.resume();
      }
    }

    analogWrite(LED_RGB_BLUE, 0);
    analogWrite(LED_RGB_GREEN, 0);
    analogWrite(LED_RGB_RED, 0);

    if (sinalDetectado) {
      storeCodeOff();
      Serial.println("Sinal IR armazenado com sucesso!");
    } else {
      Serial.println("Nenhum sinal IR válido recebido dentro do tempo limite.");
    }

    IrReceiver.resume();  // Prepara o receptor para novos sinais
    delay(500);           // Evita detecção contínua devido ao debounce
  }
  lastStateReceiverOff = currentStateReceiverOff;


  // Verificar botão de EMITIR IR Off
  if (lastStateEmitterOff == LOW && currentStateEmitterOff == HIGH) {  // Botão pressionado (pino em LOW)
    Serial.println("Botão EMITIR IR pressionado (DESLIGAR)!");
    sendCode(&aStoredIRDataOff);

    // Indicação luminosa (Sinal Enviado)
    analogWrite(LED_RGB_BLUE, 255);
    analogWrite(LED_RGB_GREEN, 0);
    analogWrite(LED_RGB_RED, 0);
    delay(200);
    analogWrite(LED_RGB_BLUE, 0);
    analogWrite(LED_RGB_GREEN, 0);
    analogWrite(LED_RGB_RED, 0);

    Serial.println("Sinal IR emitido com sucesso (DESLIGAR).");
    delay(500);  // Evita detecção contínua devido ao debounce
  }
  lastStateEmitterOff = currentStateEmitterOff;

  // Verificar botão de RECEBER IR On
  if (lastStateReceiverOn == LOW && currentStateReceiverOn == HIGH) {  // Botão pressionado (pino em LOW)
    Serial.println("Botão RECEBER IR pressionado!");
    unsigned long startRecording = millis();
    unsigned long timeout = 10000;
    bool sinalDetectado = false;

    memset(&aStoredIRDataOn, 0, sizeof(aStoredIRDataOn));  // Limpa o buffer de dados armazenados
    Serial.println("Pronto para receber sinal IR de LIGAR...");
    analogWrite(LED_RGB_BLUE, 0);
    analogWrite(LED_RGB_GREEN, 0);
    analogWrite(LED_RGB_RED, 255);

    while (millis() - startRecording < timeout) {
      if (IrReceiver.decode()) {
        Serial.println("Sinal IR detectado!");
        if (IrReceiver.decodedIRData.rawlen >= RAW_LENGTH_RECEIVED_MIN) {
          sinalDetectado = true;

          // Indicação luminosa (Sinal Recebido)
          analogWrite(LED_RGB_BLUE, 0);
          analogWrite(LED_RGB_GREEN, 0);
          analogWrite(LED_RGB_RED, 0);
          delay(200);
          analogWrite(LED_RGB_BLUE, 0);
          analogWrite(LED_RGB_GREEN, 255);
          analogWrite(LED_RGB_RED, 0);
          delay(200);
          analogWrite(LED_RGB_BLUE, 0);
          analogWrite(LED_RGB_GREEN, 0);
          analogWrite(LED_RGB_RED, 0);

          break;
        } else {
          Serial.println("Sinal IR muito curto, ignorando...");
        }
        IrReceiver.resume();
      }
    }

    analogWrite(LED_RGB_BLUE, 0);
    analogWrite(LED_RGB_GREEN, 0);
    analogWrite(LED_RGB_RED, 0);

    if (sinalDetectado) {
      storeCodeOn();
      Serial.println("Sinal IR armazenado com sucesso!");
    } else {
      Serial.println("Nenhum sinal IR válido recebido dentro do tempo limite.");
    }

    IrReceiver.resume();  // Prepara o receptor para novos sinais
    delay(500);           // Evita detecção contínua devido ao debounce
  }
  lastStateReceiverOn = currentStateReceiverOn;

  // Verificar botão de EMITIR IR On
  if (lastStateEmitterOn == LOW && currentStateEmitterOn == HIGH) {  // Botão pressionado (pino em LOW)
    Serial.println("Botão EMITIR IR pressionado (LIGAR)!");
    sendCode(&aStoredIRDataOn);

    // Indicação luminosa (Sinal Enviado)
    analogWrite(LED_RGB_BLUE, 255);
    analogWrite(LED_RGB_GREEN, 0);
    analogWrite(LED_RGB_RED, 0);
    delay(200);
    analogWrite(LED_RGB_BLUE, 0);
    analogWrite(LED_RGB_GREEN, 0);
    analogWrite(LED_RGB_RED, 0);

    Serial.println("Sinal IR emitido com sucesso (LIGAR).");
    delay(500);  // Evita detecção contínua devido ao debounce
  }
  lastStateEmitterOn = currentStateEmitterOn;
}

void storeCodeOff() {
  aStoredIRDataOff.receivedIRData = IrReceiver.decodedIRData;

  Serial.print(F("Sinal recebido e armazenado"));
  IrReceiver.printIRResultRawFormatted(&Serial, true);  // Output the results in RAW format
  IrReceiver.printIRResultShort(&Serial);               // Exibe o Protocolo, o código RAW em HEXA e o tamanho dos dados recebidos
  aStoredIRDataOff.rawCodeLength = IrReceiver.decodedIRData.rawDataPtr->rawlen - 1;
  /*
         * Store the current raw data in a dedicated array for later usage
         */
  IrReceiver.compensateAndStoreIRResultInArray(aStoredIRDataOff.rawCode);
}

void storeCodeOn() {
  aStoredIRDataOn.receivedIRData = IrReceiver.decodedIRData;

  Serial.print(F("Sinal recebido e armazenado"));
  IrReceiver.printIRResultRawFormatted(&Serial, true);  // Output the results in RAW format
  IrReceiver.printIRResultShort(&Serial);               // Exibe o Protocolo, o código RAW em HEXA e o tamanho dos dados recebidos
  aStoredIRDataOn.rawCodeLength = IrReceiver.decodedIRData.rawDataPtr->rawlen - 1;
  /*
         * Store the current raw data in a dedicated array for later usage
         */
  IrReceiver.compensateAndStoreIRResultInArray(aStoredIRDataOn.rawCode);
}

void sendCode(storedIRDataStruct* aIRDataToSend) {
  // Assume 38 KHz
  IrReceiver.stop();  // Desabilita o receptor IR

  IrSender.sendRaw(aIRDataToSend->rawCode, aIRDataToSend->rawCodeLength, IR_FREQUENCY);
  Serial.println(F("Código enviado"));

  delay(100);          // Delay para garantir que o sinal emitido não será capturado
  IrReceiver.start();  // Reativa o receptor IR
}

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Conectando à rede: ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);  // O ESP32 funcionará como um dispositivo que se conecta a um roteador ou ponto de acesso
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  randomSeed(micros());  // Cria um cliente ID único para o MQTT

  Serial.println("");
  Serial.println("WiFi conectado");
  Serial.print("Endereço de IP: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Tópico recebido [");
  Serial.print(topic);
  Serial.print("]. ");

  String message;
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }

  Serial.print("Comando recebido: ");
  Serial.println(message);

  // Tenta decodificar o JSON
  StaticJsonDocument<200> doc;
  DeserializationError error = deserializeJson(doc, message);

  if (error) {
    Serial.print("Erro ao decodificar JSON: ");
    Serial.println(error.c_str());
    return;
  }

  // Verifica o valor da chave "acao" no JSON
  const char* acao = doc["acao"];

  if (String(topic) == "comando" && String(acao) == "gravarOff") {
    unsigned long startRecording = millis();
    unsigned long timeout = 10000;
    bool sinalDetectado = false;

    memset(&aStoredIRDataOff, 0, sizeof(aStoredIRDataOff));  // Limpa o buffer de dados armazenados
    Serial.println("Pronto para receber sinal IR de DESLIGAR...");
    analogWrite(LED_RGB_BLUE, 0);
    analogWrite(LED_RGB_GREEN, 0);
    analogWrite(LED_RGB_RED, 255);

    while (millis() - startRecording < timeout) {
      if (IrReceiver.decode()) {
        Serial.println("Sinal IR detectado!");
        if (IrReceiver.decodedIRData.rawlen >= RAW_LENGTH_RECEIVED_MIN) {
          sinalDetectado = true;

          // Indicação luminosa (Sinal Recebido)
          analogWrite(LED_RGB_BLUE, 0);
          analogWrite(LED_RGB_GREEN, 0);
          analogWrite(LED_RGB_RED, 0);
          delay(200);
          analogWrite(LED_RGB_BLUE, 0);
          analogWrite(LED_RGB_GREEN, 255);
          analogWrite(LED_RGB_RED, 0);
          delay(200);
          analogWrite(LED_RGB_BLUE, 0);
          analogWrite(LED_RGB_GREEN, 0);
          analogWrite(LED_RGB_RED, 0);

          break;
        } else {
          Serial.println("Sinal IR muito curto, ignorando...");
        }
        // IrReceiver.resume();
      }
    }

    analogWrite(LED_RGB_BLUE, 0);
    analogWrite(LED_RGB_GREEN, 0);
    analogWrite(LED_RGB_RED, 0);

    if (sinalDetectado) {
      storeCodeOff();
      Serial.println("Sinal IR armazenado com sucesso!");
    } else {
      Serial.println("Nenhum sinal IR válido recebido dentro do tempo limite.");
    }

    IrReceiver.resume();  // Prepara o receptor para receber novos sinais
  } else if (String(topic) == "comando" && String(acao) == "emitirOff") {
    Serial.println("Emitindo sinal IR armazenado (DESLIGAR)...");
    sendCode(&aStoredIRDataOff);

    // Indicação luminosa (Sinal Enviado)
    analogWrite(LED_RGB_BLUE, 255);
    analogWrite(LED_RGB_GREEN, 0);
    analogWrite(LED_RGB_RED, 0);
    delay(200);
    analogWrite(LED_RGB_BLUE, 0);
    analogWrite(LED_RGB_GREEN, 0);
    analogWrite(LED_RGB_RED, 0);

    Serial.println("Sinal IR emitido com sucesso (DESLIGAR).");
  } else if (String(topic) == "comando" && String(acao) == "gravarOn") {
    unsigned long startRecording = millis();
    unsigned long timeout = 10000;
    bool sinalDetectado = false;

    memset(&aStoredIRDataOn, 0, sizeof(aStoredIRDataOn));  // Limpa o buffer de dados armazenados
    Serial.println("Pronto para receber sinal IR de LIGAR...");
    analogWrite(LED_RGB_BLUE, 0);
    analogWrite(LED_RGB_GREEN, 0);
    analogWrite(LED_RGB_RED, 255);

    while (millis() - startRecording < timeout) {
      if (IrReceiver.decode()) {
        Serial.println("Sinal IR detectado!");
        if (IrReceiver.decodedIRData.rawlen >= RAW_LENGTH_RECEIVED_MIN) {
          sinalDetectado = true;

          // Indicação luminosa (Sinal Recebido)
          analogWrite(LED_RGB_BLUE, 0);
          analogWrite(LED_RGB_GREEN, 0);
          analogWrite(LED_RGB_RED, 0);
          delay(200);
          analogWrite(LED_RGB_BLUE, 0);
          analogWrite(LED_RGB_GREEN, 255);
          analogWrite(LED_RGB_RED, 0);
          delay(200);
          analogWrite(LED_RGB_BLUE, 0);
          analogWrite(LED_RGB_GREEN, 0);
          analogWrite(LED_RGB_RED, 0);

          break;
        } else {
          Serial.println("Sinal IR muito curto, ignorando...");
        }
        // IrReceiver.resume();
      }
    }

    analogWrite(LED_RGB_BLUE, 0);
    analogWrite(LED_RGB_GREEN, 0);
    analogWrite(LED_RGB_RED, 0);

    if (sinalDetectado) {
      storeCodeOn();
      Serial.println("Sinal IR armazenado com sucesso!");
    } else {
      Serial.println("Nenhum sinal IR válido recebido dentro do tempo limite.");
    }

    IrReceiver.resume();  // Prepara o receptor para receber novos sinais
  } else if (String(topic) == "comando" && String(acao) == "emitirOn") {
    Serial.println("Emitindo sinal IR armazenado (LIGAR)...");
    sendCode(&aStoredIRDataOn);

    // Indicação luminosa (Sinal Enviado)
    analogWrite(LED_RGB_BLUE, 255);
    analogWrite(LED_RGB_GREEN, 0);
    analogWrite(LED_RGB_RED, 0);
    delay(200);
    analogWrite(LED_RGB_BLUE, 0);
    analogWrite(LED_RGB_GREEN, 0);
    analogWrite(LED_RGB_RED, 0);

    Serial.println("Sinal IR emitido com sucesso (LIGAR).");
  } else {
    Serial.println("Comando não reconhecido.");
  }
}

//Conexão com o MQTT Broker
void reconnect() {

  //Loop até estarmos reconectados
  while (!client.connected()) {

    Serial.println("Conectando ao Broker... ");

    //Client ID da ESP32
    String clientId = "ESP32Client";

    if (client.connect(clientId.c_str(), mqtt_user, mqtt_password)) {

      Serial.println("Conexão concluída!");

      //Subscrição no tópico
      client.subscribe("comando");

    } else {
      Serial.print("Conexão falhou! ");
      // Serial.print(client.state());
      Serial.println("Uma nova tentativa será executada em 3 segundos.");
      delay(3000);
    }
  }
}