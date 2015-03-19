// BeamShutter Device - microcontroller software
// filename: solenoid.h
// author: Kevin C. Zimmerman
// email: kevin.zimmerman@mu.edu

#ifndef SOLENOID_H_
#define SOLENOID_H_

#include "avr/io.h"
#include "avr/interrupt.h"

// Set output pins, timer setup
void solenoid_setup( void );

// Drive solenoid 1/2 based on State PUSH/PULL
void solenoid_activate( const State current );

#endif
