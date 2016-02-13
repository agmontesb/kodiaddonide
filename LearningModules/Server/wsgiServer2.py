from urllib import quote
from wsgiref.simple_server import make_server

def url_reconstruction(environ):
    url = environ['wsgi.url_scheme']+'://'

    if environ.get('HTTP_HOST'):
        url += environ['HTTP_HOST']
    else:
        url += environ['SERVER_NAME']

        if environ['wsgi.url_scheme'] == 'https':
            if environ['SERVER_PORT'] != '443':
               url += ':' + environ['SERVER_PORT']
        else:
            if environ['SERVER_PORT'] != '80':
               url += ':' + environ['SERVER_PORT']

    url += quote(environ.get('SCRIPT_NAME', ''))
    url += quote(environ.get('PATH_INFO', ''))
    if environ.get('QUERY_STRING'):
        url += '?' + environ['QUERY_STRING']
    return url

def application (environ, start_response):
    url = url_reconstruction(environ)
    raw_line = ' '.join([environ['REQUEST_METHOD'], url, environ['SERVER_PROTOCOL']])
    req_headers = {}
    if environ.has_key('CONTENT_TYPE'):
        req_headers['Content-Type'] = environ['CONTENT_TYPE']
    if environ.has_key('CONTENT_LENGTH'):
        req_headers['Content-Length'] = environ['CONTENT_LENGTH']
    keys = [(key[5:].title(), key) for key in environ if key.startswith('HTTP_')]
    for key1, key2 in keys:
        key1 = key1.replace('_', '-')
        req_headers[key1] = environ[key2]
    req_headers ='\n'.join(['%s: %s' % (key, value) for key, value in sorted(req_headers.items())])

    response_body = '\n'.join([raw_line, req_headers])

    rfile = environ['wsgi.input']
    nbytes = environ['CONTENT_LENGTH']
    if nbytes:
        nbytes = int(nbytes)
        response_body += '\n\n' + rfile.read(nbytes)

    status = '200 OK'
    response_headers = [
        ('Content-Type', 'text/plain'),
        ('Content-Length', str(len(response_body))),
        ('Content-Encoding', 'utf-8')
    ]
    start_response(status, response_headers)

    return [response_body]

# Instantiate the server
httpd = make_server (
    'localhost', # The host name
    50000, # A port number where to wait for the request
    application # The application object name, in this case a function
)

# Wait for a single request, serve it and quit
httpd.handle_request()