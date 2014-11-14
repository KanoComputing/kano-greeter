#!/usr/bin/env python

# user_list.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk
from gi.repository import LightDM

import os

from kano.logging import logger
from kano.gtk3.heading import Heading
from kano.gtk3.buttons import OrangeButton
from kano.gtk3.kano_dialog import KanoDialog


class UserList(Gtk.ScrolledWindow):
    HEIGHT = 250
    WIDTH = 250

    def __init__(self):
        Gtk.ScrolledWindow.__init__(self)

        self.set_size_request(self.WIDTH, self.HEIGHT)

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.box.set_spacing(10)
        self.add(self.box)

        title = Heading('Select Account', 'Log in to which account?')
        self.box.pack_start(title.container, False, False, 0)

        self._populate()

        add_account_btn = OrangeButton('Add Account')
        add_account_btn.connect('button-release-event', self.add_account)
        self.box.pack_start(add_account_btn, False, False, 0)

    def _populate(self):
        # Populate list
        user_list = LightDM.UserList()
        for user in user_list.get_users():
            logger.debug('adding user {}'.format(user.get_name()))
            self.add_item(user.get_name())

    def add_item(self, username):
        user = User(username)
        self.box.pack_start(user, False, False, 0)

    @staticmethod
    def add_account(*_):
        confirm = KanoDialog(
            title_text='Are you sure you want to create a new account?',
            description_text='A reboot will be required',
            button_dict={
                'CREATE': {'return_value': True},
                'CANCEL': {'return_value': False}
            })
        confirm.dialog.set_position(Gtk.WindowPosition.CENTER_ALWAYS)

        if confirm.run():
            os.system("sudo kano-init newuser")
            LightDM.restart()



class User(Gtk.EventBox):
    HEIGHT = 50

    def __init__(self, username):
        Gtk.EventBox.__init__(self)
        self.set_size_request(-1, self.HEIGHT)

        self.username = username

        self.get_style_context().add_class('user')

        label = Gtk.Label(username.title())
        self.add(label)

        self.connect('button-release-event', self._user_select_cb)
        self.connect('enter-notify-event', self._hover_cb)
        self.connect('leave-notify-event', self._unhover_cb)

    def _user_select_cb(self, button, event):
        logger.debug('user {} selected'.format(self.username))

        win = self.get_toplevel()
        win.go_to_password(self.username)

    def _hover_cb(self, widget, event):
        self.get_style_context().add_class('hover')

    def _unhover_cb(self, widget, event):
        self.get_style_context().remove_class('hover')
