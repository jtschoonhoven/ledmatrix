# ledmatrix
Python library for driving LED displays from a Raspberry Pi.


**Prototype in terminal...**

![cli](https://media.giphy.com/media/Pk4YTEgU8PbAByxyOY/giphy.gif)

**...then run on Neopixel!**

![irl](https://media.giphy.com/media/lqS1BUZZ5LLGOgqI0R/giphy.gif)

```bash
# clone library
git clone https://github.com/jtschoonhoven/ledmatrix.git
cd ledmatrix

# install linux dependencies
sudo apt-get install libjpeg-dev zlib1g-dev

# install python dependencies (sudo is required on RPI)
sudo pip3 install -r requirements.txt

# run
sudo python3 -m ledmatrix.animations.game_of_life --rows 10 --cols 10
```
