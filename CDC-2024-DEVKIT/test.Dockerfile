FROM  autodriveecosystem/autodrive_f1tenth_api:2024-cdc-practice 
COPY vul.sh /home
COPY autodrive_devkit/. /home/autodrive_devkit/src/autodrive_devkit
