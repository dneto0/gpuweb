#!/bin/bash

A=index.bs
A=a.bs

# Check that we have all the content, and it matches the original, modulo cosmetics
./rewrite.py -r -t -b $A >index-mirror.bs
./rewrite.py -r -a $A >0.bs
./rewrite.py       -a 0.bs >1.bs
./rewrite.py -d -v -a 0.bs >1.bs
#./rewrite.py -t -b 1.bs >2.bs
#./rewrite.py -v -t -b 1.bs >2.bs

