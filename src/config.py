TIMEOUT = 30
RETRIES = 3

if TIMEOUT <= 0:
    raise ValueError("TIMEOUT doit etre strictement positif")
