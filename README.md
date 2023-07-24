# rabbitmq-magic-eye
 
- version 0.1

## Config

Change config in .env file

## Used libraries
```
pika
python-dotenv
datetime
os
numpy
```
## Run

``` 
To run in this configuration (connecting to the configured server) you need to be connected to the "correct" VPN - available only to selected people - sorry

Also need to fill the img folder with images with the extension .jpg or .jpeg

cd src
python3 producer.py
python3 sharpening.py
python3 consumer.py
```