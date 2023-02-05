#
# Run a DBus service.
#
from dasbus.connection import SessionMessageBus
from dasbus.loop import EventLoop
from dasbus.server.interface import dbus_interface, dbus_signal
from dasbus.signal import Signal
from dasbus.typing import Str
from dasbus.xml import XMLGenerator


@dbus_interface("org.example.Chat.Room")
class Room(object):
    """The chat room."""

    def __init__(self, name):
        self._name = name
        self._message_received = Signal()

    @property
    def Name(self) -> Str:
        """The name of the chat room."""
        return self._name

    @dbus_signal
    def MessageReceived(self, msg: Str):
        """Signal that a message has been received."""
        pass

    def SendMessage(self, msg: Str):
        """Send a message to the chat room."""
        print("Room {}: {}".format(self._name, msg))
        self.MessageReceived.emit(msg)


@dbus_interface("org.example.Chat")
class Chat(object):
    """The chat service."""


if __name__ == "__main__":
    # Print the generated XML specifications.
    print("Generated interfaces:\n\n{}\n\n{}\n".format(
        XMLGenerator.prettify_xml(Chat.__dbus_xml__),
        XMLGenerator.prettify_xml(Room.__dbus_xml__)
    ))

    # Connect to the session bus.
    bus = SessionMessageBus()

    try:
        # Register the service name.
        bus.register_service("org.example.Chat")

        # Publish objects of this service.
        bus.publish_object("/org/example/Chat", Chat())
        bus.publish_object("/org/example/Chat/Rooms/1", Room("1"))
        bus.publish_object("/org/example/Chat/Rooms/2", Room("2"))
        bus.publish_object("/org/example/Chat/Rooms/3", Room("3"))

        # Start the event loop.
        print("Running...")
        loop = EventLoop()
        loop.run()
    finally:
        # Unregister the service and objects.
        bus.disconnect()
