# SCAMP Installation

## Clone the git repo: 
https://github.com/robertlagrasse/scamp.git

## Create Authentication File
sudo nano /path/to/scamp/creds/creds.json

Contents of creds.json file:
{
  "username": "your.gmail.id@gmail.com",
  "password": "your app password"
}


## Create a service
SCAMP is written in Python. While it's possible to run SCAMP from the command line, the preferred
deployment option is as a service. 


### Create a service file for SCAMP
sudo nano /etc/systemd/system/scamp.service

The contents of the scamp.service file:

[Unit]

Description=Scamp Service

After=network.target

[Service]
ExecStart=/bin/bash /path/to/scamp/scamp.sh

WorkingDirectory=/path/to/scamp

Restart=always

RestartSec=3

User= (your username)

[Install]

WantedBy=multi-user.target`


### Enable and start the service
sudo systemctl enable scamp

sudo systemctl start scamp

### Stopping, starting and monitoring the service
Standard systemctl commands apply here
* sudo systemctl restart scamp.service
* sudo systemctl start scamp.service
* sudo systemctl stop scamp.service
* systemctl status scamp.service

# What actually happens
When the service is started, it kicks off a bash script called scamp.sh.
That script installs any needed dependencies, ensures the proper directories
are in place, and starts the emailMonitor.py script that 