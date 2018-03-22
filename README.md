## Usage:

### make the c code
make
### run the tester in ipython
In [1]: %run run_and_verify.py

In [2]: run("foo", 50000, 6)
Running : ['./pb_test_write', 'foo', '50000', '6']
Writing to foo00000.txt
Writing 50000 lines total
Writing to foo00001.txt
Writing 50000 lines total
Writing to foo00002.txt
Writing 50000 lines total
Writing to foo00003.txt
Writing 50000 lines total
Writing to foo00004.txt
Writing 50000 lines total
Writing to foo00005.txt
Writing 50000 lines total

In [3]: verify("foo", 50000, 6)


