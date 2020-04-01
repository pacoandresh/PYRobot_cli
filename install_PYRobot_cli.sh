packages_python="/usr/local/lib/python3.7/dist-packages"
dir_PYRobot_cli="/home/paco/Dropbox/developing/PYRobot_cli"

link=$packages_python/PYRobot
echo "linking package "$link
sudo ln -s $dir_PYRobot_cli $packages_python/PYRobot_cli
sudo pip3 install netifaces
sudo pip3 install paho-mqtt
sudo pip3 install psutil
sudo pip3 install mprpc
sudo pip3 install pyparsing
sudo pip3 install termcolor
sudo pip3 install setproctitle
sudo pip3 install deepdiff


