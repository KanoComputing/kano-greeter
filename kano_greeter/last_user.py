#!/usr/bin/env python

import os

LAST_USER_PATH = '/var/lib/lightdm/.cache/kano-greeter/'
LAST_USER_FILE = 'last-user'

def get_last_user():
    try:
        with open(os.path.join(LAST_USER_PATH, LAST_USER_FILE)) as f:
            last_user = f.read()
            f.close()
    except:
        last_user = None
    return last_user

def set_last_user(last_user):
    if not os.path.exists(LAST_USER_PATH):
        os.makedirs(LAST_USER_PATH)
    f = open(os.path.join(LAST_USER_PATH, LAST_USER_FILE), "w+")
    f.write(last_user)
    f.close()
