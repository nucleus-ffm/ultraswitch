#####################################################
# UltraSwitch                                       #
# author: Nucleus                                   #
# Github: https://github.com/nucleus-ffm            #
# Repo: https://github.com/nucleus-ffm/ultraswitch  #
# date: 12.07.2021                                  #
#####################################################

import sys, os
from git import Repo
import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from multiprocessing import Process
import os
import time
import configparser
import shutil
import urllib.request
import zipfile


# swtich to Ultraschall
def Ultraschall(version=503):
    print("switching to ultraschall (version: " + str(version) + ")")

    currentDir = os.getcwd()
    pfad1 = currentDir + "/Ultraschall" + str(version)
    print(pfad1)
    homedir = os.path.expanduser("~")
    pfad2 = homedir + "/.config/REAPER"
    # check if symbolic links exsis
    if os.path.exists(pfad2):
        os.unlink(pfad2)
    # create new symbolic link to US config
    os.symlink(pfad1, pfad2)
    print("done")


# switch to reaper
def reaper():
    print("switching to reaper")
    currentDir = os.getcwd()
    pfad1 = currentDir + "/reaper"
    homedir = os.path.expanduser("~")
    pfad2 = homedir + "/.config/REAPER"
    if os.path.exists(pfad2):
        os.unlink(pfad2)
    os.symlink(pfad1, pfad2)
    print("done")


# handel GUI Buttons
class Handler:
    def onDestroy(self, *args):
        Gtk.main_quit()

    def show_about(self, button):
        dialog = Gtk.AboutDialog()
        dialog.set_title("AboutDialog")
        dialog.set_name("UltraSwitch")
        dialog.set_version("1.0")
        dialog.set_comments("created by: Nucleus")
        dialog.set_website("https://github.com/nucleus-ffm/ultraswitch")
        dialog.set_website_label("UltraSwitch Repository")
        dialog.set_authors(["Nucleus"])
        # dialog.set_logo(GdkPixbuf.Pixbuf.new_from_file_at_size("US-Switch-Logo.png", 64, 64))
        dialog.connect("response", lambda dialog, data: dialog.destroy())
        dialog.show_all()

    def switch_button_clicked(self, button):
        print("Switch Button pressed")
        config = configparser.ConfigParser()
        config.read("config.ini")
        currentMode = config["GENERAL"]["currentMode"]
        print("Current Mode is: ", currentMode)

        if currentMode == "Podcast":
            print("Switch to Reaper")
            reaper()
            config["GENERAL"]["currentMode"] = "Music"
            with open("config.ini", "w") as configfile:
                config.write(configfile)
            loadInformation()
        else:
            print("Switch to Ultraschall")
            Ultraschall()
            config["GENERAL"]["currentMode"] = "Podcast"
            with open("config.ini", "w") as configfile:
                config.write(configfile)
            loadInformation()

        with open("config.ini", "w") as configfile:
            config.write(configfile)

    def update_button_clicked(self, button):
        print("update_button pressed")
        downloadUS()

    def switch_version_button_clicked(self, version_chooser_combo):
        print("switch_version_button pressed")
        tree_iter = version_chooser_combo.get_active_iter()
        if tree_iter is not None:
            model = version_chooser_combo.get_model()
            title, name = model[tree_iter][:2]
            print("Selected: title=%s, name=%s" % (title, name))
            downloadUS(name)  # download version
            Ultraschall(name)  # switch to downloaded version

    def combo_box_changed(self):
        print("combo_box_changed")  # not used


# MessageBox widget
def messageBox(title, message, ok, cancel):
    def dialog_response(self, button):
        # if the button clicked gives response OK (-5)
        if button == Gtk.ResponseType.OK:
            print("Ok clicked")
            ok()
        # if the button clicked gives response CANCEL (-6)
        elif button == Gtk.ResponseType.CANCEL:
            print("cancel clicked")
            cancel()
        # if the messagedialog is destroyed (by pressing ESC)
        elif button == Gtk.ResponseType.DELETE_EVENT:
            print("dialog closed or cancelled")
            cancel()
        # destroy the messagedialog
        self.destroy()

    # define dialog
    messagedialog = Gtk.MessageDialog(
        parent=window,
        title = title,
        flags=Gtk.DialogFlags.MODAL,
        type=Gtk.MessageType.WARNING,
        buttons=Gtk.ButtonsType.OK_CANCEL,
        message_format=message,
    )

    # connect the response (of the button clicked) to the function dialog_response()
    messagedialog.connect("response", dialog_response)
    messagedialog.set_icon_from_file("US-Switch-icon.png")
    # show the messagedialog
    messagedialog.show()


def close():
    print("Goodbye...")
    Gtk.main_quit()


# show welcome screen, create Backup and download US
def firstStart():
    print("Hello, you started UltraSwitch for the first time.")
    # show messageBox
    title = "welcome to UlraSwitch"
    message = (
        "It seems that you have started UltraSwitch for the first time. "
        "UltraSwitch can switch between Reaper and Ultraschall. "
        "To do this, UltraSwtich creates symbolic links. For UltraSwtich to work properly, "
        "REAPER must be installed and Ultraschall must be downloaded and stored in this current folder'. "
        "If you already have Ultraschall installed, you will need to copy the original reaper configuration into the current folder as 'reaper'. "
        "If you do not have Ultraschall installed, simply click 'ok'. "
        "UltraSwtich will then download the latest Ultraschall release from Github. "
        "Your old configuration file will be saved here as a backup: '~./config/REAPER-Backup'. If you click on 'Cancel', UltraSwitch will close. "
    )
    messageBox(title, message, downloadUS, close)

    homedir = os.path.expanduser("~")
    currentDir = os.getcwd()
    reaperPfad = homedir + "/.config/REAPER"
    backupPfad = reaperPfad + "-Backup"
    reaper = currentDir + "/reaper"
    if os.path.exists(reaperPfad):
        if os.path.exists(backupPfad):
            pass
        else:
            shutil.copytree(reaperPfad, backupPfad)
        if os.path.exists(reaper):
            pass
        else:
            shutil.copytree(reaperPfad, reaper)


# download US release from Github
def downloadUS(version="503"):
    print("selected version: " + version)
    url = (
        "https://github.com/Ultraschall/ultraschall-portable/archive/refs/tags/us%s.zip"
        % version
    )
    currentDir = os.getcwd()
    USFile = currentDir + "/Ultraschall%s" % version
    if os.path.exists(USFile):
        print("Version already downloaded")
    else:
        print("download last US release")
        urllib.request.urlretrieve(url, USFile + ".zip")
        print("Download finished")
        print("unzip file...")
        with zipfile.ZipFile(USFile + ".zip", "r") as zip_ref:
            zip_ref.extractall(USFile)
        print("finished")


# update GUI
def loadInformation():
    config = configparser.ConfigParser()
    config.read("config.ini")
    currentMode = config["GENERAL"]["currentMode"]

    mode_label_title = builder.get_object("modus_label_title")
    mode_label_title.set_justify(Gtk.Justification.LEFT)

    print("Now load Information")
    mode_label = builder.get_object("modus_label")
    mode_label.set_text(currentMode)

    switchButton = builder.get_object("switch_button")
    if currentMode == "Music":
        switchButton.set_label("switch to podcast")
    else:
        switchButton.set_label("switch to music")

    version_label = builder.get_object("version_label")
    config.read("config.ini")
    lastVersion = currentMode = config["GENERAL"]["lastVersion"]
    version_label.set_text("US " + str(lastVersion))

    lastUpdate_label = builder.get_object("lastUpdate_label")
    lastUpdate_label.set_text("1.1.2021")

    newestVersion_label = builder.get_object("newestVersion_label")
    newestVersion_label.set_text("You are up to date")


# check if config file exsis or create it
def checkConfig():
    print("check config file")
    config = configparser.ConfigParser()
    if os.path.exists("config.ini"):
        config.read("config.ini")
        # should not happen, just for testing
        if config["GENERAL"]["firstStart"] == "True":
            firstStart()
        loadInformation()
    else:
        firstStart()
        config["GENERAL"] = {
            "firstStart": "False",
            "currentMode": "Music",
            "lastVersion": "503",
        }
        with open("config.ini", "w") as configfile:
            config.write(configfile)
        loadInformation()


# main part
if __name__ == "__main__":
    """@TODO: create system tray icon"""
    builder = Gtk.Builder()
    builder.add_from_file("Main.glade")
    builder.connect_signals(Handler())
    window = builder.get_object("gui")
    screen = Gdk.Screen.get_default()
    provider = Gtk.CssProvider()
    provider.load_from_path("style.css")
    Gtk.StyleContext.add_provider_for_screen(
        screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
    checkConfig()
    window.set_icon_from_file("US-Switch-icon.png")
    window.set_title("UltraSwitch")
    window.set_position(Gtk.WindowPosition.CENTER)
    window.connect("destroy", Gtk.main_quit)
    window.show_all()
    Gtk.main()
