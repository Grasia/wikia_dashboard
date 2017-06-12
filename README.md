# wikia_dashboard
This is a python tool for the anaylisis of Wikia wikis. The application creates a dashboard from a database dump which can be used to extract information about the wiki. It is intended for wiki administrators as well as those interested in commob-based peer production analysis

# Software Prerrequisites
To use this tool you need to have the following:

Python 3.5 (at least)
  
Bokeh  0.12.5 (at least)
 
SQLite3 3.8.6 (at least)

# Instructions for Windows systems

The easiest way to install all the needed software is to install Anaconda. The latest version of Anaconda can be found in the following location:
 
 https://www.continuum.io/downloads
 
When installing it is important to add the folder to PATH in the enviroment variables, which usually can be done automatically with the installation. Also, the Script subfolder of the Anaconda3 folder created by the installation should be added to PATH. Here you can find more information about how to add to PATH in Windows:
 
 https://www.computerhope.com/issues/ch000549.htm
 
 After the installation, it is recommended to update mentioned above. This can be done with the command "conda update <package>". For example:
 
`conda update bokeh`

Once the installation is done you can proceed and clone this repository to your local machine.

# Instructions for Linux systems

First, check you've installed python 3:
`python3 --version`

or install it if you don't have it:
`sudo apt install python3`

Install anaconda following the steps described [here](https://www.continuum.io/downloads#linux).

And, finally, install *numpy* for python3:
`pip3 install numpy`

Now you can download this project using git clone:
`git clone https://github.com/Grasia/wikia_dashboard`

# Getting a wiki datadump
To download a wiki's datadump you need to go to the statistics page. For this just add "/special:statistics" at the end of your wiki URL. For example:
http://starwars.wikia.com/Special:Statistics

On the section database dumps you should see two links: one for current pages and another one which includes history. Either one is okay, depending on what you wish to analyse. For more information please check the below link:

http://community.wikia.com/wiki/Help:Database_download

Once you download and unzipped the file, you must move it to the project folder that you previously downloaded.

# Setting up the project

After downloading both the project and the XML dump, you should have a folder named dashboard with all the project files inside it, as well as the xml database dump.

The first step for using the application is to generate the txt file from the XML dump. To do that you need to open a console and travel to the dashboard folder, where both the XML and the dump_parser.py file should be stored. Once there use the following command:

`python dump_parser.py <file.xml>`

or, in unix/linux systems with both python 2 and python 3 installed, use this:

`python3 dataHandler.py <file.txt>`

Where file.xml is the file you wish to process. The next step would be to load this data into our database. This can be done using the following command (still on the same folder):

`python dataHandler.py <file.txt>`

or, in unix:

`python3 dataHandler.py <file.txt>`

Where file.txt is the output file from the previous step. Now everything is ready to go. In the command line, you need to go to the parent folder of the folder dashboard, and then execute the following command:

`bokeh serve --show dashboard`

This will open a web browser with the application. The result should be similar to this:

![alt text](https://github.com/Grasia/wikia_dashboard/blob/master/sample_snapshot.PNG)
