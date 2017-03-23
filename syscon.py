#!/usr/bin/python
import threading
import subprocess
import os
# import time
from time import sleep
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Gio
from gi.repository import GLib
from gi.repository import GObject
# This allows Ctrl+C to exit the program
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

# -------VARS

G_MARGIN = 2
G_SCROLLFLAG = 1
BaseDir = os.environ['HOME'] + "/.icons"
# --------------------------------------------------------


def read_async(monitor, file, o, event):
    # Without this check, multiple 'ok's will be printed for each file change
    # CHANGES_DONE_HINT = 1
    # CHANGED = 0
    if event == Gio.FileMonitorEvent.CHANGES_DONE_HINT:
        print ('ok')


def launchlog():
    global sysview

    cmd = "/bin/journalctl -f "
    popen = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        # yield stdout_line
        # print stdout_line
        textbuffer = sysview.get_buffer()
        sstart, send = textbuffer.get_bounds()
        # print "insert...."
        textbuffer.insert(send, stdout_line, len(stdout_line))

        if G_SCROLLFLAG == 1:
            sstart, send = textbuffer.get_bounds()
            print "in if after get_bounds...."
            mark = textbuffer.create_mark(None, send, True)
            sysview.scroll_to_mark(mark, 0.0, 0, 0.0, 1.0)
            textbuffer.delete_mark(mark)

        # time.sleep(1)
        sleep(0.10)

    popen.stdout.close()
    print "antes del wait...."
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)


def cbk_quit(w, s):
    Gtk.main_quit()


def on_holdbutton_toggled(widget):
    global G_SCROLLFLAG
    global sysview

    if widget.get_active():
        G_SCROLLFLAG = 0
    else:
        G_SCROLLFLAG = 1
        textbuffer = sysview.get_buffer()
        sstart, send = textbuffer.get_bounds()
        mark = textbuffer.create_mark(None, send, True)
        sysview.scroll_to_mark(mark, 0.0, 0, 0.0, 1.0)
        textbuffer.delete_mark(mark)

# --------------------------------------------------------


GObject.threads_init()
GLib.threads_init()
Gdk.threads_init()

# sysconfile = open(SHADOWLOG, "w")

win = Gtk.Window()
win.set_icon_from_file(BaseDir + "/console.png")
win.set_default_size(800, 400)
win.set_border_width(0)
# win.set_position(Gtk.WindowPosition.CENTER)
# screen = win.get_screen()
# win.set_app_paintable(True)
# visual = screen.get_rgba_visual()
# win.set_visual(visual)

# win.set_decorated(False)
win.connect("delete-event", cbk_quit)
# win.connect("draw", area_draw)

# Window content Header bar
hb = Gtk.HeaderBar()
hb.set_show_close_button(True)
hb.props.title = "Syscon"
win.set_titlebar(hb)

button = Gtk.ToggleButton()
button.connect("toggled", on_holdbutton_toggled)
icon = Gio.ThemedIcon(name="go-up-symbolic")
image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
button.add(image)
hb.pack_end(button)

vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
scroll = Gtk.ScrolledWindow()
scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
sysview = Gtk.TextView()
sysview.set_wrap_mode(True)
sysview.set_border_window_size(Gtk.TextWindowType.LEFT, G_MARGIN)
sysview.set_border_window_size(Gtk.TextWindowType.RIGHT, G_MARGIN)
sysview.set_border_window_size(Gtk.TextWindowType.TOP, G_MARGIN)
sysview.set_border_window_size(Gtk.TextWindowType.BOTTOM, G_MARGIN)
sysview.get_style_context().add_class("colorize")

sysview.editable = False
sysview.cursor_visible = False
sysview.wrap_mode = Gtk.WrapMode.WORD

# ------------------------
style_provider = Gtk.CssProvider()
# css = open('/path/to/your/style.css', 'rb')  # rb needed for python 3 support
# css_data = css.read()
# css.close()
css_data = b"""
GtkWindow { background-color: rgba(7, 54, 66, 0.7); }
.colorize { font: 10px; font-family: "Ubuntu Mono"; background-color: rgba(7, 54, 66, 0.7); color: #859900}
"""
style_provider.load_from_data(css_data)
Gtk.StyleContext.add_provider_for_screen(
    Gdk.Screen.get_default(), style_provider,
    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
)
# ------------------------
win.add(vbox)
scroll.add(sysview)
vbox.pack_start(scroll, True, True, 0)

textbuffer = sysview.get_buffer()
textbuffer.set_text("beggining log...")

# sstart = textbuffer.get_start_iter()
# send = textbuffer.get_end_iter()

# ------------------------------

d = threading.Thread(target=launchlog, name='Daemon')
# d.setDaemon(True)
d.start()

# gio_file = Gio.File.new_for_path(SHADOWLOG)
# monitor = gio_file.monitor_file(Gio.FileMonitorFlags.NONE, None)
# monitor.connect("changed", read_async)

win.show_all()
Gtk.main()
