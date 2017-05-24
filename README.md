# wikia_dashboard
Python tool that creates a dashboard from a Wikia data dump. Intended for administrators with access to the latest data dump. To use this tool you need to have the following:

  -Python 3.5 +
  -Bokeh  0.12.5 +
  -SQLite3 3.8.6
  
 The easiest way to install all the needed software is to install Anaconda. The latest version of Anaconda can be found in the following location:
 
 https://www.continuum.io/downloads
 
 When installing it is important to add the folder to PATH in the enviroment variables, as well as the Scripts subfolder.After the installation, it is recommended to update all the packages needed. This can be done with the command "conda update <package>". For example:
 
> conda update bokeh

Once the installation is done you can proceed and download the project. You should have a folder with the following structure:

dashboard
   |
   +---main.py
   +---dataHandler.py
   +---dump_parser.py
   +---static
        +-----
   +---theme.yaml
   +---templates
        +---index.html


The first step for using the application is to generate the txt file from the XML dump. To do that you need to open a console and travel to the dashboard folder, where both the XML and the dump_parser.py file should be stored. Once there use the following command:

>python dump_parser.py <file.xml>

Where file.xml is the file you wish to process. The next step would be to load this data into our database. This can be done using the following command (still on the same folder):

>python dataHandler.py <file.txt>

Where file.txt is the output file from the previous step. Now everything is ready to go. In the command line, you need to go to the parent folder of the folder dashboard, and then execute the following command:

>bokeh serve --show dashboard

This will open a web browser with the application.
