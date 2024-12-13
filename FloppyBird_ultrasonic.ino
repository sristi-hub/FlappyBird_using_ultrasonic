const int trigPin=9;  //DECLARE TRIG PIN AT D11
int echoPin=10;         //DECLARE ECHO PIN AT D10
int safezone=10; 
void setup() 
{
pinMode(trigPin,OUTPUT);
pinMode(echoPin,INPUT);
Serial.begin(9600);
}
void loop()
{
long duration,cm;           //DECLARE VARIABLES TO STORE SENSOR O/P
digitalWrite(trigPin,LOW);  //MAKE THE TRIG PIN LOW
delayMicroseconds(2);       //WAIT FOR FEW MICROSECONDS
digitalWrite(trigPin,HIGH); //NOW SET THE TRIG PIN
delayMicroseconds(5);       //WAIT FOR FEW MICROSECONDS UNTIL THE TRIG PULSE IS SENT
digitalWrite(trigPin,LOW);  //MAKE THE TRIG PIN LOW AGAIN
duration=pulseIn(echoPin,HIGH); //MAKE ECHO PIN HIGH AND STORE THE BOUNCED PULSE IN VARIABLE DURATION
cm=microsecondsToCentimeters(duration); 
long inch= cm/2.54;
Serial.println(cm);
}
long microsecondsToCentimeters(long microseconds) //SPEED OF SOUND IS 29 uSEC PER CM
{
return microseconds/29/2;  //THE PULSE TRAVELS FROM THE SENSOR AND AGAIN COMES BACK SO WE DIVIDE IT BY 2 TO TAKE ONLY HALF OF THE TOTAL DISTANCE
}