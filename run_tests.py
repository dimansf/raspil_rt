from unittest import TestLoader, TextTestRunner
import os


tl = TestLoader()
r = tl.discover(start_dir=os.getcwd(), pattern='*_test.py')

tr = TextTestRunner(verbosity=2)
tr.run(r)


def set_env():
    import os 
    p = os.path.abspath('.')
    os.environ['PythonPath'] += f'{p};'