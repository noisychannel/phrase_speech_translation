# Makefile
# 
# used b/c every one has make and everyone can probably modify this Makefile to suite their specific system requirements
#
# chris taylor
#
CC=g++
LIBS=-ldl -lfst
OUT=fstprintpaths libopenfsttools.so
TMP=*.o *.os
EXTRA=-I /export/a04/gkumar/code/kaldi-new/tools/openfst/include -L /export/a04/gkumar/code/kaldi-new/tools/openfst/lib
#EXTRA= #add any -I -L modifications here...

OBJS=fstprintpaths.o utils.o
SOBJS=fstprintpaths.os utils.os

all: fstprintpaths-main libopenfsttools

utils.o: utils.cpp
	$(CC) $(EXTRA) utils.cpp -c -o utils.o

fstprintpaths.o: utils.o fstprintpaths.cpp
	$(CC) $(EXTRA) fstprintpaths.cpp -c -o fstprintpaths.o

fstprintpaths-main: fstprintpaths.o fstprintpaths-main.cpp
	$(CC) $(LIBS) $(EXTRA) $(OBJS) fstprintpaths-main.cpp -o fstprintpaths 

libopenfsttools: utils.o fstprintpaths.o
	$(CC) -fPIC $(EXTRA) -c utils.cpp -o utils.os 
	$(CC) -fPIC $(EXTRA) -c fstprintpaths.cpp -o fstprintpaths.os 
	$(CC) -shared $(SOBJS) -o libopenfsttools.so

clean:
	rm $(OUT) $(TMP) 
