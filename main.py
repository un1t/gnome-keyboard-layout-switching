import argparse
import json
import sys
import re
from typing import OrderedDict
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
    result = gnome_shell_eval(
        f"imports.ui.status.keyboard.getInputSourceManager().inputSources"
    )
    input_sources = sorted(result.values(), key=lambda v: v["index"])
    return OrderedDict(
        [
            (input_source["_shortName"], input_source["index"])
            for input_source in input_sources
        ]
    )


def get_splitted_indexes():
    primary = []
    secondary = []
    for lang, index in get_input_sources().items():
        if lang in primary_langs:
            primary.append(index)
        else:
            secondary.append(index)
    return primary, secondary


def activate_input_source(index):
    gnome_shell_eval(
        f"imports.ui.status.keyboard.getInputSourceManager().inputSources[{index}].activate()"
    )


def get_current_input_source_index():
    return gnome_shell_eval(
        "imports.ui.status.keyboard.getInputSourceManager().currentSource.index"
    )


def get_next_input_source_index(index, indexes):
    try:
        pos = indexes.index(index)
        return indexes[pos + 1]
    except (ValueError, IndexError):
        return indexes[0]


def activate_next_primary_input_source():
    primary_indexes = get_splitted_indexes()[0]

    if state.current_index in primary_indexes:
        next_index = get_next_input_source_index(state.current_index, primary_indexes)
    else:
        next_index = state.primary_index

    activate_input_source(next_index)
    state.current_index = next_index
    state.primary_index = next_index


def activate_next_secondary_input_source():
    secondary_indexes = get_splitted_indexes()[1]

    if state.current_index in secondary_indexes:
        next_index = get_next_input_source_index(state.current_index, secondary_indexes)
    else:
        next_index = state.secondary_index

    activate_input_source(next_index)
    state.current_index = next_index
    state.secondary_index = next_index


bindings = {
    frozenset([Keys.alt_l, Keys.shift_l]): activate_next_primary_input_source,
    frozenset([Keys.alt_r, Keys.shift_r]): activate_next_secondary_input_source,
}


def handler(reply):
    """This function is called when a xlib event is fired"""
    data = reply.data
    while len(data):
        event, data = rq.EventField(None).parse_binary_value(
            data, display.display, None, None
        )

        if event.type == X.KeyPress:
            state.pressed.add(event.detail)

            for hotkey, func in bindings.items():
                if state.pressed == hotkey:
                    func()

        elif event.type == X.KeyRelease:
            if event.detail in state.pressed:
                state.pressed.remove(event.detail)


class state:
    pressed = set()
    current_index = 0
    primary_index = 0
    secondary_index = 0


display = Display()  # get current display
bus = SessionBus()
primary_langs = []


def init():
    global primary_langs

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        "--primary",
        metavar="LANGUAGES",
        type=str,
        help='Comma-separated primary languages, e.g. "en,ru" ',
    )
    args = parser.parse_args(sys.argv[1:])
    if args.primary:
        primary_langs = re.split("\s*,\s*", args.primary)
        unexisted_langs = set(primary_langs) - set(get_input_sources().keys())
        if unexisted_langs:
            print(
                "Error. Input sources for the following laguages are not exists: {}.".format(
                    ", ".join(unexisted_langs)
                ),
                file=sys.stderr,
            )
            sys.exit(1)
        print(
            f"Provided languages ({str(primary_langs).strip('[]')}) are used as primary."
        )
    else:
        primary_langs = list(get_input_sources().keys())[:2]
        print(
            f"First 2 languages ({str(primary_langs).strip('[]')}) are used as primary."
        )

    state.current_index = get_current_input_source_index()
    primary_indexes, secondry_indexes = get_splitted_indexes()
    state.primary_index = primary_indexes[0]
    state.secondary_index = secondry_indexes[0]

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


if __name__ == "__main__":
    init()
    while 1:
        # Infinite wait, doesn't do anything as no events are grabbed
        event = display.screen().root.display.next_event()
