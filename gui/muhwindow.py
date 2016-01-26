import gtk, pygtk, os
from multiprocessing import Process
from gtkcodebuffer import SyntaxLoader, CodeBuffer

class Base:
    def __init__(self):
        #create the window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_default_size(640, 480)
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("key-press-event", self.macroCallback)
        self.window.show()

        #create vbox for menubar and text editor
        self.box = gtk.VBox(False, 0)
        self.window.add(self.box)
        self.box.show()

        #create menubar
        self.mbar = gtk.MenuBar()
        self.box.pack_start(self.mbar, False, False, 0)
        self.mbar.show()

        #File
        self.filem = gtk.MenuItem("File")
        self.filem.show()
        
        self.filemenu = gtk.Menu()
        self.filem.set_submenu(self.filemenu)

        self.new_file = gtk.MenuItem("New    ctrl+n")
        self.filemenu.append(self.new_file)
        self.new_file.connect("activate", self.userNewFile)
        self.new_file.show()
      
        self.open_file = gtk.MenuItem("Open File... ctrl+o")
        self.open_file.connect("activate", self.userOpenFile)
        self.filemenu.append(self.open_file)
        self.open_file.show()

        self.close_file = gtk.MenuItem("Close File... ctrl+w")
        self.close_file.connect("activate", self.removeCurrentPage)
        self.filemenu.append(self.close_file)
        self.close_file.show()

        self.save_file = gtk.MenuItem("Save    ctrl+s")
        self.save_file.connect("activate", self.userSaveFile)
        self.filemenu.append(self.save_file)
        self.save_file.show()

        self.save_file_as = gtk.MenuItem("Save As... ctrl+shift+s")
        self.save_file_as.connect("activate", self.userSaveFileAs)
        self.filemenu.append(self.save_file_as)
        self.save_file_as.show()

        self.exit = gtk.MenuItem("Exit    ctrl+shift+e")
        self.exit.connect("activate", self.quit)
        self.filemenu.append(self.exit)
        self.exit.show()

        #Game
        self.gamem = gtk.MenuItem("Game")
        self.gamem.show()
        
        self.gamemenu = gtk.Menu()
        self.gamem.set_submenu(self.gamemenu)

        self.new_game = gtk.MenuItem("Start New Game... ctrl+g")
        self.new_game.connect("activate", self.newGameDialog)
        self.gamemenu.append(self.new_game)
        self.new_game.show()

        self.mbar.append(self.filem)
        self.mbar.append(self.gamem)

        #create notebook (for files)
        self.file_notebook = gtk.Notebook()
        self.file_notebook.set_tab_pos(gtk.POS_TOP)
        self.box.pack_start(self.file_notebook, True, True, 0)
        self.file_notebook.show()

    def macroCallback(self, widget, data=None):
        keyval = data.keyval
        keyval_name = gtk.gdk.keyval_name(keyval)
        state = data.state
        ctrl = (state & gtk.gdk.CONTROL_MASK)
        if ctrl:
            if keyval_name == 's':
                self.userSaveFile(None)
            elif keyval_name == 'S':
                self.userSaveFileAs(None)
            elif keyval_name == 'o':
                self.userOpenFile(None)
            elif keyval_name == 'n':
                self.userNewFile(None)
            elif keyval_name == 'w':
                self.removeCurrentPage(None)
            elif keyval_name == 'E':
                self.quit(None)
            elif keyval_name == 'g':
                self.newGameDialog(None)

    def userNewFile(self, widget, data=None):
        tab_box = gtk.HBox(False, 0)
        tab_box.show()

        new_file_label = gtk.Label("Untitled")
        tab_box.pack_start(new_file_label, False, False, 5)
        new_file_label.show()

        close_button = gtk.Button("X")
        tab_box.pack_start(close_button, False, False, 5)
        close_button.show()

        scrolledwindow = gtk.ScrolledWindow()
        scrolledwindow.show()

        lang = SyntaxLoader("python")
        buff = CodeBuffer(lang=lang)
        textview = gtk.TextView(buff)
        textview.connect("key-press-event", self.markFileAsModified)
        textview.filepath = "" #so we don't get an error when we try to save
        scrolledwindow.add(textview)
        textview.show()

        self.file_notebook.append_page(scrolledwindow, tab_box)
        close_button.connect("clicked", self.removePage, scrolledwindow)

    def markFileAsModified(self, widget, data=None):
        keyval = data.keyval
        keyval_name = gtk.gdk.keyval_name(keyval)
        state = data.state
        ctrl = (state & gtk.gdk.CONTROL_MASK)
        if ctrl: return

        current_page_index = self.file_notebook.get_current_page()
        if current_page_index >= 0:
            current_page = self.file_notebook.get_nth_page(current_page_index)
            
            tab_box = gtk.HBox(False, 0)
            tab_box.show()

            child = current_page.get_child()
            if child.filepath != "":
                label = gtk.Label("*"+os.path.basename(child.filepath))
            else:
                label = gtk.Label("*Untitled")
            tab_box.pack_start(label, False, False, 5)
            label.show()

            close_button = gtk.Button("X")
            tab_box.pack_start(close_button, False, False, 5)
            close_button.show()

            self.file_notebook.set_tab_label(current_page, tab_box)
            close_button.connect("clicked", self.removePage, child)

    def userOpenFile(self, widget, data=None):
        chooser = gtk.FileChooserDialog(title=None, action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                        buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        chooser.show()

        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            #read file
            filepath = chooser.get_filename()
            fo = open(filepath, "r")
            text = fo.read()
            fo.close()

            #put text into textview
            #create (and pack some stuff into) box for page's label
            tab_box = gtk.HBox(False, 0)
            tab_box.show()

            file_label = gtk.Label(os.path.basename(filepath))
            tab_box.pack_start(file_label, False, False, 5)
            file_label.show()

            close_button = gtk.Button("X")
            tab_box.pack_start(close_button, False, False, 5)
            close_button.show()

            scrolledwindow = gtk.ScrolledWindow()
            scrolledwindow.show()

            lang = SyntaxLoader("python")
            buff = CodeBuffer(lang=lang)
            textview = gtk.TextView(buff)
            textview.connect("key-press-event", self.markFileAsModified)
            textview.filepath = filepath #storing so we can save file later
            scrolledwindow.add(textview)
            textview.show()

            textv_buffer = textview.get_buffer()
            textv_buffer.set_text(text)

            self.file_notebook.append_page(scrolledwindow, tab_box)
            close_button.connect("clicked", self.removePage, scrolledwindow)
        chooser.destroy()
 
    def userSaveFile(self, widget, data=None):
        current_page_index = self.file_notebook.get_current_page()
        if current_page_index >= 0:
            current_page = self.file_notebook.get_nth_page(current_page_index)
            child = current_page.get_child()
            tbuffer = child.get_buffer()
            start_iter, end_iter = tbuffer.get_start_iter(), tbuffer.get_end_iter()
            file_text = tbuffer.get_text(start_iter, end_iter)
            file_path = child.filepath

            if file_path == "":
                self.userSaveFileAs(None)
            else:
                #in case we have the little file modified asterisk
                tab_box = gtk.HBox(False, 0)
                tab_box.show()

                label = gtk.Label(os.path.basename(file_path))
                tab_box.pack_start(label, False, False, 5)
                label.show()

                close_button = gtk.Button("X")
                close_button.connect("clicked", self.removePage, child)
                tab_box.pack_start(close_button, False, False, 5)
                close_button.show()

                self.file_notebook.set_tab_label(current_page, tab_box)

                #write to file (saving)
                fo = open(file_path, "w")
                fo.write(file_text)
                fo.close()

    def userSaveFileAs(self, widget, data=None):
        current_page_index = self.file_notebook.get_current_page()
        if current_page_index >= 0:
            #get text from textview on current page
            current_page = self.file_notebook.get_nth_page(current_page_index)
            child = current_page.get_child()
            tbuffer = child.get_buffer()
            start_iter, end_iter = tbuffer.get_start_iter(), tbuffer.get_end_iter()
            file_text = tbuffer.get_text(start_iter, end_iter)
            #write the information to desired file
            chooser = gtk.FileChooserDialog(title=None, action=gtk.FILE_CHOOSER_ACTION_SAVE,
                                            buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
            chooser.show()
            response = chooser.run()
            if response == gtk.RESPONSE_OK:
                filepath = chooser.get_filename()
                child.filepath = filepath
                fo = open(filepath, "w")
                fo.write(file_text)
                fo.close()
                #change the page's title to our newly saved file
                filename = os.path.basename(filepath)
                tab_box = gtk.HBox(False, 0)
                tab_box.show()

                label = gtk.Label(filename)
                tab_box.pack_start(label, False, False, 5)
                label.show()

                close_button = gtk.Button("X")
                tab_box.pack_start(close_button, False, False, 5)
                close_button.show()

                self.file_notebook.set_tab_label(current_page, tab_box)
                close_button.connect("clicked", self.removePage, child)
            chooser.destroy()

    def removeCurrentPage(self, widget, data=None):
        page_num = self.file_notebook.get_current_page()
        self.file_notebook.remove_page(page_num)

    def removePage(self, widget, data=None):
        page_num = self.file_notebook.page_num(data)
        self.file_notebook.remove_page(page_num)

    def chooseFile(self, widget, data=None):
        chooser = gtk.FileChooserDialog(title=None, action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                        buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,
                                        gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        chooser.show()
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            filepath = chooser.get_filename()
            data.set_text(filepath)
        chooser.destroy()

    def selectAIFile(self, widget, data=None):
        "Where data is the file label to change"
        dialog = gtk.Dialog(title="Choose AI")
        dialog.set_default_size(500, 300)
        dialog.vbox.set_spacing(20)
        dialog.vbox.set_homogeneous(True)
        dialog.show()

        #stuff for choosing from example ai
        example_ai_hbox = gtk.HBox(False, 15)
        dialog.vbox.pack_start(example_ai_hbox)
        example_ai_hbox.show()

        example_ai_label = gtk.Label("Choose Example AI: ")
        example_ai_hbox.pack_start(example_ai_label, expand=False, fill=False)
        example_ai_label.show()

        example_ai_cbox = gtk.combo_box_new_text()
        example_ai_cbox.append_text("Pacifist")
        example_ai_cbox.append_text("Aggressor")
        example_ai_cbox.append_text("Proliferate")
        example_ai_cbox.append_text("Midway")
        example_ai_hbox.pack_start(example_ai_cbox)
        example_ai_cbox.show()

        def fromExampleOk():
            active = example_ai_cbox.get_active()
            path = ""
            if active == 0:
                path = os.path.abspath("../engine/ai_samples/pacifist.py")
            elif active == 1:
                path = os.path.abspath("../engine/ai_samples/aggressor.py")
            elif active == 2:
                path = os.path.abspath("../engine/ai_samples/proliferate.py")
            elif active == 3:
                path = os.path.abspath("../engine/ai_samples/midway.py")
            else:
                path = "null"
            data.set_text(path)
            dialog.destroy()

        example_ai_ok = gtk.Button("   OK   ")
        example_ai_ok.connect("clicked", lambda x: fromExampleOk())
        example_ai_hbox.pack_start(example_ai_ok, expand=False, fill=False)
        example_ai_ok.show()

        #stuff for choosing from file
        file_ai_hbox = gtk.HBox(False, 15)
        dialog.vbox.pack_start(file_ai_hbox)
        file_ai_hbox.show()

        file_ai_label = gtk.Label("Choose AI From File: ")

        file_ai_filelabelsw = gtk.ScrolledWindow()
        file_ai_filelabel = gtk.Label("null")
        file_ai_filelabel.show()
        file_ai_filelabelsw.add_with_viewport(file_ai_filelabel)
        file_ai_hbox.pack_start(file_ai_filelabelsw)
        file_ai_filelabelsw.show()

        file_ai_filebutton = gtk.Button(" Open ")
        file_ai_filebutton.connect("clicked", self.chooseFile, file_ai_filelabel)
        file_ai_hbox.pack_start(file_ai_filebutton, expand=False, fill=False)
        file_ai_filebutton.show()

        def fromFileOk():
            data.set_text(file_ai_filelabel.get_text())
            dialog.destroy()

        file_ai_okbutton = gtk.Button("   OK   ")
        file_ai_okbutton.connect("clicked", lambda x: fromFileOk())
        file_ai_hbox.pack_start(file_ai_okbutton, expand=False, fill=False)
        file_ai_okbutton.show()

        #cancel the dialog
        cancel_button = gtk.Button("Cancel")
        cancel_button.connect("clicked", lambda x: dialog.destroy())
        dialog.vbox.pack_start(cancel_button)
        cancel_button.show()

    def removeAIFile(self, widget, data=None):
        "Where data is the file label to change"
        data.set_text("null")

    def startGame(self, widget, data=None):
        arg_string = "python ../engine/Run.py "
        for i in data:
            arg_string += "\""+i.get_text()+"\""+" "
        new_game = Process(target = os.system, args=(arg_string,))
        new_game.start()
 
    def newGameDialog(self, widget, data=None):
        dialog = gtk.Dialog(title="Start New Game", parent=self.window)
        dialog.set_default_size(500, 300)
        dialog.vbox.set_spacing(2)
        dialog.vbox.set_homogeneous(True)
        dialog.show()

        #some labels have (seemingly) superfluous spaces to make everything pretty!
        #red
        redhbox = gtk.HBox(False, 5)
        redhbox.show()
        dialog.vbox.pack_start(redhbox)

        redlabel = gtk.Label("Red:       ")
        redhbox.pack_start(redlabel, expand=False, fill=False)
        redlabel.show()

        redfilelabel = gtk.Label("null")
        redfilelabelscrolledwindow = gtk.ScrolledWindow()
        redhbox.pack_start(redfilelabelscrolledwindow)
        redfilelabelscrolledwindow.add_with_viewport(redfilelabel)
        redfilelabelscrolledwindow.show()
        redfilelabel.show()

        redfilebutton = gtk.Button("Assign")
        redfilebutton.connect("clicked", self.selectAIFile, redfilelabel)
        redhbox.pack_start(redfilebutton, expand=False, fill=False)
        redfilebutton.show()

        redremovebutton = gtk.Button("Remove")
        redremovebutton.connect("clicked", self.removeAIFile, redfilelabel)
        redhbox.pack_start(redremovebutton, expand=False, fill=False)
        redremovebutton.show()


        #orange
        orangehbox = gtk.HBox(False, 5)
        orangehbox.show()
        dialog.vbox.pack_start(orangehbox)

        orangelabel = gtk.Label("Orange: ")
        orangehbox.pack_start(orangelabel, expand=False, fill=False)
        orangelabel.show()

        orangefilelabel = gtk.Label("null")
        orangefilelabelscrolledwindow = gtk.ScrolledWindow()
        orangehbox.pack_start(orangefilelabelscrolledwindow)
        orangefilelabelscrolledwindow.add_with_viewport(orangefilelabel)
        orangefilelabelscrolledwindow.show()
        orangefilelabel.show()

        orangefilebutton = gtk.Button("Assign")
        orangefilebutton.connect("clicked", self.selectAIFile, orangefilelabel)
        orangehbox.pack_start(orangefilebutton, expand=False, fill=False)
        orangefilebutton.show()

        orangeremovebutton = gtk.Button("Remove")
        orangeremovebutton.connect("clicked", self.removeAIFile, orangefilelabel)
        orangehbox.pack_start(orangeremovebutton, expand=False, fill=False)
        orangeremovebutton.show()

        #yellow
        yellowhbox = gtk.HBox(False, 5)
        yellowhbox.show()
        dialog.vbox.pack_start(yellowhbox)

        yellowlabel = gtk.Label("Yellow:   ")
        yellowhbox.pack_start(yellowlabel, expand=False, fill=False)
        yellowlabel.show()

        yellowfilelabel = gtk.Label("null")
        yellowfilelabelscrolledwindow = gtk.ScrolledWindow()
        yellowhbox.pack_start(yellowfilelabelscrolledwindow)
        yellowfilelabelscrolledwindow.add_with_viewport(yellowfilelabel)
        yellowfilelabelscrolledwindow.show()
        yellowfilelabel.show()

        yellowfilebutton = gtk.Button("Assign")
        yellowfilebutton.connect("clicked", self.selectAIFile, yellowfilelabel)
        yellowhbox.pack_start(yellowfilebutton, expand=False, fill=False)
        yellowfilebutton.show()

        yellowremovebutton = gtk.Button("Remove")
        yellowremovebutton.connect("clicked", self.removeAIFile, yellowfilelabel)
        yellowhbox.pack_start(yellowremovebutton, expand=False, fill=False)
        yellowremovebutton.show()

        #green
        greenhbox = gtk.HBox(False, 5)
        greenhbox.show()
        dialog.vbox.pack_start(greenhbox)

        greenlabel = gtk.Label("Green:   ")
        greenhbox.pack_start(greenlabel, expand=False, fill=False)
        greenlabel.show()

        greenfilelabel = gtk.Label("null")
        greenfilelabelscrolledwindow = gtk.ScrolledWindow()
        greenhbox.pack_start(greenfilelabelscrolledwindow)
        greenfilelabelscrolledwindow.add_with_viewport(greenfilelabel)
        greenfilelabelscrolledwindow.show()
        greenfilelabel.show()

        greenfilebutton = gtk.Button("Assign")
        greenfilebutton.connect("clicked", self.selectAIFile, greenfilelabel)
        greenhbox.pack_start(greenfilebutton, expand=False, fill=False)
        greenfilebutton.show()

        greenremovebutton = gtk.Button("Remove")
        greenremovebutton.connect("clicked", self.removeAIFile, greenfilelabel)
        greenhbox.pack_start(greenremovebutton, expand=False, fill=False)
        greenremovebutton.show()

        #blue
        bluehbox = gtk.HBox(False, 5)
        bluehbox.show()
        dialog.vbox.pack_start(bluehbox)

        bluelabel = gtk.Label("Blue:     ")
        bluehbox.pack_start(bluelabel, expand=False, fill=False)
        bluelabel.show()

        bluefilelabel = gtk.Label("null")
        bluefilelabelscrolledwindow = gtk.ScrolledWindow()
        bluehbox.pack_start(bluefilelabelscrolledwindow)
        bluefilelabelscrolledwindow.add_with_viewport(bluefilelabel)
        bluefilelabelscrolledwindow.show()
        bluefilelabel.show()

        bluefilebutton = gtk.Button("Assign")
        bluefilebutton.connect("clicked", self.selectAIFile, bluefilelabel)
        bluehbox.pack_start(bluefilebutton, expand=False, fill=False)
        bluefilebutton.show()

        blueremovebutton = gtk.Button("Remove")
        blueremovebutton.connect("clicked", self.removeAIFile, bluefilelabel)
        bluehbox.pack_start(blueremovebutton, expand=False, fill=False)
        blueremovebutton.show()

        #indigo
        indigohbox = gtk.HBox(False, 5)
        indigohbox.show()
        dialog.vbox.pack_start(indigohbox)

        indigolabel = gtk.Label("Indigo:  ")
        indigohbox.pack_start(indigolabel, expand=False, fill=False)
        indigolabel.show()

        indigofilelabel = gtk.Label("null")
        indigofilelabelscrolledwindow = gtk.ScrolledWindow()
        indigohbox.pack_start(indigofilelabelscrolledwindow)
        indigofilelabelscrolledwindow.add_with_viewport(indigofilelabel)
        indigofilelabelscrolledwindow.show()
        indigofilelabel.show()

        indigofilebutton = gtk.Button("Assign")
        indigofilebutton.connect("clicked", self.selectAIFile, indigofilelabel)
        indigohbox.pack_start(indigofilebutton, expand=False, fill=False)
        indigofilebutton.show()

        indigoremovebutton = gtk.Button("Remove")
        indigoremovebutton.connect("clicked", self.removeAIFile, indigofilelabel)
        indigohbox.pack_start(indigoremovebutton, expand=False, fill=False)
        indigoremovebutton.show()

        #violet
        violethbox = gtk.HBox(False, 5)
        violethbox.show()
        dialog.vbox.pack_start(violethbox)

        violetlabel = gtk.Label("Violet:  ")
        violethbox.pack_start(violetlabel, expand=False, fill=False)
        violetlabel.show()

        violetfilelabel = gtk.Label("null")
        violetfilelabelscrolledwindow = gtk.ScrolledWindow()
        violethbox.pack_start(violetfilelabelscrolledwindow)
        violetfilelabelscrolledwindow.add_with_viewport(violetfilelabel)
        violetfilelabelscrolledwindow.show()
        violetfilelabel.show()

        violetfilebutton = gtk.Button("Assign")
        violetfilebutton.connect("clicked", self.selectAIFile, violetfilelabel)
        violethbox.pack_start(violetfilebutton, expand=False, fill=False)
        violetfilebutton.show()

        violetremovebutton = gtk.Button("Remove")
        violetremovebutton.connect("clicked", self.removeAIFile, violetfilelabel)
        violethbox.pack_start(violetremovebutton, expand=False, fill=False)
        violetremovebutton.show()

        #begin simulation button
        ai_paths = [redfilelabel, orangefilelabel, yellowfilelabel,
                    greenfilelabel, bluefilelabel, indigofilelabel,
                    violetfilelabel]
        beginbutton = gtk.Button("Begin Simulation")
        beginbutton.connect("clicked", self.startGame, ai_paths)
        beginbuttonhbox = gtk.HBox(False, 0)
        dialog.vbox.pack_start(beginbuttonhbox, padding=10)
        beginbuttonhbox.pack_end(beginbutton, padding=20)
        beginbutton.show()
        beginbuttonhbox.show()

        #cancel button
        cancelbutton = gtk.Button("Cancel")
        cancelbutton.connect("clicked", lambda x: dialog.destroy())
        cancelbuttonhbox = gtk.HBox(False, 0)
        dialog.vbox.pack_start(cancelbuttonhbox, padding=10)
        cancelbuttonhbox.pack_end(cancelbutton, padding=20)
        cancelbutton.show()
        cancelbuttonhbox.show()

    def quit(self, widget, data=None):
        gtk.main_quit()

    def delete_event(self, widget, data=None):
        gtk.main_quit()

if __name__ == '__main__':
    base = Base()
    gtk.main()
