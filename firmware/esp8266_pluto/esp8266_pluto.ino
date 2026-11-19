// Commande PlutoSDR - ESP8266 sur D4 (GPIO2) via NPN 2N2222 + IRLZ44N
// Logique INVERSEE : D4 = LOW -> Pluto ALLUME ; D4 = HIGH -> Pluto ETEINT
// (D4 est a l'etat haut au demarrage de l'ESP8266 : le Pluto reste eteint)
//
// Moniteur serie : 115200 bauds, fin de ligne "Nouvelle ligne"
//   A : allumer le PlutoSDR
//   E : eteindre le PlutoSDR

#define PLUTO_PIN 2   // D4 = GPIO2

#define PLUTO_ON  LOW
#define PLUTO_OFF HIGH

void setup() {
  digitalWrite(PLUTO_PIN, PLUTO_OFF);   // Pluto eteint au demarrage
  pinMode(PLUTO_PIN, OUTPUT);

  Serial.begin(115200);
  delay(100);
  Serial.println();
  Serial.println("Commande PlutoSDR prete (Pluto eteint)");
}

void loop() {
  Serial.println("Entrer A pour allumer le PlutoSDR");
  Serial.println("Entrer E pour eteindre le PlutoSDR");

  // yield() evite le redemarrage par le watchdog de l'ESP8266
  while (Serial.available() == 0) {
    yield();
  }

  String rep = Serial.readStringUntil('\n');
  rep.trim();

  Serial.print("Commande recue : ");
  Serial.println(rep);

  if (rep.equalsIgnoreCase("A")) {
    digitalWrite(PLUTO_PIN, PLUTO_ON);
    Serial.println("PlutoSDR ALLUME");
  }
  else if (rep.equalsIgnoreCase("E")) {
    digitalWrite(PLUTO_PIN, PLUTO_OFF);
    Serial.println("PlutoSDR ETEINT");
  }
  else {
    Serial.println("Commande non reconnue");
  }

  Serial.println("-------------------");
}
