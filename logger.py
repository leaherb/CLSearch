import logging

## Create logging. Levels = [DEBUG, INFO, WARNING, ERROR, CRITICAL]
logging.basicConfig(\
    level=logging.DEBUG,\
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',\
    datefmt='%m-%d %H:%M',\
    filename='search.log',\
    filemode='w')

# Define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)

# Set a format which is simpler for console use
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')

# Tell the handler to use this format
console.setFormatter(formatter)

# Add the handler to the root logger
logging.getLogger('').addHandler(console)

# Avoid writing 'urllib3 library' messages lower than the WARNING level
logging.getLogger("urllib3").setLevel(logging.WARNING)

# Now, we can log to the root logger, or any other logger. First the root...
logging.info('Jackdaws love my big sphinx of quartz.')
