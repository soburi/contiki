/*
 * Copyright (c) 2005, Swedish Institute of Computer Science
 * Copyright (c) 2015, TOKITA Hiroshi
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 * 3. Neither the name of the Institute nor the names of its contributors
 *    may be used to endorse or promote products derived from this software
 *    without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE INSTITUTE AND CONTRIBUTORS ``AS IS'' AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED.  IN NO EVENT SHALL THE INSTITUTE OR CONTRIBUTORS BE LIABLE
 * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
 * OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
 * OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 * SUCH DAMAGE.
 *
 * This file is part of the Contiki operating system.
 *
 * Author: TOKITA Hiroshi <tokita.hiroshi@gmail.com>
 *
 */

#include <stdio.h>
#include "sys/mt.h"
#include "mtarch.h"

static volatile unsigned int *sptmp;
static struct mtarch_thread *running;

/*--------------------------------------------------------------------------*/
void
mtarch_init(void)
{

}
/*--------------------------------------------------------------------------*/
__attribute__ ((naked))
static void
mtarch_wrapper(void)
{
  /* Call thread function with argument */
  ((void (*)(void *))running->function)((void*)running->data);
}
/*--------------------------------------------------------------------------*/
void
mtarch_start(struct mtarch_thread *t,
	     void (*function)(void *), void *data)
{
  unsigned int *sp = NULL;
  int i;

  for(i = 0; i < MTARCH_STACKSIZE; ++i) {
    t->stack[i] = i;
  }

  t->data = data;
  t->function = function;
  t->sp = (unsigned int *)&t->stack[MTARCH_STACKSIZE - 1];
  sp = t->sp;

  *t->sp-- = (unsigned int)mtarch_wrapper; /* lr */
  *t->sp-- = 0; /* ip */
  *t->sp-- = 0; /* v8 */
  *t->sp-- = 0; /* v7 */
  *t->sp-- = 0; /* v6 */
  *t->sp-- = 0; /* v5 */
  *t->sp-- = (unsigned int)sp; /* r7 as framepointer */
  *t->sp-- = 0; /* v3 */
  *t->sp-- = 0; /* v2 */
  *t->sp   = 0; /* v1 */
}
/*--------------------------------------------------------------------------*/

static void
sw(void)
{

  sptmp = running->sp;

  __asm__(
    "push  { v1-v8, ip, lr }  \n\t" /* store registers */
    "mov    %0, sp            \n\t" /* swap stack */
    "mov    sp, %1            \n\t"
    "pop   { v1-v8, ip, lr }  \n\t" /* restore register */
    : "=&r" (running->sp)
    : "r" (sptmp)
    );
}
/*--------------------------------------------------------------------------*/
void
mtarch_exec(struct mtarch_thread *t)
{
  running = t;
  sw();
  running = NULL;
}
/*--------------------------------------------------------------------------*/
void
mtarch_remove(void)
{

}
/*--------------------------------------------------------------------------*/
void
mtarch_yield(void)
{
  sw();
}
/*--------------------------------------------------------------------------*/
void
mtarch_pstop(void)
{

}
/*--------------------------------------------------------------------------*/
void
mtarch_pstart(void)
{

}
/*--------------------------------------------------------------------------*/
void
mtarch_stop(struct mtarch_thread *thread)
{

}
/*--------------------------------------------------------------------------*/
int
mtarch_stack_usage(struct mt_thread *t)
{
  int i;

  for(i = 0; i < MTARCH_STACKSIZE; ++i) {
    if(t->thread.stack[i] != i) {
      return MTARCH_STACKSIZE - i;
    }
  }

  return MTARCH_STACKSIZE;
}
/*--------------------------------------------------------------------------*/
