"""Regression tests for bounded DNS, pinned connections and normal TLS identity."""
from io import BytesIO
import socket
import ssl
import threading
import time
import unittest
from unittest.mock import Mock, patch

from preview_images import enrich_images, fetch_metadata
from public_metadata_http import (DeadlineReader, PublicHTTPSConnection,
                                  connect_public, resolve_public)
from test_preview_images import ITEM


PUBLIC = [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('93.184.216.34', 443))]
PRIVATE = [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('127.0.0.1', 443))]


class TransportTests(unittest.TestCase):
    @patch('public_metadata_http.socket.socket')
    @patch('public_metadata_http.socket.getaddrinfo', side_effect=[PUBLIC, PRIVATE])
    def test_dns_change_cannot_change_actual_connected_address(self, dns, factory):
        sock = factory.return_value
        self.assertIs(connect_public(('publisher.example', 443), time.monotonic() + 1), sock)
        dns.assert_called_once_with('publisher.example', 443, type=socket.SOCK_STREAM)
        sock.connect.assert_called_once_with(('93.184.216.34', 443))
        # If the connector had re-resolved the hostname it would have received PRIVATE.

    @patch('public_metadata_http.socket.socket')
    @patch('public_metadata_http.socket.getaddrinfo', return_value=PRIVATE)
    def test_private_result_cannot_open_any_socket(self, dns, factory):
        with self.assertRaises(ValueError):
            connect_public(('publisher.example', 443), time.monotonic() + 1)
        factory.assert_not_called()

    @patch('public_metadata_http.connect_public')
    def test_pinned_https_keeps_original_tls_hostname_and_default_verification(self, connect):
        connection = PublicHTTPSConnection('publisher.example', deadline=time.monotonic() + 1)
        self.assertTrue(connection._context.check_hostname)
        self.assertEqual(connection._context.verify_mode, ssl.CERT_REQUIRED)
        # Observe the actual HTTPSConnection TLS wrap call without opening a socket.
        context = Mock()
        connection._context = context
        connection.connect()
        context.wrap_socket.assert_called_once_with(connect.return_value, server_hostname='publisher.example')

    def test_stalled_dns_does_not_block_successful_news_enrichment(self):
        release = threading.Event()
        def stalled(*a, **kw):
            release.wait(5)
            return PUBLIC
        started = time.monotonic()
        try:
            with patch('public_metadata_http.socket.getaddrinfo', side_effect=stalled):
                items, counts = enrich_images([ITEM], lookup=lambda url, deadline: fetch_metadata(url, deadline)[0], budget=.03)
            self.assertEqual(items, [ITEM])
            self.assertEqual(counts['unavailable'], 1)
            self.assertLess(time.monotonic() - started, 1)
        finally:
            release.set()

    def test_expired_deadline_does_not_start_dns(self):
        with patch('public_metadata_http.socket.getaddrinfo') as dns:
            with self.assertRaises(TimeoutError):
                resolve_public('publisher.example', 443, time.monotonic() - 1)
            dns.assert_not_called()

    def test_absolute_deadline_also_bounds_header_and_body_reads(self):
        sock = Mock()
        sock.makefile.return_value = BytesIO(b'header-body')
        reader = DeadlineReader(sock, 10)
        with patch('public_metadata_http.time.monotonic', side_effect=[9, 11]):
            self.assertEqual(reader.readinto(bytearray(6)), 6)
            with self.assertRaises(TimeoutError):
                reader.readinto(bytearray(1))
        sock.settimeout.assert_called_once_with(1)
        reader.close()


if __name__ == '__main__':
    unittest.main()
