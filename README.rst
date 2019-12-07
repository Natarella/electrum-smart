Electrum-SMART - Lightweight SmartCash client
=====================================

::

  Licence: MIT Licence
  Author: Thomas Voegtlin
  Port Maintainer: rc125
  Language: Python
  Homepage: https://smartcash.cc/


Getting started
===============

Electrum is a pure python application. If you want to use the
Qt interface, install the Qt dependencies::

    sudo apt-get install python3-pyqt5

If you downloaded the official package (tar.gz), you can run
Electrum from its root directory, without installing it on your
system; all the python dependencies are included in the 'packages'
directory. To run Electrum from its root directory, just do::

    ./electrum-smart

You can also install Electrum on your system, by running this command::

    sudo apt-get install python3-setuptools
    pip3 install .[full]

This will download and install the Python dependencies used by
Electrum, instead of using the 'packages' directory.
The 'full' extra contains some optional dependencies that we think
are often useful but they are not strictly needed.

Trezor
===============

First, you need to install Trezor Bridge (https://wallet.trezor.io/#/bridge). Check if your Trezor is working by visiting trezor's website (https://wallet.trezor.io/)

If you are using Linux, you should follow these steps::

    sudo apt-get install python-dev cython libusb-1.0-0-dev libudev-dev git
    sudo pip3 install setuptools
    sudo pip3 install trezor
    

Development version
===================

Check out the code from Github::

    git clone git://github.com/smartcash/electrum-smart.git
    cd electrum-smart

Run install (this should install dependencies)::

    pip3 install .[full]

Compile the icons file for Qt::

    sudo apt-get install pyqt5-dev-tools
    pyrcc5 icons.qrc -o gui/qt/icons_rc.py

Compile the protobuf description file::

    sudo apt-get install protobuf-compiler
    protoc --proto_path=lib/ --python_out=lib/ lib/paymentrequest.proto

Create translations (optional)::

    sudo apt-get install python-requests gettext
    ./contrib/make_locale




Creating Binaries
=================


To create binaries, create the 'packages' directory::

    ./contrib/make_packages

This directory contains the python dependencies used by Electrum.

Mac OS X / macOS
--------

See `contrib/build-osx/`.

Windows
-------

See `contrib/build-wine/`.


Android
-------

See `gui/kivy/Readme.txt` file.
