#!/usr/bin python
import webpage
import unittest
import ssl

class TestWebpageBasic(unittest.TestCase):
    # Tests the basic functionality of retrieving a webpage.
    def test_basic_webpage(self):
        x = webpage.Webpage('test.ing-site.com')
        request = x.request()
        self.assertEqual(request['headers'], {})
        self.assertEqual(request['host'], 'test.ing-site.com')
        self.assertEqual(request['parameter_string'], '')
        self.assertEqual(request['protocol'], 'http')
        self.assertEqual(request['location'], '/')
        self.assertEqual(request['parameters'], {})
        self.assertEqual(request['url'], 'test.ing-site.com')
        self.assertEqual(request['parsed_url'], 'test.ing-site.com:80')
        self.assertEqual(request['port'], '80')
        self.assertEqual(request['method'], 'GET')
        response = x.response()
        self.assertEqual(response['status_code'], '200')

class TestWebpageProtocol(unittest.TestCase):
    # Tests protocol given in URL.
    def test_protocol(self):
        x = webpage.Webpage('https://test.ing-site.com')
        request = x.request()
        self.assertEqual(request['host'], 'test.ing-site.com')
        self.assertEqual(request['protocol'], 'https')
        self.assertEqual(request['port'], '443')
        response = x.response()
        self.assertEqual(response['status_code'], '200')

    # Tests invalid protocol given as parameter.
    def test_invalid_protocol(self):
        x = webpage.Webpage('test.ing-site.com', {}, {}, '', 'muchmuchwrong')
        request = x.request()
        self.assertEqual(request['host'], 'test.ing-site.com')
        self.assertEqual(request['protocol'], 'http')
        self.assertEqual(request['port'], '80')
        response = x.response()
        self.assertEqual(response['status_code'], '200')

    # Tests if parameters protocol overrides whatever is given in the URL.
    def test_overriding_protocol(self):
        x = webpage.Webpage('https://test.ing-site.com', {}, {}, '', 'http')
        request = x.request()
        self.assertEqual(request['host'], 'test.ing-site.com')
        self.assertEqual(request['protocol'], 'http')
        self.assertEqual(request['port'], '80')
        response = x.response()
        self.assertEqual(response['status_code'], '200')

class TestWebpagePort(unittest.TestCase):
    # Tests if the parameter port overrides whatever is given in the URL.
    def test_overriding_port(self):
        x = webpage.Webpage('http://test.ing-site.com:81', {}, {}, '80')
        request = x.request()
        self.assertEqual(request['host'], 'test.ing-site.com')
        self.assertEqual(request['port'], '80')
        response = x.response()
        self.assertEqual(response['status_code'], '200')

    # Tests custom port given in the URL.
    def test_custom_url_port(self):
        x = webpage.Webpage('http://test.ing-site.com:81')
        request = x.request()
        self.assertEqual(request['host'], 'test.ing-site.com')
        self.assertEqual(request['port'], '81')
        response = x.response()
        self.assertEqual(response['status_code'], '200')

    # Tests custom port given as parameter.
    def test_custom_parameter_port(self):
        x = webpage.Webpage('http://test.ing-site.com', {}, {}, '81')
        request = x.request()
        self.assertEqual(request['host'], 'test.ing-site.com')
        self.assertEqual(request['port'], '81')
        response = x.response()
        self.assertEqual(response['status_code'], '200')

class TestWebpageParameters(unittest.TestCase):
    # Tests that parameters are correctly passed in from the URL for GET 
    # requests.
    def test_get_parameters_url(self):
        x = webpage.Webpage('test.ing-site.com?key=value', {}, {}, '', '',
            'GET')
        response = x.response()
        self.assertEqual(response['status_code'], '200')
        self.assertEqual(response['body'], 'Webpage:<br>GET: key=value')
        request = x.request()
        self.assertEqual(request['method'], 'GET')

    # Tests that parameters are correctly passed in for GET requests.
    def test_get_parameters(self):
        x = webpage.Webpage('test.ing-site.com', {'key':'value'}, {}, '', '',
            'GET')
        response = x.response()
        self.assertEqual(response['status_code'], '200')
        self.assertEqual(response['body'], 'Webpage:<br>GET: key=value')
        request = x.request()
        self.assertEqual(request['method'], 'GET')

    # Tests that parameters are encoded correctly.
    def test_encode_parameters(self):
        x = webpage.Webpage('test.ing-site.com', {'key':'!"#$%&\'()*+,-./01234'+
            '56789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrst'+
            'uvwxyz{|}~'})
        request = x.request()
        self.assertEqual(request['parameter_string'], 'key=%21%22%23%24%25%26'+
            '%27%28%29%2A%2B%2C-.%2F0123456789%3A%3B%3C%3D%3E%3F%40ABCDEFGHIJK'+
            'LMNOPQRSTUVWXYZ%5B%5C%5D%5E_%60abcdefghijklmnopqrstuvwxyz%7B%7C'+
            '%7D%7E')
        response = x.response()
        self.assertEqual(response['status_code'], '200')
        self.assertEqual(response['body'], 'Webpage:<br>GET: key=!"#$%&\'()*+,'+
            '-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijkl'+
            'mnopqrstuvwxyz{|}~')

    # Tests that parameters are correctly passed in from the URL for POST 
    # requests.
    def test_post_parameters_url(self):
        x = webpage.Webpage('test.ing-site.com?key=value', {}, {}, '', '',
            'POST')
        response = x.response()
        self.assertEqual(response['status_code'], '200')
        self.assertEqual(response['body'], 'Webpage:<br>POST: key=value')
        request = x.request()
        self.assertEqual(request['method'], 'POST')

    # Tests that parameters are correctly passed in for POST requests.
    def test_post_parameters(self):
        x = webpage.Webpage('test.ing-site.com', {'key':'value'}, {}, '', '', 
            'POST')
        response = x.response()
        self.assertEqual(response['status_code'], '200')
        self.assertEqual(response['body'], 'Webpage:<br>POST: key=value')
        request = x.request()
        self.assertEqual(request['method'], 'POST')

class TestWebpageFile(unittest.TestCase):
    # Tests that the file is correctly retrieved and saved correctly.
    def test_saved_file(self):
        x = webpage.Webpage('test.ing-site.com', {'key':'value'}, {}, '', '', 
            'POST', 0, 0, 0, '/tmp/index.txt')
        response = x.response()
        self.assertEqual(response['status_code'], '200')
        self.assertEqual(response['body'], 'Webpage:<br>POST: key=value')
        f = open('/tmp/index.txt', 'r')
        file_content = f.read()
        self.assertEqual(file_content, 'Webpage:<br>POST: key=value')
        f.close()

class TestWebpageRedirects(unittest.TestCase):
    # Tests that no redirects are followed, if redirects_follow=0.
    def test_no_redirection(self):
        x = webpage.Webpage('test.ing-site.com?redirect=1', {}, {}, '', '', '',
            0)
        response = x.response()
        self.assertEqual(response['status_code'], '301')
        redirects = x.redirects()
        self.assertEqual(redirects['follow'], 0)
        self.assertEqual(redirects['used'], 0)

    # Tests that 1 redirect is followed, if redirects_follow=1.
    def test_one_redirection(self):
        x = webpage.Webpage('test.ing-site.com?redirect=2', {}, {}, '', '', '', 
            1)
        response = x.response()
        self.assertEqual(response['status_code'], '301')
        redirects = x.redirects()
        self.assertEqual(redirects['follow'], 1)
        self.assertEqual(redirects['used'], 1)

    # Tests that 1 redirect is followed, if redirects_follow=2 but only 1 is 
    # needed.
    def test_two_one_needed_redirection(self):
        x = webpage.Webpage('test.ing-site.com?redirect=1', {}, {}, '', '', '', 
            2)
        response = x.response()
        self.assertEqual(response['status_code'], '200')
        redirects = x.redirects()
        self.assertEqual(redirects['follow'], 2)
        self.assertEqual(redirects['used'], 1)

class TestWebpageMethod(unittest.TestCase):
    # Tests that providing an invalid method gives an 
    # UnsupportedMethodException.
    def test_UnsupportedMethodException(self):
        self.assertRaises(webpage.UnsupportedMethodException, webpage.Webpage, 
            'test.ing-site.com', {}, {}, '', '', 'GETS')

class TestWebpageNoWebsite(unittest.TestCase):
    # Tests that trying to a 404 page gives a NoWebsiteFoundException.
    def test_NoWebsiteFoundException_404(self):
        self.assertRaises(webpage.NoWebsiteFoundException, webpage.Webpage, 
            'test.ing-site.com/IDoNotExist.py')

    # Tests that trying to reach a website that doesn't exists gives a timeout
    # and a NoWebsiteFoundException.
    def test_NoWebsiteFoundException_timeout(self):
        self.assertRaises(webpage.NoWebsiteFoundException, webpage.Webpage, 
            'test.ing-site.com:666', {}, {}, '', '', '', 0, 5)

class TestWebpageVerifySSL(unittest.TestCase):
    # Tests that trying to access a page with a valid SSL certificate is 
    # successfull
    def test_valid_SSL(self):
        x = webpage.Webpage('https://encrypted.google.com', {}, {}, '', '', '', 
            0, 0, 1)
        response = x.response()
        self.assertEqual(response['status_code'], '200')

    # Tests that trying to reach a website with a self signed SSL certificate
    # will give an exception.
    def test_invalid_SSL_selfsigned(self):
        self.assertRaises(ssl.SSLError, webpage.Webpage, 
            'https://test.ing-site.com:443', {}, {}, '', '', '', 0, 0, 1)

    # Tests that trying to reach a website with a self signed SSL certificate
    # and erroneous will give an exception.
    def test_invalid_SSL_erroneous(self):
        self.assertRaises(ssl.SSLError, webpage.Webpage, 
            'https://test.ing-site.com:444', {}, {}, '', '', '', 0, 0, 1)

suiteBasic = unittest.TestLoader().loadTestsFromTestCase(TestWebpageBasic)
suiteProtocol = unittest.TestLoader().loadTestsFromTestCase(TestWebpageProtocol)
suitePort = unittest.TestLoader().loadTestsFromTestCase(TestWebpagePort)
suiteParameters = unittest.TestLoader().loadTestsFromTestCase(TestWebpageParameters)
suiteFile = unittest.TestLoader().loadTestsFromTestCase(TestWebpageFile)
suiteRedirects = unittest.TestLoader().loadTestsFromTestCase(TestWebpageRedirects)
suiteMethod = unittest.TestLoader().loadTestsFromTestCase(TestWebpageMethod)
suiteNoWebsite = unittest.TestLoader().loadTestsFromTestCase(TestWebpageNoWebsite)
suiteVerifySSL = unittest.TestLoader().loadTestsFromTestCase(TestWebpageVerifySSL)

alltests = unittest.TestSuite([suiteBasic, suiteProtocol, suitePort, 
    suiteParameters, suiteFile, suiteRedirects, suiteMethod, suiteNoWebsite,
    suiteVerifySSL])
result = unittest.TestResult()
alltests.run(result)
print result # I'm just printing the results
print result.failures
