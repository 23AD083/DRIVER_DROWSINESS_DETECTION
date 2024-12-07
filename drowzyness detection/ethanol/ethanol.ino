#include <TinyGPS++.h>
#include <SoftwareSerial.h>

// Create a TinyGPS++ object
TinyGPSPlus gps;

// Create a SoftwareSerial object to communicate with the GPS module
SoftwareSerial ss(4, 3); // RX, TX

void setup() {
  // Start the serial communication with the computer
  Serial.begin(9600);
  // Start the serial communication with the GPS module
  ss.begin(9600);

  Serial.println(F("GPS6MV2 Module Test"));
}

void loop() {
  // This sketch displays information every time a new sentence is correctly encoded.
  while (ss.available() > 0) {
    gps.encode(ss.read());
    if (gps.location.isUpdated()) {
      Serial.print(F("Location: "));
      Serial.print(gps.location.lat(), 6);
      Serial.print(F(", "));
      Serial.print(gps.location.lng(), 6);
      Serial.println();
    }

    if (gps.date.isUpdated()) {
      Serial.print(F("Date: "));
      Serial.print(gps.date.month());
      Serial.print(F("/"));
      Serial.print(gps.date.day());
      Serial.print(F("/"));
      Serial.println(gps.date.year());
    }

    if (gps.time.isUpdated()) {
      Serial.print(F("Time: "));
      Serial.print(gps.time.hour());
      Serial.print(F(":"));
      Serial.print(gps.time.minute());
      Serial.print(F(":"));
      Serial.println(gps.time.second());
    }
  }
}
