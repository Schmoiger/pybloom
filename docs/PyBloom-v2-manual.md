PyBloom

Indicate the outside temperature on Philips Hue lights.

Note on typefaces:  
Code snippets and variable names that are in my program  
*Learning points* to look up in your favourite search engine  
URLs to take you to source material  
\<\> enclose information that will be different for your setup

# **Preface**

I started this project before AI was famous and API prividers were realising that they needed to charge to stay in business. All of this content was learnt by researching and trial and error. Nowadays I'd do it all very differently.

---

# **Objectives**

As is the case with many complicated things in life, this project started with a simple objective statement:

“Replace the temperature to lights feature currently implemented in IFTTT paid-for, into a free method.”

It turns out that there’s a bit to unpack from this statement in order to develop the requirements to build against. Let’s get into the detail:

* “Currently implemented in IFTTT paid-for”: [IFTT is going pro](https://www.google.com/url?q=https://staceyoniot.com/everything-you-need-to-know-about-ifttt-pro/&sa=D&ust=1603647715680000&usg=AOvVaw3ulR3e_t4pEPQZ-hF4sHlx) = no longer free. It’s not worth a monthly fee to me, for the value it delivers to my IoT home.  
* “Into a free method”: There are plenty of web-hosted services that are free, or have a free tier. Moreover, the Philips Hue service is actually hosted in my own home, so will never have a fee. My challenge is therefore to build something that is free.  
* Use services within their free tier  
* Use devices that I have lying around the house  
* “Temperature to lights feature”: Put simply, the feature that I built in IFTTT changes the colour of a Hue Bloom in my lounge in response to a temperature change. If the temperature goes above or below a certain threshold, the bloom light changes. I can then tell the temperature just by looking at the colour of the light.  
* Map outside temperature forecast to a colour  
* Show this colour in the Bloom

Because this isn’t hard enough, my wife suggested a couple of stretch targets:

* Graphically represent the temperature information  
* Maintain graphs of historical temperature information  
* Present in a way that is easy to access  
* Match the colours in the graphs to the colours in the Bloom

## **Technical Stories**

Let’s refactor these objectives into* technical stories* that I can build against.

Non-functional requirements

* Be free.  
* I settled on using the following technologies:  
* Open Weather Map API free tier  
* My Mac Mini as a development environment  
* An old first generation Raspberry Pi to be my always-on production environment  
* Main development language of Python (v3.7 in prod, v3.8 in dev)  
* Atom as my IDE  
* Flask as the web page building framework  
* Bootstrap as the CSS framework

Story: Check current weather

1. Create a weather observation class object:  
2. Initialisation function to call weather API to get current weather  
3. Representation string to give last called time  
4. Accessor for current temperature

Story: Assign colour depending on temperature 

1. Dictionary of temperature boundaries and colour if greater than  

Story: Change colour of Philips Hue Bloom to display temperature

1. Create a lounge bloom class object:  
2. Representation string to give current colour  
3. Accessor to set current colour

Story: Log the weather reading

1. Append new observation into SQL database  

Story: Make Hue colours available from external SQL database

1. Build SQL database in setup script  
2. Create lookup function to query db

Story: Calculate data points from observation

1. Export data from SQL to perform calculations  
2. Current temperature compared to this time yesterday  
3. Last 24h temperature distribution (= today) compared to previous 24h  
4. This weeks' temperature distribution compared to last week, last month, last year  
5. Render using PyGal

Story: Run every hour  
It became apparent to me that triggering the colour change when the temperature changed was beyond me. I couldn’t figure out a way to get an external service to trigger a message into my to-be-written code, whilst remaining within the free tier. For example, the Open Weather Map API has a limit of 1,000,000 calls per month. If the API proves to be chatty, and triggers a message every 0.1C, then I could use up even that generous allowance over the course of the month. So instead of having data pushed to me, I decided on scheduling regular polling of data.

1. Make observation at a time interval  
2. Calculate data points immediately after observation  
3. Create graphs

Story: Visualisation

1. Create static web page in Flask  
2. Read colours into table in web page (directly into HTML or Flask)  
3. Export bloom colours into SQLite database  
4. Create CSS  
5. CSS to make for nav bar  
6. CSS var() to take row hex from HTML and pass to CSS  
7. CSS for table  
8. Optimised for desktop, tablet, mobile  
9. Use task scheduler to take periodic observations  
10. Build rudimentary CMS  
11. Automatically update web page via CMS

Story: Serve page in local network

1. Host on the Raspberry Pi

## **Spikes**

Much of this was new to me, so I needed to spend some time researching the topics, undertaking tutorials and practice code, before I could write the application. These were my research spikes, expressed as questions. I recommend you work through the linked tutorials to get your head around the concepts.

1. How can I access my Raspberry Pi without attaching a keyboard and monitor (as a *headless* server)?  
2. [VNC tutorial](https://www.google.com/url?q=https://learn.adafruit.com/adafruit-raspberry-pi-lesson-7-remote-control-with-vnc/mac-screen-and-file-sharing&sa=D&ust=1603647715694000&usg=AOvVaw2Fx1ZEP_FB65mbiiiOopWZ)  
3. [SSH tutorial](https://www.google.com/url?q=https://www.raspberrypi.org/documentation/remote-access/ssh/unix.md&sa=D&ust=1603647715694000&usg=AOvVaw20DxTWKODOBe8cZUVAbBiN)  
4. [What to do if SSH complains about changed host](https://www.google.com/url?q=https://superuser.com/questions/1380591/ssh-how-to-add-host-to-ssh-known-host-file&sa=D&ust=1603647715694000&usg=AOvVaw0yFxIqWXym6W9_BtPxKtNu)     
5. Which tools should I install and use on my Mac for my development environment?  
6. [IDE For Python \- Best One](https://www.google.com/url?q=https://www.raspberrypi.org/forums/viewtopic.php?t%3D220413&sa=D&ust=1603647715695000&usg=AOvVaw1c0GZabVdm4Ij6xM7oGexL)  
7. [Getting Started with Atom](https://www.google.com/url?q=https://www.codecademy.com/articles/f1-text-editors&sa=D&ust=1603647715695000&usg=AOvVaw2wLFuEQBKHlSJTwIBHDnWP)    
8. How do I work with the Philips Hue API?  
9. [Get started with Hue](https://www.google.com/url?q=https://developers.meethue.com/develop/get-started-2/&sa=D&ust=1603647715696000&usg=AOvVaw3e2CfdEX3b8Hcmkj6uV4tz)   
10. How do I work with the Open Weather Map API?  
11. [Weather API](https://www.google.com/url?q=https://openweathermap.org/api&sa=D&ust=1603647715696000&usg=AOvVaw35GWhpxxiqFywC4vskWzVS)  
12. [How to use the OpenWeatherMap API with Python](https://www.google.com/url?q=https://medium.com/nexttech/how-to-use-the-openweathermap-api-with-python-c84cc7075cfc&sa=D&ust=1603647715696000&usg=AOvVaw2hKo9wTFTYeF7GaNwX1iUu)    
13. I don’t like MatPlotLib for data visualisation in Python. Which alternative should I use?  
14. [Style your data plots in Python with Pygal](https://www.google.com/url?q=https://opensource.com/article/20/6/pygal-python&sa=D&ust=1603647715697000&usg=AOvVaw2j18u2KzDZjzxaT1N_duN5)  
15. [Creating Interactive Charts with Python Pygal | Pluralsight](https://www.google.com/url?q=https://www.pluralsight.com/guides/creating-interactive-charts-with-python-pygal&sa=D&ust=1603647715697000&usg=AOvVaw0kPCwbWG9R9wjMi30OB0Ww)    
16. Having decided to use Flask to generate my website HTML from Python code, how do I use it?  
17. [The Flask Mega-Tutorial Part I: Hello, World\!](https://www.google.com/url?q=https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world&sa=D&ust=1603647715698000&usg=AOvVaw0SV4TVjZ4QTvb5Qyfa698H)  
18. [Flask Tutorial](https://www.google.com/url?q=https://www.tutorialspoint.com/flask/index.htm&sa=D&ust=1603647715698000&usg=AOvVaw2FBNi8j7HH_zLajzPtTql-)  
19. [Primer on Jinja Templating](https://www.google.com/url?q=https://realpython.com/primer-on-jinja-templating/&sa=D&ust=1603647715699000&usg=AOvVaw17Lre3BFSRiVKBWMFhIhnf)   
20. Having decided to use Bootstrap to generate by CSS to format my website, how do I use it?  
21. [Bootstrap Navbar Guideline \- examples & tutorial](https://www.google.com/url?q=https://mdbootstrap.com/docs/jquery/navigation/navbar/&sa=D&ust=1603647715699000&usg=AOvVaw3mQ1DKg-qU6bbNzUHgdiAV)  
22. [How to Customize Bootstrap](https://www.google.com/url?q=https://uxplanet.org/how-to-customize-bootstrap-b8078a011203&sa=D&ust=1603647715699000&usg=AOvVaw14VLh_U0GkyIJbwyKmDPwx)    
23. Having decided to use SQLite for my persistent data stores, how do I use it with Python and Flask?  
24. [SQLite Python](https://www.google.com/url?q=https://www.sqlitetutorial.net/sqlite-python/&sa=D&ust=1603647715700000&usg=AOvVaw2xXbFVJEsg598doODdAX-o)  
25.  [Date And Time Functions](https://www.google.com/url?q=https://www.sqlite.org/lang_datefunc.html&sa=D&ust=1603647715700000&usg=AOvVaw3ClRVVDLw4bHNFWb7T3Tyn)   
26. I want to show the same colours for the same temperature on my Bloom, on the graphs, and on the website. How do I export from the SQLite database into Python, into CSS?  
27. [JSFiddle \- Code Playground](https://www.google.com/url?q=https://jsfiddle.net/&sa=D&ust=1603647715701000&usg=AOvVaw00XGnM_2upgrOZ0mbWvY_v)   
28. How do I run two programs (the web server and gathering weather observations) simultaneously?  
29. [Introduction to APScheduler](https://www.google.com/url?q=https://medium.com/better-programming/introduction-to-apscheduler-86337f3bb4a6&sa=D&ust=1603647715701000&usg=AOvVaw25go-h9V0HfqZAG-pPZQfY)   
30. How do I run my program periodically, automatically?  
31. [Cache-Control \- HTTP](https://www.google.com/url?q=https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control&sa=D&ust=1603647715702000&usg=AOvVaw0DareDDboi-NYds7oEBhFR)  
32. [Flask before and after request functions](https://www.google.com/url?q=https://pythonise.com/series/learning-flask/python-before-after-request&sa=D&ust=1603647715702000&usg=AOvVaw08h5dmHuT4NQZ5qQbJPo8T)

---

# **Development Environment: Mac Mini**

For a development environment, I decided I needed a pretty user interface, and something that would help me keep track of all my indents and nested brackets. This isn’t particularly taxing for any modern computer, but none of my computing options are particularly modern, so I needed something lightweight. So I chose my Mac Mini to be my dev machine.

## **Atom IDE**

My machine is 10 years old, and a few macOS versions behind, so using heavyweight IDEs like Xcode is out of the question. Nor can I live without the pretty colours and error prompts without a nice IDE. I found Atom, built by the people who developed Git, and I like it lots. It’s hugely extensible with community-developed plugins, so I could create the combination for my needs. The ones I use the most turned out to be:

* Atom-beautify  
* Atom-file-icons  
* Atom-python-virtualenv  
* Busy-signal  
* Intentions  
* Linter  
* Linter-flake8  
* Linter-ui-default  
* Minimap  
* Python-autopep8

I recommend you look them up, if you’re interested in building your own Atom configuration, that will run on even old and creaky machines.

## **Google IDX online IDE**

There’s a new IDE on the block and it’s accessible from within a browser: [https://idx.google.com/](https://idx.google.com/). No more maintaining complex IDEs with plugins that always go out of date. It integrates with GitHub so everything’s in the cloud. Will this make managing complex local environments a thing of the past?

IDX does use custom environment config files (dev.nix) which are automatically generated and is added to the Git manifest.

The limitation might be obvious but bears repeating: by design some environment variables (API keys) are only local. They won’t exist in a cloud-based IDE. So the code won’t run in the cloud.

## **Virtual environments and file structure**

apt install virtualenvwrapper

There are plenty of reasons to work in a virtual environment, especially if your development machine is also your machine for everything else. I use a combination of virtualenv and virtualenvwrapper. Install using apt for all accounts, as it’s super userful.

The wrapper is actually a collection of *shell scripts*, which simplifies the creation and management of virtual environments and whole coding projects. Once installed, it makes sense that you need to let your shell app (Terminal for most people using a Mac) where these scripts are. Insert the following configuration statements into your .bash\_profile file.

export WORKON\_HOME=$HOME/.virtualenvs  
export PROJECT\_HOME=$HOME/Projects  
export VIRTUALENVWRAPPER\_PYTHON=/usr/bin/python3  
source /usr/local/bin/virtualenvwrapper.sh

Let’s go through each in order:

1. This is the location of the virtual environment files, relative to the home directory. This is the top level folder, into which the project folder is created. These files include the specific instance of Python being used, instances of any installed libraries, and any config files. The . prefix indicates that the folder is hidden in the Finder app (unless an option is checked).  
2. This is the location of the project files. Project files are in a separate top level folder, distinct from the environment files. Examples of project files are the Python script, web page source files, config tokens. The project is kept separate from the environment so that you can roll back one without rolling back the other.  
3. There are commonly a few different versions of Python installed. This makes explicit that we’re only interested in v3.  
4. As we installed virtualenvwrapper for everyone, the shell script is located in the generic usr folder.

mkproject pybloom  
workon pybloom

Once set up, it’s super easy to create and work in a virtual environment using the statements above. The first statement does three things: create a virtual environment in .virtualenvs called pybloom, and create a project folder in Projects also called pybloom, and links the two. The second statement activates the virtual environment, and changes the* working directory* to the pybloom project folder.

It’s worth taking a small detour into folder structures, as this gets quite complicated quite quickly. Unhelpfully, virtualenvwrapper and the [Flask documentation](https://www.google.com/url?q=https://flask.palletsprojects.com/en/1.1.x/tutorial/layout/&sa=D&ust=1603647715709000&usg=AOvVaw1ynue1YgbyVOd2jDfa6EzI) suggest two slightly different folder structures, so what we end up with is a hybrid. We’ll need to be clear about this structure, as Flask is sensitive about where certain files are located. This is my recommendation \- we’ll go through the content of each file as we progress through this project.

./Project/pybloom  
├── README.md  
├── pybloom.py  
├── utils.py  
├── db.sql  
├── docs/  
├── app.py  
├── app/  
│   ├── \_\_init\_\_.py  
│   ├── routes.py  
│   ├── content.py  
│   ├── templates/  
│   │   ├── base.html  
│   │   ├── feature1/  
│   │   │   ├── feature1\_page1.html  
│   │   │   └── feature1\_page2.html  
│   │   └── feature2/  
│   │       ├── feature2\_page1.html  
│   │       └── feature2\_page2.html  
│   └── static/  
│       ├── image.svg  
│       └── custom.css  
├── tests/  
│   ├── test\_data.sql  
│   └── test.py  
├── requirements.txt  
├── git/  
├── .gitignore  
└── MANIFEST.in  
./.virtualenvs/pybloom  
├── bin/  
├── lib/  
├── pyvenv.cfg  
└── credentials.py

## **Installing the packages**

I won’t spend too much time on describing the packages here, as it’ll make more sense to introduce them in context. If you're following along, go ahead and install all of them.

APScheduler  
Flask  
PyGal  
PyOWM  
Qhue  
rgbxy

(Aside: Unlike virtualenvwrapper previously, we can’t install these using apt (which downloads from the Ubuntu repository); these need to be installed using pip (from the Python Software Foundation repository). This is a shame as apt has a useful apt update && apt upgrade method which enables all packages that it knows about to be upgraded at the same time. Pip doesn’t have this, so each package needs to be updated individually.)

pip freeze \-\> requirements.txt

Once we’ve installed all that we need, this command records the versions that we’ve installed in a config file. And that’s it for setting up the Mac Mini.

---

# **Production Environment: Raspberry Pi**

Mine is a venerable RPi, a model B rev 2 from 2015\. It was purposefully undepowered in order to be cheap, but nowadays it feels really slow. But my program isn’t very compute-intensive, so it’s a perfect match. It makes a great always-on machine that doesn’t drink a lot of power.

## **Installing the OS**

I recommend starting every Pi project with a fresh install of the OS. It’s a chance to wipe away the acreted libraries that aren’t needed, and take advantage of the latest patches for everything. Simply download the [laterst version](https://www.google.com/url?q=https://www.raspberrypi.org/downloads/raspberry-pi-os/&sa=D&ust=1603647715714000&usg=AOvVaw0CSAXIXbpVio40OBcEKExB), and put onto an SD card of at least 16GB (use something like [Etcher](https://www.google.com/url?q=https://www.balena.io/etcher/&sa=D&ust=1603647715715000&usg=AOvVaw3KfBopksFiT_K5T7lWfJNz)), then boot up the Pi.

Once booted, remember to update the software, check the options to enable SSH and VNC on startup, and you’re done. Oh, make a note of its IP address; you’ll need it later.

## **Connecting the Mac to the RPi**

I make use of three different ways of connecting the Mac to the RPi, each for different use cases:

1. SSH is built into both RPi OS and macOS and is the quickest way of communicating between the two. It’s the best way of installing and upgrading libraries, as described in the next section. The biggest limitation is that if you start a thread on the RPi, then close the Terminal window on your Mac, then the RPi thread shuts down as well.  
2. VNC is built into the RPi OS, but needs an app downloaded to the Mac. It enables access to the GUI, which is the easiest way of navigating the Pi. It’s also the only way of starting processes in the RPi, which do not terminate if the VNC window is closed.  
3. AFP is supported by the Mac, and requires the netatalk library to be installed on the RPi. Obviously, you’ll need to install it by plugging in a keyboard, mouse and monitor otherwise you won’t be able to see what you’re doing\! Once installed, the RPi can appear in the Finder app as just another server. This makes promoting code from dev to prod as simple as copying and pasting.

## **Installing the packages**

To recap, these are the packages to be installed on the RPi.

APScheduler  
Flask  
PyGal  
PyOWM  
Qhue  
Rgbxy  
Netatalk

## **Virtual environments on the RPi**

Let’s connect to the RPi using SSH. At the command line, enter the following:

sudo pip install virtualenvwrapper

As the Pi is a single purpose computer, there’s less of a need to create a virtual environment. If the worst comes to the worst on the RPi, I can just re-cut another SD card and start again. So why bother? Well, it’s mainly to ensure we use the right version of Python. The code will only work on v3.x but the Pi also has v2.7 installed as well. In fact, if we run the command Python PyBloom.py will try to run the code on v2.7 \- and fail. So let’s go ahead and set up the virtual environment on the RPi.

export WORKON\_HOME=$HOME/.virtualenvs  
export PROJECT\_HOME=$HOME/Projects  
export VIRTUALENVWRAPPER\_PYTHON=/usr/bin/python3  
source /usr/local/bin/virtualenvwrapper.sh

As with the Mac, these statements complete the configuration altering the Bash script. This needs to be done in two locations on the RPi: .bashrc and .profile files. The former is loaded when you load bash after logging on (as in, from a terminal from RPi GUI) and the latter when you load Bash with logon (as in via SSH). Note that the location of the Python file is different on the RPi than the Mac, so setting the VIRTUALENVWRAPPER\_PYTHON global variable is different. (Note you can use source \~/.profile to reload the Bash profile without re-logging in.)

mkproject pybloom

As we saw before, this command sets up a project directory called pybloom in Projects, a virtual environment called pybloom in .virtualenvs, and links the two.

# **Organising the code**

The code should follow the technical stories described previously, but the mapping of module to story isn’t straightforward.

## **Mapping stories to modules**

| Technical Story | Code Module | Preparatory Spike |
| :---- | :---- | :---- |
| Check the current weather | Weather observation object in main script | How do I work with the Open Weather Map API? |
| Change the colour of the lounge bloom to display the temperature | Hue lamp object in main script | How do I work with the Philips Hue API? |
| Log the weather reading | Weather observation object in main script |  |
| Make the Hue colours available on an external database | Database utility | Having decided to use SQLite for my persistent data stores, how do I use it with Python and Flask? |
| Calculate the data points from the observation | Generate graphs function in main script |  |
| Data visualisation | Generate graphs function in main script | I don’t like MatPlotLib for data visualisation in Python. Which alternative should I use? |
| Serve page in local network | Web app HTML CSS | Having decided to use Flask to generate my website HTML from Python code, how do I use it? Having decided to use Bootstrap to generate by CSS to format my website, how do I use it? I want to show the same colours for the same temperature on my Bloom, on the graphs, and on the website. |
| Run every hour | Running the script periodically | How do I run my program periodically, automatically? How do I run two programs (the web server and gathering weather observations) simultaneously? |

Let’s get onto the actual writing.

---

# **Prerequisites**

Like all Python programs, my code builds upon libraries written by other people.

## **The code**

Each weather reading is called an *observation*. The weather\_observation class is responsible for fetching the current weather observation, for and for logging. Let’s get into it, starting with the third party libraries that I use.

from datetime import datetime, timedelta

Dates and times are funny to manage. Thankfully, both Python and SQLite have datetime modules that handle the complexity, simplifying the representation of the maths.

import qhue

Qhue provides a python wrapper for the Philips API, making it much more straightforward to access the lights as Python resources.

from rgbxy import Converter  
from rgbxy import GamutA

Philips Hue light colours are [complicated](https://www.google.com/url?q=https://developers.meethue.com/develop/get-started-2/core-concepts/%23colors-get-more-complicated&sa=D&ust=1603647715733000&usg=AOvVaw2kOci2UjyhtyWlgMLvsh3m). They use *(x,y) coordinates* that describe a point in a *colour space*.  CSS, the technology that describes the presentation of web sites, uses the *RGB representation* of colour. Thankfully, this library converts between the two, and even makes sure that the bulbs are able to show the colours (are within the bulb’s *gamut*).

import pyowm

Another wrapper, pyOWM provides a python wrapper for the OpenWeatherMap API. It provides a weather manager object that handles all the API complexity, and presents as a Python resource. The free version of the API has a limit of the number of calls allowed per month. To make sure I’m under this limit, the code writes each observation into a persistent database which can then be queried as many times as I like.

import sqlite3

To make the measurement data (and other data) persistent, it’s written into a database that can be accessed by other code objects such as the web page. Whilst there are many database technologies, I went with SQLite as it’s built into Python, so no need to download any more libraries.

import pygal

I’ve used powerful visualisation libraries like MatPlotLib and Seaborn, and they’re complicated because they’re powerful. By contrast, I found Pygal to be super easy.

from statistics import mean

Calculating mean isn’t built into Python so we need to import the function.

from dateutil.relativedelta import relativedelta

As we’ll see later, dates are handled slightly differently in each of the languages used in this project. Python hides some of the complexity in its date utilities. We’ll find the ability to calculate deltas for dates in a simple function useful.

from db\_setup import db\_connect, get\_rows

I wrote my own helper utilities to make connecting to, fetching data from, then shutting the connection to my SQLite database a little easier. Whilst there are other approaches like decorator functions to do this, a utility made more sense to me. More on this when we look at the code.

Here now are the global constants:

DATETIME\_STRING \= '%Y-%m-%d %H:%M:%S'  
FILEPATH \= './app/static/'

We’re going to need these two constants later on in the code, but because they’re trivial to understand, let’s introduce them now. The first governs how the datetime function mentioned earlier works in both Python and SQLite. More on the reason for the syntax in the section on logging.

The second constant is the file path for the web site assets. More on the reason for this file path in the section on presenting in a web page.

OWM\_KEY \= credentials.credentials\['owm\_key'\]  
HUE\_USERNAME \= credentials.credentials\['hue\_username'\]  
HUE\_IP \= credentials.credentials\['hue\_ip'\]  
HOME\_LOCATION \= credentials.credentials\['home\_location'\]

These global constants are the secrets used by the APIs to secure the calls. You’ll need to note your own in a credentials.py file, as we’ll see in a future section.

## **Putting it together**

from datetime import datetime, timedelta  
import qhue  
import pyowm  
from rgbxy import Converter  
from rgbxy import GamutA  
import sqlite3  
import pygal  
from db\_setup import db\_connect, get\_rows

DATETIME\_STRING \= '%Y-%m-%d %H:%M:%S'  
FILEPATH \= './app/static/'  
OWM\_KEY \= credentials.credentials\['owm\_key'\]  
HUE\_USERNAME \= credentials.credentials\['hue\_username'\]  
HUE\_IP \= credentials.credentials\['hue\_ip'\]  
HOME\_LOCATION \= credentials.credentials\['home\_location'\]

---

# **Weather observation object**

In this module, I use the Open Weather Map service to fetch the current weather at my location.

## **The technologies**

Open Weather Map API [https://openweathermap.org/api](https://www.google.com/url?q=https://openweathermap.org/api&sa=D&ust=1603647715738000&usg=AOvVaw0mVW2rEtwcg7JlBAqG5CH4) 

## **The code**

class WeatherObservation:

Each weather reading is called an *observation*. The WeatherObservation class is responsible for fetching the current weather observation, for and for logging. Let’s get into it.

Initialisation

def \_\_init\_\_(self, timestamp=None, temperature=None, detailed\_status=None):  
    self.timestamp \= timestamp,  
    self.temperature \= temperature,  
    self.detailed\_status \= detailed\_status

The observation has three components:  
Timestamp: time that the observation was taken  
Temperature: temperature at the location, at the time of the observation  
Detailed\_status: verbose description of weather at the location, at the time of the observation

This observation object is initialised with None values, to show if there’s never been an observation taken.

Representation string

def \_\_str\_\_(self):  
    return f'''Current weather: {self.detailed\_status}, {self.temperature} celsius (made at {self.timestamp})'''

It’s always good practice to include a representation string for debugging purposes. This is accessed by simply print ing the observation object, and the last observation content is displayed.

The mechanism for constructing this string uses Python 3’s *f-strings* - if you still use stock Python 2.7 then this won’t work for you.

Fetch new observation

def fetch(self, location):  \# expect e.g. 'London, GB'

The .fetch method fetches an observation. The API needs a location, so this is the only parameter that needs to be passed into the method. Note that the API needs a specific string format.

owm \= pyowm.OWM(OWM\_KEY)  
mgr \= owm.weather\_manager()  
weather \= mgr.weather\_at\_place(location).weather

These three commands together are how pyOWM accesses the API and then presents the observation. The weather object has a number of fields, but I’m only interested in the temperature and detailed\_status. The next three commands update the observation object.

self.timestamp \= datetime.now().strftime(DATETIME\_STRING)

The current timestamp is obtained not from the OWM API, but from the built-in datetime library. There are two chained methods used. The first .now() method is self-evident, but the second merits some examination.

Python’s datetime object is complicated because it’s built to simplify mathematical operations across time zones and local time. It’s also different to the datetime object used in other languages like SQLite. So to make sure both my Python and SQLite scripts have the same understanding of datetime, I use the built-in operators to transform to a string.

*Datetime (Python) \<-\> string (common syntax) \<-\> Datetime (SQLite)*

The .strftime() method handles the conversion into a string. But it can’t be any old string, it must be the same syntax that is accepted by both languages. The DATETIME\_STRING global constant from earlier defines this syntax:  
%Y: year in four digits, e.g. 2020  
%m: month in two digits, e.g. October \= 10  
%d: day in two digits, e..g first \= 01  
%h: hour in two digits  
%m: minute in two digits  
%s: second in two digits

self.temperature \= weather.temperature('celsius')\['temp'\]

The pyOWM.temperature object is quite extensive, so requires some parameters to access just the current temperature.

self.detailed\_status \= weather.detailed\_status

Verbose status is easier to access (although it isn’t really that verbose).

return 'Fetched new observation'

Whilst this function doesn’t need to return anything, as all it does is to fetch a new observation, it’s good practice to aid debugging to return a string. This way, the command print(observation.fetch()) returns an acknowledgement if successful.

Log an observation

def log(self):  
    \# also write to external database  
    con \= db\_connect()  
    cur \= con.cursor()

I’ll describe the db\_connect() utility in a later section, but the takeaway for now is that I’m using it to aid clarity. These two statements create a *cursor* object by connecting to the database. This object comes with a .execute method which passes a SQL statement, with a bit of SQLite cleverness, as a Python string. Here’s the SQL statement:

sql \= '''INSERT INTO observations (timestamp, temperature, detailed\_status)  
         VALUES (?, ?, ?)'''

It’s pretty basic SQL, but let’s break it down:  
INSERT INTO observations: SQL commands are in caps, variables in lower. Here, the variable is the table name within the database that we’re interested in.  
(timestamp, temperature, detailed\_status): these are the columns into which we’re going to put the values.  
VALUES (?, ?, ?): this is where the SQLite cleverness comes in; it allows us to pass in variables from the Python script into the SQL script.

cur.execute(sql, (self.timestamp, self.temperature, self.detailed\_status))

This .execute method combines the SQL and the variables to create the full SQL query that is applied to the database.

con.commit()  
con.close()

Once we’ve written the information to the table, we need to remember to commit the changes, then close the connection.

return 'Observation logged'

As before, an acknowledgement string is returned if successful.

Manually setting an observation (for debugging)

def set(self, timestamp, temperature, detailed\_status):  \# for debug  
    self.timestamp \= timestamp  
    self.temperature \= temperature  
    self.detailed\_status \= detailed\_status  
    return 'Observation set'

This final method is for debugging purposes, and allows me to set an observation manually.

## **Putting it together**

class WeatherObservation:

    def \_\_init\_\_(self, timestamp=None, temperature=None, detailed\_status=None):  
        self.timestamp \= timestamp,  
        self.temperature \= temperature,  
        self.detailed\_status \= detailed\_status

    def \_\_str\_\_(self):  
        return f'''Current weather: {self.detailed\_status},  
                     {self.temperature} celsius  
                            (made at {self.timestamp})'''

    def fetch(self, location):  \# expect e.g. 'London, GB'  
        owm \= pyowm.OWM(OWM\_KEY)  
        mgr \= owm.weather\_manager()  
        weather \= mgr.weather\_at\_place(location).weather  
        self.timestamp \= datetime.now().strftime(DATETIME\_STRING)  
        self.temperature \= weather.temperature('celsius')\['temp'\]  
        self.detailed\_status \= weather.detailed\_status  
        return 'Fetched new observation'

    def log(self):  
        \# write to external database  
        con \= db\_connect()  
        cur \= con.cursor()

        sql \= '''INSERT INTO observations (timestamp,  
                                           temperature,  
                                           detailed\_status)  
                 VALUES (?, ?, ?)'''  
        cur.execute(sql, (self.timestamp,  
                          self.temperature,  
                          self.detailed\_status))  
        con.commit()  
        con.close()  
        return 'Observation logged'

    def set(self, timestamp, temperature, detailed\_status):  \# for debug  
        self.timestamp \= timestamp  
        self.temperature \= temperature  
        self.detailed\_status \= detailed\_status  
        return 'Observation set'

---

# **Hue lamp object**

This is the module that accesses the colour light bulbs, Philips Hue Bloom, and changes the colour according to the temperature observation. The observations are accessed from the persistent SQLite database. The module then makes use of a Python library that wraps the Hue API, and a couple of utilities that do the maths to convert colours expressed as CSS hex values into xy values that the Hue lamps understand.

## **The technologies**

Philips Hue API  
Qhue library  
Rgbxy library  
SQLite database

## **The code**

Initialisation

class hue\_lamp:

    def \_\_init\_\_(self, lamp\_id):  
        \# not accessible  
        ip \= HUE\_IP  
        username \= HUE\_USERNAME

Instantiating a hue\_lamp object creates the accessors (getters and setters) for the lamp colours. These first two variables within the object are only needed during initialisation, in order to set up the connection to the Hue Bridge, so aren’t made available in an object method.

Time for a detour to get to know the Hue API. Philips encourages the hacker community and has comprehensive developer documentation on its [website](https://www.google.com/url?q=https://developers.meethue.com/develop/get-started-2/&sa=D&ust=1603647715756000&usg=AOvVaw1BaLUXZNLvTxRaxBdAmS4t), which walks through setup. Whilst the API is a RESTful interface, you don’t actually send messages to the cloud. Instead, you communicate with the Hue Bridge, which is somewhere in your internal network, so there are none of the security issues of the big bad internet.

self.bridge \= qhue.Bridge(ip, username)

The Bridge is identified uniquely by its IP address. It recognises your username as trustworthy, and allows access to its methods. How it decides you are trustworthy is simple and elegant \- when you set up the username on the Bridge, you have to press a button on the Bridge at the same time, therefore proving that you are in possession of it and that it’s in the same internal network.

self.getter \= self.bridge.lights\[lamp\_id\]()  
self.setter \= self.bridge.lights\[lamp\_id\]

The actual data object was a little difficult to get my head around, and it took a bit of trial and error to get the syntax for the *getter* and *setter* methods right. The getter is a function that returns a Python *dictionary* of all the resources associated with the bulb. This dictionary is created by Qhue from the JSON returned in the API. Here’s an example JSON response:

{  
    "state": {  
        "hue": 50000,  
        "on": true,  
        "effect": "none",  
        "alert": "none",  
        "bri": 200,  
        "sat": 200,  
        "ct": 500,  
        "xy": \[0.5, 0.5\],  
        "reachable": true,  
        "colormode": "hs"  
    },  
    "type": "Living Colors",  
    "name": "LC 1",  
    "modelid": "LC0015",  
    "swversion": "1.0.3"  
}

The setter is different as it reflects the difference in the API. The API allows sending a PUT message to the URL of the root of the bulb; you don’t have to access the URL of the actual setting.

self.is\_on \= self.getter\['state'\]\['on'\]  
self.colour \= self.getter\['state'\]\['xy'\]  
self.name \= self.getter\['name'\]

The final step in initialisation is to make a few of the statuses easier to access. Whether the light is on or not is a *boolean* within the state dictionary, which is itself within the returned dictionary. The colour (in *xy* values) is a *list* within the same dictionary. To access a dictionary within a dictionary you can simply chain the *key* names. By contrast, the name is a string in the returned dictionary, so no chaining is needed.

Representation string

def \_\_str\_\_(self):  
    if self.is\_on:  
        status \= 'on and is set to xy:' \+ str(self.colour)

As usual, I’ve written a representation string to aid in debugging. If the light is on, we have access to information on the state and colour.

else:  
    status \= 'off'

If the light is off, we don’t know its colour, so the status information is different.

return f'{self.name} is {status}'

The return string uses my favourite *f-string* Python function to construct the message.

Setter methods

def turn\_on(self):  
    self.setter.state(on=True)  
    return 'Lamp turned on'

def turn\_off(self):  
    self.setter.state(on=False)  
    return 'Lamp turned off'

These first two methods simplify the (already quite simple) way to to turn lights on and off, to make it more readable.

def set\_colour(self, colour):  \# colour is a tuple of xy values  
    self.setter.state(on=True)  
    self.setter.state(xy=colour)  
    return 'Lamp changed colour'

This final setter method first turns on the lamp if it isn’t already on, then sets its colour. Perhaps obviously, if the lamp is off, changing its colour alone will not make the bulb show the colour; the state has to be set to on as well.

The colours lookup table

At its core, there is a lookup table that converts temperature to colour. Since this colour is to be shown both on the Hue lamps and on the accompanying website, I decided to store this table externally. I had experience of using csv files for this purpose, but I decided to use SQLite. Both are supported natively by Python, but SQLite has some built-in methods which will be useful later on. This first utility function pulls this lookup table from the external database.

def lookup\_colour(temp):

This helper function takes in a temperature value, and will return a corresponding rgb hex value.

sql \= 'WHERE temperature \= (?)'  
what \= (temp, )  \# tuple with single item  
results \= get\_rows('colours', 'hex\_value', rows\_sql=sql, args=what)

We now use the second utility function that accesses our database. It’s quite a flexible function that handles opening and closing the connection to the SQLite database, and creating the SQLite query from filter criteria. Later on, we’ll get into the detail of how this utility is created, but for now, let’s see why this particular query was constructed.

The SQLite query we’re trying to construct is:

SELECT 'hex\_value'  
FROM 'colours'  
WHERE temperature \= temp

hex\_value is the column which contains the data we’re interested in  
colors is the table that contains all the data  
temperature is the row which we want to filter  
\= temp is the condition we want to apply to the row

Under the hood, the utility function makes use of the SQLite .execute(sql, args\_opt) method. If the SQLite query contains one or more (?), SQLite3 replaces the ? with the arguments from the second half of the method. This is a neat way of passing parameters from Python to SQLite.

There are a fair few syntax wrinkles to keep track of. The SQLite must be a string, the ? within that string must be enclosed by brackets, and the arguments must be presented as a tuple. In this case, we’re passing a single parameter, the temperature. Because it’s a tuple of a single value, we need the trailing comma to make it work \- it’s one of those Python things that tripped me up the first time I came across it.

return results\[0\]\[0\]  \# to return the hex value string only

The function returns a table as a list of tuples, where each tuple is a row. In this case, we’re getting a table of a single value \[(hex\_string, )\]. Both lists and tuples are *iterable*, so we can chain index values to access the string directly. It looks awkward, though.

Calculating the temperature to look up

def find\_temp\_threshold(temp):  
    rows \= get\_rows('colours', 'temperature')  
    all\_thresholds \= \[row\['temperature'\] for row in rows\]

First, let’s get all the temperature thresholds from our external table using our utility database access function. As we saw in the previous section, the result is a table comprising of a list of *dictionaries*. Each value can be accessed using an index or by its column label. In the last function, I used the index to access the value for brevity but in this function I use the label as it’s more readable. From the database setup (described later), we know that this is an *integer* which means we can use normal list methods.

max\_threshold \= max(all\_thresholds)  
min\_threshold \= min(all\_thresholds)

Finding the maximum and minimum threshold temperatures are now easy to find.

Calculating the colour

As mentioned earlier, we can’t just pass the CSS hex value of the colour we want to the Hue lamp and expect it to understand. To get the web site to talk to the bulb, we need to convert rgb hex values to xy coordinates.

temp\_threshold \= int(temp/5) \* 5  
if temp\_threshold \> max\_threshold:  
    temp\_threshold \= max\_threshold  
if temp\_threshold \< min\_threshold:  
    temp\_threshold \= min\_threshold  
return temp\_threshold

The algorithm does the following:  
Round the temperature down to the nearest multiple of 5  
If the temperature is higher than 40, return the higher bound temperature which is 40  
If the temperature is lower than \-10, return the lower bound temperature which is \-10

The resulting temperature table looks like this:

| Temperature range (celsius) | Corresponding colour (hex value) |
| :---- | :---- |
| 40 or greater | ff0000 |
| Between 35 and 40 | ff4000 |
| Between 30 and 35 | ff8000 |
| Between 25 and 30 | ffbf00 |
| Between 20 and 25 | ffff00 |
| Between 15 and 20 | bfff00 |
| Between 10 and 15 | 00ff80 |
| Between 5 and 10 | 00ffbf |
| Between 0 and 5 | 00ffff |
| Between \-5 and 0 | 00bfff |
| Between \-5 and \-10 | 0080ff |
| Lower than \-10 | 0040ff |

def convert\_temp\_to\_colour(temp):  
    temp\_threshold \= find\_temp\_threshold(temp)

Having used our little helper function to calculate the temperature threshold for our lookup table, we now use a couple of modules from the rgbxy library to do the maths of the conversion from rgb hex to xy coordinate. I’ve previously touched on why this maths is complicated, but let’s recap. The hex value is used in CSS. Each pair of hex digits is the value for each of red, green and blue. So the first entry in the table for temperatures of 40C or greater shows maximum red (ff) and no green or blue (00 each). Note that rgb values do not have any concept of saturation (brightness), so maximum saturation is assumed. So the colour for 40C is bright maximum red.

converter \= Converter(GamutA)

Each Hue bulb has its own colour *gamut*, the range of colours that it can reproduce (i.e. *colour space* constrained by its physical limitations). This first statement sets the applicable colour gamut to the one supported by my Hue Blooms, in this case gamut A.

colour \= converter.hex\_to\_xy(lookup\_colour(temp\_threshold))  
return colour

There’s a few nested things going on here, so let’s unpack them.  
We found the temp\_threshold using the algorithm described above  
The lookup\_colour function fetches the corresponding hex value from the lookup table in the external database table  
We use the .hex\_to\_xy method from the converter library to do the maths  
And because we set the gamut already, the method ensures that resulting colour is within the colour space of the Bloom lamp

Identifying the lamps

When we set colours and status of the Hue lamps, we need to be sure we’re doing so to the correct lamps. The Hue Bridge maintains a representation of all of the items (bulbs, lamps, switches, sensors etc) attached to it, and each item is assigned an ID. These are created when the item is *provisioned*.

hue\_lamp\_ids \= {  
    'den bloom': 10,  
    'lounge bloom': 11  
}

This dictionary is another lookup table that maps IDs to human-readable names, to make the code easier to follow. I got the numbers by taking a look at the JSON from the Bridge, using the web tool provided by Philips. You can find it on the development page.

## **Putting it together**

class hue\_lamp:

    def \_\_init\_\_(self, lamp\_id):  
        \# not accessible  
        ip \= '\<IP address of Hue bridge\>'  
        username \= '\<from Hue developer account\>'  
        \# accessible  
        self.bridge \= qhue.Bridge(ip, username)  
        self.getter \= self.bridge.lights\[lamp\_id\]()  
        self.setter \= self.bridge.lights\[lamp\_id\]  
        self.is\_on \= self.getter\['state'\]\['on'\]  
        self.colour \= self.getter\['state'\]\['xy'\]  
        self.name \= self.getter\['name'\]

    def \_\_str\_\_(self):  
        if self.is\_on:  
            status \= 'on and is set to xy:' \+ str(self.colour)  
        else:  
            status \= 'off'  
        return f'{self.name} is {status}'

    def turn\_on(self):  
        self.setter.state(on=True)  
        return 'Lamp turned on'

    def turn\_off(self):  
        self.setter.state(on=False)  
        return 'Lamp turned off'

    def set\_colour(self, colour):  \# colour is a tuple of xy values  
        self.setter.state(on=True)  
        self.setter.state(xy=colour)  
        return 'Lamp changed colour'

def lookup\_colour(temperature):  
    \# lookup table of temperatures to colours in database.sqlite3  
    sql \= 'WHERE temperature \= (?)'  
    what \= (temperature, )  \# tuple with single item  
    results \= get\_rows('colours', 'hex\_value', rows\_sql=sql, args=what)  
    return results\[0\]\[0\]  \# to return the hex value string only

def find\_temp\_threshold(temp):  
    \# find max and min thresholds from external database  
    rows \= get\_rows('colours', 'temperature')

    all\_thresholds \= \[row\['temperature'\] for row in rows\]  
    max\_threshold \= max(all\_thresholds)  
    min\_threshold \= min(all\_thresholds)

    temp\_threshold \= int(temp/5) \* 5  
    if temp\_threshold \> max\_threshold:  
        temp\_threshold \= max\_threshold  
    if temp\_threshold \< min\_threshold:  
        temp\_threshold \= min\_threshold  
    return temp\_threshold

def convert\_temp\_to\_colour(temp):  
    temp\_threshold \= find\_temp\_threshold(temp)  
    converter \= Converter(GamutA)  
    colour \= converter.hex\_to\_xy(lookup\_colour(temp\_threshold))  
    return colour

hue\_lamp\_ids \= {  
    'den bloom': 10,  
    'lounge bloom': 11  
}

---

# **Generate graphs function**

Whilst the point of this program is to look at the current temperature outside just by glancing at my Hue lamps, I also want to be able to look at the history of temperature measurements. I could’ve logged the temperature measurements into a csv file and examine them as a spreadsheet, but I wanted to present them in a more accessible way \= data visualisation.

Python has many powerful visualisation libraries, and I’ve spent some time with MatPlotLib (with its Seaborn) wrapper, and find it difficult because it’s comprehensive. Looking at PyGal, it seems much simpler to work with, so I decided to use it for my program.

## **The technologies**

PyGal  
Custom CSS

## **The code**

### **Observation sets**

def generate\_graphs(timestamp):  
    \# observation sets

First things first, let’s set the points that mark the bounds of the observation data. I’m interested in data over the last day, over the last week and over the last month.

now \= datetime.strptime(timestamp, DATETIME\_STRING)

If you remember from earlier, maths with dates and times is surprisingly difficult, but using the datetime module makes it all easier. However, both Python and SQLite have their own implementation of datetime, so we need to make sure both use the same *data dictionary*.

DATETIME\_STRING defines the format (data dictionary)  
The .strptime method *parses* a string into a datetime object according to the format

This statement creates a datetime object now from a timestamp string. This might seem puzzling as there’s a perfectly good datetime.now() function, but this is a different now object. It’s not the up-to-the-microsecond now() from the operating system, but the now of the most recent weather observation.

last\_day \= now \- timedelta(days=1)  
last\_week \= now \- timedelta(weeks=1)  
last\_month \= now \- timedelta(weeks=4)

The timedelta module fulfils the promise of simpler maths, with simple-to-understand syntax.

observation\_sets \= {  
    'last\_day': last\_day,  
    'last\_week': last\_week,  
    'last\_month': last\_month  
}

Having calculated the observation points, I put them in an easy-to-access Python dictionary.

### **Fetching the data**

rows \= get\_rows('colours')

There are two sets of data that we’re interested in: the colour values (which will map onto the temperatures) and the temperatures themselves. This first get\_rows fetches all the columns from the colours table. It’s important to note that the results are returned as a list of *tuples*. This is going to be hard to manipulate later as we want a list of hex values \- but hex values that PyGal understands (i.e. prefixed by \#), which isn’t the same as Python *type* hex (i.e. prefixed by 0x). We therefore need to *parse* the results.

hex\_list \= \[f'\#{hex}' for hex in \[row\['hex\_value'\] for row in rows\]\]

We use a combination of nested *list comprehension* and *f-strings* to do this conversion:  
\[row\['hex\_value'\] for row in rows\] : this list comprehension cycles through the rows, and creates a list of the hex values  
for hex in \[row\['hex\_value'\] … : an outer list comprehension cycles through the newly-created list  
\[f'\#{hex}' for hex … : each item of this outer list is inserted into the output string (in effect inserting the hash sign prefix for each element), to create the final list

temps\_count \= {row\['temperature'\]: 0 for row in rows}

This second command is to set up histogram *bins* for each of the temperature thresholds, using a bit of* dictionary comprehension*. Now we have the temperature data in more accessible formats, let’s move onto the observation data.

for string, then in observation\_sets.items():

Since we want a similar graph for each of three different time periods, we can save a bit of effort by iterating through the observation points (then). Thanks to the dictionary, we can access both the data and the string representation, which we’ll need in a moment.

sql \= 'WHERE timestamp BETWEEN datetime((?)) AND datetime((?))'  
when \= (then, now)  
results \= get\_rows('observations', rows\_sql=sql, args=when)

Again, our little get\_rows utility makes accessing the database a little easier. The double brackets look a bit odd. The variable replaced by the underlying SQLite .execute method is represented by (?). However, they are themselves parameters into SQLite’s own datetime method, which is why they need to be enclosed in another set of brackets.

The underlying SQLite query uses its own datetime method to convert Python datetime objects into SQL datetime strings. SQL doesn’t ask for the data dictionary explicitly; it’s assumed that the string corresponds to one of the accepted [formats](https://www.google.com/url?q=https://www.sqlite.org/lang_datefunc.html&sa=D&ust=1603647715795000&usg=AOvVaw3h04gmXby9fFuCPB5OFNFH). 

Once we have the bounds correctly interpreted into the query, we can select only the data that we’re interested in. This is the reason I chose SQLite over csv. If we’d used a csv file to store all the data, I’d have to read all the data into a *dataframe* into memory, then search it for the data using a library such as Pandas. Not a big overhead, but given SQLite is built into Python, it's an opportunity to import one less library.

### **Generating the bar graphs**

times \= \[row\['timestamp'\] for row in rows\]  
temps \= \[row\['temperature'\] for row in rows\]

The database gives us a list of dictionaries; each dictionary contains a timestamp and a measurement. We need to convert these multiple lists into two lists, one containing all the timestamps, and another containing all the measurements. This is akin to transposing rows and columns of a table. This is simply done using some* list comprehension*.

bar\_chart \= pygal.Bar(x\_label\_rotation=20,  
                      x\_labels\_major\_count=6,  
                      show\_minor\_x\_labels=False,  
                      show\_legend=False)

Now we get into using PyGal to generate the graph. This first statement instantiates the chart object. It’s at this point that we declare it’s a bar graph, and also tell it to rotate the x labels (so that they’ll fit), limit x-axis labels to 6 in total (otherwise they’ll look cluttered), and remove the legend (because there’s only one series being shown).

bar\_chart.add('Temperature', \[  
    {'value': temp,  
    'color': '\#' \+ lookup\_colour(find\_temp\_threshold(temp))}  
    for temp in temps\]  
)

Now we add the data series, and its title. To make the colours meaningful, the colour of the bar matches the Bloom colour. This means adding each value to be plotted individually, as a dictionary which describes the value and the colour. The colour is calculated using our previously defined functions, remembering to prefix with a hash symbol. We loop all the temperature measurements using list comprehension.

bar\_chart.x\_labels \= times

The final piece of formatting is to add labels for the x axis, using a nice simple syntax.

filename \= string \+ '\_bar.svg'  
bar\_chart.render\_to\_file(FILEPATH \+ filename)

We want the filename to reflect the data set, so this little snippet takes the string representation of the data from the dictionary key, creates a full file path prepending the FILEPATH \= './app/static/' global constant, and saves the generated graph there.

### **Generating the pie charts**

We want to generate one pie chart for every bar chart (just in case we need them). The first thing we need to do is to count the number of occurrences of temperature in the bins that were previously generated.

for temp in temps:  
    temp\_threshold \= find\_temp\_threshold(temp)  
    temps\_count\[temp\_threshold\] \+= 1

The algorithm is simplified as we’re done most of the prep work beforehand. For each temperature reading in this observation set, we first find its corresponding temperature threshold, then increment the count in its bin.

custom\_style \= Style(colors=(tuple(hex\_list)))

We can reuse the hex values from the colours table to create a custom colour key for the pie chart. These values are in the form of a list of strings, each prefixed with a hash, which we did earlier. To be properly formatted for PyGal, we now need to convert this list into a tuple, then pass it to the Style function as one of the optional *keyword arguments*.

pie\_chart \= pygal.Pie(inner\_radius=0.6,  
                      style=custom\_style)

Instantiating the pie chart is straightforward; the only configuration parameters are the size of its donut hole and the colours of the sections.

for temp, count in temps\_count.items():  
    pie\_chart.add(str(temp), count)

Each pie segment needs to be added individually, so we have a little loop.

filename \= string \+ '\_pie.svg'  
pie\_chart.render\_to\_file(FILEPATH \+ filename)

Finally, let’s save the chart to be used by the web app later.

### **Generating the box plot**

We’ll use a box plot for displaying the monthly data from the last year. The first thing we need to do is to initialise a couple of data dictionaries we’ll find useful later:

    month\_name \= {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}  
    month\_temps \= {}  
    month\_colour \= {}

Now let’s get the data for our box plot. 

     for i in range(13):

The box plot answers two questions: what has the temperature been like over the last year, and what was it like this time last year? It’s to answer the latter question that we want to go back 13 months instead of 12\.

        start \= datetime.today() \- relativedelta(months=(12 \- i), day=1, hour=0, minute=0, second=0, microsecond=0)  
        end \= start \+ relativedelta(months=1)

We want the x-axis of the plot to start on this month last year, then have a column for every month up to and including the current month. We use the relativedelta function to work the start and end of each month along the x-axis to create our monthly buckets.

        rows \= get\_rows('observations', rows\_sql=sql, args=when)

Our familiar get\_rows helper function is the wrapper for the SQL statement that extracts the temperature information from our database. We need to pass it the database, SQL we wish to execute and any modifiers to the SQL.

        when \= (start, end)

The modifier to our SQL will be the calculated start and end date of our month bucket.

        sql \= 'WHERE timestamp BETWEEN datetime((?)) AND datetime((?))'

This simple SQL statement extracts all of our data. Each (?) evaluates to a modifier in the order listed in the args tuple.

We can now populate our dictionary of monthly temperatures month\_temps with the start date of the month paired with a list of all temperatures recorded.

        month\_temps\[start\] \= \[\]  
        month\_temps\[start\].extend(row\['temperature'\] for row in rows)

To make our box plot more meaningful, we want the colour of the box in the plot to represent the mean of that month’s temperature readings, so let’s find it.

        if month\_temps\[start\]: 

Calculating the mean will fail if there’s not data to run the calculation on. We don’t want the box plot to fail if there is less than a full 13 months of data. In fact, we want this function to work on first run so when there’s only a single data point. By using this test for *truthiness* we will only try to find the mean if there’s any data in that month.

            month\_colour\[start\] \= '\#' \+ lookup\_colour( find\_temp\_threshold( mean( month\_temps\[start\])))

We use our helper functions to calculate the colour for the box in the right format.

I’ve created a custom style for the box plot because I think it works better than defaults. The last line in this style uses the colours we calculated just now.

    custom\_style \= Style(  
        background='transparent',  
        plot\_background='transparent',  
        opacity='.6',  
        opacity\_hover='.9',  
        transition='400ms ease-in',  
        colors=(\[colour for month, colour in list(month\_colour.items())\]))

PyGal makes instantiating the box plot relatively straightforward. 

    box\_plot \= pygal.Box(legend\_at\_bottom=True,  
                         legend\_at\_bottom\_columns=13,  
                         print\_labels=True,  
                         style=custom\_style)

Now we extract the data from the dictionary and pass to the box\_plot function.

    for month\_start, temps in month\_temps.items():  
        box\_plot.add(month\_name\[month\_start.month\], temps)

Finally we can render the plot to the .svg file.

    filename \= 'last\_year\_box.svg'  
    box\_plot.render\_to\_file(FILEPATH \+ filename)

### **Wrapping up**

Now we’ve done it once, we can repeat it for each of the remaining observation sets.

return 'Created graphs'

The database utility has taken care of closing the connection to the database, so all that’s left is to return an acknowledgement string for debugging purposes. The graphs themselves are already stored (or overwritten) in the predefined folder within the loop.

## **Putting it together**

def generate\_graphs(timestamp):  
    \# observation sets  
    now \= datetime.strptime(timestamp, DATETIME\_STRING)  
    last\_day \= now \- timedelta(days=1)  
    last\_week \= now \- timedelta(weeks=1)  
    last\_month \= now \- timedelta(weeks=4)  
    observation\_sets \= {  
        'last\_day': last\_day,  
        'last\_week': last\_week,  
        'last\_month': last\_month  
    }

    \# get datapoints from database  
    rows \= get\_rows('colours')  
    hex\_list \= \[f'\#{hex}' for hex in \[row\['hex\_value'\] for row in rows\]\]  
    temps\_count \= {row\['temperature'\]: 0 for row in rows}

    \# 3x graphs for every reading in last day, week, month  
    for string, then in observation\_sets.items():  
        \# fetch data  
        sql \= 'WHERE timestamp BETWEEN datetime((?)) AND datetime((?))'  
        when \= (then, now)  
        results \= get\_rows('observations', rows\_sql=sql, args=when)

        \# generate bar graph  
        times \= \[row\['timestamp'\] for row in rows\]  
        temps \= \[row\['temperature'\] for row in rows\]

        bar\_chart \= pygal.Bar(x\_label\_rotation=20,  
                              x\_labels\_major\_count=6,  
                              show\_minor\_x\_labels=False,  
                              show\_legend=False)  
        bar\_chart.add('Temperature', \[  
            {'value': temp,  
            'color': '\#' \+ lookup\_colour(find\_temp\_threshold(temp))}  
            for temp in temps\]  
        )  
        bar\_chart.x\_labels \= times  
        filename \= string \+ '\_bar.svg'  
        bar\_chart.render\_to\_file(FILEPATH \+ filename)

        \# generate pie chart  
        for temp in temps:  
            temp\_threshold \= find\_temp\_threshold(temp)  
            temps\_count\[temp\_threshold\] \+= 1  
        custom\_style \= Style(colors=(tuple(hex\_list)))  
        pie\_chart \= pygal.Pie(inner\_radius=0.6,  
                              style=custom\_style)  
        for temp, count in temps\_count.items():  
            pie\_chart.add(str(temp), count)  
        filename \= string \+ '\_pie.svg'  
        pie\_chart.render\_to\_file(FILEPATH \+ filename)

    return 'Created graphs'

---

# **Orchestrating the code**

Right at the top, I defined the structure of the code that I wanted to write, as:

1. Check the current weather  
2. Set the blooms to the current temperature  
3. Log the weather reading  
4. Generate new graphs

Now that we’ve gone through the detail of the classes and functions, following the execution code becomes quite straightforward. I’ll leave it to you, dear reader, to put it together. See you in the next section, when we present this on a web page\!

I’ve wrapped the orchestration in another function, called weather. This gives me the flexibility to call it as a module from my Flask app later, and also to run it directly from the Terminal as python pybloom.py.

## **Putting it together**

def weather():  
    \# Check current weather  
    observation \= weather\_observation()  
    observation.fetch(HOME\_LOCATION)  
    \# observation.set(datetime.now().strftime(DATETIME\_STRING), 23, 'dummy observation')  
    print(observation)

    \# Set lounge bloom to current temperature  
    lounge\_bloom \= hue\_lamp(hue\_lamp\_ids\['lounge bloom'\])  
     lounge\_bloom.set\_colour(convert\_temp\_to\_colour(observation.temperature))  
    \# Set den bloom to current temperature  
    den\_bloom \= hue\_lamp(hue\_lamp\_ids\['den bloom'\])  
    den\_bloom.set\_colour(convert\_temp\_to\_colour(observation.temperature))

    \# Log weather observation  
    observation.log()

    \# generate new graphs  
    generate\_graphs(observation.timestamp)

    return 'Fetched weather'

weather()

## **Keeping secrets**

Way back when I showed you how I organised the code, I mentioned that I kept sensitive secrets out of the main code. I had global constants for these secrets, which were imported from a separate credentials.py file, as structured below. I decided on a simple dictionary with self-evident but unique variable names. Note that both key and values are *strings*.

credentials.py  
credentials \= {  
    'hue\_ip': \<IP address of your Hue Bridge\>,  
    'hue\_username': \<given by the Hue Bridge on first sync\>,  
    'owm\_key': \<generated by service on signing up\>,  
    'home\_location': \<where you live, in the format city, country code\>  
}

---

# **Database utilities**

The database is set up automatically on first connection, but the tables within need to be instantiated.

Global libraries and constants

import sqlite3

DEFAULT\_DB \= 'database.sqlite3'

All will become clear later\!

con \= db\_connect()  \# connect to the database  
cur \= con.cursor()  \# instantiate a cursor obj

Let’s connect to the database and start creating our two tables.

**Table of Bloom colours**

colours\_sql \= """  
CREATE TABLE IF NOT EXISTS colours

We create here the colours table, using the modifier IF NOT EXISTS to make sure we don’t delete a load of data if we accidentally run this script after the system is live.

id integer PRIMARY KEY,  
temperature integer UNIQUE,  
hex\_value text NOT NULL

The three columns created are:  
The primary key, id, constrained to be an integer  
The temperature, constrained to be unique (as we should never have one temperature associated with more than one hex value)  
The corresponding hex\_value, which is constrained to be text since SQLite doesn’t have a hex data type, and can’t not exist if the temperature exists

The constraints will prevent the code from breaking as I’ve not written much error case handling.

cur.execute(colours\_sql)

We need to pre-populate this colours table.

temp\_colours \= {    
    40: 'ff0000',  \# colour value if temperature is \>= than key  
    35: 'ff4000',  \# note: value is string, not hex  
    30: 'ff8000',  
    25: 'ffbf00',  
    20: 'ffff00',  
    15: 'bfff00',  
    10: '00ff80',  
     5: '00ffbf',  
     0: '00ffff',  
    \-5: '00bfff',  
   -10: '0080ff',  
   -15: '0040ff'  
}

These values are taken from [https://www.w3schools.com/colors/colors\_picker.asp](https://www.google.com/url?q=https://www.w3schools.com/colors/colors_picker.asp&sa=D&ust=1603647715815000&usg=AOvVaw1vM8s0u0HghBmzr5Z2-yQZ). The hex values are actually strings, even though Python can very happily handle hex natively. This is because the value is intended to be used by the Python RGBxy library, the Python PyGal library, the database and the web page CSS; and neither RGBxy nor SQL can understand hex. String is therefore the common format across all of them.

colours\_sql \= '''INSERT OR IGNORE INTO colours (temperature, hex\_value)  
                 VALUES (?, ?)'''

By using the OR IGNORE modifier, we can be sure that we’re not overwriting any value if the table already exists and the script has been run in error. (I haven’t written all [CRUD](https://www.google.com/url?q=https://www.codecademy.com/articles/what-is-crud&sa=D&ust=1603647715816000&usg=AOvVaw3JoZrf65QyDbP_qYZcM32k) operations as this script is for *create* only; I’ll be writing the *update* and *delete* operations in the main code.)

for temperature, hex\_value in temp\_colours.items():  
    cur.execute(colours\_sql, (temperature, hex\_value))

The SQLite query above has spaces for two parameters, which we’ll pass as we iterate through the temp\_colours dictionary. Every key, value pair gets written as a new row.

**Table of observations**

observations\_sql \= """  
CREATE TABLE IF NOT EXISTS observations (  
    id integer PRIMARY KEY,  
    timestamp text UNIQUE,  
    temperature real NOT NULL,  
    detailed\_status text NOT NULL)"""  
cur.execute(observations\_sql)

The rows for the table of observations are:  
The primary key, id, constrained to be an integer  
The timestamp, constrained to be unique (as we should never be able to make more than one observation simultaneously)  
The corresponding observation values: temperature (constrained to be real since we want to keep the decimals) and detailed\_status (constrained to be text)

con.commit()  
con.close()  \# close connection

Finally, we commit the changes and close the connection.

Utility function to connect to the database

def db\_connect(db\_file=DEFAULT\_DB):  
    \# create connection to SQLite database  
    connection \= sqlite3.connect(db\_file)  
    return connection

Because we only have one place where we declare the database filename, it means all the code remains coherent.

Utility function to get rows from a table

def get\_rows(table, columns='\*', \*\*kwargs):

To make this utility flexible, it’s meant to simplify 3 use cases:  
Getting all the rows from the table, in which case you don’t have to call this function with any further parameters beyond the table name  
Getting only the rows that fulfil a condition described in an optional *dictionary* of keyword arguments (\*\*kwargs) (defaults to no filters)  
Getting only the named columns (defaults to all columns)

if (table \== 'colours') or (table \== 'observations'):

Some rudimentary logic to prevent calling for a table that doesn’t actually exist, as the code doesn’t handle SQLite errors.

con \= db\_connect()  \# connect to the database

Here we reuse the first utility function to connect to the database. We don’t have to remember which database file and where because we’re using the utility.

con.row\_factory \= sqlite3.Row

The next statement refactors the output from the queries into a list of dictionaries, which makes it a little easier to access the content. In this list, each item is a row, and each item consists of a dictionary of column name and value pairs. Each row is accessed directly by its index, but each column can be accessed by index or label. So to access the hex\_value for the first row we use result\[0\]\[2\] or result\[0\]\['hex\_value'\].

cur \= con.cursor()  \# instantiate a cursor obj

Next we instantiate a *cursor* object, which is SQLite’s accessor object.

rows\_sql \= ''  
args \= ()

If there aren’t any keywords passed, then we just want all the rows from the named table, and we don’t have to modify the SQLite query further.

for key, value in kwargs.items():  
    if key \== 'rows\_sql':  
        rows\_sql \= ' ' \+ value  
    elif key \== 'args':  
        args \= value

If we do have a rows filter, then we need to insert it into the SQLite query. We expect a simple dictionary of {row\_sql: sql, args: (arg1\_value, …)}. This little loop unpacks them. Note: I’m relying on the SQL string to be well-formed; the only parsing I’m doing is to add a space so that the final SQL query will be well-formed too.

if rows\_sql.count('?') \!= len(args):  
    results \= 'Unexpected number of arguments in row modifier'

Then a simple check to see if we have the same number of arguments as places to put them.

cur.execute('SELECT ' \+ columns \+ ' FROM ' \+ table \+ rows\_sql, args)

Now we have everything we need to build our .execute command. The first argument is a simple string concatenation to build the full SQL query. The second argument is the tuple of values to be inserted in place of any (?).

results \= cur.fetchall()  
con.close()  \# close connection  
return results

Once we get the results (as a list of dictionaries), we close the connection to the database and return the results.

## **Putting it together**

import sqlite3

DEFAULT\_DB \= 'database.sqlite3'

def db\_connect(db\_file=DEFAULT\_DB):  
    \# create connection to SQLite database  
    connection \= sqlite3.connect(db\_file)  
    return connection

\# utility function, handles opening and closing the database connection  
def get\_rows(table, columns='\*', \*\*kwargs):  
    \# columns\_names should be a string enclosing a tuple of selected columns  
    if (table \== 'colours') or (table \== 'observations'):  
        con \= db\_connect()  \# connect to the database  
        cur \= con.cursor()  \# instantiate a cursor obj  
        con.row\_factory \= sqlite3.Row

        rows\_sql \= ''  
        args \= ()  
        for key, value in kwargs.items():  
            if key \== 'rows\_sql':  
                rows\_sql \= ' ' \+ value  
            elif key \== 'args':  
                args \= value  
        if rows\_sql.count('?') \!= len(args):  
            results \= 'Unexpected number of arguments in row modifier'

        cur.execute('SELECT ' \+ columns \+ ' FROM ' \+ table \+ rows\_sql, args)  
        results \= cur.fetchall()  
    else:  
        results \= 'invalid table name'  
    con.close()  \# close connection  
    return results

con \= db\_connect()  \# connect to the database  
cur \= con.cursor()  \# instantiate a cursor obj

\# create table of Hue Bloom colours if one doesn't already exist  
colours\_sql \= """  
CREATE TABLE IF NOT EXISTS colours (  
    id integer PRIMARY KEY,  
    temperature integer UNIQUE,  
    hex\_value text NOT NULL)"""  
cur.execute(colours\_sql)

\# create table of weather observations if one doesn't already exist  
observations\_sql \= """  
CREATE TABLE IF NOT EXISTS observations (  
    id integer PRIMARY KEY,  
    timestamp text UNIQUE,  
    temperature real NOT NULL,  
    detailed\_status text NOT NULL)"""  
cur.execute(observations\_sql)

\# populate Hue colours db with default values if doesn't already exist  
temp\_colours \= {  \# from https://www.w3schools.com/colors/colors\_picker.asp  
    40: 'ff0000',  \# colour value if temperature is \>= than key  
    35: 'ff4000',  \# note: value is string, not hex  
    30: 'ff8000',  
    25: 'ffbf00',  
    20: 'ffff00',  
    15: 'bfff00',  
    10: '00ff40',  
     5: '00ffbf',  
     0: '00ffff',  
    \-5: '00bfff',  
   -10: '0080ff'  
}

sql \= '''INSERT OR IGNORE INTO colours (temperature, hex\_value)  
   VALUES (?, ?)'''  
for temperature, hex\_value in temp\_colours.items():  
    cur.execute(sql, (temperature, hex\_value))

con.commit()  
con.close()  \# close connection

---

# **The web server**

Part of the rationale for this project is to leverage my burgeoning Python knowledge in as many places as possible. So it seemed sensible to me to try out one of the Python web frameworks for my website. I’ve tried Django before, and it seemed quite complicated for my needs, so I went with the simpler Flask to see if it could do what I wanted. And indeed it could.

Setting up the web server with Flask consists of creating some simple initiator scripts. The file structure from earlier lists all the files we need to make. We’ll focus on the scripts here, and get to the templates and static resources in the next section.

./Project/pybloom  
│  
├── app.py  
├── app/  
│   ├── \_\_init\_\_.py  
│   ├── content.py  
│   ├── routes.py  
│   ├── templates/  
│   │   ├── base.html  
│   │   ├── index.html  
│   │   └── colours.html  
│   └── static/  
│       ├── favicon.ico  
│       ├── brand.svg  
│       ├── logo.svg  
│       ├── bar\_graph.svg  
│       └── pie\_chart.svg

## **The technologies**

Flask  
Advanced Python Scheduler  
HTTP

## **The code**

The app entity

Flask looks for an app.py script in the root of the project directory to tell it where to get the rest of the files. (You can use a different filename, but then you need to declare that in a different .flaskenv variable \- why bother.)

from app import app

That’s all you need, at least in our simple project.

A rudimentary CMS

We’ve generated our weather observation data and visualisations in the Python script, but we need a way of declaring them to the web pages. Rather than sprinkling references to filenames and file paths throughout the HTML, I decided to collect them in a content management script.

from db\_utils import get\_rows

We’re going to need our helpful database utility, so let’s import it first.

def graphs():  
    all\_graphs \= {  
        'lastday': 'last\_day\_bar.svg',  
        'lastweek': 'last\_week\_pie.svg',  
        'lastmonth': 'last\_month\_bar.svg'  
    }  
    return all\_graphs

This function collects all the graphs in one dictionary.

def colours\_table():  
    rows \= get\_rows('colours')  
    return rows

This second function fetches our temperature-colour lookup table.

We’re using functions to define the content instead of variables because I like to keep variables associated with a single *namespace* - to me it’s just cleaner and less prone to error.

Setting up the page routes in python  
   
Flask takes care of responding to all the HTTP requests with the correct web pages (web serving) and calls them *routes*.

from flask import render\_template  
from app import app  
from app import content

First let’s import all the modules that we’re going to need in this routing script.

CONTENT \= content.graphs()  
COLOURS\_TABLE \= content.colours\_table()

Second, we have a couple of global variables that tell our pages where to get their data, defined in our CMS.

@app.route('/')  
@app.route('/index')  
def index():  
    return render\_template('index.html', title='Home', content=CONTENT)

Flask uses* function decorators* to associate HTTP requests with HTML files. These statements are saying that if the web server receives a request for \<IP address of server:5000\>/ or \<IP address of server:5000\>/index it should render the index.html file.

Additionally, the render\_template() method passes a couple of parameters into the file in order to complete its rendering, the title of the page and the graph content.

@app.route('/colours')  
def colours():  
    return render\_template('colours.html', title='Colours', rows=COLOURS\_TABLE)

\<IP address of server:5000\>/colours takes us to the colours.html page.  Again  the render\_template() method passes a couple of parameters as defined in the CMS.

@app.after\_request  
def after\_request\_func(response):  
    response.headers\['Cache-Control'\] \= 'no-store'  
    return response

While testing, I noticed that the graphs were old, and that refreshing the page just re-showed the old graphs. I figured that the browser was serving a cached page, but as the data refreshes every 10 minutes, the page was old. Furthermore, clicking on the refresh button in modern browsers just re-fetches the same page from the browser cache. In order to force the browser to re-send its HTTP request, I need to make sure the HTTP response indicates that the browser should not store the page.

Let’s unpick this final decorator:  
@app.after\_request : tells Flask that this function is to be called after every web page request is responded to  
after\_request\_func(response) : works on Flask’s internal response object, which normally you wouldn’t interact with directly  
response.headers\['Cache-Control'\] \= 'no-store' : this adds a new header to the HTTP response which tells the browser not to cache the page

Initialising and running the code

We now have two processes that need to run simultaneously: the web server, and fetching the observations. There’s a library that makes the scheduling straightforward:

from apscheduler.schedulers.background import BackgroundScheduler

The Advanced Python Scheduler has a background scheduling function that is perfect for my needs.

schedule \= BackgroundScheduler(daemon=True)  
schedule.add\_job(lambda: weather(), 'interval', minutes=10)  
schedule.start()

We instantiate a schedule object as a *daemon*, which means it closes once it finishes (contrast with a *thread* that just keeps going). The job itself is a* lambda function* that calls the weather function every 10 minutes. (We should remember to import this function with from pybloom import weather at the top of the file.)

from flask import Flask  
app \= Flask(\_\_name\_\_)  
from app import routes

The remaining initialisation command tells Flask what the app is, and where it can find the routing.

In dev, I’m using the same machine to run the server as to browse it, so the correct command is flask run. By default, this runs a server in the localhost, so isn’t accessible outside of the dev machine. However, in prod, I want the RPi to serve the site to other browsers to view it, so the correct command is:

flask run \--host=0.0.0.0

To access the site, point the browser to http://\<IP address of RPi\>:5000/ (specify the port, otherwise the RPi will reject the connection to the browser).

## **Putting it together**

app.py  
from app import app

\_init\_py  
from flask import Flask  
app \= Flask(\_\_name\_\_)  
from app import routes  
from apscheduler.schedulers.background import BackgroundScheduler  
from pybloom import weather

schedule \= BackgroundScheduler(daemon=True)  
schedule.add\_job(lambda: weather(), 'interval', minutes=10)  
schedule.start()

routes.py  
from flask import render\_template  
from app import app  
from app import content

CONTENT \= content.graphs()  
COLOURS\_TABLE \= content.colours\_table()

@app.route('/')  
@app.route('/index')  
def index():  
    return render\_template('index.html', title='Home', content=CONTENT)  
@app.route('/colours')  
def colours():  
    return render\_template('colours.html', title='Colours', rows=COLOURS\_TABLE)  
@app.after\_request  
def after\_request\_func(response):  
    response.headers\['Cache-Control'\] \= 'no-store'  
    return response

content.py  
from db\_utils import get\_rows

def graphs():  
    all\_graphs \= {  
        'lastday': 'last\_day\_bar.svg',  
        'lastweek': 'last\_week\_pie.svg',  
        'lastmonth': 'last\_month\_bar.svg'  
    }  
    return all\_graphs

def colours\_table():  
    rows \= get\_rows('colours')  
    return rows

---

# **The web pages**

In the previous section, we’ve seen how to build the structure of the web app in Flask. After creating the app package, we then need to work on the HTML of the page. Finally, we’ll need to add the CSS that styles the page. To do this, the web page is written in HTML5 and CSS3, but with two scripting languages to simplify: Jinja2 for the HTML rendered by Flask, and Bootstrap CSS.

I haven’t discussed CSS yet, so let’s take a detour there. I’m a big fan of frameworks and not bothering to recreate (learn again) from first principles. The most comprehensive framework that I’ve come across for CSS is [Bootstrap](https://www.google.com/url?q=https://getbootstrap.com/docs/4.5/getting-started/introduction/&sa=D&ust=1603647715852000&usg=AOvVaw28T2Gp3XbYOaWaR4A0JCBR) from Twitter. It takes care of making the page responsive, mobile-friendly with predefined styles, without the need to create the CSS from scratch. It’s a scripting language, so there is a need to learn its vocabulary which is invoked in the HTML attributes.

The structure of the HTML makes use of inheritance. There’s a base.html that declares all the common elements, such as declaring how the Bootstrap components are downloaded from the CDN, and also the navigation elements that are common for all pages. Each subsequent page extends this base.html page, to add the actual content and other custom CSS.

## **Technologies**

HTML5, CSS3  
Jinja2  
Bootstrap CSS

## **The code**

base.html \- head

\<\!DOCTYPE html\>  
\<html lang="en"\>  
  \<head\>  
    \<meta charset="UTF-8"\>

So far so familiar. All HTML starts with these tags.

\<meta name="viewport" content="width=device-width, initial-scale=1.0"\>

This is the first tag required by Bootstrap.

“Bootstrap is developed mobile first, a strategy in which we optimize code for mobile devices first and then scale up components as necessary using CSS media queries. To ensure proper rendering and touch zooming for all devices, add the responsive viewport meta tag to your \<head\>.”

{% if title %}  
\<title\>{{ title }} \- PyBloom\</title\>  
{% else %}  
\<title\>Welcome to PyBloom\</title\>  
{% endif %}

Next we have a bit of Jinja2 logic to define the title. All this is saying is: if the variable title is passed into the HTML according to the routes.py then the title is put into the metadata. If not, a default title is used. To be honest, I probably won’t invoke this logic, but it’s there if needed in the future.

\<\!-- Bootstrap v5 CSS CDN \--\>  
\<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/5.0.0-alpha2/css/bootstrap.min.css" integrity="sha384-DhY6onE6f3zzKbjUPRc2hOzGAdEf4/Dz+WJwBvEYL/lkkIsI3ihufq9hk9K4lVoK" crossorigin="anonymous"\>

\<\!-- Bootstrap JavaScript Bundle with Popper.js \--\>  
\<script src="https://stackpath.bootstrapcdn.com/bootstrap/5.0.0-alpha2/js/bootstrap.bundle.min.js" integrity="sha384-BOsAfwzjNJHrJ8cZidOg56tcQWfp6y72vEJ8xQ9w6Quywb24iOsW913URv1IS4GD" crossorigin="anonymous"\>\</script\>

These tags are needed in order to download Bootstrap from the CDN, avoiding the need to download potentially out of date components. These first \<link\> and \<script\> tags specify the version of Bootstrap CSS and Bootstrap JavaScript to be downloaded from the CDN. I’m using Bootstrap v5 which is in alpha at time of writing. I’ll clearly need to update this to the release version at some point (and hope that nothing breaks in the meantime).

I thought of defining these URLs in my rudimentary CMS, but decided against it because 1\) sometimes Bootstrap classes only work with certain versions (e.g. the naming is not backwards compatible across major versions) so it’s better to reference a fixed snapshot; and 2\) the complete statement is quite complex, so I can eliminate transposing errors by copying directly from the Bootstrap documentation.

{% block app\_css %}{% endblock %}

This little bit of Jinja2 specifies a block where the custom CSS needed later will go.

\<link rel="shortcut icon" href="{{ url\_for('static', filename='favicon.ico') }}"\>  
\</head\>

Every website also displays a little icon in the top left of the browser tab. This last link is a combination of HTML and the very useful Jinja2 function url\_for() to tell the browser where to locate this icon file. This function concatenates the absolute file path for the static folder with the filename, and inserts into the tag href attribute. We’ll use it a lot in the HTML, as it avoids hard coding file paths very nicely.

And that’s it for the head, so we close with the \</head\> tag.

base.html \- body

The body HTML is where the Bootstrap scripting goes. The common element across the top of all of my pages will be the navigation bar. Let’s get into it\!

\<body\>  
  \<div class="container-fluid"\>

The *container* model is how Bootstrap (and all CSS) describes the elements within a web page. Think of a container as a [box](https://www.google.com/url?q=https://www.w3schools.com/css/css_boxmodel.asp&sa=D&ust=1603647715858000&usg=AOvVaw0fH-6WC1hxGwlewWbqyp7_) that has a margin, border, padding, and finally the content in the centre. By declaring each container as fluid, we let the browser resize them to fill up the full screen (the *viewport*). Resizing, re-flowing and maybe re-factoring functionality in response to the size of the device is the essence of responsive design.

\<nav class="navbar navbar-expand-md navbar-light bg-light"\>

The container for the navigation bar is the *navbar*. In the class attribute we give it a few parameters, and Bootstrap magically does the rest of the formatting.  
navbar-expand-md: the navbar will expand when the device is mid-sized; this is the *breakpoint*  
Navbar-light: light colour scheme for the navbar elements  
Bg-light: light colour scheme for the navbar background

\<span class="navbar-brand"\>

Bootstrap provides a built-in element type of brand, with a default format that distinguishes it from other navbar elements. By making the brand element in a \<span\> tag, it just sits there and looks pretty. On many websites, you can click on the brand icon and go to an “about” page. To do this, just put the brand element in an *anchor* \<a\> tag with associated href attribute. I’ll use this for the other navbar elements.

  \<img src="{{ url\_for('static', filename='brand.svg') }}" height="30" class="d-inline-block align-top" alt="PyBloom"\>  
  PyBloom  
\</span\>

We use the Jinja2 url\_for() function in order to generate the absolute file path for the brand icon. The Bootstrap attributes of d-inline-block align-top puts the block at the top left. I like this statement as an example of how using these two scripting languages makes generating the HTML and CSS so much more readable.

\<button type="button" class="navbar-toggler" data-toggle="collapse" data-target="navbarNavItems" aria-expanded="false"\>

This toggle button is the key element that enables my responsive design. In smaller screens, smaller than the mid-size breakpoint defined in the parent class above, the screen will not display any of the navbar elements except for the brand and this button. To display the navbar links, you just have to press this button, and the navbar elements are revealed in a column on the left. All the complexity of this design and the interactivity is summarised in these few attributes.  
class="navbar-toggler": declares to Bootstrap that this button is the one that toggles the navbar in smaller screens  
data-toggle="collapse": clicking the button collapses the content  
data-target="navbarNavItems": links to the items in the navbar that will be collapsed/ expanded; the toggled menu bar will look for an element that has ID=navbarNavItems   
Aria-expanded="false": sets the current behaviour (i.e. when page is loaded)

  \<span class="navbar-toggler-icon"\>\</span\>  
\</button\>

Because we need pretty icons everywhere, here’s an icon for the toggle button.

\<div class="collapse navbar-collapse" id="navbarNavItems"\>

This class contains all the remaining navbar elements, and is the subject of the toggle button. When clicking on these elements, you’ll be taken to the web page. Bootstrap handles this subset of elements as a navbar in its own right, inheriting properties from the parent navbar.  
collapse: sets the behaviour to collapse this navbar on selection  
navbar-collapse: sets this navbar as the parent breakpoint for the collapse/ expand behaviour  
id="navbarNavItems": connects this sub-navbar to the toggle button

\<div class="navbar-nav mr-auto"\>

This division groups all the sub-navbar elements together.  
navbar-nav: these elements are of the type *nav*, and will be styled as such  
mr-auto: the nav items after this group of elements will be pushed to the right side of the viewport, with the padding automatically calculated

\<li class="nav-item"\>  
  \<a class="nav-link" href="{{ url\_for('index') }}"\>Weather Station\</a\>  
\</li\>

Here is our first nav item, the actual element that takes us to the subsequent pages. The container for the element, and the content of element (the link) are styled differently, which is why we have two nested items. The container is simply declared to Bootstrap as a nav-item. The link itself is styled in a combination of Jinja2 and Bootstrap.  
Bootstrap parameters nav-link: declares to Bootstrap as a link object, which won’t look active until the mouse hovers over it  
Jinja2 script {{ url\_for('index') }}: builds the absolute file path to the target page, in this case the index.html page

\<li class="nav-item"\>  
  \<a class="nav-link" href="{{ url\_for('colours') }}"\>Colour Key\</a\>  
\</li\>

The second nav item is similar to the first, except we have Jinja2 reference the colours.html file.

\<div class="navbar-nav navbar-right"\>  
  \<li class="nav-item"\>  
    \<a class="nav-link" href="https://blog.mindrocketnow.com"\>Home\</a\>  
  \</li\>  
\</div\>

Finally, we have a home link on the right side of the navbar. The construction is very similar to the previous nav items, except it’s a shameless plug for my blog.

\<\!-- This is where the page content will go \--\>  
{% block app\_content %}{% endblock %}

\<\!-- Space for custom JS \--\>  
{% block app\_js %}{% endblock %}

We end the base.html by provisioning a couple of slots to be extended by page-specific HTML and CSS content.

index.html

The hard work of styling each page is done in the base.html document. For each of the subsequent pages, we simply have to extend it with a small amount of additional HTML.

{% extends "base.html" %}

This Jinja2 sippet does exactly that, without needing to know the file path.

{% block app\_content %}

This header tells Jinja2 where to insert the subsequent code to make up the full page code.

\<h1\>Latest data\</h1\>  
\<div\>  
  \<h2\>Last 24 hours\</h2\>  
  \<img src="{{ url\_for('static', filename=content\['lastday'\]) }}" class="img-fluid" alt="Temperature over last day"\>

\<h2\>Last week\</h2\>  
\<img src="{{ url\_for('static', filename=content\['lastweek'\]) }}" class="img-fluid" alt="Temperature over last week"\>

As before, we use a combination of Jinja2 and Bootstrap to define and style the image elements. The Jinja2 snippet references the file that was declared in the rudimentary CMS (content.py) so that the image source points to the right graph. Bootstrap styles this as a fluid image.

  \</div\>  
{% endblock %}

After closing the division, we also need to close the block.

## **Putting it together**

base.html

\<\!DOCTYPE html\>  
\<html lang="en"\>  
  \<head\>  
    \<meta charset="UTF-8"\>  
    \<meta name="viewport" content="width=device-width, initial-scale=1.0"\>

    \<\!-- A little Jinja2 logic to choose page title \--\>  
    {% if title %}  
    \<title\>{{ title }} \- PyBloom\</title\>  
    {% else %}  
    \<title\>Welcome to PyBloom\</title\>  
    {% endif %}

    \<\!-- Bootstrap v5 CSS CDN \--\>  
    \<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/5.0.0-alpha2/css/bootstrap.min.css" integrity="sha384-DhY6onE6f3zzKbjUPRc2hOzGAdEf4/Dz+WJwBvEYL/lkkIsI3ihufq9hk9K4lVoK" crossorigin="anonymous"\>

    \<\!-- Space for Custom CSS \--\>  
    {% block app\_css %}{% endblock %}

    \<\!-- Location of favicon \--\>  
    \<link rel="shortcut icon" href="{{ url\_for('static', filename='favicon.ico') }}"\>  
  \</head\>

  \<body\>  
    \<\!-- Navbar Container \--\>  
    \<div class="container-fluid"\>  
      \<\!-- Navbar Header \[contains both toggle button and navbar brand\] \--\>  
      \<nav class="navbar navbar-expand-md navbar-light bg-light"\>

        \<\!-- Navbar Brand \[image \+ title, no link\] \--\>  
        \<span class="navbar-brand"\>  
          \<img src="{{ url\_for('static', filename='brand.svg') }}" height="30" class="d-inline-block align-top" alt="PyBloom"\>  
          PyBloom  
        \</span\>

        \<\!-- Toggle Button \[handles opening navbar components on mobile screens\] \--\>  
        \<button type="button" class="navbar-toggler" data-toggle="collapse" data-target="navbarNavItems" aria-expanded"false"\>  
          \<span class="navbar-toggler-icon"\>\</span\>  
        \</button\>

        \<\!-- Navbar Collapse \[contains all other navbar components\] \--\>  
        \<div class="collapse navbar-collapse" id="navbarNavItems"\>  
          \<\!-- Navbar Menu \--\>  
          \<div class="navbar-nav mr-auto"\>  
            \<li class="nav-item"\>  
              \<a class="nav-link" href="{{ url\_for('index') }}"\>Weather Station\</a\>  
            \</li\>  
            \<li class="nav-item"\>  
              \<a class="nav-link" href="{{ url\_for('colours') }}"\>Colour Key\</a\>  
            \</li\>  
          \</div\>  
          \<\!-- a plug for my blog\! \--\>  
          \<div class="navbar-nav navbar-right"\>  
            \<li class="nav-item"\>  
              \<a class="nav-link"  href="[https://blog.mindrocketnow.com](https://www.google.com/url?q=https://blog.mindrocketnow.com&sa=D&ust=1603647715874000&usg=AOvVaw0oaX_hCjIH5JSdwapnI45R)"\>Home\</a\>  
            \</li\>  
          \</div\>  
        \</div\>  
      \</nav\>  
    \</div\>

    \<\!-- This is where the page content will go \--\>  
    {% block app\_content %}{% endblock %}

    \<\!-- Bootstrap JavaScript Bundle with Popper.js \--\>  
    \<script src="https://stackpath.bootstrapcdn.com/bootstrap/5.0.0-alpha2/js/bootstrap.bundle.min.js" integrity="sha384-BOsAfwzjNJHrJ8cZidOg56tcQWfp6y72vEJ8xQ9w6Quywb24iOsW913URv1IS4GD" crossorigin="anonymous"\>\</script\>

    \<\!-- Space for custom JS \--\>  
    {% block app\_js %}{% endblock %}  
  \</body\>

index.html

{% extends "base.html" %}

{% block app\_content %}  
  \<h1\>Latest data\</h1\>  
  \<div\>  
    \<h2\>Last 24 hours\</h2\>  
    \<img src="{{ url\_for('static', filename=content\['lastday'\]) }}" class="img-fluid" alt="Responsive image"\>  
    \<h2\>Last week\</h2\>  
    \<img src="{{ url\_for('static', filename=content\['lastweek'\]) }}" class="img-fluid" alt="Responsive image"\>  
  \</div\>  
{% endblock %}

---

# **Colour picker utility**

My stretch target was to display a table of all the colours of the Bloom lamp on a page in the website. As we've seen, the colours are in a persistent SQLite table, so all I have to do is to extract from the table, and somehow get the CSS to read the colour information. Except CSS is not an interactive language, so I needed another technology. Step forward JavaScript.

## **The technologies**

HTML  
JavaScript  
Jinja2

## **The code**

{% extends "base.html" %}

We put all the main styling into the base page, which means as before, we simply need to extend it here.

{% block app\_content %}

This HTML section will be inserted into the base.html template at the position marked app\_content.

\<table class="table"\>

We’re making use of the Bootstrap formatting for tables to make things pretty.

\<tr\>  
  \<th scope="col"\>Temperature\</th\>  
  \<th scope="col"\>Colour\</th\>  
\</tr\>

The table consists of two columns: one for Temperature and one for the corresponding Bloom colour.

{% for row in rows %}

This is our familiar Jinja2 loop, which we want to repeat for every row in the temperature conversion lookup table.

\<tr\>  
  \<td\>{{row\[1\]}}\</td\>

The first cell in the row is simply the value of temperature from the lookup table.

  \<td id="{{row\[2\]}}"\>{{row\[2\]}}\</td\>  
\</tr\>

The second cell is the value of the colour, a hex string. This same string is also used to identify the cell. Each cell will have its own background colour, so needs to be uniquely identified. We’ll implement this logic with a small bit of JavaScript, so let’s jump straight into it.

{% block app\_js %}

As with the inserted HTML, this identifies where the custom JavaScript goes. Order is important in placing JavaScript; as this overrides the Bootstrap JavaScript, the block is after the statement that pulls Bootstrap from the CDN.

\<script\>  
  "use strict";

This is the normal preamble for JavaScript. Unlike CSS, as of HTML5 there’s no need to define type="text/javascript" as no other types are allowed. The second "use strict" command instructs the browser to use the modern (ECMAScript5 from 2009\) interpreter. This is important as some commands will not work in an older interpreter, and some commands will work differently.

{% for row in rows %}  
  document.getElementById("{{ row['hex_value'] }}").style.background \= "\#{{ row['hex_value'] }}";

We can use the same Jinja2 loop structure to set the background for each hex value cell in our table. But because each iteration of the loop creates another persistent row in the JavaScript, we need to be careful not to use variables as these would simply overwrite the previous. That’s why we have this complicated command that chains a lot of functions. Let’s pick it apart.  
document.getElementById(): We assigned a unique ID for each table cell containing a hex value  
"{{ row['hex_value'] }}": This unique ID is the hex value string  
style.background: JavaScript accesses the cell colour using this method (which is slightly different to the CSS attribute of background-color)  
\= "\#{{ row['hex_value'] }}": The colour is the hex value from the lookup table, which is a string (as accepted by the SQLite database), but has to be prefixed with a hash to identify it as a hex string  
; Don’t forget to finish every JavaScript statement with a semicolon \- which isn’t required in Python or CSS or SQLite

The table now pulls the Hue bloom colour data from the external SQLite table and displays on a web page.

## **Putting it together**

{% extends "base.html" %}

{% block app\_content %}  
  \<h1\>Colour key\</h1\>  
  \<div\>  
    \<table class="table"\>  
      \<tr\>  
        \<th scope="col"\>Temperature\</th\>  
        \<th scope="col"\>Colour\</th\>  
      \</tr\>  
      {% for row in rows %}  
      \<tr\>  
        \<td\>{{ row['temperature'] }}\</td\>  
        \<td id="{{ row['hex_value'] }}"\>{{ row['hex_value'] }}\</td\>  
      \</tr\>  
      {% endfor %}  
    \</table\>  
  \</div\>  
{% endblock %}

{% block app\_js %}  
  \<script\>  
    "use strict";  
    {% for row in rows %}  
      document.getElementById("{{ row['hex_value'] }}").style.background \= "\#{{ row['hex_value'] }}";  
    {% endfor %}  
  \</script\>  
{% endblock %}

# **Restart on Reboot**

Systemd is the standard Linux initialization engine. It turns the Python script into a formal system background daemon that runs independently of any user sessions. 

[Unit]
Description=Flask Web Server
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/your_project
ExecStart=/home/pi/.virtualenvs/pybloom/bin/flask run --host=0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target

This file uses the standard INI configuration format to define a system service for systemd (the initialization daemon on Linux). It is broken into three distinct blocks, each handling a different stage of the process lifecycle.

Here is the line-by-line breakdown of how the operating system interprets this manifest.

1. The [Unit] Block
This section defines the metadata and setup dependencies for the service. It tells systemd what the service is and when it should be allowed to start.

Description=Flask Web Server
- A free-text string used to identify the service in system logs and status commands (e.g., when you run systemctl status).

After=network.target
- Defines the boot order dependency. This instructs systemd to delay starting your Flask application until the network interface controller is fully initialized and up. Without this, the Flask app could try to bind to an IP address before the Pi has finished joining your Wi-Fi or Ethernet network, causing the application to crash instantly on boot.

2. The [Service] Block
This is the core execution matrix. It dictates the security context, working directories, and binary execution commands for the daemon process.

User=pi
- The security context under which the process executes. By default, system services run as root (administrative superuser). Forcing it to run as the pi user follows the principle of least privilege, preventing a security vulnerability in your Python application from compromising the entire host operating system.

WorkingDirectory=/home/pi/your_project
- Sets the absolute root directory path where the command executes. This is critical if your Flask app relies on relative paths to find local files, templates, sqlite databases, or environmental .env files.

ExecStart=/home/pi/.virtualenvs/pybloom/bin/flask run --host=0.0.0.0
- The absolute command execution line.
- Notice that it explicitly invokes the flask binary inside your specific virtual environment (.virtualenvs/pybloom/bin/flask). This ensures the app uses your project-isolated Python dependencies rather than the global system Python.
- The --host=0.0.0.0 flag binds the server to all available network interfaces on the Pi, making it reachable from your Mac or other external devices on your local network (binding to 127.0.0.1 would confine it strictly to connections originating from inside the Pi itself).

Restart=always
- The self-healing policy rule. If your Python code throws an unhandled exception, runs out of memory, or is killed by an external signal, systemd will intercept the failure and automatically respawn a fresh worker process thread within a few seconds.

3. The [Install] Block
This section handles the configuration hook when you enable the service via sudo systemctl enable. It defines how the service anchors itself to the system boot target sequence.

WantedBy=multi-user.target
- Defines the target environment hook. multi-user.target represents a fully booted, non-graphical, multi-user console state (the standard running state of a headless server layout). Specifying this ensures that your Flask server automatically kicks off every single time the Raspberry Pi powers up, without requiring a human or agent to log in over SSH first.

Note: You do not need to call source or workon inside a system service. You simply need to point ExecStart directly to the absolute path of the flask binary inside that centralized pybloom directory.

## **Enabling the Service**

1. Reload the systemd manager configuration to catch the file updates
sudo systemctl daemon-reload

2. Enable the application service 
sudo systemctl enable pybloom.service

3. Start the application service
sudo systemctl start pybloom.service

Or simply reboot the Pi, and the service will start automatically.

4. Verify that the service is active and running successfully
sudo systemctl status pybloom.service

---

# Testing

My target for testing is to have a fully automated test suite that covers at least 95% of the code. The code is of acceptable quality if 95% of the tests pass. The reason for not aiming for 100%-100% is that some of the code is not worth testing; error handling of edge cases (e.g., network outage) is not worth testing because it’s uncommon, and if it goes wrong there's a more significant problem (e.g., the network is down).

I implemented a test suite using the pytest framework. The tests are located in the tests/ directory, and each test file is named test_*.py. The tests cover unit tests for the functions in the app, as well as integration tests for the web pages. I haven't written tests for the database, the external API calls, or the web pages as these are relatively trivial.

These tests are meant to be run ad-hoc, to prove that a new feature hasn't broken existing code (regression testing). They could also be run as part of CI e.g., triggered by a GitHub Action on a push to the repository.

## **Current test functions and what each checks**

`test_find_temp_threshold_clamps_to_database_bounds`: Verifies threshold clamping at the configured minimum and maximum values.

`test_lookup_colour_returns_matching_hex`: Verifies that a valid threshold returns the mapped hex value.

`test_lookup_colour_raises_for_missing_threshold`: Verifies that a missing threshold raises a `ValueError`.

`test_weather_observation_set_and_str`: Verifies manual field assignment and string representation formatting.

`test_get_rows_rejects_invalid_table`: Verifies invalid table names are rejected explicitly.

`test_init_db_creates_and_seeds_schema`: Verifies schema creation and default colours seeding.

`test_get_rows_returns_named_rows`: Verifies row-factory style keyed access on returned query rows.

`test_weather_orchestration_calls_external_steps`: Verifies top-level orchestration calls fetch, lamp update, log, and graph generation.

`test_hue_lamp_set_colour_combines_state_updates`: Verifies `set_colour` sends a single combined Hue state update.

`test_home_route_renders`: Verifies `/` route returns HTTP 200 and expected page content.

`test_colours_route_renders`: Verifies `/colours` route returns HTTP 200 and expected content.

`test_weather_observation_fetch_success`: Verifies successful weather fetch populates timestamp, temperature, and status.

`test_weather_observation_fetch_api_failure`: Verifies API manager failures surface as exceptions.

`test_weather_observation_fetch_none_observation`: Verifies `None` observation responses are handled as errors.

`test_weather_observation_fetch_none_weather_reading`: Verifies missing weather payloads are handled as errors.

`test_weather_observation_log_success`: Verifies observation insert/write behavior into SQLite.

`test_weather_observation_log_database_failure`: Verifies database connection failures during log are surfaced.

`test_hue_lamp_str_on`: Verifies lamp string representation when lamp state is on.

`test_hue_lamp_str_off`: Verifies lamp string representation when lamp state is off.

`test_hue_lamp_turn_on`: Verifies Hue on-command payload.

`test_hue_lamp_turn_off`: Verifies Hue off-command payload.

`test_hue_lamp_set_colour_exception`: Verifies colour set failures are surfaced from the Hue layer.

`test_hue_lamp_init_exception`: Verifies Hue bridge initialization failures are surfaced.

`test_convert_temp_to_colour`: Verifies threshold lookup plus converter path returns XY colour.

`test_generate_graphs_with_data`: Verifies graph generation path with observation data.

`test_generate_graphs_with_no_data`: Verifies graph generation path when observation set is empty.

`test_weather_with_none_temperature`: Verifies weather orchestration fails safely when temperature is missing.

`test_weather_with_none_timestamp`: Verifies weather orchestration fails safely when timestamp is missing.

`test_weather_fetch_error_propagates`: Verifies fetch exceptions are captured by weather job handling.

`test_main_block_execution`: Verifies main execution path calls `weather()`.

`test_datetime_import`: Verifies required datetime import availability.

`test_statistics_import`: Verifies required statistics import availability.

`test_generate_graphs_bar_chart_exception`: Verifies bar chart render failures are propagated.

`test_generate_graphs_pie_chart_exception`: Verifies pie chart render failures are propagated.

`test_generate_graphs_radar_chart_exception`: Verifies radar chart render failures are propagated.

`test_generate_graphs_box_chart_exception`: Verifies box chart render failures are propagated.

`test_main_block_coverage`: Verifies explicit main-block weather call path for coverage.

`test_should_start_scheduler_disabled_by_env`: Verifies scheduler start is blocked when `PYBLOOM_DISABLE_SCHEDULER=1`.

`test_should_start_scheduler_enabled_in_normal_run`: Verifies scheduler guard allows startup when no disable flag is set.

`test_initialize_runtime_init_db_only`: Verifies explicit runtime initializer can run DB setup without starting scheduler jobs.

`test_initialize_runtime_starts_scheduler_when_allowed`: Verifies explicit runtime initializer starts scheduler when background jobs are enabled and allowed.

`test_initialize_runtime_is_idempotent`: Verifies runtime initialization only runs once even if called multiple times.

`test_should_initialize_runtime_on_import_false_under_pytest`: Verifies import-time runtime initialization is skipped when running under pytest.

`test_should_initialize_runtime_on_import_true_normally`: Verifies import-time runtime initialization is enabled outside pytest.

## **How to run tests and review results**

Run tests from the project root using `uv`:

```bash
uv run pytest -q
```

What this command does:

1. Executes all tests in `tests/test_pybloom.py`.
2. Prints a compact pass/fail summary (`-q` = quiet mode).
3. Prints coverage output configured in `pyproject.toml`.

To run a single test function while debugging:

```bash
uv run pytest -q tests/test_pybloom.py::test_weather_orchestration_calls_external_steps
```

To run a subset of tests by name pattern:

```bash
uv run pytest -q -k "weather_observation or hue_lamp"
```

How to review test results:

1. Check the final summary line (for example: `37 passed`), which confirms overall suite status.
2. If any test fails, read the traceback section for:
        * failing test function name,
        * assertion message,
        * line number where the failure occurred.
3. Review the coverage table to see per-module coverage for `app`, `db_utils.py`, and `pybloom.py`.
4. Use the `Missing` column to identify exact lines not covered by tests.

Practical interpretation:

* If all tests pass and coverage remains near the current baseline, changes are likely safe to merge.
* If tests pass but coverage drops unexpectedly, add or update targeted tests before merging.
* If one integration-like test fails intermittently, re-run that single test first to rule out flaky setup.

## **How patching works (especially `monkeypatch`)**

Many tests in this project avoid real network and hardware calls by patching dependencies at runtime. In pytest, the `monkeypatch` fixture temporarily replaces attributes, functions, or environment values for the duration of a test, then automatically restores them.

Why this matters in PyBloom:

1. Real integrations (Hue bridge, OpenWeatherMap, scheduler timing) are non-deterministic.
2. Unit tests should verify our code logic, not external service uptime.
3. Patching keeps tests fast and reproducible on any machine.

Typical pattern used here:

```python
def test_lookup_colour_returns_matching_hex(monkeypatch):
        monkeypatch.setattr(
                pybloom,
                'get_rows',
                lambda table, columns='*', **kwargs: [('ffbf00',)],
        )

        assert pybloom.lookup_colour(25) == 'ffbf00'
```

What happens in that example:

1. `pybloom.get_rows` is replaced with a local lambda.
2. `lookup_colour()` runs against predictable fake data.
3. After the test, pytest restores the original `get_rows` automatically.

Common `monkeypatch` uses in this codebase:

* Replace API clients: patch `pybloom.pyowm.OWM` to simulate success/failure responses.
* Replace Hue bridge objects: patch `pybloom.qhue.Bridge` to avoid real bulb/network calls.
* Replace utility functions: patch `pybloom.generate_graphs`, `pybloom.convert_temp_to_colour`, or `db_utils.db_connect` to isolate orchestration logic.
* Replace constants/paths: patch `pybloom.FILEPATH` so graph tests write to a temp folder.

Patch where the symbol is looked up:

* If a function calls `pybloom.db_connect`, patch `pybloom.db_connect`.
* Patching `db_utils.db_connect` alone will not affect call sites that already imported a local reference.

Useful variants:

* `monkeypatch.setattr(obj, 'name', replacement)` for functions/classes.
* `monkeypatch.setenv('NAME', 'value')` for environment-driven code paths.
* `monkeypatch.delenv('NAME', raising=False)` to simulate missing env vars.

Rule of thumb:

* Use fixtures in `tests/conftest.py` when many tests need the same fake dependency.
* Use inline monkeypatching in a single test when behavior is test-specific.

## Test isolation

With automated testing comes lack of oversight of test execution. If tests are repeated, then multiple instances of the scheduled job could run at the same time. To prevent this, startup behavior is isolated behind explicit helper functions and a simple import-time pytest guard.

### Current startup model

`app/__init__.py` centralizes startup behavior in:

1. `initialize_runtime(init_database=True, start_background_jobs=True)` to run DB setup and optional scheduler startup.
2. `should_start_scheduler()` to allow disabling the scheduler with `PYBLOOM_DISABLE_SCHEDULER=1`.
3. `should_initialize_runtime_on_import()` to skip import-time initialization under pytest.

This keeps normal runs simple (`uv run flask run` still initializes immediately), while tests can import modules without accidentally starting the scheduler.

### Scheduler guard

The scheduler guard is now intentionally minimal:

def should_start_scheduler() -> bool:
    """Return True when scheduler should start for this process."""
    return os.getenv('PYBLOOM_DISABLE_SCHEDULER') != '1'

def initialize_runtime(*, init_database: bool = True, start_background_jobs: bool = True) -> None:
        global runtime_initialized
        if runtime_initialized:
                return

        if init_database:
                init_db()

        if start_background_jobs and should_start_scheduler():
                start_scheduler()
        runtime_initialized = True

def should_initialize_runtime_on_import() -> bool:
        return 'pytest' not in sys.modules

if should_initialize_runtime_on_import():
        initialize_runtime(init_database=True, start_background_jobs=True)

---

# **CI using GitHub**

GitHub is a cloud-based service that hosts Git repositories. It provides a web-based interface for managing code, tracking changes, and collaborating with others. By integrating your local Git repository with GitHub, you can easily push your code to the cloud, share it with others, and take advantage of GitHub's features like pull requests, issues, and actions.

But a Raspberry Pi is a small, low-power device that may not always be connected to the internet. This means it can't pull code from GitHub, so we can only use GitHub for Continuous Integration (CI) of our code. To do this, we need to set up a GitHub repository and configure our local Git repository to push changes to it.

The CI part is a workflow that automatically builds and tests your code whenever you push changes to the GitHub repository. This helps catch errors early and ensures that your code is always in a deployable state. You can set up CI using GitHub Actions, which allows you to define workflows that run on GitHub's servers.

## **Documentation**

GitHub initialised all repositories with a README.md file. This is a markdown file that describes the project, its purpose, and how to use it. It is displayed on the main page of the repository and serves as the first point of contact for anyone visiting the repo. I'm using it to instruct future me and AI agents on how to navigate the code.

## **Gitignore**

A critical file in any Git repository is the .gitignore file. This file tells Git which files or directories to ignore when committing changes. It is important to exclude files that are generated during the build process, temporary files, or sensitive information like credentials.

The sections of my root .gitignore:
1. PROJECT DEPENDENCIES & ENVIRONMENTS (UV / Python)
2. LOCAL DATA, CONFIGS & SECRETS (Never commit to Git)
3. RUNTIME ARTIFACTS & BACKUPS
4. SYSTEM, DESIGN & OS SPECIFIC FILES

My repo is a monorepo, meaning there are multiple sub-projects in the same repository. Each sub-project could have its own .gitignore file, perhaps separating the different technologies, which allows for more granular control over which files are ignored in each sub-project. I'm not going to bother as we won't benefit from the extra complexity, but it's worth noting that it is possible.

---

# **CD using RSync**

---

# **Conclusions**

This project has been quite a learning experience. I’ve had to get to grips with a lot of technologies, a lot of frameworks, and quite a learning curve. Here are some top tips:

1. No matter how clear the tutorials, the code never works first time. Learn by testing.  
2. Google and YouTube are great resources for finding how to do things, but relies on being able to ask the right question. Be clear on precisely what the problem is.  
3. Having to describe everything here has really helped reinforce the learnings.  
4. There’s always another feature to think up and implement. But it’s important to be clear when done=done, and the program is good enough to be used.  
5. Good enough to be used by you isn’t the same as good enough for someone else. If you want to roll out your code, have it tested by someone that doesn’t know it.

Thank you for joining me on this journey. Hope it’s been a little help with your own exploration. Also visit [https://github.com/Schmoiger/pybloom](https://www.google.com/url?q=https://github.com/Schmoiger/pybloom&sa=D&ust=1603647715894000&usg=AOvVaw0NcI94DnJ6SrquRL-4QV7x) for the full story.

---

# **Even better if…**

Over the course of this document, I’ve described how I’ve implemented the features of my program. It’s doing what I intended it to do, the lights are showing how the evenings are getting colder. It’s fine for personal consumption, but it wouldn’t be fine for others to use. Before going into new features, I should look at *operationalising* the code, which will be a whole different set of challenges:

* Operational tools: manual CRUD access to the databases \- because I built in a way of manually adding data, but didn’t build a way to remove it. For example, filling in gaps in the data when the Pi was off, or removing bad data.
* We could keep track of *versions* and feature toggles for new features. Maybe if I keep developing the code.

## **New OpenWeatherMap API v3 (TODO)**

[https://pyowm.readthedocs.io/en/latest/\#very-important-news](https://pyowm.readthedocs.io/en/latest/#very-important-news)   
[https://openweathermap.org/api/one-call-3](https://openweathermap.org/api/one-call-3)

The Open Weather Map project updated its API to v3.0 called One Call. The syntax is different; the code now needs to pass latitude and longitude values. (Free usage limits remain the same, but you do now need to sign up using a credit card.) 

The process to find (OWM’s registry of) latitude and longitude is somewhat convoluted but covered in the code snippets section of PyOWM. Once you discover them, add to an updated config file thus:

credentials.py  
credentials \= {  
    'hue\_ip': \<IP address of your Hue Bridge\>,  
    'hue\_username': \<given by the Hue Bridge on first sync\>,  
    'owm\_key': \<generated by service on signing up\>,  
    'home\_location': \<where you live, in the format city, country code\>  
    'home\_location\_lat': \<latitude pulled from OWM registry\>  
    'home\_location\_lon': \<longitude pulled from OWM registry\>  
}

We now need to add a couple more global constants at the top:

HOME\_LOCATION\_LAT \= credentials.credentials\['home\_location\_lat'\]  
HOME\_LOCATION\_LON \= credentials.credentials\['home\_location\_lon'\]

TODO

* API key invalid error. Have subscribed to new OneCall service and generated a new API key at OWM. Old one, named “Legacy” still seems to work
