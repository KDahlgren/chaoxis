#!/usr/bin/env bash


#cmd="python ../../src/drivers/driver1.py -n a,b,c -f ./replog.ded -f ./bcast_edb.ded -f ./deliv_assert.ded --evaluator c4"
cmd="python ../../src/drivers/driver1.py -n a,b,c -f ./replog_v2.ded --evaluator c4"
opt_cmd="cmd"

if [ "$1" = "$opt_cmd" ]
then
  # run command an do not hide stdout
  $cmd
else
  # run the test and hide stdout
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
fi

# remove the temp file to clean up directory
#rm tmp.txt
