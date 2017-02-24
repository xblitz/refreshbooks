from __future__ import print_function

import sys
import xmltodict

from refreshbooks import client, transport

try:
    from refreshbooks.optional import oauth as os
    _create_oauth_client = os.OAuthClient
except ImportError:
    def _create_oauth_client(*args, **kwargs):
        raise NotImplementedError('oauth support requires the "oauth" module.')


def api_url(domain):
    """Returns the Freshbooks API URL for a given domain.
    
        >>> api_url('billing.freshbooks.com')
        'https://billing.freshbooks.com/api/2.1/xml-in'
    """
    return "https://%s/api/2.1/xml-in" % (domain, )


def xml_request(method, **kwargs):
    kwargs['@method'] = method
    return xmltodict.unparse(dict(request=kwargs), pretty=True)


def fail_to_exception_response(response):
    if response['@status'] == 'fail':
        raise client.FailedRequest(response['error'])
    return response

default_request_encoder = xml_request


def default_response_decoder(*args, **kwargs):
    return fail_to_exception_response(
        xmltodict.parse(*args, **kwargs)['response']
    )


def logging_request_encoder(method, **params):
    encoded = default_request_encoder(method, **params)
    
    print("--- Request (%r, %r) ---" % (method, params), file=sys.stderr)
    print(encoded, file=sys.stderr)
    
    return encoded


def logging_response_decoder(response):
    print("--- Response ---", file=sys.stderr)
    print(response, file=sys.stderr)
    
    return default_response_decoder(response)


def build_headers(authorization_headers, user_agent):
    headers = transport.KeepAliveHeaders(authorization_headers)
    if user_agent is not None:
        headers = transport.UserAgentHeaders(headers, user_agent)
    
    return headers


def AuthorizingClient(
    domain,
    auth,
    request_encoder,
    response_decoder,
    user_agent=None
):
    """Creates a Freshbooks client for a freshbooks domain, using
    an auth object.
    """
    
    http_transport = transport.HttpTransport(
        api_url(domain),
        build_headers(auth, user_agent)
    )
    
    return client.Client(
        request_encoder,
        http_transport,
        response_decoder
    )


def TokenClient(
    domain,
    token,
    user_agent=None,
    request_encoder=default_request_encoder,
    response_decoder=default_response_decoder,
):
    """Creates a Freshbooks client for a freshbooks domain, using
    token-based auth.
    
    The optional request_encoder and response_decoder parameters can be
    passed the logging_request_encoder and logging_response_decoder objects
    from this module, or custom encoders, to aid debugging or change the
    behaviour of refreshbooks' request-to-XML-to-response mapping.
    
    The optional user_agent keyword parameter can be used to specify the
    user agent string passed to FreshBooks. If unset, a default user agent
    string is used.
    """
    
    return AuthorizingClient(
        domain,
        transport.TokenAuthorization(token),
        request_encoder,
        response_decoder,
        user_agent=user_agent
    )


def OAuthClient(
    domain,
    consumer_key,
    consumer_secret,
    token,
    token_secret,
    user_agent=None,
    request_encoder=default_request_encoder,
    response_decoder=default_response_decoder
):
    """Creates a Freshbooks client for a freshbooks domain, using
    OAuth. Token management is assumed to have been handled out of band.
    
    The optional request_encoder and response_decoder parameters can be
    passed the logging_request_encoder and logging_response_decoder objects
    from this module, or custom encoders, to aid debugging or change the
    behaviour of refreshbooks' request-to-XML-to-response mapping.
    
    The optional user_agent keyword parameter can be used to specify the
    user agent string passed to FreshBooks. If unset, a default user agent
    string is used.
    """
    return _create_oauth_client(
        AuthorizingClient,
        domain,
        consumer_key,
        consumer_secret,
        token,
        token_secret,
        user_agent=user_agent,
        request_encoder=request_encoder,
        response_decoder=response_decoder
    )
