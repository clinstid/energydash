energymon: Energy Monitor Web App
==============================

Background
----------------
In the winter of 2012, we received an electric bill for over $700. Granted that was a pretty bad winter (and we heat a sunroom that has mostly glass walls with a small electric heater that's running all the time), but it showed me that I honestly had no real grasp of the amount of power we were using, so I started doing some research on power monitors.

There were a few that existed that had relatively advanced software for drawing charts and calculating stats, but they were pretty expensive, so I thought that maybe I could build something to do what I wanted instead. I had been wanting to learn about web app development for a while, so I decided that I would look into creating my own.

Hardware
-------------
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


