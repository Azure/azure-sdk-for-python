#!/usr/bin/env python

"""
An example to show receiving events from an Event Hub partition.
"""

import threading
from proton.reactor import Container, ApplicationEvent
from eventhubs._win import EventInjector

class Program:
    def __init__(self, injector):
        self.injector = injector

    def on_reactor_init(self, event):
        event.reactor.selectable(self.injector)

    def on_hello(self, event):
        print(event.subject)

    def on_done(self, event):
        event.subject.stop()

e = EventInjector()
r = Container(Program(e))
t = threading.Thread(target=r.run)
t.start()

for i in range(1, 1000):
    e.trigger(ApplicationEvent("hello", subject=str(i)))

e.trigger(ApplicationEvent("done", subject=r))

t.join()
