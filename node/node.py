""" the node acts as the http listener and sender for the rest of the system """

# imports
import threading
import httplistener
import httprequester

threading.Thread(target=httplistener.run, daemon=True).start()
threading.Thread(target=httprequester.request).start()

def talkBack():
    pass
while True:
    talkBack()