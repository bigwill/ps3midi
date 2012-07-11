###########################################
# Simple Makefile for HIDAPI test program
#
# Alan Ott
# Signal 11 Software
# 2010-07-03
###########################################

all: ps3hid

CC=gcc
COBJS=hid.o ps3hid.o
OBJS=$(COBJS) $(CPPOBJS)
CFLAGS+=-I. -Wall -g -c 
LIBS=-framework IOKit -framework CoreFoundation


ps3hid: $(OBJS)
	gcc -dynamiclib -std=gnu99 -Wall -g hid.o ps3hid.o -current_version 1.0 -compatibility_version 1.0 -fvisibility=hidden $(LIBS) -o libPS3hid.A.dylib

$(COBJS): %.o: %.c
	$(CC) $(CFLAGS) $< -o $@

clean:
	rm -f *.o ps3hid

.PHONY: clean
