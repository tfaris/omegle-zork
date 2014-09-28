"""
Hosts a game with a random participant on Omegle.
"""
import logging
import optparse
import time

import omegle

import zork

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('CLIENT')

# Log output to file
log_file = logging.FileHandler('game.log')
log.addHandler(log_file)


class OmegleLogHandler(logging.Handler):
    def __init__(self, client, *args, **kwargs):
        super(OmegleLogHandler, self).__init__(*args, **kwargs)
        self.client = client
        
    def emit(self, record):
        msg = self.format(record)
        self.client.send(msg)


class OmegleGameHost(object):
    def __init__(self, topics=None):
        self._interests = topics
        # Create the client and register event handlers
        self.client = omegle.Client(topics=topics)
        self.client.register_handler('gotMessage', self._handle_gotMessage)
        self.client.register_handler('connected', self._handle_connected)
        self.client.register_handler('strangerDisconnected', self._handle_strangerDisconnected)
        self.client.register_handler('commonLikes', self._handle_commonLikes)
        self._thread = None
        # Initialize the game and setup log handlers
        self._game = zork.ZorkWebAdventure()
        omegle_sender = OmegleLogHandler(self.client)
        zork.zork_output.addHandler(omegle_sender)
        zork.zork_output.addHandler(log_file)

    def _handle_gotMessage(self, client, message):
        log.info(message)
        # Pass the message off to the game
        self._game.handle_input(message)
        
    def _handle_connected(self, instance):
        log.info("Connected.")
        # New connection, show the game intro.
        self._game.intro()
    
    def _handle_strangerDisconnected(self, instance):
        log.info("disconnected")
        log.info("")
        # Lost our user, reset the game for the next person.
        self._game.reset()
        self.reconnect()
        
    def _handle_commonLikes(client, likes):
        log.info("Successfully connected with UID", likes[0])
    
    def start(self):
        log.info("Starting omegle connection with interests: %s" % self._interests)
        self._thread = self.client.start()
        
    def reconnect(self):
        self.stop()
        # Sleep for a bit to make sure everything is stopped
        time.sleep(2)
        self.start()
        
    def stop(self):
        self.client.disconnect()
        self._thread.stop()

    
def main():
    parser = optparse.OptionParser()
    parser.add_option('-i', '--interests',
        help="omegle interest keywords, separated by comma",
        default="")
    (options, args) = parser.parse_args()
    
    zork = OmegleGameHost(topics=options.interests.split(','))
    zork.start()
    try:
        while True:
            i = raw_input()
            if i == 'q':
                # Quit the game completely
                zork.stop()
                break
            elif i == 'n':
                # Find a new player
                zork.reconnect()
            else:
                # Any other text is sent to the user playing the game
                zork.client.send(i)
    finally:
        zork.stop()
        

if __name__ == '__main__':
    main()