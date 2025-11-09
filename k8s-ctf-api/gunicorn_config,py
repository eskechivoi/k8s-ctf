# gunicorn_config.py

# Adjust depending on the number of CPU cores
# Usually: (2 * $NUM_CORES) + 1
workers = 4 

# Address and port in which gunicorn will server the app
bind = '0.0.0.0:8000'

# Logging
loglevel = 'info'
errorlog = '-' # stdout
accesslog = '-' # stdout

# Timeout worker
timeout = 120 

# Name and module of the app
wsgi_app = 'main:app'