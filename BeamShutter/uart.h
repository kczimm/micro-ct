// BeamShutter Device - microcontroller software
// filename: uart.h
// author: Kevin C. Zimmerman
// email: kevin.zimmerman@mu.edu

#ifndef UART_H_
#define UART_H_

#include "avr/io.h"
#include "avr/interrupt.h"

// 9600 Baud, 8 data bits, 1 stop bit, no parity
void uart_setup( void );

#endif
