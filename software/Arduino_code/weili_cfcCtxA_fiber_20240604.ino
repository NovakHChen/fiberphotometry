/*
 SeanContextTwoShockEthoTrig_20210423
 Sean

Starts shock countdown on ethovision trigger.
Gives shock for shockDur.
Hit RESET button to reset for next session.
 
*/
int ethoPin = 12;
int shockPin = 10;
int ledPin = 13;
int buttonPin = 11;
int fiberPin = 7;

long preShockDelay = 180000; //180000;
//long interShockInt = 58000; // 5000;
long postShockInt = 60000;
int shockDur = 2000;

//LEAVE IT AT 0 even with Ethovision
int hasTrig = 0;

// the setup function runs once when you press reset or power the board
void setup() {
  // initialize digital pins
  pinMode(shockPin, OUTPUT);
  //pinMode(ethoPin, INPUT);
  pinMode(fiberPin, OUTPUT);
  pinMode(ledPin, OUTPUT);
  pinMode(buttonPin, INPUT_PULLUP);
  
  Serial.begin(9600);
  Serial.println("Program starting");
  Serial.println("CFC-A One-Shock");
  Serial.println("Total Time = 242sec");
  Serial.print("Pre-Shock Time = "); Serial.println(preShockDelay);
  Serial.print("Shock Duration = "); Serial.println(shockDur);
  Serial.println("Waiting for ethovision input...");
}

// the loop function runs over and over again forever
void loop() {

  if ((digitalRead(buttonPin)==LOW) && hasTrig == 0) { //digitalRead(ethoPin)==HIGH || 
    Serial.print("button trigger IN, millis=");
    Serial.println(millis());
    digitalWrite(fiberPin, HIGH);
    delay(1000);
    digitalWrite(fiberPin, LOW);

    delay(preShockDelay); // period before shocks

    
    shockDeliver(); // deliver the first shock
    digitalWrite(fiberPin, LOW);
    
    //delay(interShockInt); // wait for the interShockInt

    //shockDeliver(); // deliver the second shock

    delay(postShockInt); // wait for the postShockInt
    Serial.print("session END, millis=");
    Serial.println(millis());
    digitalWrite(fiberPin, HIGH);
    delay(500);
    digitalWrite(fiberPin, LOW);
    
    hasTrig = 1;
  }
}

////////////////////// SUB-FUNCTIONS
void shockDeliver() {
    digitalWrite(ledPin, HIGH);
    Serial.print("SHOCK OUT, millis=");
    Serial.println(millis());
    digitalWrite(shockPin, HIGH);   // turn the shock on (HIGH is the voltage level)
    digitalWrite(fiberPin, HIGH);
//    digitalWrite(ledPin, LOW);
    delay(shockDur);  
    digitalWrite(shockPin, LOW);    // turn the shock off by making the voltage LOW
    digitalWrite(fiberPin, HIGH);
    digitalWrite(ledPin, LOW);// wait for the shock duration
    
    Serial.print("SHOCK off, millis=");
    Serial.println(millis());
}
