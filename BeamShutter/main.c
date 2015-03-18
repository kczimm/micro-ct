// BeamShutter Device - microcontroller software
// filename: main.c
// author: Kevin C. Zimmerman
// email: kevin.zimmerman@mu.edu

typedef enum state {PUSH, PULL, IDLE} State;

int main( void )
{
  State next;
  State current = IDLE;

  while( 1 )
  {
    switch( current )
    {
    case PUSH:
      // Activate solenoid circuit 1 for a period of time.
      next = IDLE;
      break;
    case PULL:
      // Activate solenoid circuit 2 for a period of time.
      next = IDLE;
      break;
    case IDLE:
      // do nothing
      break;
    }
    current = next;
  }
  return 0;
}
