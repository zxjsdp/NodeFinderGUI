ó
ºWc           @ sN  d  Z  d d l m Z m Z d d l Z d d l Z d d l Z d d l Z d d l m	 Z	 m
 Z
 e j d d k r´ d d l Z d d l Z d d l Z d d l Z d d l Z nm e j d d k rd d l Z d d l m Z d d	 l m Z d d
 l m Z d d l j Z n e d   d Z d Z d Z d Z d d Z d d Z d e e f Z d e e f Z  e! d d d d d d d d d d g
  Z" e! d d d g  Z# e! d d d d d  d d d d! g	  Z$ e! d d d g  Z% e! d d d d d  d d d d! d g
  Z& e! d d d d d d d d! g  Z' e! d d d d d! g  Z( i  a) d" e* f d#     YZ+ d$   Z, d% e- f d&     YZ. d' e- f d(     YZ/ d) e- f d*     YZ0 d+ e j1 f d,     YZ2 d-   Z3 d.   Z4 d/   Z5 d0   Z6 d1   Z7 d2   Z8 d3   Z9 d4   Z: d5   Z; d6   Z< d7   Z= e> d8 k rJe=   n  d S(9   sD   
NodeFinder: Do calibration or add Branch Label or add Clade Label.
iÿÿÿÿ(   t   with_statementt   print_functionN(   t   Popent   PIPEi    t   2t   3(   t   ttk(   t
   messagebox(   t
   filedialogs$   Cannot identify your Python version.s   0.4.6t   Jins   NodeFinder GUIt   1200x700t   ~i2   t   =s§   
%s, GUI implementation of NodeFinder
    Version  :  %s
    URL (GUI):  https://github.com/zxjsdp/NodeFinderGUI
    URL (C)  :  https://github.com/zxjsdp/NodeFinderC
s~  
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
t   ,t   ;t   )t   "t   't   #t   $t   @t   >t   <t   0t   1t   :t   ConfigFileSyntaxErrorc           B s   e  Z d  Z RS(   s   Error class for config file(   t   __name__t
   __module__t   __doc__(    (    (    s   nodefinder_gui.pyR   s   s   c           C s   t  j d t  j    S(   s3   Return a formatted time string: Hour:Minute:Second.s   %H:%M:%S(   t   timet   strftimet	   localtime(    (    (    s   nodefinder_gui.pyt   time_nowx   s    t   RightClickMenuc           B s_   e  Z d  Z d   Z d   Z d   Z d   Z d   Z d   Z d   Z	 d   Z
 d	   Z RS(
   s5  
    Simple widget to add basic right click menus to entry widgets.

    usage:

    rclickmenu = RightClickMenu(some_entry_widget)
    some_entry_widget.bind("<3>", rclickmenu)

    If you prefer to import Tkinter over Tix, just replace all Tix
    references with Tkinter and this will still work fine.
    c          sQ   |   _    j  j d   f d   d d   j  j d   f d   d d d  S(   Ns   <Control-a>c          s
     j    S(   N(   t   _select_all(   t   e(   t   self(    s   nodefinder_gui.pyt   <lambda>   s    t   addt   +s   <Control-A>c          s
     j    S(   N(   R#   (   R$   (   R%   (    s   nodefinder_gui.pyR&      s    (   t   parentt   bind(   R%   R)   (    (   R%   s   nodefinder_gui.pyt   __init__   s    	"c         C s:   |  j  j d  d k r d  S|  j  j   |  j |  d  S(   Nt   statet   disable(   R)   t   cgett   focus_forcet
   build_menu(   R%   t   event(    (    s   nodefinder_gui.pyt   __call__   s    c         C sD  t  j |  j d d } |  j j   sV | j d d d d  | j d d d d  n2 | j d d d |  j  | j d d d |  j  |  j   r° | j d d	 d |  j  n | j d d	 d d  |  j j   sî | j d d
 d d  n | j d d
 d |  j	  | j
   | j d d d |  j  | j | j | j  d S(   s   Build right click menut   tearoffi    t   labelt   CutR,   R-   t   Copyt   commandt   Pastet   Deletes
   Select AllN(   t   tkt   MenuR)   t   selection_presentt   add_commandt   _cutt   _copyt   paste_string_statet   _pastet   _cleart   add_separatorR#   t   postt   x_roott   y_root(   R%   R1   t   menu(    (    s   nodefinder_gui.pyR0      s    
c         C s   |  j  j d  d  S(   Ns   <<Cut>>(   R)   t   event_generate(   R%   (    (    s   nodefinder_gui.pyR>   ¾   s    c         C s   |  j  j d  d  S(   Ns   <<Copy>>(   R)   RH   (   R%   (    (    s   nodefinder_gui.pyR?   Á   s    c         C s   |  j  j d  d  S(   Ns	   <<Paste>>(   R)   RH   (   R%   (    (    s   nodefinder_gui.pyRA   Ä   s    c         C s   |  j  j d  d  S(   Ns	   <<Clear>>(   R)   RH   (   R%   (    (    s   nodefinder_gui.pyRB   Ç   s    c         C s'   |  j  j d d  |  j  j d  d S(   Ni    t   endt   break(   R)   t   selection_ranget   icursor(   R%   (    (    s   nodefinder_gui.pyR#   Ê   s    c         C s(   y |  j  j d d  } Wn t SXt S(   s,   Returns true if a string is in the clipboardt	   selectiont	   CLIPBOARD(   R)   t   selection_gett   Falset   True(   R%   t	   clipboard(    (    s   nodefinder_gui.pyR@   Ó   s
    (   R   R   R   R+   R2   R0   R>   R?   RA   RB   R#   R@   (    (    (    s   nodefinder_gui.pyR"   }   s   					"						t   RightClickMenuForScrolledTextc           B sh   e  Z d  Z d   Z d   Z d   Z d   Z d   Z d   Z d   Z	 d   Z
 d	   Z d
   Z RS(   s>   Simple widget to add basic right click menus to entry widgets.c          sQ   |   _    j  j d   f d   d d   j  j d   f d   d d d  S(   Ns   <Control-a>c          s
     j    S(   N(   R#   (   R$   (   R%   (    s   nodefinder_gui.pyR&   é   s    R'   R(   s   <Control-A>c          s
     j    S(   N(   R#   (   R$   (   R%   (    s   nodefinder_gui.pyR&   ê   s    (   R)   R*   (   R%   R)   (    (   R%   s   nodefinder_gui.pyR+   ã   s    	"c         C s=   |  j  j d  t j k r d  S|  j  j   |  j |  d  S(   NR,   (   R)   R.   R:   t   DISABLEDR/   R0   (   R%   R1   (    (    s   nodefinder_gui.pyR2   ì   s    c         C s÷   t  j |  j d d } | j d d d |  j  | j d d d |  j  |  j   rr | j d d d |  j  n | j d d d d	  | j d d
 d |  j  | j	   | j d d d |  j
  | j d d d |  j  | j | j | j  d S(   s
   build menuR3   i    R4   R5   R7   R6   R8   R,   R-   R9   s
   Select Alls	   Clear AllN(   R:   R;   R)   R=   R>   R?   t   _paste_string_statet   _paste_if_string_in_clipboardt   _deleteRC   R#   t
   _clear_allRD   RE   RF   (   R%   R1   RG   (    (    s   nodefinder_gui.pyR0   õ   s    
c         C s   |  j  j d  d  S(   Ns   <<Cut>>(   R)   RH   (   R%   (    (    s   nodefinder_gui.pyR>     s    c         C s   |  j  j d  d  S(   Ns   <<Copy>>(   R)   RH   (   R%   (    (    s   nodefinder_gui.pyR?     s    c         C s   |  j  j d  d  S(   Ns	   <<Clear>>(   R)   RH   (   R%   (    (    s   nodefinder_gui.pyRW     s    c         C s   |  j  j d  d  S(   Ns	   <<Paste>>(   R)   RH   (   R%   (    (    s   nodefinder_gui.pyRV     s    c         C s=   |  j  j d d d  |  j  j d d  |  j  j d  d S(   s
   select allt   sels   1.0s   end-1ct   insertRJ   (   R)   t   tag_addt   mark_sett   see(   R%   (    (    s   nodefinder_gui.pyR#   "  s    c         C s(   y |  j  j d d  } Wn t SXt S(   s,   Returns true if a string is in the clipboardRM   RN   (   R)   RO   RP   RQ   (   R%   RR   (    (    s   nodefinder_gui.pyRU   )  s
    c         C s>   t  d d d |  j d d } | r: |  j j d d  n  d S(	   s	   Clear alls	   Clear Alls   Erase all text?R)   t   defaultt   oks   1.0RI   N(   t   askokcancelR)   t   delete(   R%   t   isok(    (    s   nodefinder_gui.pyRX   5  s    	(   R   R   R   R+   R2   R0   R>   R?   RW   RV   R#   RU   RX   (    (    (    s   nodefinder_gui.pyRS   à   s   					!						t   TextEmitc           B s#   e  Z d  Z d d  Z d   Z RS(   s)   Redirect stdout and stderr to tk widgets.t   stdoutc         C s   | |  _  | |  _ d S(   s=   Initialize widget which stdout and stderr were redirected to.N(   t   widgett   tag(   R%   Re   Rf   (    (    s   nodefinder_gui.pyR+   @  s    	c         C sr   |  j  j d d  |  j  j d | |  j f  |  j  j d d d d d |  j  j d d	  |  j  j d  d
 S(   s   Proceed Redirection.R,   t   normalRI   t   stderrt
   foregroundt   redt
   backgroundt   yellowt   disabledN(   Re   t	   configureRZ   Rf   t   tag_configureR]   (   R%   t   out_str(    (    s   nodefinder_gui.pyt   writeE  s    (   R   R   R   R+   Rq   (    (    (    s   nodefinder_gui.pyRc   =  s   t   Appc           B s  e  Z d  Z d d  Z d   Z d   Z d   Z d   Z d   Z	 d   Z
 d   Z d	   Z d
   Z d   Z d   Z d   Z d   Z d   Z d   Z d   Z d   Z d   Z d   Z d   Z d   Z d   Z d   Z d   Z d   Z d   Z d   Z RS(   sj   The main class for GUI application.

    [Example]
        >>> app = App()
        >>> app.mainloop()
    c         C s¢   t  j j |  |  |  j j t  |  j j t  d |  _ g  |  _	 d |  _
 |  j   |  j   |  j   |  j   |  j   |  j   |  j   |  j   d  S(   Nt    i    (   R:   t   FrameR+   t   mastert   titlet	   GUI_TITLEt   geometryt   INIT_WINDOW_SIZEt
   final_treet   file_path_history_listt   combo_line_countt	   set_stylet   create_widgetst   configure_gridt   row_and_column_configuret   create_right_menut	   bind_funct   display_infot   create_menu_bar(   R%   Ru   (    (    s   nodefinder_gui.pyR+   W  s    			






c         C s±   t  j   } | j d d d | j d d d | j d d d f | j d	 d d
 | j d d d | j d  | j d d d d d | j d d d d d d S(   s   Set custom style for widget.t   TButtont   paddingi   s   execute.TButtonRi   Rj   s   newline.TButtoni   s   clear.TButtons   #2AA198t	   TComboboxs   config.TComboboxs   title.TLabeli
   t   fontt	   helveticai   t   bolds   config.TLabeli   t   ariali	   N(   s	   helveticai   s   bold(   R   i	   (   R   t   StyleRn   (   R%   t   s(    (    s   nodefinder_gui.pyR}   k  s*    
c         C sþ  t  j |  j d d |  _ t  j |  j d d |  _ t  j |  j d d |  _ t  j |  j d d |  _ t  j |  j d d d d |  _ t  j	 |  j d d |  _
 t  j	 |  j d d d d	 |  _ t j   |  _ t  j |  j d
 |  j |  _ t  j	 |  j d d |  _ t j |  j  |  _ t  j |  j d d d d |  _ t  j	 |  j d d d d |  _ t  j	 |  j d d d d	 |  _ t  j	 |  j d d |  _ t  j	 |  j d d |  _ t  j |  j d d d d |  _ t  j |  j d d d d |  _ t  j |  j d d d d |  _ t  j	 |  j d d d d |  _ t  j |  j d d |  _ t  j |  j d d |  _ t  j |  j d d |  _  t j |  j  |  _! t  j |  j d d d d |  _" t  j	 |  j d d |  _# t  j	 |  j d d |  _$ t  j	 |  j d d |  _% t  j	 |  j d d d d	 |  _& |  j& j' d d d d d  d!  t j |  j d" d# |  _( t  j |  j d d$ d d |  _) t  j	 |  j d d% |  _* t  j	 |  j d d d d	 |  _+ t j |  j d& d' d" d( d) d* |  _, d+ S(,   s¸   Create widgets in the main window.

        There are four main panes:
            1. tree_pane
            2. config_pane
            3. out_tree_pane
            4. log_pane
        R   i   t   texts   Origin Treet   styles   title.TLabels   Open Tree File...t   Clears   clear.TButtont   textvariables   Load Historyt   Configurations   Execute Alls   execute.TButtons   Read Config File...s   Save Config to File...s   Name As   config.TLabels   Name Bt   Infos   Add News   newline.TButtons   config.TComboboxs   Tree Outputs   View As ASCIIs
   Quick Saves   Save New Tree As...t   rowi    t   columni   t   stickyt   wet   bgs   #FAFAFAs   Results and Logs   Save Log As...t   fgs   #FDF6E3s   #002B36R,   Rm   N(-   R   Rt   Ru   t	   tree_panet   config_panet   out_tree_panet   log_panet   Labelt   choose_tree_labelt   Buttont   open_tree_file_buttont   clear_tree_inputR:   t	   StringVart	   tree_namet   Comboboxt   choose_tree_boxt   load_history_buttont   stt   ScrolledTextt   tree_paste_areat   config_labelt   execute_buttont   clear_config_area_buttont   read_config_file_buttont   save_config_to_file_buttont   name_a_labelt   name_b_labelt
   info_labelt   add_newline_buttont   name_a_comboboxt   name_b_comboboxt   info_comboboxt   config_lines_areat   out_tree_labelt   view_as_ascii_buttont   save_current_dir_buttont   save_as_buttont   clear_out_tree_buttont   gridt   out_tree_areat	   log_labelt   save_log_buttont   clear_log_buttont   log_area(   R%   (    (    s   nodefinder_gui.pyR~     s¶    																	c      	   C s  |  j  j   |  j j d d d d d d  |  j j d d d d d d  |  j j d d d d d d  |  j j d d d d d d  |  j j d d d d d d  |  j j d d d d d d  |  j j d d d d	 d d  |  j	 j d d d d d
 d	 d d  |  j
 j d d d d	 d d  |  j j d d	 d d d
 d d d  |  j j d d d d d d  |  j j d d d d	 d d  |  j j d d d d d d  |  j j d d d d	 d d  |  j j d d d d d d  |  j j d d	 d d d d  |  j j d d	 d d	 d d  |  j j d d	 d d d d  |  j j d d d d d d  |  j j d d d d d d  |  j j d d d d	 d d  |  j j d d d d d d  |  j j d d d d d
 d d d  |  j j d d d d d d  |  j j d d d d d d  |  j j d d d d	 d d  |  j j d d d d d d  |  j j d d d d d
 d d d  |  j j d d d d d d  |  j j d d d d d d  |  j  j d d d d	 d d  |  j! j d d d d d
 d d d  d  S(   NR   i    R   R   t   wensi   t   wR   i   t
   columnspanR$   i   t   wsi   i   ("   Ru   R½   R   R   R   R   R   R¡   R¢   R¦   R§   Rª   R«   R¬   R­   R®   R¯   R°   R±   R²   R³   R´   Rµ   R¶   R·   R¸   R¹   Rº   R»   R¾   R¿   RÀ   RÁ   RÂ   (   R%   (    (    s   nodefinder_gui.pyR   e  sH    %c         C s  |  j  j d d d |  j  j d d d |  j  j d d d |  j  j d d d |  j j d d d |  j j d d d |  j j d d d |  j j d d d |  j j d d d |  j j d d d |  j j d d d |  j j d d d |  j j d d d |  j j d d d |  j j d d d |  j j d d d |  j j d d d |  j j d d d |  j j d d d |  j j d d d |  j j d d d |  j j d d d |  j j d d d |  j j d d d |  j j d d d |  j j d d d |  j j d d d |  j j d d d |  j j d d d |  j j d d d d  S(   Ni    t   weighti   i   i   i   (   Ru   t   rowconfiguret   columnconfigureR   R   R   R   (   R%   (    (    s   nodefinder_gui.pyR      s<    c         C sò   t  |  j  } |  j j d |  t |  j  } |  j j d |  t  |  j  } |  j j d |  t  |  j  } |  j j d |  t  |  j  } |  j j d |  t |  j  } |  j j d |  t |  j	  } |  j	 j d |  d  S(   Ns
   <Button-3>(
   R"   R¦   R*   RS   Rª   R´   Rµ   R¶   R·   R¾   (   R%   t   right_menu_tree_chooset   right_menu_inputt   right_menu_name_at   right_menu_name_bt   right_menu_info_comboboxt   right_menu_configt   right_menu_out(    (    s   nodefinder_gui.pyR   Ö  s    c          sö     j    j d <  f d     j d <  j   j d <  f d     j d <  j   j d <  j   j	 d <  j
   j d <  j   j d <  j   j d <  j   j d <  j   j d <  f d     j d <  j   j d <  j   j d <d  S(   NR7   c            s     j  j d d  S(   Ns   1.0RI   (   Rª   Ra   (    (   R%   (    s   nodefinder_gui.pyR&   ô  s    c            s     j  j d d  S(   Ns   1.0RI   (   R·   Ra   (    (   R%   (    s   nodefinder_gui.pyR&   ø  s    c            s     j  j d d  S(   Ns   1.0RI   (   R¾   Ra   (    (   R%   (    s   nodefinder_gui.pyR&     s    (   t   _ask_open_fileR¡   R¢   t   _load_history_fileR§   R­   t   _read_config_from_fileR®   t   _save_config_to_fileR¯   t   _set_value_to_textareaR³   t
   _main_workR¬   t   _view_as_ascii_commandR¹   t   _save_new_tree_to_current_dirRº   t   _ask_save_out_as_fileR»   R¼   t   _ask_save_log_as_fileRÀ   t
   _clear_logRÁ   (   R%   (    (   R%   s   nodefinder_gui.pyR   ð  s    c         C s=  t  j |  j  } t  j | d d } | j d d d |  j  | j   | j d d d |  j  | j d d d |  j  | j   | j d d d |  j  | j	 d d	 d
 |  t  j | d d } | j d d d |  j
  | j d d d |  j  | j	 d d d
 |  t  j | d d } | j d d d |  j  | j d d d |  j  |  j   r| j d d d |  j  n | j d d d d    | j d d d |  j  | j	 d d d
 |  t  j | d d } | j d d d |  j  | j d d d |  j  | j	 d d d
 |  |  j j d
 |  d S(   s!   Create Menu Bar for NodeFinderGUIR3   i    R4   s   Open input tree file...R7   s   Save output tree to file...s   Save log to file...t   Exitt   FileRG   s   Open config file...s   Save config to file...t   ConfigsR5   R6   R8   c           S s
   t  d  S(   Ns   No string in clipboard!(   t   print(    (    (    s   nodefinder_gui.pyR&   1  s    R9   t   Editt   Documentationt   Aboutt   HelpN(   R:   R;   Ru   R=   RÑ   RC   RÙ   RÚ   t   quitt   add_cascadeRÓ   RÔ   R>   R?   RU   RA   RW   t   display_documentationt   display_aboutt   config(   R%   t   menu_bart	   file_menut   configs_menut	   edit_menut	   help_menu(    (    s   nodefinder_gui.pyR     sD    






	

c         C s"   t  t  t  t  t  t  d S(   s0   Display documentation for menu bar about button.N(   Rß   t   LONG_BARt   DOCUMENTATION(   R%   (    (    s   nodefinder_gui.pyRæ   >  s    

c         C s"   t  t  t  t  t  t  d S(   s4   Display about information for menu bar about button.N(   Rß   Rî   t   ABOUT(   R%   (    (    s   nodefinder_gui.pyRç   O  s    

c         C s|   t  |  j d  t _ t  |  j d  t _ t t  t d t t f  t t	 j
 d t	 j     t t  t d  d  S(   NRd   Rh   s     %s (Ver %s)s     %d %b %Y,  %a %H:%M:%SsH   
If you need help, please check the menu bar:

   Help -> Documentation
(   Rc   RÂ   t   sysRd   Rh   Rß   Rî   Rw   t   __version__R   R   R    (   R%   (    (    s   nodefinder_gui.pyR   U  s    

c         C s   |  j  j   j d  d  S(   Ns   <<Copy>>(   Ru   t	   focus_getRH   (   R%   (    (    s   nodefinder_gui.pyR?   a  s    c         C s   |  j  j   j d  d  S(   Ns   <<Cut>>(   Ru   Ró   RH   (   R%   (    (    s   nodefinder_gui.pyR>   f  s    c         C s   |  j  j   j d  d  S(   Ns	   <<Paste>>(   Ru   Ró   RH   (   R%   (    (    s   nodefinder_gui.pyRA   l  s    c         C s   |  j  j   j d  d  S(   Ns	   <<Clear>>(   Ru   Ró   RH   (   R%   (    (    s   nodefinder_gui.pyRW   p  s    c         C s(   y |  j  j d d  } Wn t SXt S(   s,   Returns true if a string is in the clipboardRM   RN   (   Ru   RO   RP   RQ   (   R%   RR   (    (    s   nodefinder_gui.pyRU   s  s
    c         C sß   i  } t  j d d |  } y | j   } |  j j d d  |  j j d |  | j } t j j	 |  } t
 d t   | f  |  j j d |  |  j |  j d <|  j j d  Wn" t k
 rÚ t
 d	 t    n Xd
 S(   s   Dialog to open file.t   modet   rs   1.0RI   s    [ INFO | %s ] Open tree file: %si    t   valuesR   s   [ INFO | %s ] No file choosedN(   t   tkFileDialogt   askopenfilet   readRª   Ra   RZ   t   namet   ost   patht   basenameRß   R!   R{   R¦   t   currentt   AttributeError(   R%   t   file_optt   ct   orig_tree_strt   abs_patht	   base_name(    (    s   nodefinder_gui.pyRÑ     s    	c         C sº   |  j  j   } | s/ t j j d t    n t j j |  s[ t j j d t    n[ t	 | d   } | j
   } Wd QX|  j j d d  |  j j d |  t d t    d S(   s   Load file from history.s)   [ ERROR | %s ] History file bar is blank
s   [ ERROR | %s ] No such file
Rõ   Ns   1.0RI   s   [ INFO | %s ] Load file(   R¦   t   getRñ   Rh   Rq   R!   Rû   Rü   t   isfilet   openRù   Rª   Ra   RZ   Rß   (   R%   t	   file_patht   ft   content(    (    s   nodefinder_gui.pyRÒ     s    c         C s   i  } t  j d d |  } | d k r+ d S| j   } |  j j d d  |  j j d |  | j } t j	 j
 |  } t d t   | f  d S(   s!   Read calibration config from fileRô   Rõ   Ns   1.0RI   s'   [ INFO | %s ] Read from config file: %s(   R÷   Rø   t   NoneRù   R·   Ra   RZ   Rú   Rû   Rü   Rý   Rß   R!   (   R%   R   R  t   config_contentR  R  (    (    s   nodefinder_gui.pyRÓ   ¡  s    	c         C s^   t  j d d d d  } | d k r( d St |  j j d d   } | j |  | j   d S(   s/   Save current calibration config content to fileRô   RÄ   t   defaultextensions   .txtNs   1.0s   end-1c(   R÷   t   asksaveasfileR  t   strR·   R  Rq   t   close(   R%   R	  t   text_to_save(    (    s   nodefinder_gui.pyRÔ   ±  s    c         C sø   |  j  j   |  j j   |  j j   } } } t d   | | | g  } t |  d k  sc | r· t j j d t	    t j j d  t j j d  t j j d  t
 d  n= d j |  } |  j j d	 | d
  t
 d t	   | f  d S(   s   Value to textarea.c         S s
   |  d k S(   NRs   (    (   t   x(    (    s   nodefinder_gui.pyR&   ¿  s    i   s   [ ERROR | %s ]
[Usage]
s,       Calibration:  name_a, name_b, cali_info
s'       Branch Label: name_a, branch_label
s.       Clade Label:  name_a, name_b, clade_label
Rs   s   , RI   s   
s,   [ INFO - %s ]  Added one configure line (%s)N(   R´   R  Rµ   R¶   t   filtert   lenRñ   Rh   Rq   R!   Rß   t   joinR·   RZ   (   R%   t   name_at   name_bt   infot   config_listt   one_line(    (    s   nodefinder_gui.pyRÕ   »  s     #			c         C s  |  j  j d d  } | sE t j j d t    t j d d  n  y t d d   } | j |  Wd QXt	 d	 d
 d g d t
 d t
 } t | j   d  | j   d rÏ t j j | j   d  n  Wn- t k
 rÿ } t j d d d d |  n Xd S(   s#   View tree using ascii tree program.s   1.0s   end-1cs1   [ ERROR | %s] No content in out tree area to viewt
   ValueErrors'   No content in Tree Output area to view.s   tmp_file_for_ascii_view.nwkRÄ   Nt   pythons   tree_ascii_view.pywRd   Rh   i    i   Rv   s
   File Errort   messages'   Cannot write temporary file to disk.
%s(   R¾   R  Rñ   Rh   Rq   R!   t   tkMessageBoxt	   showerrorR  R   R   Rß   t   communicatet   IOError(   R%   t   new_tree_strR	  t   pR$   (    (    s   nodefinder_gui.pyR×   Ï  s.    
		!	c         C s[   |  j  j d d  } d } t | d  + } | j |  t d t   | f  Wd QXd S(   s)   Quick save Newick tree to current folder.s   1.0s   end-1cs   New_tree.nwkRÄ   s   [ INFO | %s ] Quick save: (%s)N(   R¾   R  R  Rq   Rß   R!   (   R%   t   new_tree_contentt   new_tree_nameR	  (    (    s   nodefinder_gui.pyRØ   ì  s    c         C s^   t  j d d d d  } | d k r( d St |  j j d d   } | j |  | j   d S(   s   Dialog to save as file.Rô   RÄ   R  s   .txtNs   1.0s   end-1c(   R÷   R  R  R  R¾   R  Rq   R  (   R%   R	  R  (    (    s   nodefinder_gui.pyRÙ   ö  s    c         C s^   t  j d d d d  } | d k r( d St |  j j d d   } | j |  | j   d S(   s   Dialog to save as file.Rô   RÄ   R  s   .txtNs   1.0s   end-1c(   R÷   R  R  R  RÂ   R  Rq   R  (   R%   R	  R  (    (    s   nodefinder_gui.pyRÚ     s    c         C s=   |  j  j d d  |  j  j d d  |  j  j d d  d S(   s&   Clear all contents in log widget area.R,   Rg   s   1.0RI   Rm   N(   RÂ   Rn   Ra   (   R%   (    (    s   nodefinder_gui.pyRÛ     s    c         C su   t  |  j j d d   } t |  j j d d   } t | |  |  _ |  j j d d  |  j j	 d |  j  d S(   s   Do main job.s   1.0s   end-1cRI   N(
   t   get_tree_strRª   R  t   get_cali_listR·   t   multi_calibrationRz   R¾   Ra   RZ   (   R%   t   tree_strt   calibration_list(    (    s   nodefinder_gui.pyRÖ     s    c         C s   t  d  d S(   s&   Simple hello function for testing use.s   Hello NodeFinderGUI!N(   Rß   (   R%   (    (    s   nodefinder_gui.pyt   hello  s    N(    R   R   R   R  R+   R}   R~   R   R   R   R   R   Ræ   Rç   R   R?   R>   RA   RW   RU   RÑ   RÒ   RÓ   RÔ   RÕ   R×   RØ   RÙ   RÚ   RÛ   RÖ   R+  (    (    (    s   nodefinder_gui.pyRr   O  s:   	"	Ø	;	6			3												
			
		
			c         C s   g  |  D] } | j    ^ q S(   sS  Strip each element in list and return a new list.
    [Params]
        orig_list: Elements in original list is not clean, may have blanks or
                   newlines.
    [Return]
        clean_list: Elements in clean list is striped and clean.

    [Example]
        >>> clean_elements(['a ', '	b	', 'c
'])
        ['a', 'b', 'c']
    (   t   strip(   t	   orig_listt   _(    (    s   nodefinder_gui.pyt   clean_elements  s    c         C s(   |  j  d d  j  d d  j  d d  S(   s   Remove all blanks and return a very clean tree string.
    >>> get_clean_tree_str('((a ,((b, c), (d, e))), (f, g));'')
    '((a,((b,c),(d,e))),(f,g));'
    t    Rs   s   
s   	(   t   replace(   R)  (    (    s   nodefinder_gui.pyt   get_clean_tree_str.  s    c         C s4   |  j  |  } x |  | t k r/ | d 7} q W| S(   s#  Get the right index of givin name.
    #                                      111111111122222222
    #                            0123456789012345678901234567
    #                                           |
    >>> get_right_index_of_name('((a,((b,c),(ddd,e))),(f,g));', 'ddd')
    15
    i   (   t   findt   NONE_TREE_NAME_SYMBOL_SET(   t   clean_tree_strt   one_namet   left_index_of_name(    (    s   nodefinder_gui.pyt   get_right_index_of_name6  s
    
	c         C s   g  } |  j  |  } g  } t |   } xq | | k  r |  | d k rV | j d  n7 |  | d k r | s | j | d  q | j   n  | d 7} q* W| S(   s   Get insertion list
    t   (R   i   (   R3  R  t   appendt   pop(   R5  Rú   t   insertion_listt   current_indext   stackt   str_len(    (    s   nodefinder_gui.pyt   get_insertion_listE  s    c         C s  t  |  |  } t  |  |  } | d d d  | d d d  } } t |  t |  k  rc | n | } | | k r{ | n | } x_ t |  D]Q \ } } | t |  d k r¹ | }	 n  | | | | k r | | d }	 Pq q Wt |   }
 t d |	  |	 d k  o|
 |	 k n rDt d d d |	 |  |	 d  f  n¨ |	 d k o_|
 |	 k n rt d |  |	 d |	 |
 |	 ! nd |	 d k  rÏ|
 |	 d k  rÏt d d d |	 |  |	 |
 |	  f  n t d |  |	 d |	 d ! t d	  t d
  |	 S(   s,   Get index of the most recent common ancestorNiÿÿÿÿi   s   [Common]:   %s
i   s   [Insert]:   %s%sR0  s   [Insert]:   %ss4   [Insert]:                    ->||<-                 s4   [Insert]:                  Insert Here              (   R@  R  t	   enumerateRß   (   R5  R  R  t   insertion_list_at   insertion_list_bt   shorter_listt   longer_listt   it   each_in_shorter_listt
   cali_pointt   tree_len(    (    s   nodefinder_gui.pyt   get_index_of_tmrcaY  sB    		  

c         C sA  t  |   } t | | |  } d | | | f } | t k rJ | t | <n" t d  t d t | | f  | | t k r¢ | |  | | } } | | | }	 n | | t k r)t j d  }
 | |  | | } } |
 j |  d } t d | d  t d | d	  | j	 |  } | | | }	 n t
 d
 | |   |	 S(   s9   Do single calibration. If calibration exists, replace it.s
   %s, %s, %ss5   
[Warning]   Duplicate calibration:           [ !!! ]s   [Exists]:   %s
[ Now  ]:   %s
s   ^[^,);]+i    s   [Calibration Exists]:          s	     [- Old]s   [Calibration Replaced By]:     s	     [+ New]s	   Unknown: (   R2  RJ  t   global_insertion_list_cacheRß   t   NO_CALI_EXISTS_SYMBOL_SETt   WITH_CALI_EXISTS_SYMBOL_SETt   ret   compilet   findallt   lstripR  (   R)  R  R  t	   cali_infoR5  RH  t   current_infot	   left_partt
   right_partt   clean_str_with_calit   re_find_left_calit	   left_calit   final_right_part(    (    s   nodefinder_gui.pyt   single_calibration  s0    
c         C s  t  |   } t | |  } t |  } t d |  | d k  oP | | k n r| t d d d | | | d  f  n¨ | d k o | | k n rÀ t d | | d | | | ! nd | d k  r| | d k  rt d d d | | | | |  f  n t d | | d | d ! t d  t d  | | t k rr| |  | | } } | d | | } n£ | | t k rt j d	  }	 | |  | | } } |	 j |  d
 }
 t d |
 d  t d | d  | j	 |
  } | d | | } n t
 d | |   | S(   s£   Add single label right after one name.
    >>> add_single_branch_label('((a ,((b, c), (d, e))), (f, g));', c, '#1')
    '((a ,((b, c #1 ), (d, e))), (f, g));'
    s   [Common]:   %s
i   s   [Insert]:   %s%sR0  s   [Insert]:   %ss4   [Insert]:                    ->||<-                 s4   [Insert]:                  Insert Here              s    %s s   ^[^,);]+i    s   [Label Exists]:          s	     [- Old]s   [Label Replaced By]:     s	     [+ New]s   [Error] [Unknown Symbol]: (   R2  R8  R  Rß   t   NO_LABEL_EXISTS_SYMBOL_SETt   WITH_LABEL_EXISTS_SYMBOL_SETRN  RO  RP  RQ  R  (   R)  R  t   branch_labelR5  t   insert_pointRI  RT  RU  RV  RW  RX  RY  (    (    s   nodefinder_gui.pyt   add_single_branch_labelº  sJ      


c   
      C sf  i  a  t d  t d t    t d  t d  x; t |  D]- \ } } t d | d d j |  f  qB WxÚt |  D]Ì\ } } t |  d k r| \ } } } t d	  t t  t d
 | d d j |  f  t t  t d |  t d |  t d |  x2 | | f D]$ } | |  k r t d |   q q W| d t k rit d |  n  t	 |  | | |  }  q t |  d k r | \ } } t d	  t t  t d
 | d d j |  f  t t  t d |  t d |  | |  k rt d |   n  | d t
 k r7t d |  n  t |  | |  }  q q W|  j d d  }	 |	 S(   s1   Do calibration for multiple calibration requests.s6   

====================================================s                   [ New Job: %s]s4   ====================================================s   
[Valid Calibrations]
s	   %4d |  %si   s    ,i   s   
s	   [%d]:  %ss   , s   [Name A]:  s   [Name B]:  s   [ Info ]:  s   Name not in tree file:  i    s2   
[Warning]: Is this valid symbel?  %s     [ !!! ]
i   s   [ Name ]:  s   name_a not in tree file:  R   (   RK  Rß   R!   RA  R  R  t   THIN_BARR   t%   WARNING_CALI_OR_LABEL_INFO_SYMBOL_SETRZ  t   WARNING_BRANCH_LABEL_SYMBOL_SETR_  R1  (
   R)  t   cali_tuple_listRF  t   each_cali_tupleR  R  t   cali_or_clade_infoRú   R]  Rz   (    (    s   nodefinder_gui.pyR(  ÿ  sX    


%

!
	

!
c         C sÔ   g  } g  |  j  d  D] } | j   r | j   ^ q } x t |  D] \ } } | j   } | d d d h k r{ qG n  t | j  d   } t |  d
 k r¿ t d | d	 | f   n  | j |  qG W| S(   s   Get calibration list.s   
i    R   s   //R   i   i   s   Invalid line: [%d]: %si   (   i   i   (   t   splitR,  RA  R/  R  R   R:  (   t   raw_cali_contentt   tmp_cali_listR.  t   linesRF  t   linet   elements(    (    s   nodefinder_gui.pyR'  3  s    4	c         C s   d } t  } |  j d  } xj | D]b } | j   } | j d  rL t } n  | sX q" n  | j d  sv | j d  rz Pq" | | 7} q" W| S(   s0   Read tree content, parse, and return tree stringRs   s   
R9  s   //R   (   RP   Rf  R,  t
   startswithRQ   (   t   raw_tree_contentt   tmp_tree_strt   tree_start_flagRi  Rj  (    (    s   nodefinder_gui.pyR&  J  s    	c          C s   t    }  |  j   d S(   s   Main GUI Application.N(   Rr   t   mainloop(   t   app(    (    s   nodefinder_gui.pyt   main\  s    	t   __main__(?   R   t
   __future__R    R   Rû   RN  Rñ   R   t
   subprocessR   R   t   versiont   TkinterR:   R   R  R÷   R©   R¨   t   tkinterR   R   t   tkinter.scrolledtextt   scrolledtextt   ImportErrorRò   t
   __author__Rw   Ry   R`  Rî   Rð   Rï   t   setR4  RL  RM  R[  R\  Ra  Rb  RK  t   SyntaxErrorR   R!   t   objectR"   RS   Rc   Rt   Rr   R/  R2  R8  R@  RJ  RZ  R_  R(  R'  R&  Rr  R   (    (    (    s   nodefinder_gui.pyt   <module>   sx   

5'$'!	c]ÿ ÿ Ò					0	1	E	4			