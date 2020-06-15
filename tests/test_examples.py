#
# Copyright (C) 2019  Red Hat, Inc.  All rights reserved.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301
# USA
#
import os
import subprocess
import unittest
import socket

from abc import abstractmethod, ABCMeta
from textwrap import dedent
from time import sleep

from dasbus.connection import SystemMessageBus, SessionMessageBus

import gi
gi.require_version("Gio", "2.0")
from gi.repository import Gio


class ExamplesMixin(object, metaclass=ABCMeta):

    TIMEOUT = 3

    @property
    def _environment(self):
        return os.environ.copy()

    def _start_example(self, name):
        process = subprocess.Popen(
            ["python3", "-m", name],
            universal_newlines=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=self._environment,
        )
        return process

    def _stop_example(self, process):
        process.kill()
        outs, errs = process.communicate()
        outs = outs.strip()
        self.assertEqual(errs, "", msg=outs)
        return outs

    def _run_client(self, name):
        process = self._start_example(name)

        try:
            outs, errs = process.communicate(timeout=self.TIMEOUT)
        except subprocess.TimeoutExpired:
            process.kill()
            outs, errs = process.communicate()

        outs = outs.strip()
        errs = errs.strip()

        self.assertEqual(errs, "", msg=outs)
        self.assertEqual(process.returncode, 0, msg=outs)
        return outs

    def _check_output(self, output, expected):
        self.assertEqual(output.strip(), dedent(expected).strip())

    @abstractmethod
    def assertEqual(self, first, second, msg=None):
        pass


class SystemExamplesTestCase(unittest.TestCase, ExamplesMixin):
    """Test examples for the system bus."""

    def setUp(self):
        self._check_system_bus()

    def _check_system_bus(self):
        """Check the system bus connection."""
        bus = SystemMessageBus()

        if not bus.check_connection():
            self.skipTest("The system bus is not available.")

    def test_hostname(self):
        """Test the hostname example."""
        hostname = self._run_client(
            "examples.hostname.client"
        )
        self.assertEqual(hostname, socket.gethostname())


class SessionExamplesTestCase(unittest.TestCase, ExamplesMixin):
    """Test examples for the session bus."""

    def setUp(self):
        self._check_session_bus()

    def _check_session_bus(self):
        """Check the session bus connection."""
        bus = SessionMessageBus()

        if not bus.check_connection():
            self.skipTest("The session bus is not available.")

    def test_notification(self):
        """Test the notification example."""
        listener = self._start_example(
            "examples.notification.listener"
        )

        output = self._run_client(
            "examples.notification.client"
        )

        self._stop_example(listener)
        self.assertTrue(output)


class ExamplesTestCase(unittest.TestCase, ExamplesMixin):
    """Test examples for dasbus."""

    def setUp(self):
        self.maxDiff = None
        self._bus = Gio.TestDBus()
        self._bus.up()

    def tearDown(self):
        self._bus.down()

    @property
    def _environment(self):
        environment = super()._environment
        address = self._bus.get_bus_address()

        environment.update({
            "DBUS_SESSION_BUS_ADDRESS": address
        })

        return environment

    def test_hello_world(self):
        """Test the hello world example."""
        server = self._start_example(
            "examples.hello_world.server"
        )

        sleep(1)

        client_output = self._run_client(
            "examples.hello_world.client"
        )

        server_output = self._stop_example(server)

        self._check_output(client_output, "Hello World!")
        self._check_output(server_output, """
        """)

    def test_register(self):
        """Test the register example."""
        server = self._start_example(
            "examples.register.server"
        )

        sleep(1)

        listener = self._start_example(
            "examples.register.listener"
        )

        sleep(1)

        client_output = self._run_client(
            "examples.register.client"
        )

        listener_output = self._stop_example(listener)
        server_output = self._stop_example(server)

        self._check_output(client_output, """
        Sending a DBus structure:
        {'age': GLib.Variant('i', 1000), 'name': GLib.Variant('s', 'Alice')}
        Receiving DBus structures:
        {'age': GLib.Variant('i', 1000), 'name': GLib.Variant('s', 'Alice')}
        Registered users:
        Alice
        """)

        self._check_output(listener_output, """
        Bob's room: /org/example/Chat/Rooms/1
        Alice's room: /org/example/Chat/Rooms/2
        """)

        self._check_output(server_output, """
        """)

    def test_chat(self):
        """Test the chat example."""
        server = self._start_example(
            "examples.chat.server"
        )

        sleep(1)

        listener = self._start_example(
            "examples.chat.listener"
        )

        sleep(1)

        client_output = self._run_client(
            "examples.chat.client"
        )

        listener_output = self._stop_example(listener)
        server_output = self._stop_example(server)

        self.assertEqual(client_output, dedent("""
        Bob's room: /org/example/Chat/Rooms/1
        Alice's room: /org/example/Chat/Rooms/2
        """.strip()))

        self._check_output(listener_output, """
        """)

        self._check_output(server_output, """
        """)