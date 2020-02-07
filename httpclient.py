#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        # an example of returns if using the list.split
        # ['HTTP/1.0', '200', 'OK', 'Server:', 'BaseHTTP/0.6', 'Python/3.7.3', 'Date:', 'Fri,', '07', 'Feb', '2020', '00:36:35', 'GMT', 'Content-type:', 'application/json', '[]']
        # So obviously the second one is what we need so return list[1]
        list = data.split()
        return int(list[1])

    def get_headers(self,data):
        # note that the ("\r\n\r\n") divide the header and body
        # so if using data.split("\r\n\r\n") it will be splitted to [header,body]
        # so here since ask for the header so we need the first element of the list
        # which will return list[0]
        list = data.split("\r\n\r\n")
        return list[0]

    def get_body(self, data):
        # The final part of the request is its body.
        # here the next one will be the body so we return list[-1]
        list = data.split("\r\n\r\n")
        return list[-1]

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))

    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        # using urllib.parse.urlparse(url) to split urls into componets
        host = urllib.parse.urlparse(url).hostname
        # set the port to 80 since some times the url's components does not contain a port
        # for example in testInternetGets "http://www.cs.ualberta.ca/"
        # since "All websites on the Internet use port 80 so rather than have you type this in all the time"
        # set port = 80 when cant get port from the url
        if (urllib.parse.urlparse(url).port is None):
            port = 80
        else:
            port = urllib.parse.urlparse(url).port
        # set the path to "/" since some of the urls do not contain a path
        # for example in testInternetGets "http://slashdot.org"
        # set "/" as path when path is none
        if (urllib.parse.urlparse(url).path is ""):
            path = "/"
        else:
            path = urllib.parse.urlparse(url).path
        # start connecting
        self.connect(host,port)
        request = '''GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n'''.format(path = path, host = host)
        self.sendall(request)
        data = self.recvall(self.socket)
        #print("......")
        #print(data)
        #print("......")
        code = self.get_code(data)
        body = self.get_body(data)
        # it will return a warning about unclosed socket.
        self.close()
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        host = urllib.parse.urlparse(url).hostname
        if (urllib.parse.urlparse(url).port is None):
            port = 80
        else:
            port = urllib.parse.urlparse(url).port
        if (urllib.parse.urlparse(url).path is ""):
            path = "/"
        else:
            path = urllib.parse.urlparse(url).path
        self.connect(host,port)
        if args:
            #Use the urllib.parse.urlencode() function (with the doseq parameter set to True) to convert such dictionaries into query strings.
            content = urllib.parse.urlencode(args)
        else:
            content=''
        length = len(content)
        req = '''POST {path} HTTP/1.1\r\nHost: {host}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {length}\r\nConnection: close\r\n\r\n{content}'''.format(path = path, host = host, length = length, content = content)
        self.sendall(req)
        data = self.recvall(self.socket)
        code = self.get_code(data)
        body = self.get_body(data)
        self.close()
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            #print(url)
            return self.POST( url, args )
        else:
            #print(url)
            return self.GET( url, args )

if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
