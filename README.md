# dbc-simulator
Decode and send messages defined in a DBC file.

## Setup
``` 
git clone git@github.com:scharri/dbc-simulator.git 

# create and activate virtual environment
cd dbc-simulator
python3 -m venv venv
. venv/bin/activate

# install requirements
pip install -r requirements.txt
```

## Usage
### dbcDecoder
dbcDecoder receives CAN-Messages and shows decoded content.
| arg | comment |
| - | - |
| dbc | path to the dbc to be used |
| device | name of the can device to be used |

### dbcSender
dbcSender sends CAN-Messages with random content defined in the dbc file.
| arg | comment |
| - | - |
| dbc | path to the dbc to be used |
| device | name of the can device to be used |
| cycle_time | time in ms between two transmission cycles | 