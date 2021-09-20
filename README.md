# Zmodo Record

This is a basic python script (with docker support) that allows you to login using your Zmodo cloud account and record all your device video streams to local mp4 files to store away as long as you want.

**Please Note:** This is an experimental project for educational purposes only. As per the license agreement, there are no guarantees with this project and I am not responsible for any issues that might come up.

## Build the docker image
Run `docker build -t zmodo-record .` from the project root dir. This will build the docker image locally. It takes some time as it has to install the entire ffmpeg apt package.

## To run the docker container
This is a pretty straight-forward docker run command. Execute `docker run -d -v <MY_VIDEO_STORAGE_DIR>:/zmodo_output -e USERNAME='<MY_ZMODO_CLOUD_USERNAME>' -e PASSWORD='<MY_ZMODO_CLOUD_PASSWORD>' zmodo-record`. 

`MY_VIDEO_STORAGE_DIR` is the directory path where you want the video output stored
`MY_ZMODO_CLOUD_USERNAME` is usually your email you used for your cloud account
`MY_ZMODO_CLOUD_PASSWORD` is your Zmodo cloud account password.

This will start the python process which will download and encode the cloud stream to you local storage and automatically refresh login tokens when they expire.


## Known Issues
* When one of the Zmodo devices has a bad network connection, ffmpeg tends to loose connection a lot which causes some video file data integrity issues. I am not sure what to do about this. Any help is appreciated.
* The process handling code needs to be looked at and improved.
* The mp4 files are encoded in linked file segments. When trying to play them back, I have noticed that the seek bar does not always work correctly. Any help with this issue is much appreciated. 

If you have any issues, please open an issue in this repo.