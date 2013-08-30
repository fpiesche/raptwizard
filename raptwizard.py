try:
    from wizard import *
    from Tkinter import *
    import ttk
    import tkMessageBox
    from tkFileDialog import askdirectory, askopenfilename, asksaveasfilename
    import webbrowser
    import imp
    import re
    import os
    import sys
    import zipfile
    import shutil
    from multiprocessing import Process, Queue
    from tooltip import ToolTip
except ImportError:
    print("An import has failed!")
    exit()

class interfaceWrapper():
    # fake wrapper class for android.py's text UI

    def success(self, message):
        print("SUCCESS: " + message)
        tkMessageBox.showinfo(title="Information", message=message)

    def fail(self, message):
        print("ERROR: " + message)
        tkMessageBox.showerror(title="Error", message=message)

    def yesno(self, message):
        return False

    def info(self, message):
        print("INFO: " + message)
        tkMessageBox.showinfo(title="Information", message=message)

    def input(self, message):
        return self.orgName.get()


class raptWizard():

    wizPages = 3
    myPath = ""
    raptPath = ""
    jdkPath = ""
    pythonPath = ""
    myOS = ""
    mainWindow = Tk()
    foundPython = False
    foundRAPT = False
    foundJDK = False
    ifwrapper = interfaceWrapper()

    # build configuration
    keystore = ""
    orgName = ""
    keyPassphrase = ""
    gamePath = ""
    gameTitle = ""
    gamePackage = ""
    gameVersion = ""
    gameOrientation = ""
    imagesPath = ""
    keypass = ""
    keyAlias = ""
    storepass = ""
    requiredImages = {}

    def __init__(self):
        self.raptPath = StringVar()
        self.jdkPath = StringVar()
        self.pythonPath = StringVar()
        self.myOS = ""
        self.mainWindow.title("RAPT Wizard v1")
        self.wizPages = 3
        self.ifwrapper = interfaceWrapper()

        # build configuration
        self.gameInfo = None
        self.orgName = StringVar()
        self.orgName.set("My Developer Name")
        self.keystore = StringVar()
        self.keyPassphrase = StringVar()
        self.gamePath = StringVar()
        self.gameTitle = StringVar()
        self.gamePackage = StringVar()
        self.gameVersion = StringVar()
        self.gameOrientation = StringVar()
        self.imagesPath = StringVar()
        self.keypass = StringVar()
        self.keyAlias = StringVar()
        self.storepass = StringVar()
        self.requiredImages = {"ldpi.png": "(36x36 app icon)", "mdpi.png": "(48x48 app icon)", "hdpi.png": "(72x72 app icon)", "xhdpi.png": "(96x96 app icon)", "xxhdpi.png": "(144x144 app icon)", "presplash.png": "(loading screen)"}

        if sys.platform.startswith("win"):
            self.myOS = "win"
        elif sys.platform.startswith("linux"):
            self.myOS = "lin"
        elif sys.platform.startswith("darwin"):
            self.myOS = "mac"
        self.myPath = os.path.dirname(os.path.realpath(__file__))

        self.findJDK()
        self.findPython()
        self.findRAPT()

        if self.foundRAPT and (not os.path.exists(os.path.join(self.raptPath.get(), "android-sdk")) or not os.path.exists(os.path.join(self.raptPath.get(), "apache-ant"))):
            self.prepRAPT(self.raptPath.get())

        self.buildGUI()
        self.mainWindow.mainloop()

    def main_is_frozen(self):

        return (hasattr(sys, "frozen") or  # new py2exe
                hasattr(sys, "importers")  # old py2exe
                or imp.is_frozen("__main__"))  # tools/freeze

    """ RAPT support functionality """
    def getRapt(self):

        renpyAndroidURL = "http://www.renpy.org/dl/android/"

        import urllib
        import re
        try:
            requestObj = urllib.urlopen(renpyAndroidURL)
            androidPage = requestObj.read()
        except:
            self.ifwrapper.fail("No internet connection?")
        links = re.findall(r'href=\"(.*?).zip', androidPage)

        currentRAPT = renpyAndroidURL + links[len(links)-1] + ".zip"
        with open("rapt.zip", 'wb') as raptZip:
            self.ifwrapper.info("RAPT Wizard will now download " + currentRAPT + ".")
            try:
                requestObj = urllib.urlopen(currentRAPT)
                shutil.copyfileobj(requestObj, raptZip)
            except:
                self.ifwrapper.fail("Failed to save rapt ZIP!")
                exit()

        if zipfile.is_zipfile("rapt.zip"):
            self.ifwrapper.info("RAPT Wizard will now extract RAPT.")
            with zipfile.ZipFile("rapt.zip") as raptZip:
                raptZip.extractall()

        os.rename(links[len(links)-1], "rapt")
        os.remove("rapt.zip")
        self.raptPath.set(os.path.join(self.myPath, "rapt"))
        self.prepRAPT(self.raptPath.get())

    def chooseRAPT(self):
        if not self.foundRAPT:
            raptFile = self.find("AndroidManifest.tmpl.xml", askdirectory())
            if raptFile:
                self.raptPath.set(os.path.dirname(os.path.dirname(raptFile)))
                self.foundRAPT = True
            else:
                self.ifwrapper.fail("The directory you have chosen does not seem to be a valid copy of RAPT.")

    def findRAPT(self):
        if not self.foundRAPT:
            raptFile = self.find("AndroidManifest.tmpl.xml", self.myPath)
            if raptFile:
                self.raptPath.set(os.path.dirname(os.path.dirname(raptFile)))
                self.foundRAPT = True
            else:
                self.wizPages += 1
                print("RAPT not found.")

    def prepRAPT(self, raptPath):
        # create init files for rapt and rapt/buildlib so they can be imported from
        if not os.path.exists(os.path.join(raptPath, "__init__.py")):
            with open(os.path.join(raptPath, "__init__.py"), 'w') as raptInit:
                raptInit.write("")
        if not os.path.exists(os.path.join(raptPath, "buildlib/__init__.py")):
            with open(os.path.join(raptPath, "buildlib/__init__.py"), 'w') as raptInit:
                raptInit.write("")

        # add OUYA launcher intent to AndroidManifest if needed
        manifestTemplate = os.path.join(self.raptPath.get(), "templates/AndroidManifest.tmpl.xml")
        with open(manifestTemplate, 'r') as manifest:
            manifestText = manifest.read()
        if re.search("tv.ouya.intent.category.GAME", manifestText) is None:
            print "Adding OUYA intent to Android Manifest."
            manifestText = manifestText.replace("</intent-filter>", "<category android:name=\"tv.ouya.intent.category.GAME\"/></intent-filter>")
        with open(manifestTemplate, 'w') as manifest:
            manifest.write(manifestText)

        if not os.path.exists(os.path.join(raptPath, "android-sdk")) or not os.path.exists(os.path.join(raptPath, "apache-ant")):
            self.sdkSetup()

    """ Python support functionality """
    def findPython(self, fullSearch=False):
        # try to figure out whether python is installed
        if not self.foundPython:
            if self.main_is_frozen():
                # running from within py2exe. check for Python install in default directory.
                pyDefault = self.find("python.exe", "c:\Python27")
                if pyDefault:
                    self.pythonPath.set("c:\Python27")
                    self.foundPython = True
                else:
                    self.wizPages += 1
                    print("Python not found.")
            else:
                self.pythonPath.set(sys.executable)
                self.foundPython = True
                print("Python found at " + self.pythonPath.get())

        if fullSearch and not self.foundPython:
            if self.myOS == "win":
                pyExe = self.find("python.exe")
            else:
                pyExe = self.find("python", None, True)
            if pyExe:
                self.pythonPath.set(pyExe)

    def getPython(self):
        if self.myOS == "win":
            self.ifwrapper.info("Download and install Python", "RAPT Wizard will now open the Python download site. Download and install Python 2.7 from there and try searching for it again.")
            webbrowser.open("http://python.org/download/")
        elif self.myOS == "lin":
            self.ifwrapper.info("Download and install Python", "Python was not found but is required for RAPT Wizard to function. Please install Python 2.7 using your distribution's package management system and try again.")

    """ Python support functionality """
    def findJDK(self, fullSearch=False):
        # determine whether JDK is installed
        if not self.foundJDK:
            if "JAVA_HOME" in os.environ and (os.environ["JAVA_HOME"]):
                self.foundJDK = True
                self.jdkPath.set(os.environ["JAVA_HOME"])
                print("JDK found at " + self.jdkPath.get())
            else:
                self.wizPages += 1

        if fullSearch and not self.foundJDK:
            if self.myOS == "win":
                javacExe = self.find("javac.exe")
            else:
                javacExe = self.find("javac", None, True)
            if javacExe:
                self.jdkPath.set(os.path.join(javacExe, ".."))

    def getJDK(self):
        if self.myOS == "win" or self.myOS == "mac":
            self.ifwrapper.info("Download and install JDK", "There was no Java Development Kit found; this is required for RAPT Wizard to function. RAPT Wizard will now open the JDK download page; please install the Java Development Kit from this site and try again.")
            webbrowser.open("http://www.oracle.com/technetwork/java/javase/downloads/index.html")
        elif self.myOS == "lin":
            self.ifwrapper.info("Download and install JDK", "There was no Java Development Kit found; this is required for RAPT Wizard to function. Please install OpenJDK or Oracle JDK using your Linux distribution's package management system.")

    def sdkSetup(self):
        # let RAPT install Android SDK and Apache ANT if needed
        os.environ["PGS4A_NO_TERMS"] = "True"
        from rapt.buildlib import install_sdk as installsdk
        os.chdir(os.path.join(self.myPath, "rapt/"))
        p = Process(target=installsdk.install_sdk(self.ifwrapper))
        p.start()

# general support functions
    def find(self, name, path=None, executable=False):
        if path is None:
            if self.myOS == "win":
                path = "c:\\"
            elif self.myOS == "lin" or self.myOS == "mac":
                path = "/"

        for root, dirs, files in os.walk(path):
            if name in files and (executable == os.access(name, os.X_OK)):
                return os.path.join(root, name)

        return None

    def run(*args):
        import traceback
        import subprocess
        try:
            subprocess.check_call(args[1:])
            return True
        except:
            traceback.print_exc()
            return False

    def chooseGame(self, wizard):
        # set game path and try to load existing configuration
        selectedPath = askdirectory()
        if self.find("options.rpy", selectedPath) is None:
            tkMessageBox.showerror("Error", "The directory you have selected does not seem to be a Ren'Py game.")
            if not self.find("options.rpy", self.gamePath.get()):
                wizard.nextbtn().configure(state="disabled")
        else:
            self.gamePath.set(selectedPath)
            from rapt.buildlib import configure
            self.gameInfo = configure.Configuration(self.gamePath.get())
            self.updateConfigGUI(self.gameInfo.__dict__)
            wizard.nextbtn().configure(state="enabled")

    def updateConfigGUI(self, configDict):
        if configDict["name"] is '':
            configDict["name"] = "The title of your game."
        if configDict["package"] is '':
            configDict["package"] = "com.yourdomain.yourgame"
        if configDict["version"] is '':
            configDict["version"] = "1.0"

        self.gameTitle.set(configDict["name"])
        self.gamePackage.set(configDict["package"])
        self.gameVersion.set(configDict["version"])
        self.gameOrientation.set(configDict["orientation"])

    def updateConfig(self, wizard):
        self.gameInfo.name = self.gameTitle.get()
        self.gameInfo.icon_name = self.gameTitle.get()
        self.gameInfo.package = self.gamePackage.get()
        self.gameInfo.orientation = self.gameOrientation.get()
        from rapt.buildlib import configure
        configure.set_version(self.gameInfo, self.gameVersion.get())
        self.gameInfo.save(self.gamePath.get())
        if self.gameTitle.get() != '' and self.gamePackage.get() != '' and self.gameOrientation.get() != '' and self.gameVersion.get() != '':
            return True
        else:
            return False

    def validateChooseGame(self, wizard):
        if self.gamePath.get() == '' or self.keystore.get() == '':
            wizard.nextbtn().configure(state="disabled")

    def openGeneratePage(self, wizard):
        wizard._set_current(0)
        wizard.nextbtn().configure(text="Return")

    def generateKeystore(self, wizard, fromPage):
        from rapt.buildlib import plat
        if self.keystoreValidate():
            self.chooseKeystore(True)
            if not self.run(plat.keytool, "-genkey", "-keystore", self.keystore.get(), "-alias", "android", "-keyalg", "RSA", "-keysize", "2048", "-keypass", self.keyPassphrase.get(), "-storepass", self.keyPassphrase.get(), "-dname", "CN=" + self.orgName.get(), "-validity", "20000"):
                tkMessageBox.showerror(title='Key generation failed', message="Please make sure you have permission to write the file you have selected and try again.")
                self.keystore.set('')
            else:
                self.keypass.set(self.keyPassphrase.get())
                self.storepass.set(self.keyPassphrase.get())
                self.keyAlias.set("android")
                self.ifwrapper.success("Key saved to " + self.keystore.get())
                wizard._set_current(fromPage)
        else:
            tkMessageBox.showerror(title='Missing Information', message="Please enter both an organisation name and a pass phrase for the keystore.")

    def keystoreValidate(self):
        if self.orgName.get() != "" and self.keyPassphrase.get() != "":
            return True
        else:
            return False

    def chooseKeystore(self, generate=False):
        if generate:
            self.keystore.set(asksaveasfilename())
        else:
            self.keystore.set(askopenfilename())

    def getImageDir(self, wizard):
        imageDir = askdirectory()
        warningString = "There are some images missing from the images directory at\n" + str(imageDir) + "\n\nMake sure the following images exist in this folder:\n\n"
        showWarning = False
        for image in self.requiredImages.keys():
            if not os.path.exists(os.path.join(imageDir, image)):
                showWarning = True
                warningString += image + " " + self.requiredImages[image] + "\n"
        if showWarning:
            tkMessageBox.showerror(title="Missing images", message=warningString)
            wizard.nextbtn().configure(state="disabled")
        elif self.updateConfig(wizard):
            self.imagesPath.set(imageDir)
            wizard.nextbtn().configure(command=lambda: self.doBuild())
            wizard.nextbtn().configure(state="enabled")

    def doBuild(self):
        from rapt.buildlib import plat

        # check executable permission on zipalign tool (sigh)
        zipalign = os.path.join(self.myPath, "rapt/android-sdk/tools/zipalign")
        if not os.access(zipalign, os.X_OK):
            if plat.macintosh or plat.linux:
                os.chmod(zipalign, 0744)

        # copy keystore file
#        keystoreTarget = os.path.join(self.raptPath.get(), "android.keystore")
#        if self.keystore.get() != keystoreTarget:
#            if os.path.exists(keystoreTarget):
#                try:
#                    shutil.move(keystoreTarget, os.path.join(self.raptPath.get(), "android.keystore.backup"))
#                except OSError:
#                    tkMessageBox.showerror(title="Keystore file already exists", message="The signing key file at " + keystoreTarget + " already exists! Please remove or rename it.")
#                    return
#            shutil.copyfile(self.keystore.get(), keystoreTarget)

        # copy images
        # create necessary folders
        for subdir in ["ldpi", "mdpi", "hdpi", "xhdpi", "xxhdpi"]:
            subdir = os.path.join(self.raptPath.get(), "res/drawable-" + subdir)
            if not os.path.exists(subdir):
                os.makedirs(subdir)

        for file in os.listdir(self.imagesPath.get()):
            # skip OSX's special folders
            if file[:1] == ".":
                continue

            fullFile = os.path.join(self.imagesPath.get(), file)
            if file == "presplash.png":
                shutil.copyfile(fullFile, os.path.join(self.gamePath.get(), "android-presplash.png"))
            elif file == "ouya_icon.png":
                shutil.copyfile(fullFile, os.path.join(self.raptPath.get(), "res/drawable-xhdpi/ouya_icon.png"))
            else:
                targetDir = os.path.join(self.raptPath.get(), "res/drawable-" + file[:-4])
                shutil.copyfile(fullFile, os.path.join(targetDir + "/icon.png"))
            # copy 144x144 icon to default path
            if file == "xxhdpi.png":
                shutil.copyfile(fullFile, os.path.join(self.gamePath.get(), "android-icon.png"))

        # ONWARDS
        os.chdir(os.path.join(self.myPath, "rapt/"))
        from rapt.buildlib import build as raptbuild
        raptbuild.build(self.ifwrapper, self.gamePath.get(), ["release"])

        # check for the finished file and copy it out, then exit

        unsignedFile = ""
        unalignedFile = ""
        finishedFile = self.gamePackage.get() + ".apk"

        for file in os.listdir(os.path.join(self.raptPath.get(), "bin/")):
            if file.endswith("-unsigned.apk"):
                apkPrefix = file[:-13]
                unsignedFile = file
                unalignedFile = apkPrefix + "-unaligned.apk"

        if unsignedFile != "" and not os.path.exists(os.path.join(self.raptPath.get(), "bin/" + unalignedFile)):
            # unsigned file exists, unaligned file does not
            jarsigner = os.path.join(self.jdkPath.get(), "bin/jarsigner")

            if plat.windows:
                jarsigner += ".exe"

            if not self.run(jarsigner, "-keystore", self.keystore.get(), "-sigalg", "SHA1withRSA", "-digestalg", "SHA1", "-storepass", self.storepass.get(), "-keypass", self.keypass.get(), os.path.join(self.raptPath.get(), "bin/" + unsignedFile), self.keyAlias.get()):
                self.ifwrapper.fail("Build succeeded, but signing failed!\n\nCheck https://developer.android.com/tools/publishing/app-signing.html#signapp on how to do this manually.\n\nYou can now save the unsigned file somewhere.")
                shutil.copyfile(unsignedFile, asksaveasfilename(defaultextension="apk", initialfile=self.gamePackage.get() + "-unsigned.apk"))
                exit()
            else:
                shutil.move(os.path.join(self.raptPath.get(), "bin/" + unsignedFile), os.path.join(self.raptPath.get(), "bin/" + unalignedFile))

        if unalignedFile != "" and not os.path.exists(os.path.join(self.raptPath.get(), "bin/" + apkPrefix + ".apk")):
            # unaligned file exists, final release file does not
            alignedFile = asksaveasfilename(defaultextension="apk", initialfile=self.gamePackage.get() + ".apk")
            if not self.run(zipalign, "-f", "4", os.path.join(self.raptPath.get(), "bin/" + unalignedFile), alignedFile):
                self.ifwrapper.fail("Package is signed, but zipalign failed!\n\nCheck https://developer.android.com/tools/publishing/app-signing.html#align on how to do this manually.\n\nYou can now save the signed file somewhere.")
                shutil.copyfile(unalignedFile, asksaveasfilename(defaultextension="apk", initialfile=self.gamePackage.get() + "-unaligned.apk"))
                exit()

        self.ifwrapper.success("Build succeeded! Your finished .apk is saved as " + alignedFile + "!")
        exit()

    def buildGUI(self):
        wizard = Wizard(npages=self.wizPages, padding=0)
        wizard.master.minsize(640, 400)
        currentPage = 0

    # key generation
        keystorePage = ttk.Frame(wizard.page_container(currentPage))
        ttk.Label(keystorePage, justify="right", text="RAPT Wizard v1: Generate Keystore\n\n").grid(column=0, row=0, sticky=E, columnspan=4)
        ttk.Label(keystorePage, justify="left", wraplength=640, text="This page will allow you to generate an Android signing key.\n\nYou will need this to sign an Android package so it is accepted by app stores. You should keep this file safe and make backups so you can reuse it for future releases.\n\n").grid(column=0, row=1, sticky=W, columnspan=3)
        ttk.Label(keystorePage, text="Organisation Name:").grid(column=0, row=2, sticky=W)
        orgEntry = ttk.Entry(keystorePage, textvariable=self.orgName, width=48, validatecommand=self.keystoreValidate())
        orgEntry.grid(column=1, row=2, sticky=W)
        orgHelp = ToolTip(orgEntry, text="The \"developer name\" you release games under.")
        ttk.Label(keystorePage, text="Passphrase:").grid(column=0, row=3, sticky=W)
        passphraseEntry = ttk.Entry(keystorePage, textvariable=self.keyPassphrase, width=48, validatecommand=self.keystoreValidate())
        passphraseEntry.grid(column=1, row=3, sticky=W)
        passHelp = ToolTip(passphraseEntry, text="A secret passphrase used to secure the signing key. You will need to enter this to sign Android apps.")
#        ttk.Label(keystorePage, text="Keystore file:").grid(column=0, row=4, sticky=W)
        saveKeystore = ttk.Button(keystorePage, text="Save key as...", command=lambda: self.generateKeystore(wizard, currentPage - 1))
        saveKeystore.grid(column=1, row=4, sticky=E)
        keystoreHelp = ToolTip(saveKeystore, text="Generates a signing key and saves it to a file.")
        wizard.add_page_body(keystorePage)
        wizard.pack(fill='both', expand=True)
        currentPage += 1

    # prerequisites: JDK
        if not self.foundJDK:
            print("Adding page for JDK.")
            getJDKPage = ttk.Frame(wizard.page_container(currentPage))
            currentPage += 1
            ttk.Label(getJDKPage, justify="right", text="RAPT Wizard v1: JDK Installation\n\n").grid(column=0, row=0, sticky=E, columnspan=4)
            ttk.Label(getJDKPage, justify="left", wraplength=640, text="JDK not found.\n\nThe Java Development Kit is required for RAPT to work. If you have the JDK installed already, you can choose its main directory to make use of that installation.\nAlternately, RAPT Wizard can either search your entire computer for a JDK installation (this may take a while) or take you to the download site.\n\n").grid(column=0, row=1, sticky=W, columnspan=4)
            ttk.Label(getJDKPage, text="JDK directory:").grid(column=0, row=2, sticky=W)
            ttk.Entry(getJDKPage, textvariable=self.pythonPath, width=48).grid(column=1, row=2, sticky=W)
            ttk.Button(getJDKPage, text="Choose...", command=lambda: self.jdkPath.set(askopenfilename())).grid(column=2, row=2, sticky=E)
            ttk.Button(getJDKPage, text="Download JDK", command=lambda: self.getJDK()).grid(column=1, row=3, sticky=E)
            ttk.Button(getJDKPage, text="Search...", command=lambda: self.findJDK()).grid(column=2, row=3, sticky=E)

    # prerequisites: Python
        if not self.foundPython:
            print("Adding page for Python.")
            getPythonPage = ttk.Frame(wizard.page_container(currentPage))
            currentPage += 1
            ttk.Label(getPythonPage, justify="right", text="RAPT Wizard v1: Python Installation\n\n").grid(column=0, row=0, sticky=E, columnspan=4)
            ttk.Label(getPythonPage, justify="left", wraplength=640, text="Python not found.\n\nA Python installation is required for RAPT. If you have Python installed already, you can choose its main executable to make use of that installation.\nAlternately, RAPT Wizard can either search for a Python installation (this may take a while) or take you to the download site.\n\n").grid(column=0, row=1, sticky=W, columnspan=4)
            ttk.Label(getPythonPage, text="Python executable:").grid(column=0, row=2, sticky=W)
            ttk.Entry(getPythonPage, textvariable=self.pythonPath, width=48).grid(column=1, row=2, sticky=W)
            ttk.Button(getPythonPage, text="Choose...", command=lambda: self.pythonPath.set(askopenfilename())).grid(column=2, row=2, sticky=E)
            ttk.Button(getPythonPage, text="Download Python", command=lambda: self.getPython()).grid(column=1, row=3, sticky=E)
            ttk.Button(getPythonPage, text="Search...", command=lambda: self.findPython(True)).grid(column=2, row=3, sticky=E)
            wizard.add_page_body(getPythonPage)
            wizard.pack(fill='both', expand=True)

    # prerequisites: RAPT
        if not self.foundRAPT:
            getRAPTPage = ttk.Frame(wizard.page_container(currentPage))
            currentPage += 1
            ttk.Label(getRAPTPage, justify="right", text="RAPT Wizard v1: RAPT Installation\n\n").grid(column=0, row=0, sticky=E, columnspan=4)
            ttk.Label(getRAPTPage, justify="left", wraplength=640, text="RAPT not found.\n\nThere is no RAPT installation in this directory. If you have RAPT installed already, you can choose its installation directory to make use of that installation.\nAlternately, RAPT Wizard can either search for a RAPT installation or download and install it for you.\n\n").grid(column=0, row=1, sticky=W, columnspan=4)
            ttk.Label(getRAPTPage, text="RAPT directory:").grid(column=0, row=2, sticky=W)
            ttk.Entry(getRAPTPage, textvariable=self.raptPath, width=48).grid(column=1, row=2, sticky=W)
            ttk.Button(getRAPTPage, text="Choose...", command=lambda: self.chooseRAPT()).grid(column=2, row=2, sticky=E)
            ttk.Button(getRAPTPage, text="Download RAPT", command=lambda: self.getRapt()).grid(column=1, row=3, sticky=E)
            ttk.Button(getRAPTPage, text="Search...", command=lambda: self.findRAPT()).grid(column=2, row=3, sticky=E)
            wizard.add_page_body(getRAPTPage)
            wizard.pack(fill='both', expand=True)

    # choose game page
        chooseGamePage = ttk.Frame(wizard.page_container(currentPage))
        ttk.Label(chooseGamePage, justify="right", text="RAPT Wizard v1: Choose Game\n\n").grid(column=0, row=0, sticky=E, columnspan=4)
        ttk.Label(chooseGamePage, justify="left", wraplength=640, text="Please select the game you would like to make an Android build of.\n\n").grid(column=0, row=1, sticky=W, columnspan=4)
        ttk.Label(chooseGamePage, text="Game directory:").grid(column=0, row=2, sticky=W)
        gameDirEntry = ttk.Entry(chooseGamePage, state="readonly", textvariable=self.gamePath, width=48, validatecommand=lambda: self.validateChooseGame(wizard), validate="all")
        gameDirEntry.grid(column=1, row=2, sticky=W)
        ToolTip(gameDirEntry, text="This is the directory of the game you want to make an Android build of.")
        ttk.Button(chooseGamePage, text="Choose...", command=lambda: self.chooseGame(wizard)).grid(column=2, row=2, sticky=E)
        ttk.Label(chooseGamePage, text="Android keystore:").grid(column=0, row=3, sticky=W)
        keystoreEntry = ttk.Entry(chooseGamePage, state="readonly", textvariable=self.keystore, width=48, validatecommand=lambda: self.validateChooseGame(wizard), validate="all")
        keystoreEntry.grid(column=1, row=3, sticky=W)
        ToolTip(keystoreEntry, text="The keystore is the local copy of your Android signing key. You need to have one to build Android apps.")
        chooseKeystoreButton = ttk.Button(chooseGamePage, text="Choose...", command=lambda: self.chooseKeystore()).grid(column=2, row=3, sticky=E)
        generateKeystoreButton = ttk.Button(chooseGamePage, text="Generate", command=lambda: self.openGeneratePage(wizard)).grid(column=3, row=3, sticky=E)

        ttk.Label(chooseGamePage, text="Key file password:").grid(column=0, row=7, sticky=W)
        storepassEntry = ttk.Entry(chooseGamePage, textvariable=self.storepass, width=48)
        storepassEntry.grid(column=1, row=7, sticky=W)
        ToolTip(storepassEntry, text="The password for the key file you have selected.")
        ttk.Label(chooseGamePage, text="Signing key alias:").grid(column=0, row=8, sticky=W)
        keyAliasEntry = ttk.Entry(chooseGamePage, textvariable=self.keyAlias, width=48)
        keyAliasEntry.grid(column=1, row=8, sticky=W)
        ToolTip(keyAliasEntry, text="The alias of the signing key you want to use.")
        ttk.Label(chooseGamePage, text="Signing key password:").grid(column=0, row=9, sticky=W)
        keypassEntry = ttk.Entry(chooseGamePage, textvariable=self.keypass, width=48)
        keypassEntry.grid(column=1, row=9, sticky=W)
        ToolTip(keypassEntry, text="The password for the specific signing key.")

        wizard.add_page_body(chooseGamePage)
        wizard.pack(fill='both', expand=True)
        currentPage += 1
        wizard._set_current(1)

    # build configuration
        configurePage = ttk.Frame(wizard.page_container(currentPage))
        ttk.Label(configurePage, justify="right", text="RAPT Wizard v1: Game Settings\n\n").grid(column=0, row=0, sticky=E, columnspan=4)
        ttk.Label(configurePage, justify="left", wraplength=640, text="This is some information needed for building the Android version of your game.\n\n").grid(column=0, row=1, sticky=W, columnspan=4)
        ttk.Label(configurePage, text="Title:").grid(column=0, row=2, sticky=W)
        titleEntry = ttk.Entry(configurePage, textvariable=self.gameTitle, validate="focusout", validatecommand=lambda: self.updateConfig(wizard), width=48)
        titleEntry.grid(column=1, row=2, sticky=W)
        titleHelp = ToolTip(titleEntry, text="The title of your game.")
        ttk.Label(configurePage, text="Package Name:").grid(column=0, row=3, sticky=W)
        pkgEntry = ttk.Entry(configurePage, textvariable=self.gamePackage, validatecommand=lambda: self.updateConfig(wizard), width=48)
        pkgEntry.grid(column=1, row=3, sticky=W)
        pkgNameHelp = ToolTip(pkgEntry, text="The Android package name for your game. This MUST be unique.\nThe convention is to use your domain name (reversed for sorting purposes) followed by the name of your product, e.g.\n\ncom.mydomain.mygame\n\nFor further info, google up \"Java package naming conventions\".")
        ttk.Label(configurePage, text="Game Version:").grid(column=0, row=4, sticky=W)
        versionEntry = ttk.Entry(configurePage, textvariable=self.gameVersion, validatecommand=lambda: self.updateConfig(wizard), width=48)
        versionEntry.grid(column=1, row=4, sticky=W)
        versionHelp = ToolTip(versionEntry, text="The version number of your game. This should be numeric.")
        ttk.Label(configurePage, text="Screen Orientation:").grid(column=0, row=5, sticky=W)
        orientationBox = ttk.Combobox(configurePage, state="readonly", textvariable=self.gameOrientation, values=("landscape", "portrait"), validate="focusout", validatecommand=lambda: self.updateConfig(wizard))
        orientationBox.current(0)
        orientationBox.grid(column=1, row=5, sticky=W)
        orientationHelp = ToolTip(orientationBox, text="The screen orientation you would like the game to run in.")
        ttk.Label(configurePage, text="Image directory:").grid(column=0, row=6, sticky=W)
        imageDirEntry = ttk.Entry(configurePage, textvariable=self.imagesPath, state="readonly", width=48)
        imageDirEntry.grid(column=1, row=6, sticky=W)
        ToolTip(imageDirEntry, text="The directory containing the images for the build.\n\nThis MUST have at least the following files:\n\nldpi.png (36x36 app icon)\nmdpi.png (48x48 app icon)\nhdpi.png (72x72 app icon)\nxhdpi.png (96x96 app icon)\nxxhdpi.png (144x144 app icon)\npresplash.png (loading screen the same size as your game screen)\n\nOptionally, you can include ouya_icon.png (732x412) if you want your build to work on the OUYA store.")
        ttk.Button(configurePage, text="Choose...", command=lambda: self.getImageDir(wizard)).grid(column=3, row=6, sticky=E)
        wizard.add_page_body(configurePage)
        wizard.pack(fill='both', expand=True)

#        wizard.nextbtn().configure(state="disabled")

#        wizard.nextbtn().configure(command=lambda: self.updateConfig(wizard))

        # ttk.Label(gameinfo, text="Game icon:").grid(column=0, row=1, sticky=W)
        # ttk.Entry(gameinfo, textvariable=gameicon, width=48).grid(column=2, row=1, sticky=W)
        # ttk.Button(gameinfo, text="Choose...", command=lambda: gameicon.set(askopenfilename())).grid(column=3, row=1, sticky=E)

        # ttk.Label(gameinfo, text="OUYA icon:").grid(column=0, row=2, sticky=W)
        # ttk.Entry(gameinfo, textvariable=ouyaicon, width=48).grid(column=2, row=2, sticky=W)
        # ttk.Button(gameinfo, text="Choose...", command=lambda: ouyaicon.set(askopenfilename())).grid(column=3, row=2, sticky=E)

        # ttk.Label(gameinfo, text="Loading screen:").grid(column=0, row=3, sticky=W)
        # ttk.Entry(gameinfo, textvariable=loadscreen, width=48).grid(column=2, row=3, sticky=W)
        # ttk.Button(gameinfo, text="Choose...", command=lambda: loadscreen.set(askopenfilename())).grid(column=3, row=3, sticky=E)

        # ttk.Button(mainframe, text="Build!", command=lambda: doBuild()).grid(column=2, row=0, sticky=E)

wizard = raptWizard()
