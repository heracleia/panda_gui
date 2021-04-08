#!/bin/sh

# Install ROS Kinetic
# Follow the installation guide on the following link: - http://wiki.ros.org/kinetic/Installation/Ubuntu
# Install MoveIt 1 - Kinetic
# Follow the installation guide till creating a catkin workspace on the following link: - http://docs.ros.org/en/kinetic/api/moveit_tutorials/html/doc/getting_started/getting_started.html

# Usage:
# For Installing all required dependencies (Useful for fresh or docker installs)
# ./install.sh install_deps
# For fresh install along with libfranka in the src folder
# ./install.sh install_deps build_franka_from_src
# For libfranka in src folder and not requiring dependencies installed from apt
# ./install.sh dont_install_deps build_franka_from_src
# For just rebuilding the catking workspace after usual edits
# ./install.sh

RED='\033[0;31m'
NC='\033[0m' # No Color
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $DIR
# Check if the current directory is a ROS Workspace, else exit
# checks to see if a valid catkin workspace has been created
TWO_DOTS=$(cd ../../ && pwd)
THREE_DOTS=$(cd ../../.. && pwd)
if [[ -d ../../src && $TWO_DOTS != $THREE_DOTS ]]; then
    echo "Valid Catkin Workspace exists"
else
    printf "${RED}Not a valid catkin workspace! Terminating installation...${NC}"
    # exit the whole thing
    exit 1
fi
# As this directory will be in the ROS package, we gotta move to src folder, which is parent of parent of the $DIR
cd ../..
DIR="$(pwd)"

install_librealsense2(){
  cd $DIR/src
  git clone https://github.com/microsoft/vcpkg
  cd vcpkg
  ./bootstrap-vcpkg.sh
  ./vcpkg integrate install
  ./vcpkg install realsense2
  cd ..
}


if [ $1 = "install_deps" ]
  then
    # Install All dependencies
    sudo apt -y install ros-$ROS_DISTRO-cv-bridge
    sudo apt -y install ros-$ROS_DISTRO-vision-opencv
    sudo apt -y install python-numpy
    install_librealsense2

    sudo apt -y install ros-$ROS_DISTRO-realsense2-camera
    sudo apt -y install ros-$ROS_DISTRO-realsense2-description
    sudo apt -y install ros-$ROS_DISTRO-libfranka
    # Installing catkin Build tools
    sudo apt -y install python-catkin-tools
    sudo apt-get install libboost-filesystem-dev
fi

# Clone all required repositories
# Let's make bash function, to make code easier
print_git_status() {
  # This function will print status of git
  # It will print if any changes exist, and if there are any new commits in the remote
  git fetch --all
  if git status -u | grep -q 'fast-forwarded'; then
        printf "${RED}New commits exist for $1. Please check for new release${NC}\n"
  fi
}

clone_specific_commits() {
  # The first argument would be the folder name, it would be the folder name to which automatically
  # created when the repo is cloned
  # Second argument is the HTTPS URL of the repo
  # 3rd arguments is the SHA1 hash of that commit which is assumed to be stable
  # 4th argument is branch
  cd $DIR/src
  if [ -d "$DIR/src/$1" ]
  then
      echo "The folder $1 already exists, checking the git status"
      cd $1
      print_git_status
  else
      echo "The specified $1 doesnt exists, so cloning from the repo"
      git clone --branch $3 --recursive $2
      cd $1
      git reset $4 --hard
      # The below command will print if this is the latest, or any new commits are available
      print_git_status
      printf "\n"
  fi
}
# Clone all the below repos into the src folder
clone_specific_commits "panda_simulation" "https://github.com/erdalpekel/panda_simulation.git" "master" "9b53b0efc4bbdbf21d6d3c250dd06d495e2aae9f"
clone_specific_commits "panda_moveit_config" "https://github.com/erdalpekel/panda_moveit_config.git" "melodic-devel" "a145fc96ff906f03c5bf818b32108d0422c2cf3c"
clone_specific_commits "franka_ros" "https://github.com/erdalpekel/franka_ros.git" "simulation" "45df2e90fe9e49162397774080284cf6d4c23abd"
clone_specific_commits "summit_xl_common" "https://github.com/RobotnikAutomation/summit_xl_common.git" "kinetic-devel" "fdbcb6bcb9b52722c7222e547369e64a1aab59c7"
clone_specific_commits "robotnik_msgs" "https://github.com/RobotnikAutomation/robotnik_msgs.git" "master" "678f1886e8c6f790d7a9769d044e7684b45bce42"
clone_specific_commits "robotnik_sensors" "https://github.com/RobotnikAutomation/robotnik_sensors.git" "kinetic-devel" "63557b6d3ea441744b19ef0e360a8b5dd5b9655c"
clone_specific_commits "summit_xl_sim" "https://github.com/RobotnikAutomation/summit_xl_sim.git" "kinetic-devel" "e73caa11e2bcde5080e8953282c020f685f419c6"
clone_specific_commits "gazebo-pkgs" "https://github.com/JenniferBuehler/gazebo-pkgs.git" "master" "a7ebecca4393d43393e315d379a876e71820fd96"
clone_specific_commits "general-message-pkgs" "https://github.com/JenniferBuehler/general-message-pkgs.git" "master" "f0c7a0cc811187cca8e928bc7c5906e463c24945"


if [ $2 = "build_franka_from_src" ]
  then
    clone_specific_commits "libfranka" "https://github.com/heracleia/libfranka.git" "0-7-0-patched" "5a2eecd539e54b5cf9db848e810f70c841227942"
    cd $DIR/src/libfranka
    mkdir build && cd build
    cmake -DCMAKE_BUILD_TYPE=Release ..
    make -j12
fi
# Build the workspace
cd $DIR
# Here we have to check if the libfranka folder exists, if yes, then we have build differently everytime
if [ -d "$DIR/src/libfranka/build" ]
then
    echo "Libfranka exists in Catkin Worspace, building accordingly"
    catkin build -DFranka_DIR:PATH=$DIR/src/libfranka/build
else
    printf "${RED}Hoping that Libfranka is already installed. If not please install it using apt. More details in README${NC}\n"
    catkin build
fi

# Source it so that you have latest binaries appropriately sourced
source devel/setup.bash
