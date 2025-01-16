#include <IRremote.h>
#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// Constantes
#define RAW_LENGTH_RECEIVED_MIN 75  // Tamanho mínimo do código raw a ser recebido
#define RAW_BUFFER_LENGTH 750       // For air condition remotes it requires 750. Default is 200.
#define IR_FREQUENCY 38             // Frequência do sinal IR
#define MSG_BUFFER_SIZE (500)       // Define o tamanho do buffer

// Definindo os GPIOs usados
#define IR_RECEIVE 13  // Pino (D13) conectado ao LED IR Receptor VS1838B
#define LED_RED 16     // Pino (RX2) conectado ao LED vermelho
#define IR_SENDER 18   // Pino (D18) conectado ao LED IR Emissor
#define LED_WHITE 17   // Pino (TX2) conectado ao LED branco

// Variáveis Globais

// Sinal IR
bool sinalRecebido = false;

// Configuração Wi-Fi
const char* ssid = "brisa-4160473";
const char* password = "nsexdx3q";

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
} sStoredIRData;

// Protótipos de Funcoes
void storeCode();
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
  pinMode(LED_RED, OUTPUT);                           // Configura o pino do LED_RED como saída

  IrSender.begin(IR_SENDER);   // Inicializando o emissor IR com o pino padrao
  disableLEDFeedback();        // Desabilita o feedback do LED no pino padrao
  pinMode(LED_WHITE, OUTPUT);  // Configura o pino do LED_WHITE como saída

  setup_wifi();  // Conecta à rede WiFi

  // Setando as informações para o objeto "cliente"
  espClient.setCACert(root_ca);
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);  //Passando função como argumento
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
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

void sendCode(storedIRDataStruct* aIRDataToSend) {
  // Assume 38 KHz
  IrSender.sendRaw(aIRDataToSend->rawCode, aIRDataToSend->rawCodeLength, IR_FREQUENCY);
  Serial.println(F("Código enviado"));
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

  if (String(topic) == "comando" && String(acao) == "gravar") {
    unsigned long startRecording = millis();
    unsigned long timeout = 10000;
    bool sinalDetectado = false;

    memset(&sStoredIRData, 0, sizeof(sStoredIRData));  // Limpa o buffer de dados armazenados
    Serial.println("Pronto para receber sinal IR...");
    digitalWrite(LED_RED, HIGH);

    while (millis() - startRecording < timeout) {
      if (IrReceiver.decode()) {
        Serial.println("Sinal IR detectado!");
        if (IrReceiver.decodedIRData.rawlen >= RAW_LENGTH_RECEIVED_MIN) {
          sinalDetectado = true;

          // Indicação luminosa (Sinal Recebido)
          digitalWrite(LED_RED, LOW);
          delay(50);
          digitalWrite(LED_RED, HIGH);
          delay(50);
          digitalWrite(LED_RED, LOW);
          delay(50);
          digitalWrite(LED_RED, HIGH);
          delay(50);

          break;
        } else {
          Serial.println("Sinal IR muito curto, ignorando...");
        }
        IrReceiver.resume();
      }
    }

    digitalWrite(LED_RED, LOW);

    if (sinalDetectado) {
      storeCode();
      Serial.println("Sinal IR armazenado com sucesso!");
    } else {
      Serial.println("Nenhum sinal IR válido recebido dentro do tempo limite.");
    }

    IrReceiver.resume();  // Prepara o receptor para receber novos sinais
  } else if (String(topic) == "comando" && String(acao) == "emitir") {
    Serial.println("Emitindo sinal IR armazenado...");
    sendCode(&sStoredIRData);

    // Indicação luminosa (Sinal Enviado)
    digitalWrite(LED_WHITE, HIGH);
    delay(200);
    digitalWrite(LED_WHITE, LOW);
    Serial.println("Sinal IR emitido com sucesso.");
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