import json
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


def gnome_shell_eval(code):
    remote_object = bus.get("org.gnome.Shell", "/org/gnome/Shell")
    result = remote_object.Eval(code)
    if result[1] != "":
        return json.loads(result[1])


def get_input_sources():
    return gnome_shell_eval(
        f"imports.ui.status.keyboard.getInputSourceManager().inputSources"
    )


def activate_input_source(index):
    gnome_shell_eval(
        f"imports.ui.status.keyboard.getInputSourceManager().inputSources[{index}].activate()"
    )


def get_current_input_source_index():
    return gnome_shell_eval(
        "imports.ui.status.keyboard.getInputSourceManager().currentSource.index"
    )


def activate_next_input_source(indexes):
    index = get_current_input_source_index()
    try:
        pos = indexes.index(index)
        next_index = indexes[pos + 1]
    except (ValueError, IndexError):
        next_index = indexes[0]
    activate_input_source(next_index)


def func1():
    activate_next_input_source(main_indexes)


def func2():
    activate_next_input_source(other_indexes)


bindings = {
    frozenset([Keys.alt_l, Keys.shift_l]): func1,
    frozenset([Keys.alt_r, Keys.shift_r]): func2,
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


display = Display()  # get current display
bus = SessionBus()
pressed = set()
main_langs = ["en", "ru"] # TODO: command line arguments
main_indexes = []
other_indexes = []


input_sources = get_input_sources()
for val in input_sources.values():
    lang = val["_shortName"]
    index = val["index"]
    if lang in main_langs:
        main_indexes.append(index)
    else:
        other_indexes.append(index)

    main_indexes.sort()
    other_indexes.sort()


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
