try:
	from .development import *
except ImportError:
	from .server import *