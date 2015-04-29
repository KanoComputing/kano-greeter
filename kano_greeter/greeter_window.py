#!/usr/bin/env python

# greeter-window.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import LightDM

from kano.logging import logger
from kano.gtk3.apply_styles import apply_common_to_screen
from kano.gtk3.top_bar import TopBar
from kano.gtk3.application_window import ApplicationWindow
from kano.gtk3.kano_dialog import KanoDialog
from kano.gtk3.buttons import OrangeButton

from kano_greeter.user_list import UserList
from kano_greeter.password_view import PasswordView
from kano_greeter.newuser_view import NewUserView


class GreeterWindow(ApplicationWindow):
    WIDTH = 400
    HEIGHT = -1

    greeter = LightDM.Greeter

    def __init__(self):
        apply_common_to_screen()

        ApplicationWindow.__init__(self, _('Login'), self.WIDTH, self.HEIGHT)
        self.connect("delete-event", Gtk.main_quit)

        # Create a new LightDM.Greeter instance which will be used by the 2 views
        self.greeter = GreeterWindow.greeter.new()

        # Create the two views: one for normal Login, the other to create a new account
        self.password_view = PasswordView('', self.greeter)
        self.newuser_view = NewUserView(self.greeter)

        self.grid = Gtk.Grid()
        self.set_main_widget(self.grid)

        self.grid.set_column_spacing(30)
        self.grid.set_row_spacing(30)

        self.top_bar = TopBar(_('Login'))
        self._remove_top_bar_buttons()
        self.top_bar.set_size_request(self.WIDTH, -1)
        self.grid.attach(self.top_bar, 0, 0, 3, 1)

        self.shutdown_btn = OrangeButton(_('Shutdown'))
        self.shutdown_btn.connect('clicked', self.shutdown)
        align = Gtk.Alignment(xalign=1.0,
                              xscale=0.0)
        align.add(self.shutdown_btn)
        self.grid.attach(align, 1, 2, 1, 1)

        self.grid.attach(Gtk.Label(), 0, 3, 3, 1)

        self.top_bar.set_prev_callback(self._back_cb)

        self.user_list = UserList()

        self.go_to_users()

        cursor = Gdk.Cursor.new(Gdk.CursorType.ARROW)
        self.get_root_window().set_cursor(cursor)

    def _remove_top_bar_buttons(self):
        self.top_bar.box.remove(self.top_bar.close_button)
        self.top_bar.box.remove(self.top_bar.next_button)

    def set_main(self, wdg):
        child = self.grid.get_child_at(1, 1)
        if child:
            self.grid.remove(child)

        self.grid.attach(wdg, 1, 1, 1, 1)
        self.show_all()

    def go_to_users(self):
        self.set_main(self.user_list)
        self.top_bar.disable_prev()

    def go_to_password(self, user):
        # Called when we switch between views using top-left arrow button
        self.set_main(self.password_view)
        self.top_bar.enable_prev()
        self.password_view.grab_focus(user)

    def go_to_newuser(self):
        # Called when we switch between views using top-left arrow button
        self.set_main(self.newuser_view)
        self.top_bar.enable_prev()
        self.newuser_view.grab_focus()

    def _back_cb(self, event, button):
        self.go_to_users()

    @staticmethod
    def shutdown(*args):
        confirm = KanoDialog(title_text = _('Are you sure you want to shut down?'),
                             button_dict= [
                                {
                                    'label': _('Cancel').upper(),
                                    'color': 'red',
                                    'return_value': False
                                },
                                {
                                    'label': _('OK').upper(),
                                    'color': 'green',
                                    'return_value': True
                                }
                             ])
        confirm.dialog.set_position(Gtk.WindowPosition.CENTER_ALWAYS)

        if confirm.run():
            LightDM.shutdown()
