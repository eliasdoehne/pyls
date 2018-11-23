# pyls

pyls is a Python implementation of the UNIX `ls` command, with support for the following options: 

  - `l`: Show results in a list format
  - `a`: Show entries starting with `.`
  - `S`: Sort the output by file size
  - `R`: Recursively list subdirectories
  
# Installation

pyls requires Python 3.7. In all following commands, the `python` and `pip` commands are assumed to refer to Python 3.7. Depending on your configuration, you may need to substitute them with `python3.7` and `pip3.7`.

The `pyls` command is made available by installing the module with the command `pip install .`. Alternatively, pyls can be executed as a script (`python pyls.py`), or as a python module (`python -m pyls`).

pyls was tested and developed with Ubuntu 18.04.1 LTS, Python 3.7.0 and pytest 4.0.0.

# Usage

In the following examples, the `pyls` command may be replaced with any other method mentioned in the Installation section. For example, `pyls -l some_dir` can equivalently be replaced with `python -m pyls -l some_dir` or `python pyls.py -l some_dir`.


## Examples

The following examples show the output of pyls when run in the pyls source directory. The exact output may be different due to file changes in future versions of pyls, and depending on the computer's locale configuration.

  - `pyls`:
  
        dev-requirements.txt  pyls.py  README.md  setup.py  test


  - `pyls -a` (in a terminal with width 80, resulting in a multi-column layout):
  
        .   dev-requirements.txt  .gitignore  README.md  test  
        ..  .git                  pyls.py     setup.py  

        
  - `pyls -l`:
  
        total 32
        -rw-r--r-- 1 user group     7 Nov 20 18:58 dev-requirements.txt
        -rw-r--r-- 1 user group 10377 Nov 21 15:17 pyls.py
        -rw-r--r-- 1 user group  4905 Nov 21 17:32 README.md
        -rw-r--r-- 1 user group   179 Nov 20 18:58 setup.py
        drwxr-xr-x 2 user group  4096 Nov 21 16:02 test

  - `pyls -la`:
  
        total 48
        drwxr-xr-x  4 user group  4096 Nov 21 17:32 .
        drwxrwxr-x 16 user group  4096 Nov 20 18:58 ..
        -rw-r--r--  1 user group     7 Nov 20 18:58 dev-requirements.txt
        drwxr-xr-x  8 user group  4096 Nov 21 15:17 .git
        -rw-r--r--  1 user group  1174 Nov 20 18:58 .gitignore
        -rw-r--r--  1 user group 10377 Nov 21 15:17 pyls.py
        -rw-r--r--  1 user group  4905 Nov 21 17:32 README.md
        -rw-r--r--  1 user group   179 Nov 20 18:58 setup.py
        drwxr-xr-x  2 user group  4096 Nov 21 16:02 test



  - `pyls -laS`:
  
        total 48
        -rw-r--r--  1 user group 10377 Nov 21 15:17 pyls.py
        -rw-r--r--  1 user group  4905 Nov 21 17:32 README.md
        drwxr-xr-x  4 user group  4096 Nov 21 17:32 .
        drwxrwxr-x 16 user group  4096 Nov 20 18:58 ..
        drwxr-xr-x  8 user group  4096 Nov 21 15:17 .git
        drwxr-xr-x  2 user group  4096 Nov 21 16:02 test
        -rw-r--r--  1 user group  1174 Nov 20 18:58 .gitignore
        -rw-r--r--  1 user group   179 Nov 20 18:58 setup.py
        -rw-r--r--  1 user group     7 Nov 20 18:58 dev-requirements.txt

  - `pyls -lR`:
  
        .:
        total 32
        -rw-r--r-- 1 user group     7 Nov 20 18:58 dev-requirements.txt
        -rw-r--r-- 1 user group 10377 Nov 21 15:17 pyls.py
        -rw-r--r-- 1 user group  4905 Nov 21 17:32 README.md
        -rw-r--r-- 1 user group   179 Nov 20 18:58 setup.py
        drwxr-xr-x 2 user group  4096 Nov 21 16:02 test
        
        test:
        total 12
        -rw-r--r-- 1 user group    0 Nov 20 18:58 __init__.py
        -rw-r--r-- 1 user group 3529 Nov 21 15:17 test_data.py
        -rw-r--r-- 1 user group 7067 Nov 20 18:58 test_pyls.py



## Tests

The repository includes many tests comparing pyls to the output of the system ls command. To run the tests, first install the development dependencies with `pip install -r dev-requirements.txt`. The tests can then be executed by running the `pytest` command, which should result in output similar to:


    ============================= test session starts ==============================
    platform linux -- Python 3.7.0, pytest-4.0.0, py-1.7.0, pluggy-0.8.0
    rootdir: /path/to/pyls, inifile:
    collected 620 items                                                            
    
    test/test_pyls.py ...................................................... [  8%]
    ........................................................................ [ 20%]
    ........................................................................ [ 31%]
    ........................................................................ [ 43%]
    ........................................................................ [ 55%]
    ........................................................................ [ 66%]
    ........................................................................ [ 78%]
    ........................................................................ [ 90%]
    ..................................................ssssssssssss           [100%]
    
    ==================== 608 passed, 12 skipped in 5.00 seconds ====================


The project also includes several test cases which execute the pyls command on directories outside of the project structure. By default, these tests are skipped. To run them, remove the line `@pytest.mark.skip` from the file `test/test_pyls.py`.
