energymon: Energy Monitor Web App
=================================

Background
----------
In the winter of 2012, we received an electric bill for over $700. Granted that was a pretty bad winter (and we heat a sunroom that has mostly glass walls with a small electric heater that's running all the time), but it showed me that I honestly had no real grasp of the amount of power we were using, so I started doing some research on power monitors.

There were a few that existed that had relatively advanced software for drawing charts and calculating stats, but they were pretty expensive, so I thought that maybe I could build something to do what I wanted instead. I had been wanting to learn about web app development for a while, so I decided that I would look into creating my own.

Hardware
--------
The basic building blocks for the hardware that provides data for energymon are a transmitter and receiver pair called an <a href="http://www.currentcost.net/Monitor%20Details.html">Envi kit</a>. The kit includes two clamps that go around the main power lines that come into the breaker box, a transmitter that the clamps plug into, and a receiver that pairs with the transmitter and displays power usage information.

In addition to displaying information, the receiver also has an RJ-45 serial port on the back. That serial port transmits an xml message every 6 seconds with the data it received from the transmitter. The Current Cost folks have graciously provided an <a href="http://www.currentcost.com/download/Envi%20XML%20v19%20-%202011-01-11.pdf">XML description document</a> that aided me in gleaning meaningful data from the messages. I also purchased an RJ-45 to USB serial adapter that thankfully has Linux drivers.

The XML messages look like this:

    <msg><src>CC128-v0.15</src><dsb>00013</dsb><time>00:10:07</time><tmprF>68.7</tmprF><sensor>0</sensor><id>00077</id><type>1</type><ch1><watts>00006</watts></ch1><ch2><watts>00269</watts></ch2><ch3><watts>00328</watts></ch3></msg>

In a more readable format:

    <msg>
        <src>CC128-v0.15</src>
        <dsb>00013</dsb>
        <time>00:10:07</time>
        <tmprF>68.7</tmprF>
        <sensor>0</sensor>
        <id>00077</id>
        <type>1</type>
        <ch1>
            <watts>00006</watts>
        </ch1>
        <h2>
            <watts>00269</watts>
        </ch2>
        <ch3>
            <watts>00328</watts>
        </ch3>
    </msg>

Most of the message is pretty easy to figure out. The `dsb` tag stands for "days since birth" and I backtracked to figure that out for myself and I store that in the `settings.py` file.

Software Components
-------------------

### Serial Data Collector
The transmitter and receiver have to be relatively close to each other. The manual says that they will work up to 100 feet apart if you subtract 10 feet for each wall the signal has to pass through. In my experience, they really need to be in the same room. So, I decided to hook up the receiver to a netbook that I had just sitting around. The netbook is pretty light on hardware, it's a 1.6 GHz single core Atom processor with 2GB of RAM, but that's plenty for receiving a line of XML every 6 seconds. However, I wanted to keep the transport of the XML as lightweight as possible as I am pondering the idea of moving this task to a Raspberry Pi or maybe even an Arduino at some point.

This meant that I wanted to avoid parsing the XML and just forward it to another agent to deal with. I decided to run a [RabbitMQ](http://rabbitmq.com) server on the netbook to queue up the messages and then let an agent on my server pull them from the queue when it was up and running. I started by using the [Pika](https://github.com/pika/pika) library for Python, but I was having some odd problems with it, so I switched to [py-amqplib](https://code.google.com/p/py-amqplib/) and that has worked great for me.

The file `envir_collector.py` contains the code that I use for collecting the XML messages off the serial port and adding the messages to the queue.

### XML Parser and Database Writer
The server runs `envir.py` (this could probably use a better name) to pull messages from the queue hosted on the netbook, parse the XML, and create database (SQLite) entries. The database contains entries for all of the readings that are pulled from the queue. If we actually get readings every 6 seconds (which I do now that the transmitter and receiver are close enough), that's 5,256,000 entries per year. It will be interesting to see how well SQLite can scale when I have multiple years of data.

### Data Caching
In my early attempt to try to use the data I was getting, I was generating a CSV file so I could import the data into a spreadsheet and construct some charts. At this point, I realized that trying to plot data points from every 6 seconds was not going to work. In addition to that, if I wanted to plot a chart for the past 7 days, month, or even longer, I both had to reduce the number of data points and cache the data rather than having to pull it from the database every time.

For this, we have `energymon_cache.py`. This process runs on a 60 second cycle and pulls new entries from the database. It breaks down the granularity of the data from every 6 seconds to once per minute. This means that for a year of data, we have 526,000 entries, which is a little easier to deal with. 

For caching, I'm using [redis](http://redis.io/). The basic setup is that I have a sorted set that contains the timestamps for each minute (in seconds since 01-Jan-1970) as scores and members. The timestamp member is a key for a hash where the hash value for each key is the average usage in watts for that minute. Using the scores in the sorted set, I can perform a time range query to get a list of keys to look up the usage in watts. I'm not sure I'm particularly happy with this setup because it's not intuitive, but it was still a good learning exercise for using redis.

### Web App
The web app at this point is at a very early stage. I'm using Flask for the framework (I started with django, but it just seemed too heavy for what I was doing) and SQLAlchemy for the database ORM. I'm using jquery and [Flot](http://www.flotcharts.org/) to build a basic time-based chart, but it's very crude at the moment (the timeframe for the chart is hardcoded in the html template). So far, I like Flot and think I will continue with it. I gave Google Data Visualization a try, but I wasn't enamored with their JSON structure for the data input, so I've put it aside for the moment.

Still a lot of work to do on this, but it's been an excellent learning experience so far.

