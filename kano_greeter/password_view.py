#!/usr/bin/env python

# password_view.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk
from gi.repository import LightDM

import os

from kano.logging import logger
from kano.gtk3.buttons import KanoButton, OrangeButton
from kano.gtk3.heading import Heading
from kano.gtk3.kano_dialog import KanoDialog

from kano_greeter.last_user import set_last_user

class PasswordView(Gtk.Grid):
    greeter = LightDM.Greeter()

    def __init__(self, user):
        Gtk.Grid.__init__(self)

        self.get_style_context().add_class('password')
        self.set_row_spacing(10)

        self._reset_greeter()

        self.user = user
        title = Heading('Enter your password',
                        'If you haven\'t changed your password,\n'
                        'use "kano"')
        self.attach(title.container, 0, 0, 1, 1)
        self.password = Gtk.Entry()
        self.password.set_visibility(False)
        self.password.set_alignment(0.5)
        self.password.connect('activate', self._login_cb)
        self.attach(self.password, 0, 1, 1, 1)

        self.login_btn = KanoButton('LOGIN')
        self.login_btn.connect('clicked', self._login_cb)
        self.attach(self.login_btn, 0, 2, 1, 1)

        delete_account_btn = OrangeButton('Remove Account')
        delete_account_btn.connect('clicked', self.delete_user)
        self.attach(delete_account_btn, 0, 3, 1, 1)

    def _reset_greeter(self):
        PasswordView.greeter = PasswordView.greeter.new()
        PasswordView.greeter.connect_sync()

        # connect signal handlers to LightDM
        PasswordView.greeter.connect('show-prompt', self._send_password_cb)
        PasswordView.greeter.connect('authentication-complete',
                                     self._authentication_complete_cb)
        PasswordView.greeter.connect('show-message', self._auth_error_cb)

    def _login_cb(self, event=None, button=None):
        logger.debug('Sending username to LightDM')

        self.login_btn.start_spinner()
        PasswordView.greeter.authenticate(self.user)

        if PasswordView.greeter.get_is_authenticated():
            logger.debug('User is already authenticated, starting session')
            start_session()

    def _send_password_cb(self, _greeter, text, prompt_type):
        logger.debug('Need to show prompt: {}'.format(text))
        if _greeter.get_in_authentication():
            logger.debug('Sending password to LightDM')
            _greeter.respond(self.password.get_text())

    def _authentication_complete_cb(self, _greeter):
        logger.debug('Authentication process is complete')

        if not _greeter.get_is_authenticated():
            logger.warn('Could not authenticate user {}'.format(self.user))
            self._auth_error_cb('Incorrect password (The default is "kano")')

            return

        logger.info(
            'The user {} is authenticated. Starting LightDM X Session'
            .format(self.user))

        set_last_user(self.user)

        if not _greeter.start_session_sync('lightdm-xsession'):
            logger.error('Failed to start session')
        else:
            logger.info('Login failed')

    def _auth_error_cb(self, text, message_type=None):
        logger.info('There was an error logging in: {}'.format(text))

        win = self.get_toplevel()
        win.go_to_users()

        error = KanoDialog(title_text='Error Logging In',
                           description_text=text,
                           parent_window=self.get_toplevel())
        error.dialog.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        error.run()

    def grab_focus(self):
        self.password.grab_focus()

    def delete_user(self, *_):
        import pam

        password_input = Gtk.Entry()
        password_input.set_visibility(False)
        password_input.set_alignment(0.5)

        confirm = KanoDialog(
            title_text='Are you sure you want to delete {}\'s account?'.format(
                self.user),
            description_text='A reboot will be required',
            widget=password_input,
            button_dict={
                'DELETE': {'return_value': True},
                'CANCEL': {'return_value': False}
            })
        confirm.dialog.set_position(Gtk.WindowPosition.CENTER_ALWAYS)

        if not confirm.run():
            return

        password = password_input.get_text()

        if pam.authenticate(self.user, password):
            os.system('sudo kano-init deleteuser {}'.format(self.user))
            LightDM.restart()
        else:
            error = KanoDialog(title_text='Incorrect password')
            error.dialog.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
            error.run()
