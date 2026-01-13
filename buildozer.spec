[app]

# (str) Title of your application
title = TCL Smart Remote

# (str) Package name
package.name = tcl_smart_remote

# (str) Package domain (needed for android/ios packaging)
package.domain = com.ahab.projectremote

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,txt,md

# (str) Application version
version = 0.1

# (list) Application requirements
requirements = python3,kivy==2.3.0,requests,android

# (str) Presplash of the application
presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (list) Permissions
android.permissions = INTERNET,ACCESS_WIFI_STATE,CHANGE_WIFI_STATE,ACCESS_NETWORK_STATE,ACCESS_FINE_LOCATION

# (int) Target Android API, should be as high as possible.
android.api = 34

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
# 25b is recommended for Kivy 2.3.0
android.ndk = 25b

# (str) Android NDK directory (if empty, it will be downloaded)
android.ndk_path = 

# (str) Android SDK directory (if empty, it will be downloaded)
android.sdk_path = 

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (str) Android entry point, default is ok for Kivy-based app
android.entrypoint = org.kivy.android.PythonActivity

# (str) Bootstrap to use for android builds
p4a.bootstrap = sdl2

# (bool) Copy library to the dist
android.copy_libs = 1

# (list) Architects to build for
android.archs = arm64-v8a, armeabi-v7a

# (bool) Allow the app to accept the Android SDK license
android.accept_sdk_license = True

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (bool) Clean build (recommended after significant changes or conflicts)
clean_build = True
