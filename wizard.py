import ttk
import Tkinter


class Wizard(object, ttk.Notebook):
    def __init__(self, master=None, **kw):
        npages = kw.pop('npages', 3)
        kw['style'] = 'Wizard.TNotebook'
        ttk.Style(master).layout('Wizard.TNotebook.Tab', '')
        ttk.Notebook.__init__(self, master, **kw)

        self._children = {}

        for page in range(npages):
            self.add_empty_page()

        self.current = 0
        self._wizard_buttons()

    def _wizard_buttons(self):
        """Place wizard buttons in the pages."""
        for indx, child in self._children.iteritems():
            btnframe = ttk.Frame(child)
            btnframe.pack(side='bottom', fill='x', padx=6, pady=12)

            nextbtn = ttk.Button(btnframe, text="Next", command=self.next_page)
            nextbtn.pack(side='right', anchor='e', padx=6)
            if indx != 0:
                prevbtn = ttk.Button(btnframe, text="Previous",
                                     command=self.prev_page)
                prevbtn.pack(side='right', anchor='e', padx=6)

                if indx == len(self._children) - 1:
                    nextbtn.configure(text="Finish", command=self.close)

    def next_page(self):
        self.current += 1

    def prev_page(self):
        self.current -= 1

    def nextbtn(self):
        currentPage = self._children[self.current]
        _list = currentPage.winfo_children()
        for item in _list:
            if item.winfo_children():
                _list.extend(item.winfo_children())
        for item in _list:
            if isinstance(item, ttk.Button):
                if "Next" in item.configure()["text"] or "Finish" in item.configure()["text"]:
                    return item

    def close(self):
        self.master.destroy()

    def add_empty_page(self):
        child = ttk.Frame(self, padding=0)
        self._children[len(self._children)] = child
        self.add(child)

    def add_page_body(self, body):
        body.pack(side='top', fill='both', padx=6, pady=12)

    def page_container(self, page_num):
        if page_num in self._children:
            return self._children[page_num]
        else:
            raise KeyError("Invalid page: %s" % page_num)

    def _get_current(self):
        return self._current

    def _set_current(self, curr):
        if curr not in self._children:
            raise KeyError("Invalid page: %s" % curr)

        self._current = curr
        self.select(self._children[self._current])

    current = property(_get_current, _set_current)


def demo():
    root = Tkinter.Tk()
    wizard = Wizard(npages=3)
    wizard.master.minsize(400, 350)
    page0 = ttk.Label(wizard.page_container(0), text='Page 1')
    page1 = ttk.Label(wizard.page_container(1), text='Page 2')
    page2 = ttk.Label(wizard.page_container(2), text='Page 3')
    wizard.add_page_body(page0)
    wizard.add_page_body(page1)
    wizard.add_page_body(page2)
    wizard.pack(fill='both', expand=True)
    root.mainloop()

if __name__ == "__main__":
    demo()
