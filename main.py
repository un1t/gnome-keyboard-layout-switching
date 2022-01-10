from Xlib.display import Display
from Xlib import X
from Xlib.ext import record
from Xlib.protocol import rq
from pydbus import SessionBus


class Keys:
    alt_l = 64
    alt_r = 108
    shift_l = 50
    shift_r = 62


display = Display()  # get current display
bus = SessionBus()
pressed = set()


def switch_to(index):
    remote_object = bus.get('org.gnome.Shell', '/org/gnome/Shell')
    remote_object.Eval(f"imports.ui.status.keyboard.getInputSourceManager().inputSources[{index}].activate()")


def get_current_index():
    remote_object = bus.get('org.gnome.Shell', '/org/gnome/Shell')
    result = remote_object.Eval("imports.ui.status.keyboard.getInputSourceManager().currentSource.index")
    return int(result[1])


def func1():
    index = get_current_index()
    if index == 0:
        switch_to(1)
    else:
        switch_to(0)


def func2():
    index = get_current_index()
    if index == 2:
        switch_to(3)
    else:
        switch_to(2)


bindings = {
    frozenset([Keys.alt_l, Keys.shift_l]): func1,
    frozenset([Keys.alt_r, Keys.shift_r]): func2
}


def handler(reply):
    """This function is called when a xlib event is fired"""
    data = reply.data
    while len(data):
        event, data = rq.EventField(None).parse_binary_value(
            data, display.display, None, None
        )

        if event.type == X.KeyPress:
            pressed.add(event.detail)

            for hotkey, func in bindings.items():
                if pressed == hotkey:
                    func()

        elif event.type == X.KeyRelease:
            if event.detail in pressed:
                pressed.remove(event.detail)


# Monitor keypress and button press
ctx = display.record_create_context(
    0,
    [record.AllClients],
    [
        {
            "core_requests": (0, 0),
            "core_replies": (0, 0),
            "ext_requests": (0, 0, 0, 0),
            "ext_replies": (0, 0, 0, 0),
            "delivered_events": (0, 0),
            "device_events": (X.KeyReleaseMask, X.ButtonReleaseMask),
            "errors": (0, 0),
            "client_started": False,
            "client_died": False,
        }
    ],
)
display.record_enable_context(ctx, handler)
display.record_free_context(ctx)

while 1:
    # Infinite wait, doesn't do anything as no events are grabbed
    event = display.screen().root.display.next_event()
