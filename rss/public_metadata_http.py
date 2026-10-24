"""Deadline-limited metadata transport with public-IP pinning and normal TLS."""
import http.client
import io
import ipaddress
import queue
import socket
import threading
import time
from urllib.parse import urlsplit
from urllib.request import HTTPHandler, HTTPSHandler

from export_feed import safe_url


def remaining(deadline):
    seconds = deadline - time.monotonic()
    if seconds <= 0:
        raise TimeoutError('metadata deadline expired')
    return seconds


def resolve_public(host, port, deadline):
    result = queue.Queue(maxsize=1)

    def resolve():
        try:
            result.put((socket.getaddrinfo(host, port, type=socket.SOCK_STREAM), None))
        except Exception as error:
            result.put((None, error))

    # A stuck OS resolver must not keep a worker or the Python process alive.
    remaining(deadline)
    threading.Thread(target=resolve, daemon=True).start()
    try:
        addresses, error = result.get(timeout=remaining(deadline))
    except queue.Empty:
        raise TimeoutError('metadata DNS deadline expired') from None
    if error:
        raise error
    if not addresses or any(not ipaddress.ip_address(a[4][0]).is_global for a in addresses):
        raise ValueError('non-public destination')
    return addresses


def public_destination(url, image=False, deadline=None):
    if not safe_url(url, image=image):
        raise ValueError('unsafe URL')
    p = urlsplit(url)
    resolve_public(p.hostname, p.port or (443 if p.scheme == 'https' else 80),
                   deadline if deadline is not None else time.monotonic() + 8)
    return url


def connect_public(address, deadline):
    host, port = address
    addresses = resolve_public(host, port, deadline)
    error = None
    # Connect to these exact sockaddr tuples, never re-resolve the hostname.
    for family, socktype, protocol, _, sockaddr in addresses[:8]:
        sock = socket.socket(family, socktype, protocol)
        try:
            sock.settimeout(remaining(deadline))
            sock.connect(sockaddr)
            sock.settimeout(remaining(deadline))
            return sock
        except Exception as current:
            error = current
            sock.close()
    raise error or OSError('no public connection')


class DeadlineReader(io.RawIOBase):
    def __init__(self, sock, deadline):
        self.sock, self.deadline = sock, deadline
        self.stream = sock.makefile('rb', buffering=0)

    def readable(self):
        return True

    def readinto(self, buffer):
        self.sock.settimeout(remaining(self.deadline))
        return self.stream.readinto(buffer)

    def close(self):
        self.stream.close()
        super().close()


class DeadlineSocket:
    def __init__(self, sock, deadline):
        self.sock, self.deadline = sock, deadline

    def __getattr__(self, name):
        return getattr(self.sock, name)

    def makefile(self, mode):
        if mode != 'rb':
            raise ValueError('unsupported metadata socket mode')
        return io.BufferedReader(DeadlineReader(self.sock, self.deadline))

    def sendall(self, data):
        self.sock.settimeout(remaining(self.deadline))
        return self.sock.sendall(data)


class PinnedConnection:
    def __init__(self, *args, deadline, **kwargs):
        super().__init__(*args, **kwargs)
        self.deadline = deadline
        self._create_connection = lambda address, *a, **kw: connect_public(address, deadline)

    def connect(self):
        # HTTPSConnection still performs hostname verification/SNI using self.host.
        super().connect()
        self.sock = DeadlineSocket(self.sock, self.deadline)


class PublicHTTPConnection(PinnedConnection, http.client.HTTPConnection):
    pass


class PublicHTTPSConnection(PinnedConnection, http.client.HTTPSConnection):
    pass


class PublicHTTPHandler(HTTPHandler):
    def __init__(self, deadline):
        super().__init__()
        self.deadline = deadline

    def http_open(self, req):
        return self.do_open(lambda *a, **kw: PublicHTTPConnection(*a, deadline=self.deadline, **kw), req)


class PublicHTTPSHandler(HTTPSHandler):
    def __init__(self, deadline):
        super().__init__()
        self.deadline = deadline

    def https_open(self, req):
        return self.do_open(lambda *a, **kw: PublicHTTPSConnection(*a, deadline=self.deadline, **kw), req,
                            context=self._context)
