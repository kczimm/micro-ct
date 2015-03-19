// BeamShutter Device - microcontroller software
// filename: uart.c
// author: Kevin C. Zimmerman
// email: kevin.zimmerman@mu.edu

#define USART_BAUDRATE 9600
#define BAUD_PRESCALE (((F_CPU / (USART_BAUDRATE * 16UL)))-1)

// 9600 Baud, 8 data bits, 1 stop bit, no parity
void uart_setup( void )
{
  //TODO: Is it necessary to make pin RX0 as input (pull-up enabled)?
  // Enable RX complete interrupt enable
  UCSR0B = (1 << RXCIE0);

  UBRRH = (BAUD_PRESCALE >> 8);
  UBRRL = BAUD_PRESCALE;

  // Enable global interrupts
  sli();
}

ISR( USART_RXC_vect ) //TODO: update vector name
{
  // Set next State to PUSH/PULL
}
