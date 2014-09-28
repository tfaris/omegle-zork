import logging
import requests

import pyquery

zork_output = logging.getLogger("ZorkGame")
zork_output.setLevel(logging.INFO)


class ZorkWebAdventure(object):
    """
    Makes http requests to the ZORK online game at
    http://www.web-adventures.org/cgi-bin/webfrotz?s=ZorkDungeon
    """
    URL = 'http://www.web-adventures.org/cgi-bin/webfrotz?s=ZorkDungeon&n=24289'
    # Remove lines that clutter up our output. The intent is not
    # to remove copyright info, but not sure how else to handle it.
    # THese would otherwise appear on every output line.
    reject_keywords = [
        'ZORK I: The Great Underground Empire',
        'registered',
        'Copyright',
        'Revision',
    ]

    def __init__(self):
        self.reset()
        
    def reset(self):
        self._session = requests.Session()
        
    def _request(self, input=None):
        """
        Send a request outwards.
        """
        try:
            data = {}
            if input:
                data['a'] = input
            # Make the POST request
            pq = pyquery.PyQuery(self._session.post(self.URL, data=data).content)
            # Get the HTML of the body but remove extra tags we don't
            # want to output.
            body_html = pq('body').remove('style,script,form,table,font').html().strip()
            # Filter out empty lines
            lines = filter(
                lambda i: i and not(any([rk in i for rk in self.reject_keywords])),
                body_html.split('<br/>')
            )
            # Finally join the lines back together and remove any more
            # unwanted clutter.
            return '\n'.join([l.strip() for l in lines]).replace('&gt;', '')
        except Exception, ex:
            zork_output.debug(str(ex))
            return "Sorry... I hit a snag (%s).\n\nTry again?" % ex.message
        
    def _out(self, msg):
        """
        Send output to the zork log.
        """
        zork_output.info(msg)
        
    def intro(self):
        self._out(
            """
            ZORK I
            ****************************
            Thanks to web-adventures.org for providing a fantastic implementation of ZORK.
            http://www.web-adventures.org/cgi-bin/webfrotz?s=ZorkDungeon
            
            Now play :)
            """
        )
        self._out(self._request())
        
    def handle_input(self, input):
        self._out(self._request(input=input))
