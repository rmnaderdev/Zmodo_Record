# Zmodo Record

This is a basic python script (with docker support) that allows you to login using your Zmodo cloud account and record all your device video streams to local mp4 files to store away as long as you want (zmodo-record) or send the video streams as rtsp streams to be used for something like [Home Assistant](https://www.home-assistant.io/getting-started) (zmodo-proxy)

**Please Note:** This is an experimental project for educational purposes only. As per the license agreement, there are no guarantees with this project and I am not responsible for any issues that might come up.

## Build the docker images
* The following commands will build the docker image locally. It takes some time as it has to install the entire ffmpeg apt package

### Zmodo Record
Run `docker build -t zmodo-record -f Record_Dockerfile .` from the project root dir

### Zmodo Proxy
Run `docker build -t zmodo-proxy -f Proxy_Dockerfile .` from the project root dir

## To run the docker container

### Zmodo Record
Execute `docker run -d -v <MY_VIDEO_STORAGE_DIR>:/zmodo_output -e USERNAME='<MY_ZMODO_CLOUD_USERNAME>' -e PASSWORD='<MY_ZMODO_CLOUD_PASSWORD>' zmodo-record`

### Zmodo Proxy
Execute `docker run -d -e USERNAME='<MY_ZMODO_CLOUD_USERNAME>' -e PASSWORD='<MY_ZMODO_CLOUD_PASSWORD>'  zmodo-proxy`

`MY_VIDEO_STORAGE_DIR` is the directory path where you want the video output stored
`MY_ZMODO_CLOUD_USERNAME` is usually your email you used for your cloud account
`MY_ZMODO_CLOUD_PASSWORD` is your Zmodo cloud account password.
`MY_RTSP_SERVER` is the host address and port to an RTSP proxy of your choice. (Ex: 'rtsp://moouwu.local:8554') I recommend [rtsp-simple-proxy](https://github.com/aler9/rtsp-simple-proxy), a great project by [aler9](https://github.com/aler9).


## Known Issues
* When killing the Python process, any video segment that is currently being written to does not get properly closed (the last video file segment is corrupt) 

If you have any issues, please open an issue in this repo.
