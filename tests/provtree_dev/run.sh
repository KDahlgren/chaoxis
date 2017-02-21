#!/usr/bin/env bash


cmd="python ../../src/drivers/driver1.py -n a,b,c -f ./provTree_dev.ded --evaluator c4"

# run the test
$cmd > tmp.txt
  
# check if test passed (TODO: make more sophisticated)
if grep -Fxq "PROGRAM EXITED SUCCESSFULLY" tmp.txt
then
  echo "TEST PASSED"
  rm tmp.txt
else
  echo "TEST FAILED"
  echo -e "Please see ./tmp.txt for execution outputs, or run the following command for more info :\n$cmd"
fi

# remove the temp file to clean up directory
#rm tmp.txt

