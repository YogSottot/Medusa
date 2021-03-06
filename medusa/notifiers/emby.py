# coding=utf-8

# Author: Nic Wolfe <nic@wolfeden.ca>
#
# This file is part of Medusa.
#
# Medusa is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Medusa is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Medusa. If not, see <http://www.gnu.org/licenses/>.

import json

from requests.compat import urlencode
from six.moves.urllib.error import URLError
from six.moves.urllib.request import Request, urlopen
from .. import app, logger
from ..helper.exceptions import ex


class Notifier(object):

    def _notify_emby(self, message, host=None, emby_apikey=None):
        """Handles notifying Emby host via HTTP API

        Returns:
            Returns True for no issue or False if there was an error

        """

        # fill in omitted parameters
        if not host:
            host = app.EMBY_HOST
        if not emby_apikey:
            emby_apikey = app.EMBY_APIKEY

        url = 'http://%s/emby/Notifications/Admin' % host
        values = {'Name': 'Medusa', 'Description': message, 'ImageUrl': app.LOGO_URL}
        data = json.dumps(values)
        try:
            req = Request(url, data)
            req.add_header('X-MediaBrowser-Token', emby_apikey)
            req.add_header('Content-Type', 'application/json')

            response = urlopen(req)
            result = response.read()
            response.close()

            logger.log(u'EMBY: HTTP response: ' + result.replace('\n', ''), logger.DEBUG)
            return True

        except (URLError, IOError) as e:
            logger.log(u'EMBY: Warning: Couldn\'t contact Emby at ' + url + ' ' + ex(e), logger.WARNING)
            return False


##############################################################################
# Public functions
##############################################################################

    def test_notify(self, host, emby_apikey):
        return self._notify_emby('This is a test notification from Medusa', host, emby_apikey)

    def update_library(self, show=None):
        """Handles updating the Emby Media Server host via HTTP API

        Returns:
            Returns True for no issue or False if there was an error

        """

        if app.USE_EMBY:

            if not app.EMBY_HOST:
                logger.log(u'EMBY: No host specified, check your settings', logger.DEBUG)
                return False

            if show:
                if show.indexer == 1:
                    provider = 'tvdb'
                elif show.indexer == 2:
                    logger.log(u'EMBY: TVRage Provider no longer valid', logger.WARNING)
                    return False
                else:
                    logger.log(u'EMBY: Provider unknown', logger.WARNING)
                    return False
                query = '?%sid=%s' % (provider, show.indexerid)
            else:
                query = ''

            url = 'http://%s/emby/Library/Series/Updated%s' % (app.EMBY_HOST, query)
            values = {}
            data = urlencode(values)
            try:
                req = Request(url, data)
                req.add_header('X-MediaBrowser-Token', app.EMBY_APIKEY)

                response = urlopen(req)
                result = response.read()
                response.close()

                logger.log(u'EMBY: HTTP response: ' + result.replace('\n', ''), logger.DEBUG)
                return True

            except (URLError, IOError) as e:
                logger.log(u'EMBY: Warning: Couldn\'t contact Emby at ' + url + ' ' + ex(e), logger.WARNING)
                return False
