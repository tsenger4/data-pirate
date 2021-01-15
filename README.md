# data-pirate
Repository for Data Pirate Challenge project.

# **Overview**

The main objective of this project is extract from a specific website Brazilian range postal codes and stores the output into a file.

The project was developed using the technologies below:

`Pip >= 20.0.2`

`Virtualenv >= 20.0.18`

`Python >= 3.8.3`

`Scrapy >= 2.4.1`

`Spidermon >= 1.14.0`

## How it works

The python application accesses the postal codes welcome page and extracts the available `<options>` from main form, containing the UF index reference to get data of the specific query data form page through individual POST requisitions. 

In each iteration, some small activities are executed to parse the collected attributes. The main activities are cleaning, validation and storing the data. 
When the application is running, a log text file is created for each execution, according to the current datetime. 

The application is monitored and tested at run time execution and a Telegram notification is sent to a specific chat/group with the log results of each action realized. 

At the end of execution, the output generated is available with the postal codes ranges in json lines format.

## Setup the environment

 1. To create the virtual environment, is necessary add the package on system python pip default installation

`pip install virtualenv`

 2. Check the Python 3 installation folder

`which python3`

 3. Copy the installation path to set the environment ENV3-DATAPIRATE

`virtualenv --python='/usr/local/bin/python3' ENV3-DATAPIRATE`

 4. Navigate and access the project folder root

`cd date-pirate/`

 5. Activate the virtualenv

`source ./ENV3-DATAPIRATE/bin/activate`

 6. Install the project requirements packages

`pip install -r requirements.txt`

 7. Execute the Data Pirate spider

`scrapy runspider data-pirate.py`

### Telegram notification

Spidermon allows the test execution log to be sent through requests to the Slack or Telegram applications. In this project, Telegram was chosen due to its ease of configuration. This step is not mandatory. 
An example with the response of requests is available below:

 - Success
 
	![enter image description here](https://cdn.discordapp.com/attachments/799615244078940163/799615320313692180/telegram-2.png)

	> The test monitor to checked the spider extracted items, was found a number bigger than the minimum acceptable items.

 - Failure
 
	![enter image description here](https://cdn.discordapp.com/attachments/799615244078940163/799615315407011840/telegram-1.png)

	> The test monitor to checked the spider extracted items, was found a number smaller than the minimum acceptable items.

## Output

The output with postal code ranges is available on this format:

 - Columns attributes
 
	`["UF", "UF-COUNTER", "UNIQUE ID", "RANGE BEGIN", "RANGE END", "COUNTY", "RANGE RAW", "NOTE", "NOTE 2"]`

 - Example for one county of Acre
 
	`["AC", "ac-11", "ab0f3ebd9f84323b9571851cce8762e9", "69983-000", "69984-999", "Marechal Thaumaturgo", "69983-000 a 69984-999", "Não codificada por logradouros", "Total do município"]`

 - Example for one county of Alagoas

	`["AL", "al-58", "652088ecc2a331a0aecb680fa73969de", "57440-000", "57441-999", "Monteirópolis", "57440-000 a 57441-999", "Não codificada por logradouros", "Total do município"]`

## Notes

 1. The parser will extract only postal code ranges of two UF's. To get for all UF, is necessary just uncomment the line that references the *input* element. `DataPirateSpider:parse::L2`
 2. At the spider development, I have been indentified the opportunity to realize de parsing with only one requisition per UF, according with Form params accepted by the page. It was not implemented because the objective of this project is just to demonstrate the skills about manage and follow data between different pages.

Any suggestions or comments, please keep in touch.