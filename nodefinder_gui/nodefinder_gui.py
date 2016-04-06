#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
NodeFinder: Do calibration or add Branch Label or add Clade Label.
"""

from __future__ import (with_statement, print_function)

import os
import re
import sys
import time
from subprocess import Popen, PIPE

if sys.version[0] == '2':
    import Tkinter as tk
    import ttk
    import tkMessageBox
    import tkFileDialog
    import ScrolledText as st
elif sys.version[0] == '3':
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox as tkMessageBox
    from tkinter import filedialog as tkFileDialog
    import tkinter.scrolledtext as st
else:
    raise ImportError('Cannot identify your Python version.')

__version__ = '0.4.6'
__author__ = 'Jin'

GUI_TITLE = "NodeFinder GUI"
INIT_WINDOW_SIZE = '1200x700'
THIN_BAR = '~' * 50
LONG_BAR = '=' * 50

ABOUT = """
%s, GUI implementation of NodeFinder
    Version  :  %s
    URL (GUI):  https://github.com/zxjsdp/NodeFinderGUI
    URL (C)  :  https://github.com/zxjsdp/NodeFinderC
""" % (GUI_TITLE, __version__)

DOCUMENTATION = """
Documentation of %s (Ver. %s)

[Basic Usage]

    1. Open Newick tree file
    2. Input calibration configs
    3. Press "Execute All" button to execute

[Config Syntax]

    name_a, name_b, calibration_infomation_1
    name_c, name_d, calibration_infomation_2
    name_a, name_b, clade_label_information
    name, branch_label_information
    ..., ..., ...

[Simple Example]

    Given a Newick tree like this:

        ((a ,((b, c), (d, e))), (f, g));

    Use this calibration config (blanks are OK) (fake data):

        c, b, >0.05<0.07
        a, e, >0.1<0.2
        c, f, >0.3<0.5
        d, e, $1
        a, #1

    We will get output tree like this:

        ((a #1 , ((b, c)>0.05<0.07, (d, e)$1))>0.1<0.2, (f, g))>0.3<0.5;

    Topology (ASCII style):

                +---------- a #1
                |
                | >0.1<0.2
            +---|       +-- b
            |   |   +---| >0.05<0.07
            |   |   |   +-- c
            |   +---|
            |       |   +-- d
            |       +---| $1
        ----|>0.3<0.5   +-- e
            |
            |           +-- f
            +-----------|
                        +-- g
""" % (GUI_TITLE, __version__)

# Use set(list()) for Python2.6 compatibility
NONE_TREE_NAME_SYMBOL_SET = set(
    [',', ';', ')', '"', "'", '#', '$', '@', '>', '<'])
NO_CALI_EXISTS_SYMBOL_SET = set([',', ';', ')'])
WITH_CALI_EXISTS_SYMBOL_SET = set(
    ['>', '<', '@', '0', '1', "'", '"', '$', ':'])
NO_LABEL_EXISTS_SYMBOL_SET = set([',', ';', ')'])
WITH_LABEL_EXISTS_SYMBOL_SET = set(
    ['>', '<', '@', '0', '1', "'", '"', '$', ':', '#'])
WARNING_CALI_OR_LABEL_INFO_SYMBOL_SET = set(
    ['>', '<', '@', '#', '$', "'", '"', ':'])
WARNING_BRANCH_LABEL_SYMBOL_SET = set(['@', '#', '$', "'", ':'])

global_insertion_list_cache = {}


class ConfigFileSyntaxError(SyntaxError):
    """Error class for config file"""
    pass


def time_now():
    """Return a formatted time string: Hour:Minute:Second."""
    return time.strftime("%H:%M:%S", time.localtime())


class RightClickMenu(object):
    """
    Simple widget to add basic right click menus to entry widgets.

    usage:

    rclickmenu = RightClickMenu(some_entry_widget)
    some_entry_widget.bind("<3>", rclickmenu)

    If you prefer to import Tkinter over Tix, just replace all Tix
    references with Tkinter and this will still work fine.
    """

    def __init__(self, parent):
        self.parent = parent
        # bind Control-A to select_all() to the widget.  All other
        # accelerators seem to work fine without binding such as
        # Ctrl-V, Ctrl-X, Ctrl-C etc.  Ctrl-A was the only one I had
        # issue with.
        self.parent.bind("<Control-a>", lambda e: self._select_all(), add='+')
        self.parent.bind("<Control-A>", lambda e: self._select_all(), add='+')

    def __call__(self, event):
        # if the entry widget is disabled do nothing.
        if self.parent.cget('state') == 'disable':
            return
        # grab focus of the entry widget.  this way you can see
        # the cursor and any marking selections
        self.parent.focus_force()
        self.build_menu(event)

    def build_menu(self, event):
        """Build right click menu"""
        menu = tk.Menu(self.parent, tearoff=0)
        # check to see if there is any marked text in the entry widget.
        # if not then Cut and Copy are disabled.
        if not self.parent.selection_present():
            menu.add_command(label="Cut", state='disable')
            menu.add_command(label="Copy", state='disable')
        else:
            # use Tkinter's virtual events for brevity.  These could
            # be hardcoded with our own functions to immitate the same
            # actions but there's no point except as a novice exercise
            # (which I recommend if you're a novice).
            menu.add_command(label="Cut", command=self._cut)
            menu.add_command(label="Copy", command=self._copy)
        # if there's string data in the clipboard then make the normal
        # Paste command.  otherwise disable it.
        if self.paste_string_state():
            menu.add_command(label="Paste", command=self._paste)
        else:
            menu.add_command(label="Paste", state='disable')
        # again, if there's no marked text then the Delete option is disabled.
        if not self.parent.selection_present():
            menu.add_command(label="Delete", state='disable')
        else:
            menu.add_command(label="Delete", command=self._clear)
        # make things pretty with a horizontal separator
        menu.add_separator()
        # I don't know of if there's a virtual event for select all though
        # I did look in vain for documentation on -any- of Tkinter's
        # virtual events.  Regardless, the method itself is trivial.
        menu.add_command(label="Select All", command=self._select_all)
        menu.post(event.x_root, event.y_root)

    def _cut(self):
        self.parent.event_generate("<<Cut>>")

    def _copy(self):
        self.parent.event_generate("<<Copy>>")

    def _paste(self):
        self.parent.event_generate("<<Paste>>")

    def _clear(self):
        self.parent.event_generate("<<Clear>>")

    def _select_all(self):
        self.parent.selection_range(0, 'end')
        self.parent.icursor('end')
        # return 'break' because, for some reason, Control-a (little 'a')
        # doesn't work otherwise.  There's some natural binding that
        # Tkinter entry widgets want to do that send the cursor to Home
        # and deselects.
        return 'break'

    def paste_string_state(self):
        """Returns true if a string is in the clipboard"""
        try:
            # this assignment will raise an exception if the data
            # in the clipboard isn't a string (such as a picture).
            # in which case we want to know about it so that the Paste
            # option can be appropriately set normal or disabled.
            clipboard = self.parent.selection_get(selection='CLIPBOARD')
        except:
            return False
        return True


class RightClickMenuForScrolledText(object):
    """Simple widget to add basic right click menus to entry widgets."""

    def __init__(self, parent):
        self.parent = parent
        # bind Control-A to select_all() to the widget.  All other
        # accelerators seem to work fine without binding such as
        # Ctrl-V, Ctrl-X, Ctrl-C etc.  Ctrl-A was the only one I had
        # issue with.
        self.parent.bind("<Control-a>", lambda e: self._select_all(), add='+')
        self.parent.bind("<Control-A>", lambda e: self._select_all(), add='+')

    def __call__(self, event):
        # if the entry widget is disabled do nothing.
        if self.parent.cget('state') == tk.DISABLED:
            return
        # grab focus of the entry widget.  this way you can see
        # the cursor and any marking selections
        self.parent.focus_force()
        self.build_menu(event)

    def build_menu(self, event):
        """build menu"""
        menu = tk.Menu(self.parent, tearoff=0)
        # check to see if there is any marked text in the entry widget.
        # if not then Cut and Copy are disabled.
        # if not self.parent.selection_get():
        #     menu.add_command(label="Cut", state=tk.DISABLED)
        #     menu.add_command(label="Copy", state=tk.DISABLED)
        # else:
        # use Tkinter's virtual events for brevity.  These could
        # be hardcoded with our own functions to immitate the same
        # actions but there's no point except as a novice exercise
        # (which I recommend if you're a novice).
        menu.add_command(label="Cut", command=self._cut)
        menu.add_command(label="Copy", command=self._copy)
        # if there's string data in the clipboard then make the normal
        # Paste command.  otherwise disable it.
        if self._paste_string_state():
            menu.add_command(label="Paste",
                             command=self._paste_if_string_in_clipboard)
        else:
            menu.add_command(label="Paste", state='disable')
        # again, if there's no marked text then the Delete option is disabled.
        menu.add_command(label="Delete", command=self._delete)
        # make things pretty with a horizontal separator
        menu.add_separator()
        # I don't know of if there's a virtual event for select all though
        # I did look in vain for documentation on -any- of Tkinter's
        # virtual events.  Regardless, the method itself is trivial.
        menu.add_command(label="Select All", command=self._select_all)
        menu.add_command(label="Clear All", command=self._clear_all)
        menu.post(event.x_root, event.y_root)

    def _cut(self):
        self.parent.event_generate("<<Cut>>")

    def _copy(self):
        self.parent.event_generate("<<Copy>>")

    def _delete(self):
        self.parent.event_generate("<<Clear>>")

    def _paste_if_string_in_clipboard(self):
        self.parent.event_generate("<<Paste>>")

    def _select_all(self, ):
        """select all"""
        self.parent.tag_add('sel', "1.0", "end-1c")
        self.parent.mark_set('insert', "1.0")
        self.parent.see('insert')
        return 'break'

    def _paste_string_state(self):
        """Returns true if a string is in the clipboard"""
        try:
            # this assignment will raise an exception if the data
            # in the clipboard isn't a string (such as a picture).
            # in which case we want to know about it so that the Paste
            # option can be appropriately set normal or disabled.
            clipboard = self.parent.selection_get(selection='CLIPBOARD')
        except:
            return False
        return True

    def _clear_all(self):
        """Clear all"""
        isok = askokcancel('Clear All', 'Erase all text?', parent=self.parent,
                           default='ok')
        if isok:
            self.parent.delete('1.0', 'end')


class TextEmit(object):
    """Redirect stdout and stderr to tk widgets."""

    def __init__(self, widget, tag='stdout'):
        """Initialize widget which stdout and stderr were redirected to."""
        self.widget = widget
        self.tag = tag

    def write(self, out_str):
        """Proceed Redirection."""
        self.widget.configure(state='normal')
        self.widget.insert('end', out_str, (self.tag,))
        self.widget.tag_configure('stderr', foreground='red',
                                  background='yellow')
        self.widget.configure(state='disabled')
        self.widget.see('end')


class App(tk.Frame):
    """The main class for GUI application.

    [Example]
        >>> app = App()
        >>> app.mainloop()
    """

    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        # Setting title.
        self.master.title(GUI_TITLE)
        # Setting initial window size.
        self.master.geometry(INIT_WINDOW_SIZE)
        self.final_tree = ''
        self.file_path_history_list = []
        self.combo_line_count = 0

        # GUI creating
        self.set_style()
        self.create_widgets()
        self.configure_grid()
        self.row_and_column_configure()
        self.create_right_menu()
        self.bind_func()
        self.display_info()
        self.create_menu_bar()

    def set_style(self):
        """Set custom style for widget."""
        s = ttk.Style()

        # Configure button style
        s.configure('TButton', padding=5)
        s.configure(
            'execute.TButton',
            foreground='red',
        )
        s.configure(
            'newline.TButton',
            padding=6),
        s.configure(
            'clear.TButton',
            foreground='#2AA198',
        )

        # Configure Combobox style
        s.configure('TCombobox', padding=6)
        s.configure('config.TCombobox', )

        # Configure Title Frame
        s.configure(
            'title.TLabel',
            padding=10,
            font=('helvetica', 11, 'bold'),
        )
        s.configure(
            'config.TLabel',
            padding=1,
            font=('arial', 9),
        )

    def create_widgets(self):
        """Create widgets in the main window.

        There are four main panes:
            1. tree_pane
            2. config_pane
            3. out_tree_pane
            4. log_pane
        """
        # +-------------------+-------------------+
        # |                   |                   |
        # |                   |                   |
        # |    tree_pane      |   config_pane     |
        # |                   |                   |
        # |                   |                   |
        # +-------------------+-------------------+
        # |                   |                   |
        # |                   |                   |
        # |   out_tree_pane   |     log_pane      |
        # |                   |                   |
        # |                   |                   |
        # +-------------------+-------------------+
        self.tree_pane = ttk.Frame(self.master, padding=(5))
        self.config_pane = ttk.Frame(self.master, padding=(5))
        self.out_tree_pane = ttk.Frame(self.master, padding=(5))
        self.log_pane = ttk.Frame(self.master, padding=(5))

        # +-------------------+-------------------+
        # |                   |                   |
        # |        1          |                   |
        # |    tree_pane      |                   |
        # |                   |                   |
        # |                   |                   |
        # +-------------------+-------------------+
        # |                   |                   |
        # |                   |                   |
        # |                   |                   |
        # |                   |                   |
        # |                   |                   |
        # +-------------------+-------------------+
        self.choose_tree_label = ttk.Label(
            self.tree_pane,
            text='Origin Tree',
            style='title.TLabel',
        )

        self.open_tree_file_button = ttk.Button(
            self.tree_pane,
            text='Open Tree File...',
        )

        self.clear_tree_input = ttk.Button(
            self.tree_pane,
            text='Clear',
            style='clear.TButton',
        )

        self.tree_name = tk.StringVar()
        self.choose_tree_box = ttk.Combobox(self.tree_pane,
                                            textvariable=self.tree_name)

        self.load_history_button = ttk.Button(
            self.tree_pane,
            text='Load History',
        )

        self.tree_paste_area = st.ScrolledText(
            self.tree_pane)

        # +-------------------+-------------------+
        # |                   |                   |
        # |                   |         2         |
        # |                   |    config_pane    |
        # |                   |                   |
        # |                   |                   |
        # +-------------------+-------------------+
        # |                   |                   |
        # |                   |                   |
        # |                   |                   |
        # |                   |                   |
        # |                   |                   |
        # +-------------------+-------------------+
        self.config_label = ttk.Label(self.config_pane, text='Configuration',
                                      style='title.TLabel')

        self.execute_button = ttk.Button(
            self.config_pane,
            text='Execute All',
            style='execute.TButton',
        )

        self.clear_config_area_button = ttk.Button(
            self.config_pane,
            text='Clear',
            style='clear.TButton',
        )

        self.read_config_file_button = ttk.Button(
            self.config_pane,
            text='Read Config File...',
        )

        self.save_config_to_file_button = ttk.Button(
            self.config_pane,
            text='Save Config to File...',
        )

        self.name_a_label = ttk.Label(
            self.config_pane, text='Name A', style='config.TLabel')

        self.name_b_label = ttk.Label(
            self.config_pane, text='Name B', style='config.TLabel')

        self.info_label = ttk.Label(
            self.config_pane, text='Info', style='config.TLabel')

        self.add_newline_button = ttk.Button(
            self.config_pane,
            text='Add New',
            style='newline.TButton',
        )

        self.name_a_combobox = ttk.Combobox(
            self.config_pane, style='config.TCombobox')

        self.name_b_combobox = ttk.Combobox(
            self.config_pane, style='config.TCombobox')

        self.info_combobox = ttk.Combobox(
            self.config_pane, style='config.TCombobox')

        self.config_lines_area = st.ScrolledText(
            self.config_pane, )

        # +-------------------+-------------------+
        # |                   |                   |
        # |                   |                   |
        # |                   |                   |
        # |                   |                   |
        # |                   |                   |
        # +-------------------+-------------------+
        # |                   |                   |
        # |         3         |                   |
        # |   out_tree_pane   |                   |
        # |                   |                   |
        # |                   |                   |
        # +-------------------+-------------------+
        self.out_tree_label = ttk.Label(
            self.out_tree_pane,
            text='Tree Output',
            style='title.TLabel',
        )

        self.view_as_ascii_button = ttk.Button(
            self.out_tree_pane,
            text='View As ASCII'
        )

        self.save_current_dir_button = ttk.Button(
            self.out_tree_pane,
            text='Quick Save',
        )

        self.save_as_button = ttk.Button(
            self.out_tree_pane,
            text='Save New Tree As...',
        )

        # Clear out tree button
        self.clear_out_tree_button = ttk.Button(
            self.out_tree_pane,
            text='Clear',
            style='clear.TButton',
        )
        self.clear_out_tree_button.grid(row=0, column=4, sticky='we')

        # Out Tree area
        self.out_tree_area = st.ScrolledText(self.out_tree_pane,
                                             bg='#FAFAFA')

        # +-------------------+-------------------+
        # |                   |                   |
        # |                   |                   |
        # |                   |                   |
        # |                   |                   |
        # |                   |                   |
        # +-------------------+-------------------+
        # |                   |                   |
        # |                   |         4         |
        # |                   |     log_pane      |
        # |                   |                   |
        # |                   |                   |
        # +-------------------+-------------------+
        self.log_label = ttk.Label(self.log_pane, text='Results and Log',
                                   style='title.TLabel')

        # Save log button
        self.save_log_button = ttk.Button(
            self.log_pane,
            text='Save Log As...',
        )

        # Clear out tree button
        self.clear_log_button = ttk.Button(
            self.log_pane,
            text='Clear',
            style='clear.TButton',
        )

        self.log_area = st.ScrolledText(
            self.log_pane,
            fg='#FDF6E3',
            bg='#002B36',
            state='disabled',
        )

    def configure_grid(self):
        self.master.grid()
        # +-------------------+-------------------+
        # |                   |                   |
        # |                   |                   |
        # |    tree_pane      |   config_pane     |
        # |                   |                   |
        # |                   |                   |
        # +-------------------+-------------------+
        # |                   |                   |
        # |                   |                   |
        # |   out_tree_pane   |     log_pane      |
        # |                   |                   |
        # |                   |                   |
        # +-------------------+-------------------+
        self.tree_pane.grid(row=0, column=0, sticky='wens')
        self.config_pane.grid(row=0, column=1, sticky='wens')
        self.out_tree_pane.grid(row=1, column=0, sticky='wens')
        self.log_pane.grid(row=1, column=1, sticky='wens')

        # tree_pane
        self.choose_tree_label.grid(row=0, column=0, sticky='w')
        self.open_tree_file_button.grid(row=0, column=1, sticky='we')
        self.clear_tree_input.grid(row=0, column=2, sticky='we')
        self.choose_tree_box.grid(row=1, column=0, columnspan=2, sticky='we')
        self.load_history_button.grid(row=1, column=2, sticky='e')
        self.tree_paste_area.grid(
            row=2, column=0, columnspan=3, sticky='wens')

        # config_pane
        self.config_label.grid(row=0, column=0, sticky='w')
        self.execute_button.grid(row=0, column=2, sticky='we')
        self.clear_config_area_button.grid(row=0, column=3, sticky='we')
        self.read_config_file_button.grid(row=1, column=2, sticky='we')
        self.save_config_to_file_button.grid(row=1, column=3, sticky='we')
        self.name_a_label.grid(row=2, column=1, sticky='ws')
        self.name_b_label.grid(row=2, column=2, sticky='ws')
        self.info_label.grid(row=2, column=3, sticky='ws')
        self.add_newline_button.grid(row=3, column=0, sticky='we')
        self.name_a_combobox.grid(row=3, column=1, sticky='we')
        self.name_b_combobox.grid(row=3, column=2, sticky='we')
        self.info_combobox.grid(row=3, column=3, sticky='we')
        self.config_lines_area.grid(
            row=4, column=0, columnspan=4, sticky='wens')

        # out_tree_pane
        self.out_tree_label.grid(row=0, column=0, sticky='w')
        self.view_as_ascii_button.grid(row=0, column=1, sticky='we')
        self.save_current_dir_button.grid(row=0, column=2, sticky='we')
        self.save_as_button.grid(row=0, column=3, sticky='we')
        self.out_tree_area.grid(
            row=1, column=0, columnspan=5, sticky='wens')

        # log_pane
        self.log_label.grid(row=0, column=0, sticky='w')
        self.save_log_button.grid(row=0, column=1, sticky='we')
        self.clear_log_button.grid(row=0, column=2, sticky='we')
        self.log_area.grid(row=1, column=0, columnspan=3, sticky='wens')

    def row_and_column_configure(self):
        # +-------------------+-------------------+
        # |                   |                   |
        # |                   |                   |
        # | row: 0, column: 0 | row: 0, column: 1 |
        # |                   |                   |
        # |                   |                   |
        # +-------------------+-------------------+
        # |                   |                   |
        # |                   |                   |
        # | row: 1, column: 0 | row: 1, column: 1 |
        # |                   |                   |
        # |                   |                   |
        # +-------------------+-------------------+
        # Configure row and column
        self.master.rowconfigure(0, weight=1)
        self.master.rowconfigure(1, weight=1)
        self.master.columnconfigure(0, weight=1)
        self.master.columnconfigure(1, weight=1)

        # Orig Tree, Left Up
        self.tree_pane.rowconfigure(0, weight=0)
        self.tree_pane.rowconfigure(1, weight=0)
        self.tree_pane.rowconfigure(2, weight=1)
        self.tree_pane.columnconfigure(0, weight=1)
        self.tree_pane.columnconfigure(1, weight=0)
        self.tree_pane.columnconfigure(2, weight=0)

        # Config label, Right Up
        self.config_pane.rowconfigure(0, weight=0)
        self.config_pane.rowconfigure(1, weight=0)
        self.config_pane.rowconfigure(2, weight=0)
        self.config_pane.rowconfigure(3, weight=0)
        self.config_pane.rowconfigure(4, weight=1)
        self.config_pane.columnconfigure(0, weight=0)
        self.config_pane.columnconfigure(1, weight=1)
        self.config_pane.columnconfigure(2, weight=1)
        self.config_pane.columnconfigure(3, weight=1)

        # Out tree, Left Down
        self.out_tree_pane.rowconfigure(0, weight=0)
        self.out_tree_pane.rowconfigure(1, weight=1)
        self.out_tree_pane.columnconfigure(0, weight=1)
        self.out_tree_pane.columnconfigure(1, weight=0)
        self.out_tree_pane.columnconfigure(2, weight=0)
        self.out_tree_pane.columnconfigure(3, weight=0)

        # Log pane, Right Down
        self.log_pane.rowconfigure(0, weight=0)
        self.log_pane.rowconfigure(1, weight=1)
        self.log_pane.columnconfigure(0, weight=1)
        self.log_pane.columnconfigure(1, weight=0)
        self.log_pane.columnconfigure(2, weight=0)

    def create_right_menu(self):
        # Right click menu for choose tree combobox
        right_menu_tree_choose = RightClickMenu(self.choose_tree_box)
        self.choose_tree_box.bind('<Button-3>', right_menu_tree_choose)

        # Right Click menu for tree input area
        right_menu_input = RightClickMenuForScrolledText(self.tree_paste_area)
        self.tree_paste_area.bind('<Button-3>', right_menu_input)

        # Right click menu for three input combobox in config_pane
        right_menu_name_a = RightClickMenu(self.name_a_combobox)
        self.name_a_combobox.bind('<Button-3>', right_menu_name_a)
        right_menu_name_b = RightClickMenu(self.name_b_combobox)
        self.name_b_combobox.bind('<Button-3>', right_menu_name_b)
        right_menu_info_combobox = RightClickMenu(self.info_combobox)
        self.info_combobox.bind('<Button-3>', right_menu_info_combobox)

        # Right click menu for config input area
        right_menu_config = RightClickMenuForScrolledText(
            self.config_lines_area)
        self.config_lines_area.bind('<Button-3>', right_menu_config)

        # Right click menu for output area
        right_menu_out = RightClickMenuForScrolledText(self.out_tree_area)
        self.out_tree_area.bind('<Button-3>', right_menu_out)

    def bind_func(self):
        # input_pane
        self.open_tree_file_button['command'] = self._ask_open_file
        self.clear_tree_input['command'] = \
            lambda: self.tree_paste_area.delete('1.0', 'end')
        self.load_history_button['command'] = self._load_history_file

        # config_pane
        self.clear_config_area_button['command'] = lambda: \
            self.config_lines_area.delete('1.0', 'end')
        self.read_config_file_button['command'] = self._read_config_from_file
        self.save_config_to_file_button['command'] = self._save_config_to_file
        self.add_newline_button['command'] = self._set_value_to_textarea
        self.execute_button['command'] = self._main_work

        # output_pane
        self.view_as_ascii_button['command'] = self._view_as_ascii_command
        self.save_current_dir_button['command'] = \
            self._save_new_tree_to_current_dir
        self.save_as_button['command'] = self._ask_save_out_as_file
        self.clear_out_tree_button['command'] = \
            lambda: self.out_tree_area.delete('1.0', 'end')

        # log_pane
        self.save_log_button['command'] = self._ask_save_log_as_file
        self.clear_log_button['command'] = self._clear_log

    def create_menu_bar(self):
        """Create Menu Bar for NodeFinderGUI"""
        menu_bar = tk.Menu(self.master)

        # File Menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label='Open input tree file...',
                              command=self._ask_open_file)
        file_menu.add_separator()
        file_menu.add_command(label='Save output tree to file...',
                              command=self._ask_save_out_as_file)
        file_menu.add_command(label='Save log to file...',
                              command=self._ask_save_log_as_file)
        file_menu.add_separator()
        file_menu.add_command(label='Exit', command=self.quit)
        menu_bar.add_cascade(label='File', menu=file_menu)

        # Configure Menu
        configs_menu = tk.Menu(menu_bar, tearoff=0)
        configs_menu.add_command(label='Open config file...',
                                 command=self._read_config_from_file)
        configs_menu.add_command(label='Save config to file...',
                                 command=self._save_config_to_file)
        menu_bar.add_cascade(label="Configs", menu=configs_menu)

        # Edit Menu
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Cut", command=self._cut)
        edit_menu.add_command(label="Copy", command=self._copy)
        # try:
        #     edit_menu.add_command(label="Paste", command=self._paste)
        # except Exception:
        #     pass
        if self._paste_string_state():
            edit_menu.add_command(label="Paste", command=self._paste)
        else:
            edit_menu.add_command(
                label='Paste',
                command=lambda: print('No string in clipboard!'))
        edit_menu.add_command(label="Delete", command=self._delete)
        menu_bar.add_cascade(label="Edit", menu=edit_menu)

        # Help Menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="Documentation",
                              command=self.display_documentation)
        help_menu.add_command(label="About", command=self.display_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)

        self.master.config(menu=menu_bar)

    def display_documentation(self):
        """Display documentation for menu bar about button."""
        print(LONG_BAR)
        print(DOCUMENTATION)
        # print('Documentation of %s (Ver. %s):\n' % (GUI_TITLE, __version__))
        # print('[Basic Usage]')
        # print('  1. Open Newick tree file')
        # print('  2. Input calibration configs')
        # print('  3. Press "Execute All" button to execute\n')
        # print('[Config Syntax]')
        # print('  name_a, name_b, calibration_infomation_1')
        # print('  name_c, name_d, calibration_infomation_2')
        # print('  name_a, name_b, clade_label_information')
        # print('  name, branch_label_information')
        # print('  ..., ..., ...')
        print(LONG_BAR)

    def display_about(self):
        """Display about information for menu bar about button."""
        print(LONG_BAR)
        print(ABOUT)
        print(LONG_BAR)

    def display_info(self):
        sys.stdout = TextEmit(self.log_area, 'stdout')
        sys.stderr = TextEmit(self.log_area, 'stderr')

        print(LONG_BAR)
        print('  %s (Ver %s)' % (GUI_TITLE, __version__))
        print(time.strftime("  %d %b %Y,  %a %H:%M:%S",
                            time.localtime()))
        print(LONG_BAR)
        print('\nIf you need help, please check the menu bar:\n\n'
              '   Help -> Documentation\n')

    def _copy(self):
        # self.master.clipboard_clear()
        # self.master.clipboard_append(self.master.focus_get().selection_get())
        self.master.focus_get().event_generate("<<Copy>>")

    def _cut(self):
        # self.master.clipboard_clear()
        # self.master.clipboard_append(self.master.focus_get().selection_get())
        # # self.master.focus_get().selection_clear()
        self.master.focus_get().event_generate("<<Cut>>")

    def _paste(self):
        # print(self.master.selection_get(selection='CLIPBOARD'))
        self.master.focus_get().event_generate("<<Paste>>")

    def _delete(self):
        self.master.focus_get().event_generate("<<Clear>>")

    def _paste_string_state(self):
        """Returns true if a string is in the clipboard"""
        try:
            # this assignment will raise an exception if the data
            # in the clipboard isn't a string (such as a picture).
            # in which case we want to know about it so that the Paste
            # option can be appropriately set normal or disabled.
            clipboard = self.master.selection_get(selection='CLIPBOARD')
        except:
            return False
        return True

    def _ask_open_file(self):
        """Dialog to open file."""
        file_opt = {}
        c = tkFileDialog.askopenfile(mode='r', **file_opt)
        try:
            orig_tree_str = c.read()
            self.tree_paste_area.delete('1.0', 'end')
            self.tree_paste_area.insert('end', orig_tree_str)

            abs_path = c.name
            base_name = os.path.basename(abs_path)
            print('[ INFO | %s ] Open tree file: %s' % (time_now(), base_name))
            # Add to history (Feature Not Implemented)
            self.file_path_history_list.insert(0, abs_path)
            self.choose_tree_box['values'] = self.file_path_history_list
            self.choose_tree_box.current('0')
        except AttributeError:
            print('[ INFO | %s ] No file choosed' % time_now())

    def _load_history_file(self):
        """Load file from history."""
        file_path = self.choose_tree_box.get()
        if not file_path:
            sys.stderr.write('[ ERROR | %s ] History file bar is blank\n' %
                             time_now())
        elif not os.path.isfile(file_path):
            sys.stderr.write('[ ERROR | %s ] No such file\n' % time_now())
        else:
            with open(file_path, 'r') as f:
                content = f.read()
            self.tree_paste_area.delete('1.0', 'end')
            self.tree_paste_area.insert('end', content)
            print('[ INFO | %s ] Load file' % time_now())

    def _read_config_from_file(self):
        """Read calibration config from file"""
        file_opt = {}
        c = tkFileDialog.askopenfile(mode='r', **file_opt)
        if c is None:
            # No file selected
            return
        config_content = c.read()
        self.config_lines_area.delete('1.0', 'end')
        self.config_lines_area.insert('end', config_content)

        abs_path = c.name
        base_name = os.path.basename(abs_path)
        print('[ INFO | %s ] Read from config file: %s' %
              (time_now(), base_name))

    def _save_config_to_file(self):
        """Save current calibration config content to file"""
        f = tkFileDialog.asksaveasfile(mode='w', defaultextension=".txt")
        # asksaveasfile return `None` if dialog closed with "cancel".
        if f is None:
            return
        text_to_save = str(self.config_lines_area.get('1.0', 'end-1c'))
        f.write(text_to_save)
        f.close()

    def _set_value_to_textarea(self):
        """Value to textarea."""
        name_a, name_b, info = self.name_a_combobox.get(), \
                               self.name_b_combobox.get(), self.info_combobox.get()
        config_list = filter(lambda x: x != '', [name_a, name_b, info])
        if len(config_list) < 2 or not info:
            sys.stderr.write('[ ERROR | %s ]\n[Usage]\n' % time_now())
            sys.stderr.write(
                '    Calibration:  name_a, name_b, cali_info\n')
            sys.stderr.write(
                '    Branch Label: name_a, branch_label\n')
            sys.stderr.write(
                '    Clade Label:  name_a, name_b, clade_label\n')
            print('')
        else:
            one_line = ', '.join(config_list)
            self.config_lines_area.insert('end', one_line + '\n')
            print('[ INFO - %s ]  Added one configure line (%s)' %
                  (time_now(), one_line))

    def _view_as_ascii_command(self):
        """View tree using ascii tree program."""
        new_tree_str = self.out_tree_area.get('1.0', 'end-1c')
        if not new_tree_str:
            sys.stderr.write('[ ERROR | %s] No content in out tree '
                             'area to view' % time_now())
            tkMessageBox.showerror(
                'ValueError',
                'No content in Tree Output area to view.')
        try:
            with open('tmp_file_for_ascii_view.nwk', 'w') as f:
                f.write(new_tree_str)
            p = Popen(
                [
                    'python',
                    'tree_ascii_view.pyw',
                    'tmp_file_for_ascii_view.nwk'
                ],
                stdout=PIPE,
                stderr=PIPE)
            print(p.communicate()[0])
            if p.communicate()[1]:
                sys.stderr.write(p.communicate()[1])
        except IOError as e:
            tkMessageBox.showerror(
                title='File Error',
                message='Cannot write temporary file to disk.\n%s' % e)

    # Quick Save button
    def _save_new_tree_to_current_dir(self):
        """Quick save Newick tree to current folder."""
        new_tree_content = self.out_tree_area.get('1.0', 'end-1c')
        new_tree_name = 'New_tree.nwk'
        with open(new_tree_name, 'w') as f:
            f.write(new_tree_content)
            print('[ INFO | %s ] Quick save: (%s)' % (
                time_now(), new_tree_name))

    # Save as button for outcome
    def _ask_save_out_as_file(self):
        """Dialog to save as file."""
        f = tkFileDialog.asksaveasfile(mode='w', defaultextension=".txt")
        # asksaveasfile return `None` if dialog closed with "cancel".
        if f is None:
            return
        text_to_save = str(self.out_tree_area.get('1.0', 'end-1c'))
        f.write(text_to_save)
        f.close()

    # Save as button for log
    def _ask_save_log_as_file(self):
        """Dialog to save as file."""
        f = tkFileDialog.asksaveasfile(mode='w', defaultextension=".txt")
        # asksaveasfile return `None` if dialog closed with "cancel".
        if f is None:
            return
        text_to_save = str(self.log_area.get('1.0', 'end-1c'))
        f.write(text_to_save)
        f.close()

    def _clear_log(self):
        """Clear all contents in log widget area."""
        self.log_area.configure(state='normal')
        self.log_area.delete('1.0', 'end')
        self.log_area.configure(state='disabled')

    def _main_work(self):
        """Do main job."""
        tree_str = get_tree_str(self.tree_paste_area.get('1.0', 'end-1c'))
        calibration_list = get_cali_list(
            self.config_lines_area.get('1.0', 'end-1c'))
        self.final_tree = multi_calibration(tree_str, calibration_list)
        self.out_tree_area.delete('1.0', 'end')
        self.out_tree_area.insert('end', self.final_tree)

    def hello(self):
        """Simple hello function for testing use."""
        print('Hello NodeFinderGUI!')


def clean_elements(orig_list):
    """Strip each element in list and return a new list.
    [Params]
        orig_list: Elements in original list is not clean, may have blanks or
                   newlines.
    [Return]
        clean_list: Elements in clean list is striped and clean.

    [Example]
        >>> clean_elements(['a ', '\tb\t', 'c\n'])
        ['a', 'b', 'c']
    """
    return [_.strip() for _ in orig_list]


def get_clean_tree_str(tree_str):
    """Remove all blanks and return a very clean tree string.
    >>> get_clean_tree_str('((a ,((b, c), (d, e))), (f, g));'')
    '((a,((b,c),(d,e))),(f,g));'
    """
    return tree_str.replace(' ', '').replace('\n', '').replace('\t', '')


def get_right_index_of_name(clean_tree_str, one_name):
    """Get the right index of givin name.
    #                                      111111111122222222
    #                            0123456789012345678901234567
    #                                           |
    >>> get_right_index_of_name('((a,((b,c),(ddd,e))),(f,g));', 'ddd')
    15
    """
    left_index_of_name = clean_tree_str.find(one_name)
    while clean_tree_str[left_index_of_name] not in \
            NONE_TREE_NAME_SYMBOL_SET:
        left_index_of_name += 1
    return left_index_of_name


def get_insertion_list(clean_tree_str, name):
    """Get insertion list
    """
    insertion_list = []
    current_index = clean_tree_str.find(name)
    stack = []
    str_len = len(clean_tree_str)
    while current_index < str_len:
        if clean_tree_str[current_index] == '(':
            stack.append('(')
        elif clean_tree_str[current_index] == ')':
            if not stack:
                insertion_list.append(current_index + 1)
            else:
                stack.pop()
        current_index += 1

    return insertion_list


def get_index_of_tmrca(clean_tree_str, name_a, name_b):
    """Get index of the most recent common ancestor"""
    insertion_list_a = get_insertion_list(clean_tree_str, name_a)
    insertion_list_b = get_insertion_list(clean_tree_str, name_b)
    # print(insertion_list_a)
    # print(insertion_list_b)
    insertion_list_a, insertion_list_b = insertion_list_a[::-1], \
                                         insertion_list_b[::-1]
    shorter_list = insertion_list_a if len(insertion_list_a) < \
                                       len(insertion_list_b) else insertion_list_b
    longer_list = insertion_list_a if shorter_list == insertion_list_b else \
        insertion_list_b
    # print('[Shorter List]: ', shorter_list)
    # print('[Longer List]:  ', longer_list)
    for i, each_in_shorter_list in enumerate(shorter_list):
        if i == len(shorter_list) - 1:
            cali_point = each_in_shorter_list
        if shorter_list[i] != longer_list[i]:
            cali_point = shorter_list[i - 1]
            break

    tree_len = len(clean_tree_str)
    print('[Common]:   %s\n' % cali_point)
    if cali_point < 20 <= tree_len - cali_point:
        print('[Insert]:   %s%s' % (
            ' ' * (20 - cali_point),
            clean_tree_str[:cali_point + 20])
        )
    elif cali_point >= 20 > tree_len - cali_point:
        print('[Insert]:   %s' % (
            clean_tree_str[
                cali_point- 20:cali_point + (tree_len - cali_point)])
        )
    elif cali_point < 20 and tree_len - cali_point < 20:
        print('[Insert]:   %s%s' % (
            ' ' * (20 - cali_point),
            clean_tree_str[:cali_point + (tree_len - cali_point)])
        )
    else:
        print('[Insert]:   %s' % (
            clean_tree_str[cali_point - 20:cali_point + 20])
        )
    print('[Insert]:                    ->||<-                 ')
    print('[Insert]:                  Insert Here              ')

    return cali_point


def single_calibration(tree_str, name_a, name_b, cali_info):
    """Do single calibration. If calibration exists, replace it."""
    clean_tree_str = get_clean_tree_str(tree_str)
    cali_point = get_index_of_tmrca(clean_tree_str, name_a, name_b)

    # Check if there are duplicate calibration
    current_info = '%s, %s, %s' % (name_a, name_b, cali_info)
    if cali_point not in global_insertion_list_cache:
        global_insertion_list_cache[cali_point] = current_info
    else:
        print('\n[Warning]   Duplicate calibration:           [ !!! ]')
        print('[Exists]:   %s\n'
              '[ Now  ]:   %s\n' % (global_insertion_list_cache[cali_point],
                                    current_info))

    # No calibration before
    if clean_tree_str[cali_point] in NO_CALI_EXISTS_SYMBOL_SET:
        left_part, right_part = clean_tree_str[:cali_point], \
                                clean_tree_str[cali_point:]
        clean_str_with_cali = left_part + cali_info + right_part
    # There was calibration there
    # '>':  >0.05<0.07
    # '<':  <0.38
    # '@':  @0.56
    # '0':  0.5
    # '1':  1
    # "'":  '>0.05<0.07'
    # '"':  ">0.05<0.07"
    # '$':  $1
    # ':':  :0.12345
    elif clean_tree_str[cali_point] in WITH_CALI_EXISTS_SYMBOL_SET:
        # ((a,((b,c),(d,e)))>0.3<0.5,(f,g));
        # left_part = '((a,((b,c),(d,e)))'
        # right_part = '>0.3<0.5,(f,g));'
        # re will find '>0.3<0.5' part
        re_find_left_cali = re.compile('^[^,);]+')
        left_part, right_part = clean_tree_str[:cali_point], \
                                clean_tree_str[cali_point:]
        left_cali = re_find_left_cali.findall(right_part)[0]
        print('[Calibration Exists]:          ', left_cali, '  [- Old]')
        print('[Calibration Replaced By]:     ', cali_info, '  [+ New]')
        # '>0.3<0.5,(f,g));'.lstrip('>0.3<0.5') will be ',(f,g));'
        final_right_part = right_part.lstrip(left_cali)
        clean_str_with_cali = left_part + cali_info + final_right_part
    else:
        raise ValueError('Unknown: ' + clean_tree_str[cali_point])
    return clean_str_with_cali


def add_single_branch_label(tree_str, name_a, branch_label):
    """Add single label right after one name.
    >>> add_single_branch_label('((a ,((b, c), (d, e))), (f, g));', c, '#1')
    '((a ,((b, c #1 ), (d, e))), (f, g));'
    """
    clean_tree_str = get_clean_tree_str(tree_str)
    insert_point = get_right_index_of_name(clean_tree_str, name_a)

    tree_len = len(clean_tree_str)
    print('[Common]:   %s\n' % insert_point)
    if insert_point < 20 <= tree_len - insert_point:
        print('[Insert]:   %s%s' % (
            ' ' * (20 - insert_point),
            clean_tree_str[:insert_point + 20])
              )
    elif insert_point >= 20 > tree_len - insert_point:
        print('[Insert]:   %s' % (
            clean_tree_str[
                insert_point - 20:insert_point + (tree_len - insert_point)])
              )
    elif insert_point < 20 and tree_len - insert_point < 20:
        print('[Insert]:   %s%s' % (
            ' ' * (20 - insert_point),
            clean_tree_str[:insert_point + (tree_len - insert_point)])
              )
    else:
        print('[Insert]:   %s' % (
            clean_tree_str[insert_point - 20:insert_point + 20])
              )
    print('[Insert]:                    ->||<-                 ')
    print('[Insert]:                  Insert Here              ')

    # Check is there was something there
    # Nothing there before
    if clean_tree_str[insert_point] in NO_LABEL_EXISTS_SYMBOL_SET:
        left_part, right_part = clean_tree_str[:insert_point], \
                                clean_tree_str[insert_point:]
        clean_str_with_cali = left_part + ' %s ' % branch_label + right_part
    # There was calibration there
    # '>':  >0.05<0.07
    # '<':  <0.38
    # '@':  @0.56
    # '0':  0.5
    # '1':  1
    # "'":  '>0.05<0.07'
    # '"':  ">0.05<0.07"
    # '$':  $1
    # ':':  :0.12345
    elif clean_tree_str[insert_point] in WITH_LABEL_EXISTS_SYMBOL_SET:
        # ((a,((b,c),(d,e)))>0.3<0.5,(f,g));
        # left_part = '((a,((b,c),(d,e)))'
        # right_part = '>0.3<0.5,(f,g));'
        # re will find '>0.3<0.5' part
        re_find_left_cali = re.compile('^[^,);]+')
        left_part, right_part = (clean_tree_str[:insert_point],
                                 clean_tree_str[insert_point:])
        left_cali = re_find_left_cali.findall(right_part)[0]
        print('[Label Exists]:          ' + left_cali + '  [- Old]')
        print('[Label Replaced By]:     ' + branch_label + '  [+ New]')
        # '>0.3<0.5,(f,g));'.lstrip('>0.3<0.5') will be ',(f,g));'
        final_right_part = right_part.lstrip(left_cali)
        clean_str_with_cali = (left_part + ' %s ' % branch_label +
                               final_right_part)
    else:
        raise ValueError('[Error] [Unknown Symbol]: ' +
                         clean_tree_str[insert_point])
    return clean_str_with_cali


def multi_calibration(tree_str, cali_tuple_list):
    """Do calibration for multiple calibration requests."""
    global global_insertion_list_cache
    global_insertion_list_cache = {}
    print('\n\n====================================================')
    print('=============== [ New Job: %s] ===============' % time_now())
    print('====================================================')
    for i, each_cali_tuple in enumerate(cali_tuple_list):
        if len(each_cali_tuple) == 3:
            name_a, name_b, cali_or_clade_info = each_cali_tuple
            print('\n')
            print('[%d]:  %s' % (i + 1, ', '.join(each_cali_tuple)))
            print(THIN_BAR)
            print('[Name A]:  ', name_a)
            print('[Name B]:  ', name_b)
            print('[ Info ]:  ', cali_or_clade_info)
            for name in (name_a, name_b):
                if name not in tree_str:
                    raise ConfigFileSyntaxError('Name not in tree file:  ',
                                                name)
            if cali_or_clade_info[0] not in \
                    WARNING_CALI_OR_LABEL_INFO_SYMBOL_SET:
                print('\n[Warning]: Is this valid symbel?  %s     [ !!! ]\n' %
                      cali_or_clade_info)
            tree_str = single_calibration(tree_str, name_a, name_b,
                                          cali_or_clade_info)
            print(THIN_BAR)
        elif len(each_cali_tuple) == 2:
            name_a, branch_label = each_cali_tuple
            print('\n')
            print('[%d]:  %s' % (i + 1, ', '.join(each_cali_tuple)))
            print(THIN_BAR)
            print('[ Name ]:  ', name_a)
            print('[ Info ]:  ', branch_label)
            if name_a not in tree_str:
                raise ConfigFileSyntaxError('name_a not in tree file:  ',
                                            name_a)
            if branch_label[0] not in WARNING_BRANCH_LABEL_SYMBOL_SET:
                print('\n[Warning]: Is this valid symbel?  %s     [ !!! ]\n' %
                      branch_label)
            tree_str = add_single_branch_label(tree_str, name_a, branch_label)
            print(THIN_BAR)
    final_tree = tree_str.replace(',', ', ')
    return final_tree


def get_cali_list(raw_cali_content):
    """Get calibration list."""
    tmp_cali_list = []
    lines = [_.strip() for _ in raw_cali_content.split('\n') if _.strip()]
    for i, line in enumerate(lines):
        line = line.strip()
        if line[0] in {'#', '//'}:
            continue
        elements = clean_elements(line.split(','))
        if len(elements) not in [2, 3]:
            # error_msg = (
            #     '[Calibration lines]:  name_a, name_b, cali_info\n'
            #     '[Branch label lines]: name, branch_label(#)\n'
            #     '[Clade label lines]:  name_a, name_b, '
            #     'clade_ladel')
            # raise ConfigFileSyntaxError('Invalid calibration line [%d]: %s'
            #                             % (i + 1, line) +
            #                             'Usage:\n\n%s' % error_msg)
            raise ConfigFileSyntaxError('Invalid line: [%d]: %s' % (i + 1, line))
        tmp_cali_list.append(elements)
    return tmp_cali_list


def get_tree_str(raw_tree_content):
    """Read tree content, parse, and return tree string"""
    tmp_tree_str = ''
    tree_start_flag = False
    lines = raw_tree_content.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('('):
            tree_start_flag = True
        if not tree_start_flag:
            continue
        if line.startswith('//') or line.startswith('#'):
            break
        else:
            tmp_tree_str += line
    return tmp_tree_str


def main():
    """Main GUI Application."""
    app = App()
    app.mainloop()


if __name__ == '__main__':
    main()
