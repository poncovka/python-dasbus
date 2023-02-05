#
# Watch a DBus signal.
#
from dasbus.connection import SessionMessageBus
from dasbus.loop import EventLoop


def callback(msg):
    print("Received a signal with: {}".format(msg))


bus = SessionMessageBus()
proxy = bus.get_proxy(
    "org.example.Chat",
    "/org/example/Chat/Rooms/3"
)
proxy.MessageReceived.connect(
    callback
)

print("Listening...")
loop = EventLoop()
loop.run()
