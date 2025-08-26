/* ----------------------------------------------------------
 * | Temperature regulation sketch |
 * | For Newport diode laser mount 700C built-in TEC |
 * | Use Arduino DUE with Opto-2-2 isolator shield for protection |
 * ---------------------------------------------------------
 *
 * NOTE: YOU WILL NEED TO MODIFY THE loop() FUNCTION BELOW!!
 */

#include <SerialCommand.h>
SerialCommand sCmd;
// Regulation switch
int TEC0_regulating = 0;

// Output
int TEC0_outPin = DAC0; // TEC0 Output pin position

// Input
int TEC0_inPin = A0; // TEC0 input pin position
// high/low
int highOut = 4095; // these are provided but are not being used
int lowOut = 0;

int defaultOut = 2027; // Default output, experimental value to give 0 (or slightly positive, slightly cooling) final output.
int setpoint = 2000; // Roughly 17C, as default

//PID: correction = a * (setpoint temperature - temperature)
float Kp = 2.0; //proportional correction factor
float Ki = 0.3; //integral correction factor
int TEC0_lastError = 0; //the last temperature error
float TEC0_lastOut;
int TEC0_lastIn;
float correction; // Adjust for output

void setup(){
  // Set the baud rate at max, 115200 bits per second
  Serial.begin(115200); 
  sCmd.addCommand("setup", TEC_setup);   
  sCmd.addCommand("start", TEC_start);
  sCmd.addCommand("stop", TEC_stop);
  sCmd.addCommand("status", TEC_status);
  sCmd.addCommand("setout", TEC_setout);
  
  analogWriteResolution(12); // 12-bit output for DUE
  analogReadResolution(12); // 12-bit input for DUE
  
  TEC0_lastOut = defaultOut;
  analogWrite(TEC0_outPin, TEC0_lastOut); // Set default output to 1.5V. After op-amp it will be 0V.
  // wait for stabilization
  delay(500);

  // Let the computer know we are ready
  Serial.println("Op-amp TEC READY #0");
}

void loop(){
  // Process serial commands
  sCmd.readSerial();  
  if(TEC0_regulating) {
    TEC0_lastIn = analogRead(TEC0_inPin); //TEC0_inPin is A0, which is connected to the temp sensor
    int TEC0_error = TEC0_lastIn - setpoint;
    //TEC0_lastOut = constrain(int(TEC0_lastOut + Ki*TEC0_error + Kp*(TEC0_error - TEC0_lastError)), defaultOut, defaultOut + 1024); // For DUE (12-bit); Protection (1000 - defaultOut) so that the TEC won't be heating.
    TEC0_lastOut = constrain((TEC0_lastOut + Ki*TEC0_error + Kp*(TEC0_error - TEC0_lastError)), defaultOut, defaultOut + 1024); // For DUE (12-bit); Protection (1000 - defaultOut) so that the TEC won't be heating.
    //The relative sign between Ki, Kp and lastOut will depend on how the circuit is built, i.e., where higher lastOut means more cooling or the other way around.
    TEC0_lastError = TEC0_error;
    analogWrite(TEC0_outPin, TEC0_lastOut);
  delay(100); // Wait 0.1 sec, i.e., check 10 times a second.
}
}

void TEC_setup() {
  char* arg;
  // Get setpoint
  arg = sCmd.next();
  if (arg != NULL) setpoint = atoi(arg);
  // Get Kp
  arg = sCmd.next();
  if (arg != NULL) Kp = atof(arg);
  // Get Ki
  arg = sCmd.next();
  if (arg != NULL) Ki = atof(arg);
  int32_t kpI = Kp * 1000;
  int32_t kiI = Ki * 1000;
  Serial.print(kpI);
  Serial.print(" ");
  Serial.print(kiI);
  Serial.println("Done setting.");
}

void TEC_start() {
  char* arg = sCmd.next();
  if (arg != NULL) TEC0_regulating = atoi(arg);
  else TEC0_regulating = 1; // default if no arg
  TEC0_lastOut = defaultOut;
  analogWrite(TEC0_outPin, TEC0_lastOut);
  Serial.println("S Started.");
}

void TEC_stop() {
  TEC0_regulating = 0;
  TEC0_lastOut = defaultOut;
  analogWrite(TEC0_outPin, TEC0_lastOut);
  Serial.println("S Stopped.");
}

void TEC_setout() {
  char* arg = sCmd.next();
  if (arg != NULL) {
    TEC0_lastOut = atoi(arg);
    analogWrite(TEC0_outPin, TEC0_lastOut); 
    Serial.println("S Setout Done.");
  }
}

//Returns voltage reading
void TEC_status() {
  TEC0_lastIn = analogRead(TEC0_inPin);
  // Format: label and two integers
  Serial.print(TEC0_lastIn);
  Serial.print(" ");
  Serial.println(TEC0_lastOut);  // Ends the line
}
