all: hid

CC=gcc
COBJS=hid.o
OBJS=$(COBJS) $(CPPOBJS)
CFLAGS+=-I. -Wall -g -c 
LIBS=-framework IOKit -framework CoreFoundation


hid: $(OBJS)
	gcc -dynamiclib -std=gnu99 -Wall -g hid.o -current_version 1.0 -compatibility_version 1.0 -fvisibility=hidden $(LIBS) -o libHid.A.dylib

$(COBJS): %.o: %.c
	$(CC) $(CFLAGS) $< -o $@

clean:
	rm -f *.o *.dylib

.PHONY: clean
