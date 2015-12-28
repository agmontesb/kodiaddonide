# -*- coding: utf-8 -*-
'''
Created on 4/12/2015

@author: Alex Montes Barrios
'''
import os
import re
import urllib
import urllib2
import urlparse
import socket
import cookielib
import operator
import StringIO
import mimetools
import mimetypes
import tkSimpleDialog
import optparse

import gzip
import zlib
from urllib import urlencode
from _pytest.config import Parser


BOUNDARY = mimetools.choose_boundary()

def createParser():
    parser = optparse.OptionParser()

    parser.add_option('--url', dest = 'url')

    parser.add_option('-H', '--header', action = 'callback', callback = headerProc, type = 'string', nargs = 1, dest = 'header', default = [])
    parser.add_option('-A', '--user-agent', action = 'callback', callback = headerProc, type = 'string', nargs = 1)
    parser.add_option('-e', '--referer', action = 'callback', callback = headerProc, type = 'string', nargs = 1)
    parser.add_option('--compressed', action = 'callback', callback = headerProc)

    parser.add_option('-F', '--form', action = 'callback', callback = formProc, type = 'string', nargs = 1, dest = 'form', default = [])
    parser.add_option('-d', '--data', action = 'callback', callback = dataProc, type = 'string', nargs = 1, dest = 'data', default = [])
    parser.add_option('--data-urlencode', action = 'callback', callback = dataProc, type = 'string', nargs = 1)
    parser.add_option('--data-raw', action = 'callback', callback = dataProc, type = 'string', nargs = 1)
    parser.add_option('--data-binary', action = 'callback', callback = dataProc, type = 'string', nargs = 1)

    parser.add_option('-i', '--include', action = 'store_true', dest = 'include', default = False)

    parser.add_option('-L', '--location', action = 'store_true', dest = 'location', default = False)
    parser.add_option('--post301', action = 'store_true', dest = 'post301', default = False)
    parser.add_option('--post302', action = 'store_true', dest = 'post302', default = False)
    parser.add_option('--post303', action = 'store_true', dest = 'post303', default = False)


    parser.add_option('-o', '--output', dest = 'output')
    parser.add_option('-O', '--remote-name', action = 'store_true', dest = 'remote_name', default = False)
    parser.add_option('--remote-dirs', action = 'store_true', dest = 'remote_dirs', default = False)
    parser.add_option('--create-dirs', action = 'store_true', dest = 'create_dirs', default = False)

    parser.add_option('-b', '--cookie', dest = 'cookie')
    parser.add_option('-c', '--cookie-jar', dest = 'cookie_jar')

    parser.add_option('-u', '--user', dest = 'user')
    parser.add_option('--digest', action = 'store_const', const = 'digest', dest = 'auth_method', default = 'basic')
    parser.add_option('--basic', action = 'store_const', const = 'basic', dest = 'auth_method')

    parser.add_option('-x', '--proxy', dest = 'proxy')
    parser.add_option('-U', '--proxy-user', dest = 'proxy_user')    
    parser.add_option('--proxy-digest', action = 'store_const', const = 'digest', dest = 'proxy_auth', default = 'basic')
    parser.add_option('--proxy-basic', action = 'store_const', const = 'basic', dest = 'proxy_auth')

    parser.add_option('-G', '--get', action = 'store_const', const = 'GET', dest = 'req_method', default = '')
    parser.add_option('--head', action = 'store_const', const = 'HEAD', dest = 'req_method')
    parser.add_option('--post', action = 'store_const', const = 'POST', dest = 'req_method')
    
    return parser
    
def dataProc(option, opt_str, value, parser):
    if opt_str == '--data':
        if value.startswith('@'):
            fileName = value[1:]
            with open(fileName, 'r') as f:
                value = '&'.join(urllib.urlencode(f.readlines()))
    elif opt_str == '--data-urlencode':
        name1, sep1, value1 = value.partition('=')
        name2, sep2, value2 = value.partition('@')
        if not sep1 and not sep2:value = urllib.urlencode(value)
        elif sep1 and ('=' + value1) == value: value = urllib.urlencode(value[1:])
        elif sep2 and ('@' + value2) == value:
            with open(value2, 'r') as f:
                value = urllib.urlencode(f.read())
        elif name1 and '@' not in name1:
            value = name1 + "=" + urllib.urlencode(value1)
        elif name2:
            with open(value2, 'r') as f:
                value = name2 + "=" + urllib.urlencode(f.read())
    elif opt_str == '--data-binary':
        if value.startswith('@'):
            fileName = value[1:]
            with open(fileName, 'rb') as f:
                value = f.read()
    elif opt_str == '--data-raw':
        pass
    parser.values.data.append(value)
    pass

def formProc(option, opt_str, value, parser):
        name, suffix = value.strip('"').split('=', 1)
        value, mimetype = suffix.partition(';')[0:3:2]
        if mimetype:
            mimetype = 'Content-' + mimetype.replace('=',':').capitalize()
        if value[0] in '<@':
            prefix = value[0]
            value = value[1:]
            mimetype = mimetype.partition('=')[2]
            if not mimetype: 
                mimetype = mimetypes.guess_type(value)[0] or 'application/octet-stream'
            rtype = 'r' if 'text' in mimetype else 'rb'
            with open(value, rtype) as f: body = f.read()
            mimetype = 'Content-Type: ' + mimetype
            if prefix == '@':
                contentDisp = 'Content-Disposition: file; name"%s"; filename="%s"' % (name, value)
            else:
                contentDisp = 'Content-Disposition: form-data; name"%s"' % name
            parser.values.form.extend(['--' + BOUNDARY,
                                       contentDisp,
                                       mimetype,
                                       '',
                                       body,])
            pass
        else:
            mimetype = 'Content-Type:' + mimetype or 'text/plain'
            parser.values.form.extend(['--' + BOUNDARY,
                                       'Content-Disposition: form-data; name"%s"' % name,
                                       mimetype,
                                       '',
                                       value,])
            
def headerProc(option, opt_str, value, parser):
    if opt_str == '--user-agent':
        value = 'User-Agent: ' + value
    elif opt_str == '--referer':
        value = 'Referer: ' + value
    elif opt_str == '--compressed':
        value = 'Accept-encoding: gzip,deflate'
    toappend = value.split(': ', 1)
    parser.values.header.append(toappend)


class network:
    CURL_PATTERN = r'(?<= )(-[-\da-zA-Z]+)(?= )'

    def __init__(self, initCurlComm = '', defDirectory = ''):
        self.baseOptions = self.parseCommand(initCurlComm) if initCurlComm else []
        self.log = LogNetFlow()
        self.defDirectory = defDirectory
        self.parser = createParser()
        pass
    
    def parseCommand(self, curlCommand):
        curlCommand, headers = curlCommand.partition('<headers>')[0:3:2]
        if headers:
            headers = urlparse.parse_qs(headers)
            strHeaders = ' '.join(['-H "%s: %s"' % (key,value[0]) for key, value in headers.items()])
            curlCommand += ' ' + strHeaders
        curlStr = ' ' + curlCommand.replace('<post>', ' --data ').lstrip('curl ') + ' '
        opvalues = [elem for elem in map(operator.methodcaller('strip', ' "') ,re.split(self.CURL_PATTERN, curlStr)) if elem]
        return opvalues
    
    def openUrl(self, urlToOpen):
        self.log.clearLog()
        opvalues = self.parseCommand(urlToOpen)
        opvalues = self.baseOptions + opvalues
        if not opvalues[-1]: return None
        values, args = self.parser.parse_args(opvalues)
        assert len(args) == 1, 'Opciones no reconocibles ' + str(args)
        urlStr = args[0]
        values.url = urlStr.strip('"')
        
        opener = self.getOpener(values)
        self.request = self.getRequest(values)
        self.log.logRequest(self.request)
        try:
            self.response = opener.open(self.request)
        except Exception as e:
            self.request = None
            data = e
        else:
            data = self.response.read()
            responseinfo = self.response.info()
            content_encoding = responseinfo.get('Content-Encoding')
            data = unCompressMethods(data, content_encoding)
            if "text" in responseinfo.gettype():
                encoding = None
                if 'content-type' in responseinfo:
                    content_type = responseinfo.get('content-type').lower()
                    match = re.search('charset=(\S+)', content_type)
                    if match: encoding = match.group(1)
                charset = encoding or 'iso-8859-1'
                data = data.decode(charset, 'replace')
            self.processData(values, data)
            self.response.close()
        return data
        pass
    
    def processData(self, values, data):
        response = self.response
        request = self.request
        self.log.logResponse(response)        
        if values.include: data = str(self.log) + data
        
        cookie_jar = values.cookie_jar
        if cookie_jar and os.path.isfile(cookie_jar):
            cj = cookielib.LWPCookieJar(cookie_jar)
            cj.extract_cookies(response, request)
            cj.save(cookie_jar)
        
        filename = ''
        if values.remote_name:        
            filename = urlparse.urlparse(response.geturl()).path
            filename = os.path.split(filename)[1]
            
        if values.output:filename = values.output.strip('\'"')
        
        if not filename: return
        directory, filename = os.path.split(filename)
        if directory and not os.path.exists(directory):
            if values.create_dirs: os.makedirs(directory)
        directory = directory or self.defDirectory
        filename = os.path.join(directory, filename) 

        binaryFlag = "text" not in response.info().gettype()
        access = 'wb' if binaryFlag else 'w'
        out_data = data if binaryFlag else data.encode('utf-8')
        with open(filename, access) as f:
            f.write(out_data)
    
    
    
    def getOpener(self, values):
        include = None if values.include else self.log
        pSwitches = [values.post301, values.post302, values.post303]
        opener_handlers = [LogHandler(values.url)] 
        opener_handlers.append(netHTTPRedirectHandler(location = values.location, include = include, postSwitches = pSwitches))
    
        cookie_val = None
        if values.cookie_jar: cookie_val = values.cookie_jar
        if values.cookie: cookie_val = values.cookie 

        if cookie_val != None:
            cj = cookielib.LWPCookieJar()
            if os.path.isfile(cookie_val): cj.load(cookie_val)
            opener_handlers.append(urllib2.HTTPCookieProcessor(cj))
 
        passwordManager = urllib2.HTTPPasswordMgrWithDefaultRealm()           
        if values.user:
            user, password = values.user.partition(':')[0:3:2]
            if not password:
                try:
                    password = tkSimpleDialog.askstring("Enter password for " + user, "Enter password:", show='*')
                except:
                    password = input("Enter password for " + user)
            passwordManager.add_password(None, values.url, user, password)
            opener_handlers.append(urllib2.HTTPBasicAuthHandler(passwordManager))
            if values.auth_method == 'digest':
                opener_handlers.append(urllib2.HTTPDigestAuthHandler(passwordManager))
            pass
        
        if values.proxy:            
            proxyStr = values.proxy
            protocol, user, password, proxyhost = urllib2._parse_proxy(proxyStr)
            protocol = protocol or 'http'
            proxy_handler = urllib2.ProxyHandler({protocol:proxyhost})
            opener_handlers.append(proxy_handler)
            if not user:
                if values.proxy_user:
                    user, password = values.proxy_user.partition(':')
            if user and not password:
                try:
                    password = tkSimpleDialog.askstring("Enter proxy password for " + user, "Enter password:", show='*')
                except:
                    input("Enter proxy password for " + user)
                passwordManager.add_password(None, proxyhost, user, password)
                opener_handlers.append(urllib2.ProxyBasicAuthHandler(passwordManager))
                if values.proxy_auth == 'digest':
                    opener_handlers.append(urllib2.ProxyDigestAuthHandler(passwordManager))
            pass
        

        opener = urllib2.build_opener(*opener_handlers)
        return opener
    
    def getRequest(self, values):
        postdata = ''
        if values.form:
            values.form.append('--' + BOUNDARY + '--')
            values.form.append('')
            postdata += '\r\n'.join(values.form)
            values.header.append(['Content-type', 'multipart/form-data; boundary=%s' % BOUNDARY])
            values.header.append(['Content-length', '%s' % len(postdata)])
            values.data = []
        
        if values.data:
            urlencodedata = '&'.join(values.data)
            if urlencodedata and values.req_method == 'GET':
                values.url += '?' + urlencodedata
            else:
                postdata = urlencodedata
        postdata = postdata or None
        
        headers = {}
        for key, value in values.header:
            if value: headers[key] = value
            elif headers.has_key(key): headers.pop(key)
            
        urlStr = values.url        
        request = urllib2.Request(urlStr, postdata, headers)
        if values.req_method  and values.req_method not in ['GET', 'POST']: 
            setattr(request, 'get_methd', lambda: values.req_method)
        return request
        pass
    
class LogNetFlow:
    SEPARATOR = '\n' + 80*'='
    HEAD_SEP = '\n' + 80*'-'
    def __init__(self):
        self.log = ''
        pass
    
    def logRequest(self, request):
        request_data = self.SEPARATOR
        genHdr = []
        try:
            remadd = socket.gethostbyname(request.get_host()) + ':' + str(socket.getservbyname(request.get_type()))
        except:
            pass
        else:
            genHdr.append(('Remote Address', remadd))
        genHdr.append(('Request Url', request.get_full_url()))
        genHdr.append(('Request Method', request.get_method()))
#         genHdr.append(('Status Code', str(request.getcode())))

        for key, value in genHdr: request_data += '\n' + key + ': ' + str(value)

        request_data += self.HEAD_SEP
        request_headers = request.headers 
        for key, value in sorted(request_headers.items()): request_data += '\n' + key + ': ' + str(value)
        self.log += request_data
        pass
    
    def logResponse(self, response):
        response_data = self.SEPARATOR
        responseinfo = response.info() 
        for key, value in sorted(responseinfo.items()): response_data += '\n' + key + ': ' + str(value)
        self.log += response_data
        pass
    
    def getNetFlow(self):
        return self.log
    
    def clearLog(self):
        self.log = ''
    
    def __str__(self):
        return self.getNetFlow()        
    
class LogHandler(urllib2.BaseHandler):
    handler_order = 480
    SEPARATOR = '\n' + 35*'=' + ' %s ' + 35*'='  
    HEAD_SEP = '\n' + 80*'-'
    
    def __init__(self, values):
        scheme = urlparse.urlsplit(values.url)[0]
        setattr(self, scheme + '_request', self.requestProcessor)
        setattr(self, scheme + '_response', self.responseProcessor)
        for code in [301, 302, 303, 401, 407]:
            setattr(self, '%s_error_%s' % ('http', code), self.errorProcessor)
            
        self.log = ''
        self.include = values.include
        self.location = values.location
        self.errCode = 0
        self.postswitches = [values.post301, values.post302, values.post303]
        self.origReqMethod = values.req_method
        pass
    
    def requestProcessor(self, request):
        if self.include:
            request_data = self.SEPARATOR % 'Request'
            genHdr = []
            try:
                remadd = socket.gethostbyname(request.get_host()) + ':' + str(socket.getservbyname(request.get_type()))
            except:
                pass
            else:
                genHdr.append(('Remote Address', remadd))
            genHdr.append(('Request Url', request.get_full_url()))
            genHdr.append(('Request Method', request.get_method()))
    #         genHdr.append(('Status Code', str(request.getcode())))
    
            for key, value in genHdr: request_data += '\n' + key + ': ' + str(value)
    
            request_data += self.HEAD_SEP
            request_headers = request.headers 
            for key, value in sorted(request_headers.items()): request_data += '\n' + key + ': ' + str(value)
            if request.unredirected_hdrs:
                request_data += self.HEAD_SEP
                for key, value in request.unredirected_hdrs.items(): request_data += '\n' + key + ': ' + str(value)
            self.log += request_data
        if self.origReqMethod and self.origReqMethod not in ['GET', 'POST'] and self.errCode in [301,302,303]:
            setattr(request, 'get_method', lambda: self.origReqMehod)
            self.errCode = 0
        return request
        pass
    
    def responseProcessor(self, request, response):
        if self.include:
            response_data = self.SEPARATOR  % 'Response'
            hdr = [('code', response.getcode()), ('Message', response.msg)]
            for key, value in hdr: response_data += '\n' + key + ': ' + str(value)        
            response_data += self.HEAD_SEP
            responseinfo = response.info() 
            for key, value in sorted(responseinfo.items()): response_data += '\n' + key + ': ' + str(value)
            self.log += response_data
        return response
        pass
    
    def errorProcessor(self, req, fp, code, msg, headers):
        if self.include:
            error_data = self.SEPARATOR  % 'Error'
            hdr = [('Error code: ', code), ('Message', msg)]
            for key, value in hdr: error_data += '\n' + key + ': ' + str(value)        
            error_data += self.HEAD_SEP
            self.log += error_data
        if self.location:
            self.errCode = code
            return None
        else:
            raise urllib2.URLError('Redirection not allowed')
        pass
    
    

class netHTTPRedirectHandler(urllib2.HTTPRedirectHandler):
    def __init__(self, location = True, include = None, postSwitches = None):
        self.location = location
        self.include = include
        self.postSwitches = postSwitches or []
        self.log = ''
        
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if self.include: self.include.logRequest(req)
        if not self.location: return None
        newreq = urllib2.HTTPRedirectHandler.redirect_request(self, req, fp, code, msg, headers, newurl)
        method = req.get_method()
        if method not in ['GET','POST'] or method == 'POST' and self.postSwitches[code - 301]:
            newreq.get_method = req.get_method
            if method == 'POST': newreq.data = req.data
        return newreq
    
    def http_error_302(self, req, fp, code, msg, hdrs):
        if self.include: self.include.logResponse(fp)
        return urllib2.HTTPRedirectHandler.http_error_301(self, req, fp, code, msg, hdrs)


def unCompressMethods(data, compMethod):
    if compMethod == 'gzip':
        compressedstream = StringIO.StringIO(data)
        gzipper = gzip.GzipFile(fileobj=compressedstream)
        data = gzipper.read()
        gzipper.close()
    return data


if __name__ == '__main__':
    initConf = '--user-agent "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36"'
    net = network(initConf, defDirectory = 'c:/testFiles')
    print 'Hello world' 
    urlStr = 'curl "http://www.larebajavirtual.com/admin/login/autenticar" -i -L -H "Cookie: PHPSESSID=3aq7b04etgak304bdkkvavmgc3; SERVERID=A; __utma=122436758.286328447.1449155983.1449156151.1449156151.1; __utmc=122436758; __utmz=122436758.1449156151.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _ga=GA1.2.286328447.1449155983; _gat=1; __zlcmid=Y0f9JrZKNnst3j" -H "Origin: http://www.larebajavirtual.com" -H "Accept-Encoding: gzip, deflate" -H "Accept-Language: es-ES,es;q=0.8,en;q=0.6" -H "Upgrade-Insecure-Requests: 1" -H "User-Agent: Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36" -H "Content-Type: application/x-www-form-urlencoded" -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8" -H "Cache-Control: max-age=0" -H "Referer: http://www.larebajavirtual.com/admin/login/index/pantalla/" -H "Connection: keep-alive" --data "username=9137521&password=agmontesb&login=Ingresar" --compressed'
    urlStr = 'curl "http://aa6.cdn.vizplay.org/v/4da9d8f843be8468108d62cb506cc286.mp4?st=9VECn4qJ9eja2lxhz5ynjQ&hash=Pway1DZi6ARlvoBfz8BvEA" -H "Origin: http://videomega.tv" -H "Accept-Encoding: identity;q=1, *;q=0" -H "Accept-Language: es-ES,es;q=0.8,en;q=0.6" -H "User-Agent: Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36" -H "Accept: */*" -H "Referer: http://videomega.tv/cdn.php?ref=tBmn3h4X3AA3X4h3nmBt" -H "Connection: keep-alive" -H "Range: bytes=0-" --compressed'
    urlStr = 'curl "http://videomega.tv/cdn.php?ref=tBmn3h4X3AA3X4h3nmBt"  --cookie-jar "cookies.lwp" --include -L'
    urlStr = 'curl "http://hqq.tv/player/get_md5.php?server=aHR0cDovLzlxZjdoOS52a2NhY2hlLmNvbQ"%"3D"%"3D&link=aGxzLXZvZC1zNi9mbHYvYXBpL2ZpbGVzL3ZpZGVvcy8yMDE1LzExLzI3LzE0NDg1Nzc5NjI2MjQzOD9zb2NrZXQ"%"3D&at=8abd81bdd68782fb91010541aa2044df&adb=0"%"2F&b=1&vid=D5RM53HN4X3M" -H "Cookie: __cfduid=d999c2d230c10b08a26d77d4227d71c8b1448502346; video_D5RM53HN4X3M=watched; user_ad=watched; _ga=GA1.2.197051833.1449399878; noadvtday=0; incap_ses_257_146471=ZIzkX4wa5yESEeaczQyRA+g4ZFYAAAAA4lmajNgKvr85nmfXjJC/+A==; __PPU_CHECK=1; __PPU_SESSION_c-f=Xf4e8d,1449409702,1,1449409582X; visid_incap_146471=quZ+QT56TmKQd6TqlyOm+EdkVlYAAAAAQUIPAAAAAAA0mlg9lN8zyBplBfZvmrin; incap_ses_209_146471=mPDTGK78tXa1dGIwoYTmAtY7ZFYAAAAA2E7y0JGu8xDbhxMVTR/Peg==" -H "Accept-Encoding: gzip, deflate, sdch" -H "Accept-Language: es-ES,es;q=0.8,en;q=0.6" -H "User-Agent: Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36" -H "Accept: */*" -H "Referer: http://hqq.tv/" -H "X-Requested-With: XMLHttpRequest" -H "Connection: keep-alive" --compressed'
    urlStr = 'curl "http://hqq.tv/player/get_md5.php?b=1&vid=D5RM53HN4X3M&server=aHR0cDovLzlxZjdoOS52a2NhY2hlLmNvbQ%3D%3D&adb=0%2F&at=043a566afeb0bf2b668296a2128011d6&link=aGxzLXZvZC1zNi9mbHYvYXBpL2ZpbGVzL3ZpZGVvcy8yMDE1LzExLzI3LzE0NDg1Nzc5NjI2MjQzOD9zb2NrZXQ%3D"'
    urlStr = 'curl "http://videomega.tv/cdn.php?ref=tBmn3h4X3AA3X4h3nmBt" -H "User-Agent: Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36"   -H "Referer: http://www.novelashdgratis.tv/"'
    urlStr = 'curl "http://videomega.tv/cdn.php?ref=3f0UiU3oXggXo3UiU0f3" -H "User-Agent: Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36"   -H "Referer: http://www.novelashdgratis.tv/"'
#     data  = urlOpen(urlStr)
    urlStr ='curl "http://www.larebajavirtual.com/" -H "Accept-Encoding: gzip, deflate, sdch" -H "Accept-Language: es-ES,es;q=0.8,en;q=0.6" -H "Upgrade-Insecure-Requests: 1" -H "User-Agent: Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36" -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8" -H "Referer: http://www.larebajavirtual.com/" -H "Cookie: PHPSESSID=3aq7b04etgak304bdkkvavmgc3; SERVERID=A; __utma=122436758.286328447.1449155983.1449156151.1449156151.1; __utmc=122436758; __utmz=122436758.1449156151.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _ga=GA1.2.286328447.1449155983; _gat=1; __zlcmid=Y0f9JrZKNnst3j" -H "Connection: keep-alive" -H "Cache-Control: max-age=0" --compressed'
    urlStr ='curl "http://www.bvc.com.co/pps/tibco/portalbvc/Home/Mercados/enlinea/acciones" -H "Accept-Encoding: gzip, deflate, sdch" -H "Accept-Language: es-ES,es;q=0.8,en;q=0.6" -H "Upgrade-Insecure-Requests: 1" -H "User-Agent: Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36" -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8" -H "Referer: http://www.bvc.com.co/pps/tibco/portalbvc/Home/Mercados/enlinea/acciones?action=dummy" -H "Cookie: JSESSIONID=48E5CEBA94C459BEEF1157BC23970A3A.tomcatM1p6101; __utmt=1; submenuheader=-1c; style=null; __utma=146679143.72887542.1448644509.1449008313.1449593287.5; __utmb=146679143.3.10.1449593287; __utmc=146679143; __utmz=146679143.1448644509.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)" -H "Connection: keep-alive" -H "Cache-Control: max-age=0" --compressed'
    urlStr = 'curl "http://www.larebajavirtual.com/admin/login/autenticar" -i -L -H "Cookie: PHPSESSID=3aq7b04etgak304bdkkvavmgc3; SERVERID=A; __utma=122436758.286328447.1449155983.1449156151.1449156151.1; __utmc=122436758; __utmz=122436758.1449156151.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _ga=GA1.2.286328447.1449155983; _gat=1; __zlcmid=Y0f9JrZKNnst3j" -H "Origin: http://www.larebajavirtual.com" -H "Accept-Encoding: gzip, deflate" -H "Accept-Language: es-ES,es;q=0.8,en;q=0.6" -H "Upgrade-Insecure-Requests: 1" -H "User-Agent: Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36" -H "Content-Type: application/x-www-form-urlencoded" -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8" -H "Cache-Control: max-age=0" -H "Referer: http://www.larebajavirtual.com/admin/login/index/pantalla/" -H "Connection: keep-alive" --data "username=9137521&password=agmontesb&login=Ingresar" --compressed'
    urlStr = 'curl "http://localhost:8080/" -F "firstname=Doug" -F "lastname=Hellman" -F "biography=@C:/testFiles/bio.txt"' 
    urlStr = 'curl "http://powvideo.net/iframe-x5gab53lm207-607x360.html" -H "User-Agent: Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36" -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8" -H "Referer: http://powvideo.net/preview-x5gab53lm207-607x360.html" -L -i -I --compressed'
    urlStr = 'curl "http://imgs24.com/i/Mr_Holmes-813244846-large.th.jpg" --output "c:/testFiles/mipng.jpg"'
    urlStr = 'curl "http://imgs24.com/i/Mr_Holmes-813244846-large.th.jpg" -H "If-None-Match: ""48bdcd-34ab-46895a3c78eb2""" -H "Accept-Encoding: gzip, deflate, sdch" -H "Accept-Language: es-ES,es;q=0.8,en;q=0.6" -H "Upgrade-Insecure-Requests: 1" -H "User-Agent: Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36" -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8" -H "Referer: http://pelis24.com/hd/" -H "Cookie: __cfduid=decb65f5cc969051bbdbb4fb2837d8be91449850247" -H "Connection: keep-alive" -H "If-Modified-Since: Tue, 28 Apr 2009 04:10:14 GMT" -H "Cache-Control: max-age=0" --output "c:/testFiles/pic/holmes.jpg" --create-dirs --compressed'
    urlStr = 'curl "https://openload.co/embed/EzDsB4C1Lk8/" --user-agent "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36" -H "accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"  --compressed'
    urlStr = 'curl "http://localhost:8080/" -F "firstname=Doug" -F "lastname=Hellman" -F "biography=@C:/testFiles/bio.txt"'
    urlStr = 'curl "http://imgs24.com/i/Mr_Holmes-813244846-large.th.jpg" --output "c:/testFiles/mipng.jpg"'
    urlStr = 'curl "http://www.larebajavirtual.com/admin/login/autenticar" -i -L -H "Cookie: PHPSESSID=3aq7b04etgak304bdkkvavmgc3; SERVERID=A; __utma=122436758.286328447.1449155983.1449156151.1449156151.1; __utmc=122436758; __utmz=122436758.1449156151.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _ga=GA1.2.286328447.1449155983; _gat=1; __zlcmid=Y0f9JrZKNnst3j" -H "Origin: http://www.larebajavirtual.com" -H "Accept-Encoding: gzip, deflate" -H "Accept-Language: es-ES,es;q=0.8,en;q=0.6" -H "Upgrade-Insecure-Requests: 1" -H "User-Agent: Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36" -H "Content-Type: application/x-www-form-urlencoded" -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8" -H "Cache-Control: max-age=0" -H "Referer: http://www.larebajavirtual.com/admin/login/index/pantalla/" -H "Connection: keep-alive" --data "username=9137521&password=agmontesb&login=Ingresar" --compressed'
    urlStr = 'curl "https://www.httpwatch.com/httpgallery/authentication/authenticatedimage/default.aspx?0.5612395589430635" --cookie "None"  -H "User-Agent: Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36" --user "httwatch:vacaciones" -o "c:/testFiles/httpwatch.png" -H "Referer: https://www.httpwatch.com/httpgallery/authentication/" -H "Cookie: LastPassword=montes; __utmt=1; ARRAffinity=a76654ca7f49a0cbbce2d3d460023ceaf63cbee2a548fd4bf7dd6f0b4758ad31; __utma=1.1454154178.1450557677.1450557677.1450557755.2; __utmb=1.7.10.1450557755; __utmc=1; __utmz=1.1450557755.2.2.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not"%"20provided)" -L'
    urlStr = 'curl "http://www.larebajavirtual.com/admin/login/autenticar" --cookie "None" -o "c:/testFiles/testCase.txt" -H "Cookie: __utma=122436758.286328447.1449155983.1450276163.1450366939.5; __utmz=122436758.1449156151.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); PHPSESSID=pf0t4q65l5u9kbqj16mgb47ke5; SERVERID=B; _gat=1; _ga=GA1.2.286328447.1449155983; __zlcmid=Y0f9JrZKNnst3j" -H "Origin: http://www.larebajavirtual.com" -H "Accept-Encoding: gzip, deflate" -H "Accept-Language: es-ES,es;q=0.8,en;q=0.6" -H "Upgrade-Insecure-Requests: 1" -H "User-Agent: Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36" -H "Content-Type: application/x-www-form-urlencoded" -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8" -H "Cache-Control: max-age=0" -H "Referer: http://www.larebajavirtual.com/admin/login/index/pantalla/" -H "Connection: keep-alive" --data "username=9137521&password=agmontesb&login=Ingresar"  -L --compressed'
    urlStr = 'curl "https://www.httpwatch.com/httpgallery/authentication/authenticatedimage/default.aspx?0.5612395589430635" -o "c:/testFiles/httpwatch.png" -H "Authorization: Basic aHR0cHdhdGNoOmJhcnJpb3M=" -H "Accept-Encoding: gzip, deflate, sdch" -H "Accept-Language: es-ES,es;q=0.8,en;q=0.6" -H "User-Agent: Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36" -H "Accept: image/webp,image/*,*/*;q=0.8" -H "Referer: https://www.httpwatch.com/httpgallery/authentication/" -H "Cookie: LastPassword=montes; __utmt=1; ARRAffinity=a76654ca7f49a0cbbce2d3d460023ceaf63cbee2a548fd4bf7dd6f0b4758ad31; __utma=1.1454154178.1450557677.1450557677.1450557755.2; __utmb=1.7.10.1450557755; __utmc=1; __utmz=1.1450557755.2.2.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not"%"20provided)" -H "Connection: keep-alive" --compressed'
    urlStr = 'curl "https://www.httpwatch.com/httpgallery/authentication/authenticatedimage/default.aspx?0.5612395589430635" -o "c:/testFiles/httpwatch.png" -H "Host: www.httpwatch.com" -H "Authorization: Basic aHR0cHdhdGNoOmJhcnJpb3M="  -H "User-Agent: Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"  -H "Referer: https://www.httpwatch.com/httpgallery/authentication/" -H "Cookie: LastPassword=montes; __utmt=1; ARRAffinity=a76654ca7f49a0cbbce2d3d460023ceaf63cbee2a548fd4bf7dd6f0b4758ad31; __utma=1.1454154178.1450557677.1450557677.1450557755.2; __utmb=1.7.10.1450557755; __utmc=1; __utmz=1.1450557755.2.2.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not"%"20provided)"'
    urlStr = 'curl "https://www.httpwatch.com/httpgallery/authentication/authenticatedimage/default.aspx?0.5612395589430635" --cookie "None"  -H "User-Agent: Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36" --user "httpwatch:mi_mensaje_especial" -o "c:/testFiles/httpwatch.png" -H "Referer: https://www.httpwatch.com/httpgallery/authentication/" -H "Cookie: LastPassword=montes; __utmt=1; ARRAffinity=a76654ca7f49a0cbbce2d3d460023ceaf63cbee2a548fd4bf7dd6f0b4758ad31; __utma=1.1454154178.1450557677.1450557677.1450557755.2; __utmb=1.7.10.1450557755; __utmc=1; __utmz=1.1450557755.2.2.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not"%"20provided)" -L'
    urlStr = 'curl "http://vimeo.com/" --proxy "https://sitenable.com/o.php" --cookie "None"  -H "User-Agent: Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36" -o "testCase.txt" --compressed'    
    data = net.openUrl(urlStr)
    print 'Alex' in data
    pass

