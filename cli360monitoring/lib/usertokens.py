#!/usr/bin/env python3

import requests
import json
from prettytable import PrettyTable

from .config import Config
from .functions import printError, printWarn

class UserTokens(object):

    def __init__(self, config):
        self.config = config
        self.usertokens = None

        self.table = PrettyTable()
        self.table.field_names = ['Token', 'Name', 'Tags']
        self.table.align['Token'] = 'l'
        self.table.align['Name'] = 'l'
        self.table.align['Tags'] = 'l'

    def fetchData(self):
        """Retrieve the list of all usertokens"""

        # if data is already downloaded, use cached data
        if self.usertokens != None:
            return True

        # check if headers are correctly set for authorization
        if not self.config.headers():
            return False

        if self.config.debug:
            print('GET', self.config.endpoint + 'usertoken?', self.config.params())

        # Make request to API endpoint
        response = requests.get(self.config.endpoint + 'usertoken', params=self.config.params(), headers=self.config.headers())

        # Check status code of response
        if response.status_code == 200:
            # Get list of usertokens from response
            json = response.json()
            if 'tokens' in json:
                self.usertokens = json['tokens']
                return True
            else:
                printWarn('No usertokens found')
                self.usertokens = None
                return False
        else:
            printError('An error occurred:', response.status_code)
            self.usertokens = None
            return False

    def list(self, token: str = '', format: str = 'table'):
        """Iterate through list of usertokens and print details"""

        if self.fetchData():
            if self.usertokens != None:

                # if JSON was requested and no filters, then just print it without iterating through
                if (format == 'json' and not token):
                    print(json.dumps(self.usertokens, indent=4))
                    return

                for usertoken in self.usertokens:
                    if token:
                        if usertoken['token'] == token:
                            self.print(usertoken)
                            break
                    else:
                        self.print(usertoken)

            if (format == 'table'):
                print(self.table)
            elif (format == 'csv'):
                print(self.table.get_csv_string(delimiter=self.config.delimiter))

    def token(self):
        """Print the data of first usertoken"""

        if self.fetchData() and len(self.usertokens) > 0:
            return self.usertokens[0]['token']

    def create(self, name: str = '', tags: str = ''):
        """Create a new usertoken"""

        # check if headers are correctly set for authorization
        if not self.config.headers():
            return False

        if self.config.debug:
            print('POST', self.config.endpoint + 'usertoken', self.config.params())

        if self.config.readonly:
            return False

        parameters = ''
        if name and tags:
            parameters = 'name=' + name + '&tags=' + tags
        elif name:
            parameters = 'name=' + name

        response = requests.post(self.config.endpoint + 'usertoken', data=parameters, headers=self.config.headers())

        # Check status code of response
        if response.status_code == 200:
            print('Created usertoken')
            return True
        else:
            printError('Failed to create usertoken with response code:', response.status_code)
            return False

    def print(self, usertoken, format: str = 'table'):
        """Print the data of the specified usertoken"""

        if (format == 'json'):
            print(json.dumps(usertoken, indent=4))
            return

        token = usertoken['token']
        name = usertoken['name'] if 'name' in usertoken and usertoken['name'] else ''

        tags = ''
        if 'tags' in usertoken and usertoken['tags']:
            for tag in usertoken['tags']:
                if tags:
                    tags += ', ' + tag
                else:
                    tags = tag

        self.table.add_row([token, name, tags])
