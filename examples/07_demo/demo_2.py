#
# Call a DBus method.
#
from dasbus.connection import SessionMessageBus

bus = SessionMessageBus()
proxy = bus.get_proxy(
    "org.example.Chat",
    "/org/example/Chat/Rooms/3"
)
proxy.SendMessage("Hello World!")
