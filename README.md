# wikia_dashboard
This is a python tool for the anaylisis of Wikia wikis. The application creates a dashboard from a database dump which can be used to extract information about the wiki. It is intended for wiki administrators as well as those interested in commob-based peer production analysis

# Software Prerrequisites
To use this tool you need to have the following:

Python 3.5 (at least)

Bokeh  0.12.6 (at least)

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

First, check you've installed both python 3 and pip3:
`python3 --version`
`pip3 --version`

or install it if you don't have them:
`sudo apt install python3`
`sudo apt install python3-pip`

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

## Using a sample datadump
Alternatively, you can use the Laguna Negra's datadump included in this repo as an example.

To use this, you'll need to decompress the 7zip file located in sample_data into the dashboard folder. And then follow the instructions written below.
In a unix-like system this could be simply done with the 7zip utility:
`7z e sample_data/eslagunanegra_pages_full.xml.7z -odashboard/`

# Setting up the project

After downloading both the project and the XML dump, you should have a folder named dashboard with all the project files inside it, as well as the xml database dump.

The first step for using the application is to generate the csv file from the XML dump. To do that you need to open a console and travel to the dashboard folder, where both the XML and the dump_parser.py file should be stored. Once there use the following command:

`python dump_parser.py <file.xml>`

or, in unix/linux systems with both python 2 and python 3 installed, use this:

`python3 dump_parser.py <file.txt>`

Where file.xml is the file you wish to process. The next step would be to load this data into our database. This can be done using the following command (still on the same folder):

`python database_generator.py <file.csv>`

or, in unix:

`python3 database_generator.py <file.csv>`

Where file.txt is the output file from the previous step. Now everything is ready to go. In the command line, you need to go to the parent folder of the folder dashboard, and then execute the following command:

`bokeh serve --show dashboard`

This will open a web browser with the application. The result should be similar to this:

![alt text](https://github.com/Grasia/wikia_dashboard/blob/master/sample_snapshot.PNG)

# Run the webapp
Alternatively to directly use `bokeh`, you can use the launch.py script. It makes it easy and handy to run the webapp successively, specially if you're working with different datasets.

Just go to the root of the project and run `python3 launch.py <databasename>`. The script will search for an available port and will start bokeh listening on that port, as well as it will open a browser tab with the corresponding address.

If you want to know which databases are available to be launched, simply run `python3 launch.py`.
