from mock import patch, Mock, sentinel
from nose.tools import raises
from refreshbooks.exceptions import TransportException
from urllib2 import HTTPError

@patch('refreshbooks.transports.use_urllib2.u')
def test_urllib2_transport_exception(u):
    class FakeHttpError(HTTPError):
        def __init__(self, code, content):
            self.code = code
            self.content = content

        def read(self):
            return self.content

    u.HTTPError = FakeHttpError
    u.urlopen.return_value = Mock()
    u.urlopen.return_value.read.side_effect = FakeHttpError(sentinel.code, sentinel.content)

    try:
        from refreshbooks.transports.use_urllib2 import Transport
        Transport('x', dict)("foo")
    except TransportException, e:
        assert e.status is sentinel.code
        assert e.content is sentinel.content
    else:
        assert False, "Didn't fire expected exception"

def test_httplib2_transport_exception():
    httplib2mock = Mock()
    client = Mock()
    httplib2mock.Http.return_value = client
    client.request.return_value = (Mock(status=400), sentinel.content)

    with patch.dict('sys.modules', httplib2=httplib2mock):
        try:
            from refreshbooks.transports.use_httplib2 import Transport
            Transport('x', dict)("foo")
        except TransportException, e:
            assert e.status == 400
            assert e.content is sentinel.content
        else:
            assert False, "Didn't fire expected exception"

def test_requests_transport_exception():
    requestsmock = Mock()
    requestsmock.post.return_value = Mock(status_code=400, content=sentinel.content)

    with patch.dict('sys.modules', requests=requestsmock):
        try:
            from refreshbooks.transports.use_requests import Transport
            Transport('x', dict)("foo")
        except TransportException, e:
            assert e.status == 400
            assert e.content is sentinel.content
        else:
            assert False, "Didn't fire expected exception"
