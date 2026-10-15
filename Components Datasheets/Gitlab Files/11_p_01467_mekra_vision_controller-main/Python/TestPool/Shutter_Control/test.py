from _automation_wrapper_ import TestEnv
from tools.helpFunctions import camera_steps as cs

import inspect
print("LOADED:", cs.__file__)
print("SIGNATURE:", inspect.signature(cs.set_control))