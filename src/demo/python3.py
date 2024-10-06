import subprocess
import sys

args = [sys.executable, 'python2.py', 'arg1', 'arg2', 'arg3']
result = subprocess.check_output(args, universal_newlines=True)

output = result.strip().split('\n')
returned_arg1 = output[0]
returned_arg2 = output[1]
returned_arg3 = output[2]

print("Returned arg1:", returned_arg1)
print("Returned arg2:", returned_arg2)
print("Returned arg3:", returned_arg3)
