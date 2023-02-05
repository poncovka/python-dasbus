#
# Use a DBus property.
#
from dasbus.connection import SessionMessageBus

bus = SessionMessageBus()
proxy = bus.get_proxy(
    "org.example.Chat",
    "/org/example/Chat/Rooms/3"
)
print(proxy.Name)
