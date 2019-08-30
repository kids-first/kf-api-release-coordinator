Service Authentication
======================

Because communication between Task Services and the Coordinator may occur over
the public internet, it is vital that each side verify any requests recieved.

The primary mechanism for this is through an `OAuth2 Client Credentials flow <https://tools.ietf.org/html/rfc6749#section-4.4>`_
where the services and credentials are mediated by Auth0
(which calls this flow 'Machine-to-Machine').

The Coordinator and each Task Service must be registered in the Kids First
account to recieve a set of credentials which will allow them to generate
access tokens of the ``client_credentials`` grant type as needed.
`This article <https://auth0.com/blog/using-m2m-authorization>`_ outlines the
process of setting up a new application in Auth0 and using it to generate
access tokens.

Identifying Outgoing Requests
-----------------------------

Each outward request to the Coordinator or a Task service will need to provide
a way of identifying itself to the recipient service.
This may be done through the standard mechanism of attaching the JWT obtained
through the above process to ``Authorization`` header, and prefixed with
``Bearer``.
It's recommended that each service issuing tokens with each request cache a
single token for as long as it is valid so as to reduce network requests to
Auth0 and reduce the number of valid tokens in circulation at any given time.

Authenticating Incoming Requests
--------------------------------

Requests recieved either by the Coordinator from a Task Service or by a Task
Service by the Coordinator must be verified as originating from an authorized
service.
If they are not, it's possible that anyone may issue requests and invoke
unallowed actions such as continually spinning release tasks, prematurely
ending tasks, or releasing private data to the public.

To verify the identity of a request, the ``Bearer`` token attached to the
request's ``Authorization`` header may be validated by checking the signature
against the Kids First keys.
These keys are provided publicly at:
https://kids-first.auth0.com/.well-known/jwks.json
