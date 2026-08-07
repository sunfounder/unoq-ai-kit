# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------
import sphinx_rtd_theme
import time  ###

project = 'Arduino Uno Q AI Starter Kit'
copyright = f'{time.localtime().tm_year}, SunFounder'  ###
author = 'www.sunfounder.com'

# -- sphinx_rtd_theme Theme options -----------------------------------------------------
html_theme_options = {
    'flyout_display': 'attached',
    'version_selector': False,
    'language_selector': False,
}

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    # 'sphinx.ext.autosectionlabel',
    'sphinx_copybutton',
    'sphinx_rtd_theme',
    'sphinx_design',
    'sphinxcontrib.mermaid'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_static_path = ['_static']
html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]


# SunFounder logo

html_js_files = [
    'https://ezblock.cc/readDocFile/custom.js', 
    './lang.js', # new
]
html_css_files = [
    'https://ezblock.cc/readDocFile/custom.css',
]

#### RTD+

# html_js_files = [
#     'https://ezblock.cc/readDocFile/custom.js',
#     'https://ezblock.cc/readDocFile/readTheDoc/src/js/ace.js',
#     'https://ezblock.cc/readDocFile/readTheDoc/src/js/ext-language_tools.js',
#     'https://ezblock.cc/readDocFile/readTheDoc/src/js/theme-chrome.js',
#     'https://ezblock.cc/readDocFile/readTheDoc/src/js/mode-python.js',
#     'https://ezblock.cc/readDocFile/readTheDoc/src/js/mode-sh.js',
#     'https://ezblock.cc/readDocFile/readTheDoc/src/js/monokai.js',
#     'https://ezblock.cc/readDocFile/readTheDoc/src/js/xterm.js',
#     'https://ezblock.cc/readDocFile/readTheDoc/src/js/FitAddon.js',
#     'https://ezblock.cc/readDocFile/readTheDoc/src/js/readTheDocIndex.js',

# ]
# html_css_files = [
#     'https://ezblock.cc/readDocFile/custom.css',
#     'https://ezblock.cc/readDocFile/readTheDoc/src/css/index.css',
#     'https://ezblock.cc/readDocFile/readTheDoc/src/css/xterm.css',
# ]



# Multi-language

language = 'en' # Before running make html, set the language.
locale_dirs = ['locale/'] # .po files for other languages are placed in the locale/ folder.

gettext_compact = False # Support for generating the contents of the folders inside source/ into other languages.



# open link in a new window

rst_epilog = """

.. |link_unoq_manual| raw:: html

    <a href="https://docs.arduino.cc/hardware/uno-q" target="_blank">UNO Q Manual</a>

.. |link_unoq_datasheet| raw:: html

    <a href="https://docs.arduino.cc/resources/datasheets/ABX00111-datasheet.pdf" target="_blank">UNO Q Datasheet</a>

.. |link_unoq_schematics| raw:: html

    <a href="https://docs.arduino.cc/resources/schematics/ABX00111-schematics.pdf" target="_blank">UNO Q Schematics</a>

.. |link_arduino_cloud| raw:: html

    <a href="https://app.arduino.cc/" target="_blank">Arduino Cloud</a>

.. |link_cloud_devices| raw:: html

    <a href="https://app.arduino.cc/devices" target="_blank">devices</a>

.. |link_cloud_things| raw:: html

    <a href="https://app.arduino.cc/things" target="_blank">things</a>

.. |link_cloud_dashboards| raw:: html

    <a href="https://app.arduino.cc/dashboards" target="_blank">dashboards</a>

.. |link_unoq_step_files| raw:: html

    <a href="https://docs.arduino.cc/resources/models/ABX00162-step.zip" target="_blank">UNO Q 3D Step Files</a>

.. |link_unoq_full_pinout| raw:: html

    <a href="https://docs.arduino.cc/resources/pinouts/ABX00162-full-pinout.pdf" target="_blank">UNO Q Full Pinout (PDF)</a>

.. |link_app_get_start| raw:: html

    <a href="https://docs.arduino.cc/software/app-lab/getting-started/quickstart/" target="_blank">Arduino App Lab Getting Started</a>

.. |link_arduino_software| raw:: html

    <a href="https://www.arduino.cc/en/software" target="_blank">Arduino Software</a>

.. |link_board_mode| raw:: html

    <a href="https://docs.arduino.cc/hardware/uno-q#board-modes" target="_blank">board modes</a>

.. |link_arduino_lib_page| raw:: html

    <a href="https://www.arduino.cc/reference/en/libraries/" target="_blank">Libraries</a>

.. |link_sf_facebook| raw:: html

    <a href="https://bit.ly/raphaelkit" target="_blank">here</a>

.. |link_wiki_avometer| raw:: html

    <a href="https://en.wikipedia.org/wiki/Avometer" target="_blank">Wikipedia - Avometer</a>

.. |link_docs_ide| raw:: html

    <a href="https://docs.arduino.cc/software/ide-v2/tutorials/getting-started-ide-v2/" target="_blank">Getting Started with Arduino IDE 2</a>

.. |link_arduino_forum| raw:: html

    <a href="https://forum.arduino.cc/" target="_blank">Arduino Forum</a>

.. |link_arduino_project_hub| raw:: html

    <a href="https://projecthub.arduino.cc/" target="_blank">Arduino Project Hub</a>

.. |link_arduino_docs| raw:: html

    <a href="https://docs.arduino.cc/" target="_blank">Official Arduino Documentation</a>

.. |link_download_arduino| raw:: html

    <a href="https://www.arduino.cc/en/software#future-version-of-the-arduino-ide" target="_blank">Arduino Software Page</a>

.. |link_arduino_reference| raw:: html

    <a href="https://www.arduino.cc/reference/en/" target="_blank">Language Reference</a>

"""


# language links

rst_epilog += """

.. |link_german_tutorials| raw:: html

    <a href="https://docs.sunfounder.com/projects/inventor-lab-kit/de/latest/" target="_blank">Deutsch Online-Kurs</a>

.. |link_jp_tutorials| raw:: html

    <a href="https://docs.sunfounder.com/projects/inventor-lab-kit/ja/latest/" target="_blank">日本語オンライン教材</a>

.. |link_en_tutorials| raw:: html

    <a href="https://docs.sunfounder.com/projects/inventor-lab-kit/en/latest/" target="_blank">English Online-tutorials</a>

"""

# component pic
rst_epilog += """

.. |list_green_led| image:: /img/list_cpn/list_green_led.png 
.. |list_red_led| image:: /img/list_cpn/list_red_led.png 
.. |list_blue_led| image:: /img/list_cpn/list_blue_led.png 
.. |list_yellow_led| image:: /img/list_cpn/list_yellow_led.png 
.. |list_white_led| image:: /img/list_cpn/list_white_led.png 
.. |list_rgb_led| image:: /img/list_cpn/list_rgb_led.png 
.. |list_10ohm| image:: /img/list_cpn/list_10ohm.png 
.. |list_100ohm| image:: /img/list_cpn/list_100ohm.png 
.. |list_220ohm| image:: /img/list_cpn/list_220ohm.png 
.. |list_330ohm| image:: /img/list_cpn/list_330ohm.png 
.. |list_1kohm| image:: /img/list_cpn/list_1kohm.png 
.. |list_2kohm| image:: /img/list_cpn/list_2kohm.png 
.. |list_5_1ohm| image:: /img/list_cpn/list_5_1ohm.png 
.. |list_10kohm| image:: /img/list_cpn/list_10kohm.png 
.. |list_100kohm| image:: /img/list_cpn/list_100kohm.png 
.. |list_1mohm| image:: /img/list_cpn/list_1mohm.png 
.. |list_active_buzzer| image:: /img/list_cpn/list_active_buzzer.png 
.. |list_passive_buzzer| image:: /img/list_cpn/list_passive_buzzer.png 
.. |list_button| image:: /img/list_cpn/list_button.png 
.. |list_thermistor| image:: /img/list_cpn/list_thermistor.png 
.. |list_photoresistor| image:: /img/list_cpn/list_photoresistor.png 
.. |list_potentiometer| image:: /img/list_cpn/list_potentiometer.png 
.. |list_7segment| image:: /img/list_cpn/list_7segment.png 
.. |list_74hc595| image:: /img/list_cpn/list_74hc595.png 
.. |list_ultrasonic| image:: /img/list_cpn/list_ultrasonic.png 
.. |list_meter| image:: /img/list_cpn/list_meter.png 
.. |list_wire| image:: /img/list_cpn/list_wire.png
.. |list_breadboard| image:: /img/list_cpn/list_breadboard.png 
.. |list_usb_cable| image:: /img/list_cpn/list_usb_cable.png 
.. |list_uno_q| image:: /img/list_cpn/list_uno_q.png 

.. |list_4digit| image:: /img/list_cpn/list_4digit.png 
.. |list_bat_cable| image:: /img/list_cpn/list_bat_cable.png 
.. |list_battery| image:: /img/list_cpn/list_battery.png
.. |list_pan_tilt| image:: /img/list_cpn/list_pan_tilt.png 
.. |list_fan| image:: /img/list_cpn/list_fan.png 
.. |list_joystick_module| image:: /img/list_cpn/list_joystick_module.png 
.. |list_l293d| image:: /img/list_cpn/list_l293d.png 
.. |list_moisture_module| image:: /img/list_cpn/list_moisture_module.png
.. |list_motor| image:: /img/list_cpn/list_xh254_motor.png 
.. |list_power_module| image:: /img/list_cpn/list_power_module.png 
.. |list_pump| image:: /img/list_cpn/list_pump.png 
.. |list_rab| image:: /img/list_cpn/list_rab.png 
.. |list_rc522_module| image:: /img/list_cpn/list_rc522_module.png 
.. |list_receiver| image:: /img/list_cpn/list_receiver.png 
.. |list_relay_module| image:: /img/list_cpn/list_relay_module.png 
.. |list_remote| image:: /img/list_cpn/list_remote.png 
.. |list_servo| image:: /img/list_cpn/list_servo.png 
.. |list_stepper| image:: /img/list_cpn/list_stepper.png 
.. |list_uln2003_module| image:: /img/list_cpn/list_uln2003_module.png 
.. |list_i2c_lcd1602| image:: /img/list_cpn/list_i2c_lcd1602.png


.. |list_tilt_switch| image:: /img/list_cpn/list_tilt_switch.png
.. |list_dht11| image:: /img/list_cpn/list_dht11.png
.. |list_pir| image:: /img/list_cpn/list_pir.png
.. |list_imu| image:: /img/list_cpn/list_imu.png

.. |list_pan_tilt_kit| image:: /img/list_cpn/list_pan_tilt.png

"""
# purchase links

rst_epilog += """

.. |link_Inventor_Lab_Kit| raw:: html

    <a href="https://www.sunfounder.com/collections/esp32-1/products/sunfounder-esp32-ultimate-starter-kit-with-esp32-camera-extension-board-battery" target="_blank">Purchase Link for Inventor Lab Kit</a>

.. |link_Inventor_kit| raw:: html

    <a href="https://www.sunfounder.com/products/sunfounder-esp32-ultimate-starter-kit-with-esp32-camera-extension-board-battery" target="_blank">Inventor Lab Kit</a>

"""
