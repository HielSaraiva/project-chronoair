#define BOTAO1 19
#define BOTAO2 21
#define BOTAO3 22
#define BOTAO4 23

void setup() {
    Serial.begin(115200);  // Inicializa o monitor serial
    pinMode(BOTAO1, INPUT_PULLDOWN);  // Ativa pull-up interno
    pinMode(BOTAO2, INPUT_PULLUP);
    pinMode(BOTAO3, INPUT_PULLUP);
    pinMode(BOTAO4, INPUT_PULLUP);
}

void loop() {
    if (digitalRead(BOTAO1) == LOW) {
        Serial.println("Botão 1 pressionado!");
        delay(300);  // Debounce
    }
    if (digitalRead(BOTAO2) == LOW) {
        Serial.println("Botão 2 pressionado!");
        delay(300);
    }
    if (digitalRead(BOTAO3) == LOW) {
        Serial.println("Botão 3 pressionado!");
        delay(300);
    }
    if (digitalRead(BOTAO4) == LOW) {
        Serial.println("Botão 4 pressionado!");
        delay(300);
    }
}
