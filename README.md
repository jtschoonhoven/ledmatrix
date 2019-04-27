# ledmatrix
Python library for driving LED displays from a Raspberry Pi.

```bash
# clone library
git clone https://github.com/jtschoonhoven/ledmatrix.git
cd ledmatrix

# install linux dependencies
sudo apt-get install libjpeg-dev zlib1g-dev

# install python dependencies
python3 -m venv ./venv
source venv/bin/activate
python3 -m pip install -r requirements.txt

# run
sudo python3 -m ledmatrix.game_of_life
```
