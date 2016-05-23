# From Python 2.4 Queue.py
# Bug is handling marshal type 'f' which
# doesn't seem to be used in later releases

def get(remaining=5.0):
    if remaining <= 0.0:
        return False
