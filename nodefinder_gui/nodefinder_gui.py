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


__version__ = '0.4.2'
__author__ = 'Jin'

GUI_TITLE = "NodeFinder GUI"
INIT_WINDOW_SIZE = '1200x700'

_insertion_list_point_dict = {}


class ConfigFileSyntaxError(SyntaxError):
    """Error class for config file"""
    pass


def time_now():
    """Return a formatted time string: Hour:Minute:Second."""
    return time.strftime("%H:%M:%S", time.localtime())


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
        self.set_style()
        self.master.grid()
        self.combo_line_count = 0
        self.create_widgets()

    def set_style(self):
        """Set custom style for widget."""
        s = ttk.Style()

        # Configure button style
        s.configure('TButton', padding=(5))
        s.configure(
            'execute.TButton',
            foreground='red',
            )
        s.configure(
            'newline.TButton',
            padding=(6)),
        s.configure(
            'clear.TButton',
            foreground='#2AA198',
            )

        # Configure Combobox style
        s.configure('TCombobox', padding=(6))
        s.configure('config.TCombobox')

        # Configure Title Frame
        s.configure(
            'title.TLabel',
            padding=(10),
            font=('helvetica', 11, 'bold'),
            )
        s.configure(
            'config.TLabel',
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

        self.tree_pane.grid(row=0, column=0, sticky='wens')
        self.config_pane.grid(row=0, column=1, sticky='wens')
        self.out_tree_pane.grid(row=1, column=0, sticky='wens')
        self.log_pane.grid(row=1, column=1, sticky='wens')

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
            style='title.TLabel')
        self.choose_tree_label.grid(row=0, column=0, sticky='w')

        self.choose_tree_label.grid(row=0, column=0, sticky='w')

        file_opt = {}

        self.open_tree_file_button = ttk.Button(
            self.tree_pane,
            text='Open Tree File...',
            )
        self.open_tree_file_button.grid(row=0, column=1, sticky='we')

        self.clear_tree_input = ttk.Button(
            self.tree_pane,
            text='Clear',
            style='clear.TButton'
            )
        self.clear_tree_input.grid(row=0, column=2, sticky='we')

        self.tree_name = tk.StringVar()
        self.choose_tree_box = ttk.Combobox(self.tree_pane,
                                            textvariable=self.tree_name)
        self.choose_tree_box.grid(row=1, column=0, columnspan=2, sticky='we')

        self.load_history_button = ttk.Button(
            self.tree_pane,
            text='Load History',
            )
        self.load_history_button.grid(row=1, column=2, sticky='e')

        self.tree_paste_area = st.ScrolledText(
            self.tree_pane)
        self.tree_paste_area.grid(
            row=2, column=0, columnspan=3, sticky='wens')

        def ask_open_file():
            """Dialog to open file."""
            c = tkFileDialog.askopenfile(mode='r', **file_opt)
            try:
                orig_tree_str = c.read()
                self.tree_paste_area.delete('1.0', 'end')
                self.tree_paste_area.insert('end', orig_tree_str)

                abs_path = c.name
                base_name = os.path.basename(abs_path)
                print('[ INFO | %s ] File open: %s' % (time_now(), base_name))
                # Add to history (Feature Not Implemented)
                self.file_path_history_list.insert(0, abs_path)
                self.choose_tree_box['values'] = self.file_path_history_list
                self.choose_tree_box.current('0')
            except AttributeError:
                print('[ INFO | %s ] No file choosed' % time_now())

        self.open_tree_file_button['command'] = ask_open_file

        self.clear_tree_input['command'] = \
            lambda: self.tree_paste_area.delete('1.0', 'end')

        def load_history_file():
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

        self.load_history_button['command'] = load_history_file

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
        self.config_label.grid(row=0, column=0, sticky='w')

        self.execute_button = ttk.Button(
            self.config_pane,
            text='Execute All',
            style='execute.TButton')
        self.execute_button.grid(row=0, column=2, sticky='we')

        self.clear_config_area_button = ttk.Button(
            self.config_pane,
            text='Clear',
            style='clear.TButton'
            )
        self.clear_config_area_button.grid(row=0, column=3, sticky='we')

        self.name_a_label = ttk.Label(
            self.config_pane, text='Name A', style='config.TLabel')
        self.name_a_label.grid(row=2, column=1, sticky='w')
        self.name_b_label = ttk.Label(
            self.config_pane, text='Name B', style='config.TLabel')
        self.name_b_label.grid(row=2, column=2, sticky='w')
        self.info_label = ttk.Label(
            self.config_pane, text='Info', style='config.TLabel')
        self.info_label.grid(row=2, column=3, sticky='w')

        self.add_newline_button = ttk.Button(
            self.config_pane,
            text='Add New',
            style='newline.TButton')
        self.add_newline_button.grid(
            row=3, column=0, sticky='we')

        self.name_a_combobox = ttk.Combobox(
            self.config_pane, style='config.TCombobox')
        self.name_a_combobox.grid(row=3, column=1, sticky='we')
        self.name_b_combobox = ttk.Combobox(
            self.config_pane, style='config.TCombobox')
        self.name_b_combobox.grid(row=3, column=2, sticky='we')
        self.info_combobox = ttk.Combobox(
            self.config_pane, style='config.TCombobox')
        self.info_combobox.grid(row=3, column=3, sticky='we')

        self.config_lines_area = st.ScrolledText(
            self.config_pane, height=17)
        self.config_lines_area.grid(
            row=4, column=0, columnspan=4, sticky='wens')

        self.clear_config_area_button['command'] = lambda: \
            self.config_lines_area.delete('1.0', 'end')

        def set_value_to_textarea():
            """Value to textarea."""
            name_a, name_b, info = self.name_a_combobox.get(),\
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

        self.add_newline_button['command'] = set_value_to_textarea

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
            style='title.TLabel')
        self.out_tree_label.grid(row=0, column=0, sticky='w')

        self.view_as_ascii_button = ttk.Button(
            self.out_tree_pane,
            text='View As ASCII'
            )
        self.view_as_ascii_button.grid(row=0, column=1, sticky='we')

        def view_as_ascii_command():
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
        self.view_as_ascii_button['command'] = view_as_ascii_command

        # Quick Save button
        def save_new_tree_to_current_dir():
            """Quick save Newick tree to current folder."""
            new_tree_content = self.out_tree_area.get('1.0', 'end-1c')
            new_tree_name = 'New_tree.nwk'
            with open(new_tree_name, 'w') as f:
                f.write(new_tree_content)
                print('[ INFO | %s ] Quick save: (%s)' % (
                    time_now(), new_tree_name))

        self.save_current_dir_button = ttk.Button(
            self.out_tree_pane,
            text='Quick Save',
            command=save_new_tree_to_current_dir)
        self.save_current_dir_button.grid(row=0, column=2, sticky='we')

        # Save as button
        def ask_save_as_file(**file_opt):
            """Dialog to save as file."""
            return tkFileDialog.asksaveasfile(mode='w', **file_opt)

        self.save_as_button = ttk.Button(
            self.out_tree_pane,
            text='Save New Tree As...',
            command=ask_save_as_file)
        self.save_as_button.grid(row=0, column=3, sticky='we')

        # Clear out tree button
        self.clear_out_tree_button = ttk.Button(
            self.out_tree_pane,
            text='Clear',
            style='clear.TButton'
            )
        self.clear_out_tree_button.grid(row=0, column=4, sticky='we')

        # Out Tree area
        self.out_tree_area = st.ScrolledText(self.out_tree_pane, bg='#FAFAFA')
        self.out_tree_area.grid(
            row=1, column=0, columnspan=5, sticky='wens')

        self.clear_out_tree_button['command'] = \
            lambda: self.out_tree_area.delete('1.0', 'end')

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
        self.log_label.grid(row=0, column=0, sticky='w')

        # Save log button
        self.save_log_button = ttk.Button(
            self.log_pane,
            text='Save Log As...',
            )
        self.save_log_button.grid(row=0, column=1, sticky='we')

        # Clear out tree button
        self.clear_log_button = ttk.Button(
            self.log_pane,
            text='Clear',
            style='clear.TButton'
            )
        self.clear_log_button.grid(row=0, column=2, sticky='we')

        self.log_area = st.ScrolledText(
            self.log_pane,
            fg='#FDF6E3',
            bg='#002B36',
            state='disabled',)
        self.log_area.grid(row=1, column=0, columnspan=3, sticky='wens')

        def ask_save_log(**file_opt):
            """Save log"""
            return tkFileDialog.asksaveasfile(mode='w', **file_opt)

        self.save_log_button['command'] = ask_save_log

        def clear_log():
            """Clear all contents in log widget area."""
            self.log_area.configure(state='normal')
            self.log_area.delete('1.0', 'end')
            self.log_area.configure(state='disabled')

        self.clear_log_button['command'] = clear_log

        # Output
        sys.stdout = TextEmit(self.log_area, 'stdout')
        sys.stderr = TextEmit(self.log_area, 'stderr')

        print('=' * 52)
        print('    %s  (%s)' % (GUI_TITLE, __version__))
        print(time.strftime("    %d %b %Y, %a  %H:%M:%S",
                            time.localtime()))
        print('=' * 52)

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

        def main_work():
            """Do main job."""
            tree_str = get_tree_str(self.tree_paste_area.get('1.0', 'end-1c'))
            calibration_list = get_cali_list(
                self.config_lines_area.get('1.0', 'end-1c'))
            self.final_tree = multi_calibration(tree_str, calibration_list)
            self.out_tree_area.delete('1.0', 'end')
            self.out_tree_area.insert('end', self.final_tree)

        self.execute_button['command'] = main_work


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


def find_right_paren(clean_tree_str, left_index_now):
    """Find the index of paired right parenthesis ')' of given '('.
    Example:
        #          1111111111222222222233
        #01234567890123456789012345678901
        '((a ,((b, c), (d, e))), (f, g));'
        #     |              |
        #     +--------------+
        #     5              20

        >>> find_right_paren('((a ,((b, c), (d, e))), (f, g));', 5)
        20
    """
    stack = []
    paren_index_right = left_index_now
    stack.append('(')
    while len(stack) > 0:
        paren_index_right += 1
        if clean_tree_str[paren_index_right] == '(':
            stack.append('(')
        elif clean_tree_str[paren_index_right] == ')':
            stack.pop()
    return paren_index_right


def find_first_left_paren(clean_tree_str, one_name):
    """Find the index of first '(' on the left side of given name.
    Example:
        #                                    1111111111222222
        #                          01234567890123456789012345
        #                               ^
        #                               |

        >>> find_first_left_paren('((a,((b,c),(d,e))),(f,g));', 'c')
        5
    """
    index_left = clean_tree_str.find(one_name)
    while clean_tree_str[index_left] != '(':
        index_left -= 1
    return index_left


def find_first_right_paren(clean_tree_str, one_name):
    """Find the index of first ')' on the right side of given name.
    Example:
        #                                    1111111111222222
        #                          01234567890123456789012345
        #                                         ^
        #                                         |

        >>> find_first_right_paren('((a,((b,c),(d,e))),(f,g));', 'd')
        15
    """
    index_right = clean_tree_str.find(one_name)
    while clean_tree_str[index_right] != ')':
        index_right += 1
    return index_right


def left_side_left_paren(clean_tree_str, left_index_now):
    """Find first '(' on the left side of current '('.
    Example:
        #          1111111111222222222233
        #01234567890123456789012345678901
        '((a ,((b, c), (d, e))), (f, g));'
        #     ^                          ^
        #     |        |
        #     new      now

        >>> left_side_left_paren('((a,((b,c),(d,e))),(f,g));', 14)
        5
    """
    stack = []
    stack.append(')')
    while len(stack) > 0:
        if left_index_now == 0:
            return left_index_now
        left_index_now -= 1
        if clean_tree_str[left_index_now] == ')':
            stack.append(')')
        elif clean_tree_str[left_index_now] == '(':
            if len(stack) == 1:
                return left_index_now
            stack.pop()
        else:
            continue
    return left_index_now


def get_right_index_of_name(clean_tree_str, one_name):
    """Get the right index of givin name.
    #                                      111111111122222222
    #                            0123456789012345678901234567
    #                                           |

    >>> get_right_index_of_name('((a,((b,c),(ddd,e))),(f,g));', 'ddd')
    15
    """
    left_index_of_name = clean_tree_str.find(one_name)
    while clean_tree_str[left_index_of_name] not in set([',', ';', ')', '"',
                                                         "'", '#', '$', '@',
                                                         '>', '<']):
        left_index_of_name += 1
    return left_index_of_name


def get_insertion_list(clean_tree_str, name_to_find):
    """Get a list of insertition point index and return it."""
    insertion_list = []
    left_index_now = clean_tree_str.find(name_to_find) - 1
    if clean_tree_str[left_index_now] != '(' and\
            clean_tree_str[left_index_now] == ',':
        index_right_paren = find_first_right_paren(
            clean_tree_str, name_to_find)
        # insertion_list.append(index_right_paren+1)
        left_index_now = index_right_paren
    else:
        left_index_now = clean_tree_str.find(name_to_find) - 1
        insertion_list.append(
            find_right_paren(clean_tree_str, left_index_now)+1)
    # print(left_index_now)
    while left_index_now >= 0:
        if left_index_now == 0:
            # final_point = find_right_paren(clean_tree_str, left_index_now)
            # print('Final point: ', final_point)
            # insertion_list.append(final_point + 1)
            # print('[Final Insertion List]: ', name_to_find,
            #       '\n\t\t\t', insertion_list)
            return insertion_list
        left_index_now = left_side_left_paren(clean_tree_str, left_index_now)
        # print('new index: %d' % left_index_now)
        insertion_list.append(
            find_right_paren(clean_tree_str, left_index_now) + 1)
        # print('Insertion list now: ', insertion_list)
    return insertion_list


def single_calibration(tree_str, name_a, name_b, cali_info):
    """Do single calibration. If calibration exists, replace it."""
    clean_tree_str = get_clean_tree_str(tree_str)
    insertion_list_a = get_insertion_list(clean_tree_str, name_a)
    insertion_list_b = get_insertion_list(clean_tree_str, name_b)
    insertion_list_a, insertion_list_b = insertion_list_a[::-1],\
        insertion_list_b[::-1]
    shorter_list = insertion_list_a if len(insertion_list_a) <\
        len(insertion_list_b) else insertion_list_b
    longer_list = insertion_list_a if shorter_list == insertion_list_b else\
        insertion_list_b
    # print('[Shorter List]: ', shorter_list)
    # print('[Longer List]:  ', longer_list)
    for i, each_in_shorter_list in enumerate(shorter_list):
        if i == len(shorter_list) - 1:
            cali_point = each_in_shorter_list
        if shorter_list[i] != longer_list[i]:
            cali_point = shorter_list[i - 1]
            break
    # print('[Common]:         ', cali_point)
    print('\n[Insert]:  ', clean_tree_str[cali_point-20:cali_point+20])
    print('[Insert]:  ', '                 ->||<-                  ')
    print('[Insert]:  ', '               Insert Here               ')

    # Check if there are duplicate calibration
    current_info = '%s, %s, %s' % (name_a, name_b, cali_info)
    if cali_point not in _insertion_list_point_dict:
        _insertion_list_point_dict[cali_point] = current_info
    else:
        print('\n[Warning]   Duplicate calibration:           [ !!! ]')
        print('[Exists]:   %s\n'
              '[ Now  ]:   %s\n' % (_insertion_list_point_dict[cali_point],
                                    current_info))

    # No calibration before
    if clean_tree_str[cali_point] in set([',', ';', ')']):
        left_part, right_part = clean_tree_str[:cali_point],\
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
    elif clean_tree_str[cali_point] in set(['>', '<', '@', '0', '1', "'",
                                            '"', '$', ':']):
        # ((a,((b,c),(d,e)))>0.3<0.5,(f,g));
        # left_part = '((a,((b,c),(d,e)))'
        # right_part = '>0.3<0.5,(f,g));'
        # re will find '>0.3<0.5' part
        re_find_left_cali = re.compile('^[^,);]+')
        left_part, right_part = clean_tree_str[:cali_point],\
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
    insertition_point = get_right_index_of_name(clean_tree_str, name_a)
    print('\n[Insert]:  ',
          clean_tree_str[insertition_point-20:insertition_point+20])
    print('[Insert]:  ', '                 ->||<-                  ')
    print('[Insert]:  ', '               Insert Here               ')

    # Check is there was something there
    # Nothing there before
    if clean_tree_str[insertition_point] in set([',', ';', ')']):
        left_part, right_part = clean_tree_str[:insertition_point],\
            clean_tree_str[insertition_point:]
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
    elif clean_tree_str[insertition_point] in set(['>', '<', '@', '0', '1',
                                                   "'", '"', '$', ':', '#']):
        # ((a,((b,c),(d,e)))>0.3<0.5,(f,g));
        # left_part = '((a,((b,c),(d,e)))'
        # right_part = '>0.3<0.5,(f,g));'
        # re will find '>0.3<0.5' part
        re_find_left_cali = re.compile('^[^,);]+')
        left_part, right_part = clean_tree_str[:insertition_point],\
            clean_tree_str[insertition_point:]
        left_cali = re_find_left_cali.findall(right_part)[0]
        print('[Label Exists]:          ' + left_cali + '  [- Old]')
        print('[Label Replaced By]:     ' + branch_label + '  [+ New]')
        # '>0.3<0.5,(f,g));'.lstrip('>0.3<0.5') will be ',(f,g));'
        final_right_part = right_part.lstrip(left_cali)
        clean_str_with_cali = (left_part + ' %s ' % branch_label +
                               final_right_part)
    else:
        raise ValueError('[Error] [Unknown Symbol]: ' +
                         clean_tree_str[insertition_point])
    return clean_str_with_cali


def multi_calibration(tree_str, cali_tuple_list):
    """Do calibration for multiple calibration requests."""
    global _insertion_list_point_dict
    _insertion_list_point_dict = {}
    print('\n\n====================================================')
    print('=============== [ New Job: %s] ===============' % time_now())
    print('====================================================')
    for i, each_cali_tuple in enumerate(cali_tuple_list):
        if len(each_cali_tuple) == 3:
            name_a, name_b, cali_or_clade_info = each_cali_tuple
            print('\n')
            print('[%d]:  %s' % (i+1, ', '.join(each_cali_tuple)))
            print('-' * 52)
            print('[Name A]:  ', name_a)
            print('[Name B]:  ', name_b)
            print('[ Info ]:  ', cali_or_clade_info)
            for name in (name_a, name_b):
                if name not in tree_str:
                    raise ConfigFileSyntaxError('Name not in tree file:  ',
                                                name)
            if cali_or_clade_info[0] not in set(['>', '<', '@', '#',
                                                 '$', "'", '"', ':']):
                print('\n[Warning]: Is this valid symbel?  %s     [ !!! ]\n' %
                      cali_or_clade_info)
            tree_str = single_calibration(tree_str, name_a, name_b,
                                          cali_or_clade_info)
            print('-' * 52)
        elif len(each_cali_tuple) == 2:
            name_a, branch_label = each_cali_tuple
            print('\n')
            print('[%d]:  %s' % (i+1, ', '.join(each_cali_tuple)))
            print('-' * 52)
            print('[ Name ]:  ', name_a)
            print('[ Info ]:  ', branch_label)
            if name_a not in tree_str:
                raise ConfigFileSyntaxError('name_a not in tree file:  ',
                                            name_a)
            if branch_label[0] not in set(['@', '#', '$', "'", ':']):
                print('\n[Warning]: Is this valid symbel?  %s     [ !!! ]\n' %
                      branch_label)
            tree_str = add_single_branch_label(tree_str, name_a, branch_label)
            print('-' * 52)
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
            raise ConfigFileSyntaxError('Invalid line: [%d]: %s' % (i+1, line))
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


# def write_str_to_file(orig_tree_file_name, str_to_write):
#     """Write string to a file"""
#     re_extension = re.compile('[^.]+$')
#     extension = re_extension.findall(orig_tree_file_name)[0]
#     out_file_name = orig_tree_file_name.rstrip(extension) + 'cali.'\
#         + extension
#     with open(out_file_name, 'w') as f:
#         f.write(str_to_write)
#         print('\n[New Tree Written] >>>>> %s\n' % out_file_name)


def main():
    """Main GUI Application."""
    app = App()
    app.mainloop()


if __name__ == '__main__':
    main()
