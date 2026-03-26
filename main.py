import sys
import io
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from api_checker import APIChecker

checker = APIChecker()
try:
    checker.run()
finally:
    checker.close()
