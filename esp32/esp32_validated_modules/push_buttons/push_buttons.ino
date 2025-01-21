#define BUTTON1 22  // Botão 1 no pino 32
#define BUTTON2 23  // Botão 2 no pino 33
#define LED_RED 4   // LED Vermelho no pino 4
#define LED_GREEN 16 // LED Verde no pino 16
#define LED_BLUE 17  // LED Azul no pino 17

void setup() {
  // Configuração dos botões como entrada com pull-up interno
  pinMode(BUTTON1, INPUT_PULLUP);
  pinMode(BUTTON2, INPUT_PULLUP);

  // Configuração dos pinos do LED como saída
  pinMode(LED_RED, OUTPUT);
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_BLUE, OUTPUT);

  // Inicializar LED desligado
  digitalWrite(LED_RED, LOW);
  digitalWrite(LED_GREEN, LOW);
  digitalWrite(LED_BLUE, LOW);
}

void loop() {
  // Leitura do estado dos botões
  bool button1State = digitalRead(BUTTON1) == LOW; // LOW = pressionado
  bool button2State = digitalRead(BUTTON2) == LOW; // LOW = pressionado

  // Controle do LED RGB
  if (button1State && button2State) {
    // Ambos pressionados: LED verde
    digitalWrite(LED_RED, LOW);
    digitalWrite(LED_GREEN, HIGH);
    digitalWrite(LED_BLUE, LOW);
  } else if (button1State) {
    // Apenas o botão 1 pressionado: LED vermelho
    digitalWrite(LED_RED, HIGH);
    digitalWrite(LED_GREEN, LOW);
    digitalWrite(LED_BLUE, LOW);
  } else if (button2State) {
    // Apenas o botão 2 pressionado: LED azul
    digitalWrite(LED_RED, LOW);
    digitalWrite(LED_GREEN, LOW);
    digitalWrite(LED_BLUE, HIGH);
  } else {
    // Nenhum botão pressionado: LED apagado
    digitalWrite(LED_RED, LOW);
    digitalWrite(LED_GREEN, LOW);
    digitalWrite(LED_BLUE, LOW);
  }

  delay(50); // Pequeno atraso para estabilidade
}
