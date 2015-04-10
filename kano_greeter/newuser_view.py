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

from kano_world.functions import login as kano_world_authenticate
from kano_init.user import user_exists, create_user
from kano.utils import run_cmd


class NewUserView(Gtk.Grid):
    greeter = LightDM.Greeter()

    def __init__(self):
        Gtk.Grid.__init__(self)

        self.get_style_context().add_class('password')
        self.set_row_spacing(5)

        self._reset_greeter()

        title = Heading(_('Create new user'),
                        _('Synchronize your Kano World\n' \
                          'account, or create a new one.'))

        self.attach(title.container, 0, 0, 1, 1)
        self.label = Gtk.Label("Use your Kano World email account")
        self.label.get_style_context().add_class('login')
        self.attach(self.label, 0, 1, 1, 1)

        self.username = Gtk.Entry()
        self.username.set_alignment(0.5)
        self.attach(self.username, 0, 2, 1, 1)

        self.password = Gtk.Entry()
        self.password.set_visibility(False)
        self.password.set_alignment(0.5)
        self.attach(self.password, 0, 3, 1, 1)

        self.login_btn = KanoButton(_('Login & Synchronize'))
        self.login_btn.connect('clicked', self._btn_login_pressed)
        self.attach(self.login_btn, 0, 4, 1, 1)

        self.newuser_btn = KanoButton(_('Create new user (reboot)'))
        self.newuser_btn.connect('clicked', self._new_user_reboot)
        self.attach(self.newuser_btn, 0, 5, 1, 1)

    def _new_user_reboot(self, event=None, button=None):
        '''
        Schedules kano-init to create a new user from scracth on next reboot,
        then performs the actual reboot
        '''
        confirm = KanoDialog(
            title_text = _('Are you sure you want to create a new account?'),
            description_text = _('A reboot will be required'),
            button_dict = [
                {
                    'label': _('Cancel').upper(),
                    'color': 'red',
                    'return_value': False
                    },
                {
                    'label': _('Create').upper(),
                    'color': 'green',
                    'return_value': True
                    }
                ])
        confirm.dialog.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        
        if confirm.run():
            os.system("sudo kano-init newuser")
            LightDM.restart()

    def _reset_greeter(self):
        NewUserView.greeter = NewUserView.greeter.new()
        NewUserView.greeter.connect_sync()

        # connect signal handlers to LightDM
        NewUserView.greeter.connect('show-prompt', self._send_password_cb)
        NewUserView.greeter.connect('authentication-complete',
                                    self._authentication_complete_cb)
        NewUserView.greeter.connect('show-message', self._auth_error_cb)

    def _error_message_box(self, title, description):
        '''
        Show a standard error message box
        '''
        errormsg=KanoDialog(title_text=title,
                            description_text=description,
                            button_dict= [
                                {
                                    'label': _('Ok').upper(),
                                    'color': 'red',
                                    'return_value': True
                                    }])

        errormsg.dialog.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        errormsg.run()

        # Stop spinner; cleanup view fields
        self.login_btn.stop_spinner()
        self.password.set_text('')
        return

    def _btn_login_pressed(self, event=None, button=None):
        '''
        Authenticates against Kano World. If successful synchronizes to a local
        Unix account, and tells lightdm to go forward with local a login.
        '''

        logger.debug('Synchronizing Kano World account')
        self.login_btn.start_spinner()

        loggedin=False
        reason=''

        # TODO: Disable the "login" button unless these entry fields are non-empty
        # Collect credentials from the view
        password=self.password.get_text()
        username=self.username.get_text()
        atsign=username.find('@')
        if atsign:
            username_plain=username[:atsign]

        # Now try to login to Kano World
        try:
            logger.debug('Authenticating user: {} to Kano World'.format(username))
            (loggedin, reason)=kano_world_authenticate(username, password)
            logger.debug('Kano World auth response: {} - {}'.format(loggedin, reason))
        except Exception as e:
            reason=str(e)
            logger.debug('Kano World auth Exception: {}'.format(reason))
            pass

        if not loggedin:
            # Authentication failed, show error message and return to dialog
            self._error_message_box(title=_('Failed to authenticate to Kano World'), description=reason)
            return
        else:
            # We are authenticated: Does the user already exist on this kit?
            if not user_exists(username_plain):
                try:
                    create_user(username_plain)
                except Exception as e:
                    title=_("Error synchronizing user {}".format(username_plain))
                    description=str(e)
                    self._error_message_box(title, description)
                    return

                # First time login: Do the synchronization under the new user's security context
                # FIXME: Do we need to call --sync two times?
                cmd = 'su - {username} -c "/usr/bin/kano-sync --sync -s"'.format(username=username_plain)
                run_cmd(cmd)
                run_cmd(cmd)
                cmd3 = 'su - {username} -c "/usr/bin/kano-sync --restore -s"'.format(username=username_plain)
                run_cmd(cmd)
            else:
                # Non first login synchronization
                cmd = '{bin_dir}/kano-sync --sync -s'.format(bin_dir=bin_dir)
                run_cmd(cmd)

            title=_("User {} has been created".format(username_plain))
            description=_("Logging in with the new user !")
            self._error_message_box(title, description)

            # Tell Lidghtdm to proceed with login session using the new user
            NewUserView.greeter.authenticate(username_plain)
            if NewUserView.greeter.get_is_authenticated():
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
            self._auth_error_cb(_('Incorrect password (The default is "kano")'))

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

        error = KanoDialog(title_text=_('Error Logging In'),
                           description_text=text,
                           parent_window=self.get_toplevel())
        error.dialog.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        error.run()

    def grab_focus(self):
        self.username.grab_focus()
