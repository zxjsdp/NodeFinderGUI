NodeFinderGUI
=============
GUI for NodeFinder Program

Introduction
------------

This is GUI implementation  for NodeFinder program, used for adding information to
bipartition/multifurcating Newick format phylogenetic tree:

1. Calibration info;
2. Clade Label;
3. Branch Label


Command Line Version
--------------------
[NodeFinder](https://github.com/zxjsdp/NodeFinder)


Screenshot
----------
![Screenshot](./data/screen_shot.png)


Simple Usage
------------

Config line syntax:

    name_a, name_b, calibration_infomation
    name_a, name_b, clade_label_information
    name, branch_label_information
    ..., ..., ...

Input tree need to be Newick format phylogenetic tree. For example:

    (human, (cat, dog));

You can add multiple lines at the same time. The program will finish all
operations automatically.

Please refer to [NodeFinder](https://github.com/zxjsdp/NodeFinder) for more detailed
usage and other information.


Demo
----

Input:
    
    AF083022_Poikilolaimus_regenfussi, AF083017_Rhabditoides_inermiformis, >0.109<0.317
    AF083022_Poikilolaimus_regenfussi, DQ094172_Ascarophis_arctica, >0.222<0.358

Output log:

    [1]:  AF083022_Poikilolaimus_regenfussi, AF083017_Rhabditoides_inermiformis, >0.109<0.317
    ----------------------------------------------------
    [Name A]:   AF083022_Poikilolaimus_regenfussi
    [Name B]:   AF083017_Rhabditoides_inermiformis
    [ Info ]:   >0.109<0.317
    [Insert]:   toides_inermiformis),((((((((DQ094172_As
    [Insert]:                       ->||<-                  
    [Insert]:                    Insert Here               
    ----------------------------------------------------


    [2]:  AF083022_Poikilolaimus_regenfussi, DQ094172_Ascarophis_arctica, >0.222<0.358
    ----------------------------------------------------
    [Name A]:   AF083022_Poikilolaimus_regenfussi
    [Name B]:   DQ094172_Ascarophis_arctica
    [ Info ]:   >0.222<0.358
    [Insert]:   helenchus_avenae)))),AF036607_Teratoceph
    [Insert]:                    ->||<-                  
    [Insert]:                  Insert Here               
    ----------------------------------------------------


Implementation
--------------

Given two species, this program finds all ancestor nodes for each species by
using stack (to exclude other monophyletic group) and parenthesis. Then compare
these two ancestor node list and find the index of most recent common
ancestor nodes. 

For example:

    List of ancestor nodes index:
    species1:     [57, 62, 73, 102, 162, 214, 258]
                                ^    ^    ^    ^
                                |    |    |    |
    species2: [39, 48, 81, 94, 102, 162, 214, 258]

    Then 102 will be the index of most recent common ancestor node.
