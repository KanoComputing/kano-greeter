#!/usr/bin/env python

# user_list.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk

import os
import pwd

from kano.logging import logger
from kano.gtk3.scrolled_window import ScrolledWindow
from kano.gtk3.heading import Heading
from kano.gtk3.buttons import OrangeButton, KanoButton
from kano.gtk3.kano_dialog import KanoDialog

from kano_greeter.last_user import get_last_user

class KanoUserList:
    def __init__(self):
        # Alternative to LightDM.UsersList due to signals
        # causing a segmentation fault in the application
        pass

    def get_users(self, minimum_id=1000):
        '''
        Returns a list of interactive users on the system
        as reported by Unix /etc/password database
        '''
        interactive_users=[]
        system_users=pwd.getpwall()

        # special usernames to exlude from the list
        exclude=('nobody')

        for user in system_users:
            if user.pw_uid >= minimum_id and user.pw_name not in exclude:
                # This is an interactive user created by Kano
                interactive_users.append(user.pw_name)

        return interactive_users


class UserList(ScrolledWindow):
    HEIGHT = 300
    WIDTH = 250

    def __init__(self):
        ScrolledWindow.__init__(self)

        self.apply_styling_to_widget()

        self.set_size_request(self.WIDTH, self.HEIGHT)

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.box.set_spacing(10)
        self.add(self.box)

        title = Heading(_('Select Account'), _('Log in to which account?'))
        self.box.pack_start(title.container, False, False, 0)

        self.last_username = get_last_user()

        self._populate()

        add_account_btn = OrangeButton(_('Add Account'))
        add_account_btn.connect('clicked', self.add_account)
        self.box.pack_start(add_account_btn, False, False, 0)

    def _populate(self):
        # Populate list
        user_list = KanoUserList()
        for user_name in user_list.get_users():
            logger.debug('adding user {}'.format(user_name))
            self.add_item(user_name)

    def add_item(self, username):
        user = User(username)
        self.box.pack_start(user, False, False, 0)
        if username == self.last_username:
            user.grab_focus()

    def add_account(self, control):
        logger.debug('opening new user dialog')
        win = self.get_toplevel()
        win.go_to_newuser()


class User(KanoButton):
    HEIGHT = 50

    def __init__(self, username):
        KanoButton.__init__(self, text=username.title(), color='orange')
        self.set_size_request(-1, self.HEIGHT)

        self.username = username
        self.connect('clicked', self._user_select_cb)

    def _user_select_cb(self, button):
        logger.debug('user {} selected'.format(self.username))
        win = self.get_toplevel()
        win.go_to_password(self.username)
