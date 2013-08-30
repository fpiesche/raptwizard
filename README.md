After my recent blog post about how to use RAPT to make an OUYA-compatible build of Ren’py games, I went off and wrote a little Python tool to make the process a bit easier. It’ll automatically try to detect your Python installation, download any required software and allows you to generate a key.

Currently, it requires Python to be installed - I don’t have a Windows installation handy to make a Py2EXE build, so if you’re running Windows you will have to install Python from python.org/download/ to run it - just open raptwizard.py to launch.

Setting up prerequisites
------------------------

When you first start the wizard, you will be presented with the "RAPT Installation" screen.

If you already have a working RAPT installation, press “Choose” to manually select your RAPT folder, or “Search” to try and find it (this may take a REALLY LONG TIME). Otherwise, you can press “Download RAPT” to automatically download it as well as the other required pieces of software. Downloading RAPT will grab easily a couple hundred megabytes of data - RAPT, the Android SDK, the required libraries for the Android SDK, and Apache Ant - so may take a fair while, during which the wizard may become unresponsive. Occasionally during this process, the wizard will pop up messages telling you what’s going on.

If you do not have the Java Development Kit installed, you will be presented with a similar screen for this; however the “Download” link here will only open the download website for you to download and install the JDK. If you press “Search” after installing the JDK, the installation path will be automatically filled in.


Building a game
---------------

If your prerequisites are all fulfilled, you will proceed to the Choose Game screen.

On this screen, there are the following options:

* Game directory - click “Choose” to select the game you want to make an Android build of.
* Android keystore - click “Choose” to select your Android signing key file if you have one or “Generate” to create one (see “Generating an Android signing key” below)
* Key file password - enter the passphrase for your keystore file here.
* Signing key alias - enter the alias of the specific key to use from the keystore.
* Signing key password - the password for the selected signing key goes here.

Generating an Android signing key
---------------------------------

In order to submit an app to the Google Play, Ouya, Amazon etc. app store, it needs to be “signed” to verify your identity as the developer. This uses a cryptographic key blah blah I could go on and explain everything but you really don’t need to know in any great detail.

TLDR: you must sign your .apk to submit it to any public app store. You need an Android signing key for this.

If you click “Generate” next to the “Android keystore” field, you are taken to the key generation screen.

You only need to enter two things here:

* Organisation name is the name that you would like to publish your games under.
* The Passphrase is the password that both the key storage file and the specific Android key will be secured with. Technically using the same password for this is bad practice, but for the sake of this it will do.

Press “Save key as…" to select the filename to save the signing key under. Put this in a safe place and make backups - you will want to use this every time you want to build any Android app, with Ren’py or otherwise.

Building your game
------------------

Once you have selected the game to build and your signing key, you will proceed to the Game Settings screen. This is where you enter information about your game for use by app stores.

* Title is the title under which you would like your game to appear.
* Package name is an internal reference for use by Android (and app stores) - the naming standard for these is ext.yourdomain.yourgame; eg. for the Google Maps app this is com.google.maps. If you would like more detail, read [what Wikipedia has to say on Java package naming conventions](https://en.wikipedia.org/wiki/Java_package#Package_naming_conventions).
* Game version is the version number for this release of the game.
* Screen orientation determines whether Ren’py will run your game in landscape or portrait mode. Choose this to match the format of your game visuals. NOTE that Android-based consoles such as the OUYA always run in Landscape mode.
* Image directory is a directory containing icon files and a loading screen for the game.

The files that go into your Image directory are as follows:

* ldpi.png (required) - 36x36 app icon
* mdpi.png (required) - 48x48 app icon
* hdpi.png (required) - 72x72 app icon
* xhdpi.png (required) - 96x96 app icon
* xxhdpi.png (required) - 144x144 app icon
* presplash.png (required) - your loading screen
* ouya_icon.png (optional) - 732x412 OUYA app icon

Once you have entered this information, click “Finish” to make your build! When the build is complete, you will be prompted to save the finished .apk file somewhere and can submit it to app stores!

If something goes wrong along the way, the wizard will notify you to the best of its ability and (if possible) suggest what you need to do to complete your build.

I’m happy to take comments, bug reports and suggestions either here or at @ektoutie on Twitter!
