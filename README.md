# jMeter Performace Result Upload Utility
[jMeter](https://jmeter.apache.org/) is an Open Source testing software. It is 100% pure Java application for load and performance testing. jMeter is designed to cover categories of tests like load, functional, performance, regression, etc.

jMeter run produces output in various format like xml, csv etc. This utility will read .csv report and store it into Mongo db provided by user.

## Installation
### Checkout Repository
```
git clone https://github.com/digitedevops/jMeter-Performance-Report-Parser.git
```
#### Pre-Requisite
1. We need Mongo DB to store performance report csv data. You can use Mongo DB Docker image for the same. Refer [Mongo Docker Image documentation](https://hub.docker.com/_/mongo/)
2. Set host ip and port for Mongo DB in perf/perf.ini file

#### Create Virtual Environment
Virtualenv is the easiest and recommended way to configure a custom Python environment for your services.
To install virtualenv execute below command:
```sh
$pip3 install virtualenv
```
You can check version for virtual environment version by typing below command:
```sh
$virtualenv --version
```
Create a virtual environment for a project:
```
$ cd my_project_folder
$ virtualenv virtenv
```
virtualenv `virtenv` will create a folder in the current directory which will contain the Python executable files, and a copy of the pip library which you can use to install other packages. The name of the virtual environment (in this case, it was `virtenv`) can be anything; omitting the name will place the files in the current directory instead.

This creates a copy of Python in whichever directory you ran the command in, placing it in a folder named `virtenv`.

You can also use the Python interpreter of your choice (like python3.6).
```
$virtualenv -p /usr/bin/python3.6 virtenv
```
To begin using the virtual environment, it needs to be activated:
```
$ source virtenv/bin/activate
```
The name of the current virtual environment will now appear on the left of the prompt (e.g. (virtenv)Your-Computer:your_project UserName$) to let you know that it’s active. From now on, any package that you install using pip will be placed in the virtenv folder, isolated from the global Python installation. You can add python packages needed in your microservice decelopment within virtualenv. 

#### Install python module dependanceies
```
pip install -r requirements.txt
```
#### To start microservice 
```
python perf/perfreport.py
```
#### To access index page
```
http://<yourip>:5002/index
```
