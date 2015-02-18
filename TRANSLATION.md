# Translation

Translation files are found in the `po/` directory.

## i18n not released yet

Kano OS is not fully i18n-aware and locales are not installed for end users, yet. You can translate this application, but as of now, users will still see the default English message strings.

## How to add a new translation

In this example, we're going to add a French translation:

    # install your target locale `fr_FR.utf8` with:
    sudo dpkg-reconfigure locales
    
    cd po/
    # create messages.pot
    make messages
    
    # create fr.po from messages.pot:
    msginit -l fr_FR.utf8
    
    # now use your favourite editor to translate fr.po
    
    # build locale files:
    make
    
    cd ..

    # prepare for testing as described in README.md
    # then change this in /usr/share/xgreeters/kano-greeter-devel.desktop
    Exec=dash -c "LC_ALL=fr_FR.utf8 /path/to/repo/bin/kano-greeter"
    
    # run test as in described in README.md

## How to make sure your code is i18n-aware

Add the gettext `_()` macro to all the user-visible message strings in your Python. List the Python source files that contain message strings in `PYPOTFILES`.

If you added new message strings or made changes to existing ones, do `make messages` to keep the template file up-to-date.

After that, merge the existing translations with `make update` and ask your translators to update their translations.

## To-Do

Pootle or Transifex integration.
