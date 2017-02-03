#!/usr/bin/env python3
import i3ipc
import Xlib
import Xlib.display
from Xlib import X, XK
import subprocess

display = Xlib.display.Display()
i3ipc = i3ipc.Connection()

class i3:
	def __init__(self, cmd): self.cmd = cmd
	def __repr__(self): return "i3(%r)" % self.cmd
	def __call__(self): return i3ipc.command(self.cmd)

class run:
	def __init__(self, cmd): self.cmd = cmd
	def __repr__(self): return "run(%r)" % self.cmd
	def __call__(self): return subprocess.Popen(self.cmd, shell=True)

class mode:
	def __init__(self, id): self.id = id
	def __repr__(self): return "mode(%r)" % self.id
	def __call__(self): return grab_keys(self.id)

mods = {"c": X.ControlMask, "s": X.ShiftMask, "w": X.Mod4Mask, "a": X.Mod1Mask}
modmask = 0
for mod in mods:
	modmask |= mods[mod]

def parse_key(k):
	if k[0] == "<" and k[-1] == ">":
		return (0, 0)
	parts = k.split("-")
	modmask = 0
	for mod in parts[:-1]:
		if mod not in mods:
			raise Exception("Invalid mod '%s'" % mod)
		modmask |= mods[mod]
	keysym = XK.string_to_keysym(parts[-1])
	if keysym == 0:
		print("Invalid key '%s'" % parts[-1])
	return (keysym, modmask)

keymap = None
bound = {}
keys = {}
def grab_keys(*maps):
	global keys
	keys = {}
	def add(map):
		if "<extends>" in keymap[map]:
			add(keymap[map]["<extends>"])
		for k, f in keymap[map].items():
			keys[parse_key(k)] = f
	for map in maps:
		add(map)

	rebind()
	display.sync()

def rebind():
	global bound
	root = display.screen().root
	for key in bound.keys():
		root.ungrab_key(key[0], key[1])

	bound = {}
	for (code, mask), func in keys.items():
		code = display.keysym_to_keycode(code)
		if (code, mask) == (0, 0):
			continue
		bound[code, mask] = func
		bound[code, mask | X.Mod2Mask] = func
		bound[code, mask | X.LockMask] = func
		bound[code, mask | X.Mod2Mask | X.LockMask] = func

	for key in bound.keys():
		root.grab_key(key[0], key[1], 1, X.GrabModeAsync, X.GrabModeAsync)

def start(keys):
	global keymap, root

	import Xlib.keysymdef
	for group in Xlib.keysymdef.__all__:
		XK.load_keysym_group(group)

	global keymap
	keymap = keys
	grab_keys(None)

	while True:
		evt = display.next_event()
		if evt.type == X.KeyPress:
			print(type(evt), evt.detail, hex(evt.state), flush=True)
			k = evt.detail, evt.state & modmask
			print(k, bound.get(k, None), flush=True)
			if k in bound:
				bound[k]()
		if evt.type == X.MappingNotify and evt.request == X.MappingKeyboard:
			print(evt, flush=True)
			display.refresh_keyboard_mapping(evt)
			rebind()

def backlight(mode):
	states = [0, 1, 2, 3, 5, 10, 20, 33, 50, 75, 100]
	def closest(list, n):
		aux = []
		for v in list:
			aux.append(abs(n - v))
		return aux.index(min(aux))

	def f():
		n = float(subprocess.check_output("xbacklight"))
		idx = closest(states, n) + mode
		if 0 <= idx < len(states):
			run("xbacklight -set %d -time 0" % states[idx])()
	return f

keys = {
	None: {
		"XF86_MonBrightnessUp":   backlight(+1),
		"XF86_MonBrightnessDown": backlight(-1),
		"XF86_AudioMute":         run("pactl set-sink-mute @DEFAULT_SINK@ toggle"),
		"XF86_AudioRaiseVolume":  run("pactl set-sink-volume @DEFAULT_SINK@ +5%"),
		"XF86_AudioLowerVolume":  run("pactl set-sink-volume @DEFAULT_SINK@ -5%"),

		"w-Print":   run("scrot    '%Y-%m-%d_%H-%M-%S.png' -e 'mv $f ~/Screenshots'"),
		"w-a-Print": run("scrot -u '%Y-%m-%d_%H-%M-%S.png' -e 'mv $f ~/Screenshots'"),

		"w-Return": i3("exec --no-startup-id x-terminal-emulator"),
		"w-d": i3("exec --no-startup-id dmenu_run"),
		"Caps_Lock": i3("exec --no-startup-id compose ~/dot/htmlent.txt"),

		"w-c": i3("reload"),
		"w-z": i3("restart"),
		"c-a-BackSpace": i3("exit"),

		"w-x": i3("kill"),
		"w-s-x": i3("focus parent;" * 10 + "kill"),

		"w-f": i3("fullscreen"),
		"w-a": i3("focus parent"),
		"w-s-a": i3("focus child"),
		"w-space": i3("focus mode_toggle"),
		"w-s-space": i3("floating toggle"),

		"w-1": i3("workspace 1"),
		"w-2": i3("workspace 2"),
		"w-3": i3("workspace 3"),
		"w-4": i3("workspace 4"),
		"w-5": i3("workspace 5"),
		"w-6": i3("workspace 6"),
		"w-7": i3("workspace 7"),
		"w-8": i3("workspace 8"),
		"w-9": i3("workspace 9"),
		"w-0": i3("workspace 10"),

		"w-s-1": i3("move container to workspace 1; workspace 1"),
		"w-s-2": i3("move container to workspace 2; workspace 2"),
		"w-s-3": i3("move container to workspace 3; workspace 3"),
		"w-s-4": i3("move container to workspace 4; workspace 4"),
		"w-s-5": i3("move container to workspace 5; workspace 5"),
		"w-s-6": i3("move container to workspace 6; workspace 6"),
		"w-s-7": i3("move container to workspace 7; workspace 7"),
		"w-s-8": i3("move container to workspace 8; workspace 8"),
		"w-s-9": i3("move container to workspace 9; workspace 9"),
		"w-s-0": i3("move container to workspace 10; workspace 10"),

		"w-h": i3("focus left"),
		"w-j": i3("focus down"),
		"w-k": i3("focus up"),
		"w-l": i3("focus right"),

		"w-s-h": i3("move left"),
		"w-s-j": i3("move down"),
		"w-s-k": i3("move up"),
		"w-s-l": i3("move right"),

		"w-r": mode("resize"),
	},
	"resize": {
		"<name>": "Resize",
		"<extends>": None,

		"h": i3("resize shrink width  10 px"),
		"j": i3("resize grow   height 10 px"),
		"k": i3("resize shrink height 10 px"),
		"l": i3("resize grow   width  10 px"),

		"s-h": i3("resize shrink width  1 px"),
		"s-j": i3("resize grow   height 1 px"),
		"s-k": i3("resize shrink height 1 px"),
		"s-l": i3("resize grow   width  1 px"),

		"Escape": mode(None)
	}
}

start(keys)
