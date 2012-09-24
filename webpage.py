#!/usr/bin python
import httplib
import re
import socket
import ssl

class Webpage:
    __redirects = {}
    __response = {}
    __response_all = {}
    __request = {}
    __request_all = {}

    def __init__(self, url, parameters = {},headers = {}, port = '', 
        protocol = '', method = 'GET', redirects_follow = 0, timeout = 0, 
        verify_ssl = 0, filename = ''):
        self.__redirects['follow'] = redirects_follow
        self.__redirects['used'] = 0
        # Determine the calling method and make it uppercase.
        if method == '':
            method = 'GET'
        self.__request['method'] = method.upper()
        if re.match('GET$|HEAD$|POST$', self.__request['method']) is None:
            raise UnsupportedMethodException(self.__request['method'])
        self.__request['url'] = url
        self.__request['headers'] = headers
        # Parse URL into components.
        self.__request = self.__parse_url(url, self.__request, parameters, port, 
            protocol)
        self.__request_all[0] = self.__request
        # Send the request.
        self.__response = self.__make_request(self.__request, timeout, 
            verify_ssl)
        self.__response_all[0] = self.__response
        # If the response was a 3xx HTTP status code, the user has chosen to
        # automatically redirect, and the method used was either GET or HEAD
        if (self.__redirects['follow'] > 0 and 
            re.match('300|301|302|303|305|307', self.__response['status_code']) 
            and re.match('HEAD|GET', self.__request['method'])):
            while (self.__redirects['follow'] > self.__redirects['used'] and 
                re.match('300|301|302|303|305|307', 
                self.__response['status_code'])):
                self.__redirects['used'] += 1
                for item in self.__response['headers']:
                    if item[0] == 'location':
                        # Parse URL into components, remember to set parameters
                        # to {} to clear out old parameters.
                        self.__request = self.__parse_url(item[1], 
			    self.__request, {})
                        self.__request_all[len(self.__request_all)] = (
                            self.__request)
                        # Send the request.
                        self.__response = self.__make_request(self.__request, 
                            timeout, verify_ssl)
                        self.__response_all[len(self.__response_all)] = (
                            self.__response)
        if filename != '':
            f = open(filename, 'w')
            f.write(self.__response['body'])
            f.close()
    
    def __parse_url(self, url, request, parameters = {}, port = '', 
        protocol = ''):
        # Parse parameters. If parameters already are set use that setting. 
        if len(parameters) == 0 and url.find('?') != -1:
            parameters_tmp = url[url.find('?')+1:].split('&')
            for item in parameters_tmp:
                key = item[0:item.find('=')]
                value = item[item.find('=')+1:]
                parameters[key] = value
        # Parse port. If port already set use that setting. If no port set
        # wait for protocol is specified and use 80 for http & 443 for https.
        if port == '' and re.search(':([0-9]{1,5})',url) is not None:
            port = re.search(':([0-9]{1,5})',url).group(0)[1:]
        # Parse protocol. If protocol already set use that setting. 
        # If protocol is specified in url that it used, otherwise if the port 
        # port has been specified 443 is used as https.
        # Defaults to 'http'.
        if (protocol == 'https' or 
            (protocol != 'http' and 
            (re.match('[hH]{1}[tT]{2}[pP]{1}[sS]{1}',url) is not None or 
            (port == '443' and 
            (re.match('[hH]{1}[tT]{2}[pP]{1}',url) is None))))):
            protocol = 'https'
            if port == '':
                port = '443'
        else:
            protocol = 'http'
            if port == '':
                port = '80'
        # Make the parameter string if method = GET.
        parameter_string = self.__urlencode(parameters)
        # Parse host from URL.
        host_url = re.sub('[hH]{1}[tT]{2}[pP]{1}[s]?://','',url)
        if host_url.find(':') != -1:
            host = host_url[0:host_url.find(':')]
        elif host_url.find('/') != -1:
            host = host_url[0:host_url.find('/')]
        elif host_url.find('?') != -1:
            host = host_url[0:host_url.find('?')]
        else:
            host = host_url
        # Parse location from URL.
        if host_url.find('/') != -1:
            location = host_url[host_url.find('/'):]
            if location.find('?') != -1:
                location = location[0:location.find('?')]
            else:
                location = location
        else:
            location = '/'
        return {'location':location,'host':host,'port':port,
            'parameters':parameters,'parameter_string':parameter_string,
            'protocol':protocol,'method':request['method'],
            'url':url,'headers':request['headers'],'parsed_url':host+':'+port}

    def __make_request(self, request, timeout, verify_ssl):
        # raise NoWebsiteFoundException('Nothing found')
        if request['protocol'] == 'https':
            if timeout > 0 and verify_ssl == 0:
                conn = httplib.HTTPSConnection(request['host'], request['port'], 
                    None, None, False, timeout)
            elif verify_ssl == 0:
                conn = httplib.HTTPSConnection(request['host'], request['port'], 
                    None, None, False)
            elif timeout > 0 and verify_ssl != 0:
                conn = VerifiedHTTPSConnection(request['host'], request['port'], 
                    None, None, False, timeout)
            elif verify_ssl != 0:
                conn = VerifiedHTTPSConnection(request['host'], request['port'], 
                    None, None, False)
        else:
            if timeout == 0:
                conn = httplib.HTTPConnection(request['host'], request['port'], 
                    False)
            else:
                conn = httplib.HTTPConnection(request['host'], request['port'], 
                    False, timeout)
        if request['method'] == 'GET' or request['method'] == 'HEAD':
            location = request['location']+'?'+request['parameter_string']
        elif request['method'] == 'POST':
            location = request['location']
            # In order for the POST parameters to be accepted we need the 
            # content-type & accept header to be set, so if they're not set we 
            # set them here.
            if "Content-type" not in request['headers']:
                request['headers']['Content-type'] = (
                    'application/x-www-form-urlencoded')
            if "Accept" not in request['headers']:
                request['headers']['Accept'] = 'text/plain'
        # Make the request.
        try:
            conn.request(request['method'], location, request['parameter_string'], 
                request['headers'])
        except socket.timeout:
            raise NoWebsiteFoundException('Timeout after '+str(timeout)+' seconds')
        r1 = conn.getresponse()
        if r1.status == 404:
            raise NoWebsiteFoundException('404 Not Found')
        response = {'headers':r1.getheaders(),'body':r1.read(),
            'status_code':str(r1.status),'status_string':r1.reason,
            'http_version':str(r1.version)}
        conn.close()
        return response

    def __replace_characters(self, string):
        string = string.replace('%','%25')
        dic = {'!':'%21','"':'%22','#':'%23','$':'%24','&':'%26',
            '\'':'%27','(':'%28',')':'%29','*':'%2A','+':'%2B',',':'%2C',
            '/':'%2F',':':'%3A',';':'%3B','<':'%3C','=':'%3D','>':'%3E',
            '?':'%3F','@':'%40','[':'%5B','\\':'%5C',']':'%5D','^':'%5E',
            '`':'%60','{':'%7B','|':'%7C','}':'%7D','~':'%7E'}
        for i, j in dic.iteritems():
            string = string.replace(i, j)
        string = string.replace(' ','+')
        return string

    def __urlencode(self, parameters):
        parameter_string = ''
        if len(parameters) > 0:
            for k, v in parameters.items():
                parameter_string += ('&'+self.__replace_characters(''.join(k))+
                    '='+self.__replace_characters(''.join(v)))
            parameter_string = parameter_string[1:]
        return parameter_string

    def response(self):
        return self.__response

    def request(self):
        return self.__request

    def response_all(self):
        return self.__response_all

    def request_all(self):
        return self.__request_all

    def redirects(self):
        return self.__redirects

class NoWebsiteFoundException(Exception):
    def __init__(self, value):
        self.value = ('The website couldn\'t be found with the following '+
            'reason: '+value)
    def __str__(self):
        return repr(self.value)

class UnsupportedMethodException(Exception):
    def __init__(self, value):
        self.value = 'The "'+value+'" method is unsupported!'
    def __str__(self):
        return repr(self.value)

# Solution inspired by this website: http://www.muchtooscrawled.com/2010/03/
# https-certificate-verification-in-python-with-urllib2/
class VerifiedHTTPSConnection(httplib.HTTPSConnection):
    def connect(self):
        # overrides the version in httplib so that we do certificate 
        # verification
        sock = socket.create_connection((self.host, self.port), self.timeout)
        if self._tunnel_host:
            self.sock = sock
            self._tunnel()
        # wrap the socket using verification with the root certs in 
        # trusted_root_certs
        self.sock = ssl.wrap_socket(sock, self.key_file, self.cert_file,
            cert_reqs=ssl.CERT_REQUIRED, ca_certs="ca.pem")
