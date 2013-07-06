# energymon: Energy Monitor Web App #

## Background ##
In the winter of 2012, we received an electric bill for over $700. Granted that was a pretty bad winter (and we heat a sunroom that has mostly glass walls with a small electric heater that's running all the time), but it showed me that I honestly had no real grasp of the amount of power we were using, so I started doing some research on power monitors.

There were a few that existed that had relatively advanced software for drawing charts and calculating stats, but they were pretty expensive, so I thought that maybe I could build something to do what I wanted instead. I had been wanting to learn about web app development for a while, so I decided that I would look into creating my own.

## Screenshot ##

![alt text](https://github.com/clinstid/energymon/raw/master/energymon_screenshot_2013-07-06.png "energymon screenshot")

## High Level Design ##

![alt text](https://github.com/clinstid/energymon/raw/master/high_level_design.png "energymon screenshot")

## Hardware ##
The basic building blocks for the hardware that provides data for energymon are a transmitter and receiver pair called an <a href="http://www.currentcost.net/Monitor%20Details.html">Envi kit</a>. The kit includes two clamps that go around the main power lines that come into the breaker box, a transmitter that the clamps plug into, and a receiver that pairs with the transmitter and displays power usage information.

In addition to displaying information, the receiver also has an RJ-45 serial port on the back. That serial port transmits an xml message every 6 seconds with the data it received from the transmitter. The Current Cost folks have graciously provided an <a href="http://www.currentcost.com/download/Envi%20XML%20v19%20-%202011-01-11.pdf">XML description document</a> that aided me in gleaning meaningful data from the messages. I also purchased an RJ-45 to USB serial adapter that thankfully has Linux drivers.

The XML messages look like this:

```xml
    <msg><src>CC128-v0.15</src><dsb>00013</dsb><time>00:10:07</time><tmprF>68.7</tmprF><sensor>0</sensor><id>00077</id><type>1</type><ch1><watts>00006</watts></ch1><ch2><watts>00269</watts></ch2><ch3><watts>00328</watts></ch3></msg>
```

In a more readable format:

```xml
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
```

* **src**: The firmware version running on the receiver.
* **dsb**: Days since birth - If you know when you started, you can backtrack from this value to figure out the actual day of the reading, but *envir_collector.py* creates a timestamp at the time of reading. That takes care of two problems. The first is that at least my receiver seems to lose time, so as long as the system running *envir_collector.py* is using NTP, the time and date should be correct.
* **time**: Timestamp according to the receiver.
* **tmprF**: The temperature in degrees Fahrenheit from a sensor on the receiver.
* **sensor**: I believe this value is referring to the mains sensors.
* **id**: Radio ID from the sensor.
* **type**: Sensor type, 1 is electricity (not sure what other types there are).
* **ch[1-3]**: The mains sensors, readings are in watts. Mine happens to have 3 although only 2 of mine are in use.

There are also historical messages sent every few hours that include reading history, but I'm ignoring those since I'm storing the real-time readings. It's on my "to do" list to read those as well and store them in the database.

## Software Components ##

### Data Collection ###
The `envir_collector.py` module is a multi-threaded process with the following threads: 

* **Collector**: Listens on the USB/serial line for transmissions from the receiver. Each line is added to a `Queue` to be processed.
* **Writer**: Pulls work items from the `Queue`, parses the XML and creates an `EnvirMsg` object that generates a document to save in the `envir_reading` collection in the database. 

This gives us documents in the `envir_reading` collection every 6 seconds as long as the link between the transmitter and receiver are working well.

Example:
```javascript
    > db.envir_reading.findOne()
    {
            "_id" : ObjectId("51b1456172ea814c7fb8bf09"),
            "reading_timestamp" : ISODate("2013-06-07T02:28:49.432Z"),
            "receiver_days_since_birth" : 19,
            "receiver_time" : "22:22:00",
            "ch1_watts" : 7,
            "ch2_watts" : 323,
            "ch3_watts" : 328,
            "total_watts" : 658,
            "temp_f" : 69.2
    }
```

### Stats ###
The `energymon_statsd.py` daemon is a python application that uses the documents in the `envir_reading` collection to build collections with coarser granularity so we can build charts with less data points. As you can see in the screenshot, there are charts based on hour-level granularity. 

For exmaple, the first main chart covers the last 24 hours. So, the first collection built is called `hours` and it contains averages of the 6-second readings from `envir_reading`. This provides a quick MongoDB query to pick up averages over the last 24 hours.

Building on the `hours` collection, there are also `hours_in_day` and `hours_per_dow` that cover averages for each of the 24 hours in any day and averages for each hour for each day of the week, respectively.

The stats are updated every 60 seconds and `energymon_statsd.py` keeps track of where it left off by saving a document in the `bookmarks` collection.

### Web App ###
The `energymon_app.py` module is a Flask-based web application. It pulls data from MongoDB and displays two main sections in the application:

* **Current**: The top section shows the most recent reading on the left and a line graph of readings for the last 24 hours on the right.
* **Stats/Charts**: The bottom, larger section presents tabs that have stats and charts for different time frames.
