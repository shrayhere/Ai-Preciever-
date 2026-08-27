import os
import sys

# Ensure root directory is in sys.path for Vercel Serverless Function
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app
