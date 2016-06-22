#!/usr/bin/env bash

# Params
IFACE="eth0"
LOCAL=$(ip -4 address show $IFACE | grep 'inet' | sed 's/.*inet \([0-9\.]\+\).*/\1/')
LOCAL_USER=$(whoami)

REMOTE="campus.elis.ugent.be"
REMOTE_USER="gurbain"
REMOTE_HOME="/home/gurbain/private"
REMOTE_BIN_FOLDER="${REMOTE_HOME}/bin"
REMOTE_SRC_FOLDER="${REMOTE_HOME}/src"

RPYC_NAME="rpyc"
PLUMBUM_NAME="plumbum"
NUMPY_NAME="numpy"
MATPLOTLIB_NAME="matplotlib"
PSUTIL_NAME="psutil"
BLENDER_NAME="blender"
XVFB_NAME="xvfb_1.11.4-0ubuntu10.17_amd64"
MODEL_NAME="mouse_locomotion"

RPYC_TAG="v3.3"
PLUMBUM_TAG="v1.6.1"
MODEL_TAG="gabriel"

RPYC_SRC="https://github.com/tomerfiliba/${RPYC_NAME}"
PLUMBUM_SRC="https://github.com/tomerfiliba/${PLUMBUM_NAME}"
MODEL_SRC="https://github.com/HBPNeurorobotics/${MODEL_NAME}"
NUMPY_SRC="https://pypi.python.org/packages/1a/5c/57c6920bf4a1b1c11645b625e5483d778cedb3823ba21a017112730f0a12/numpy-1.11.0.tar.gz#md5=bc56fb9fc2895aa4961802ffbdb31d0b"
MATPLOTLIB_SRC="https://pypi.python.org/packages/8f/f4/c0c7e81f64d5f4d36e52e393af687f28882c53dcd924419d684dc9859f40/matplotlib-1.5.1.tar.gz#md5=f51847d8692cb63df64cd0bd0304fd20"
PSUTIL_SRC="https://pypi.python.org/packages/22/a8/6ab3f0b3b74a36104785808ec874d24203c6a511ffd2732dd215cf32d689/psutil-4.3.0.tar.gz#md5=ca97cf5f09c07b075a12a68b9d44a67d"
BLENDER_BIN="http://download.blender.org/release/Blender2.76/blender-2.76b-linux-glibc211-x86_64.tar.bz2"
XVFB_BIN="${XVFB_NAME}.deb"


# Create a command to execute remotely
echo "[INSTALL PACKAGES] ======== Access Control ======== "
printf "[INSTALL PACKAGES] Enter your password to execute all commands on ${REMOTE}: "
read -s REMOTE_PWD
printf "\n"
REMOTE_CMD="sshpass -p ${REMOTE_PWD} ssh ${REMOTE_USER}@${REMOTE} 'cd ${REMOTE_HOME} && "

# Download package sources
echo "[INSTALL PACKAGES] ======== Downloading source packages ======== "
echo "[INSTALL PACKAGES] Download: ${RPYC_NAME}, ${PLUMBUM_NAME}, ${MODEL_NAME}, ${NUMPY_NAME}, ${MATPLOTLIB_NAME} and ${PSUTIL_NAME}"
eval "${REMOTE_CMD} mkdir -p ${REMOTE_SRC_FOLDER}'"
eval "${REMOTE_CMD} cd ${REMOTE_SRC_FOLDER} && git clone ${RPYC_SRC} && cd ${REMOTE_SRC_FOLDER}/${RPYC_NAME} && git checkout ${RPYC_TAG} '"
eval "${REMOTE_CMD} cd ${REMOTE_SRC_FOLDER} && git clone ${PLUMBUM_SRC} && cd ${REMOTE_SRC_FOLDER}/${PLUMBUM_NAME} && git checkout ${PLUMBUM_TAG} '"
eval "${REMOTE_CMD} cd ${REMOTE_SRC_FOLDER} && git clone ${MODEL_SRC} && cd ${REMOTE_SRC_FOLDER}/${MODEL_NAME} && git checkout ${MODEL_TAG} '"

#eval "${REMOTE_CMD} wget ${NUMPY_SRC} -O ${NUMPY_NAME}.tar.bz2 && mkdir -p ${REMOTE_SRC_FOLDER}/${NUMPY_NAME} && tar -xvf ${NUMPY_NAME}.tar.bz2 -C ${REMOTE_SRC_FOLDER}/${NUMPY_NAME} --strip-components 1 && rm ${NUMPY_NAME}.tar.bz2 '"
#eval "${REMOTE_CMD} wget ${MATPLOTLIB_SRC} -O ${MATPLOTLIB_NAME}.tar.bz2 && mkdir -p ${REMOTE_SRC_FOLDER}/${MATPLOTLIB_NAME} && tar -xvf ${MATPLOTLIB_NAME}.tar.bz2 -C ${REMOTE_SRC_FOLDER}/${MATPLOTLIB_NAME} --strip-components 1 && rm ${MATPLOTLIB_NAME}.tar.bz2 '"
eval "${REMOTE_CMD} wget ${PSUTIL_SRC} -O ${PSUTIL_NAME}.tar.bz2 && mkdir -p ${REMOTE_SRC_FOLDER}/${PSUTIL_NAME} && tar -xvf ${PSUTIL_NAME}.tar.bz2 -C ${REMOTE_SRC_FOLDER}/${PSUTIL_NAME} --strip-components 1 && rm ${PSUTIL_NAME}.tar.bz2 '"

# Install packages
echo "[INSTALL PACKAGES] ======== Installing source packages ======== "
eval "${REMOTE_CMD} cp ${REMOTE_SRC_FOLDER}/${RPYC_NAME}/bin/* ${REMOTE_BIN_FOLDER} '"
eval "${REMOTE_CMD} cd ${REMOTE_SRC_FOLDER}/${RPYC_NAME} && python setup.py install --user '"
eval "${REMOTE_CMD} cd ${REMOTE_SRC_FOLDER}/${PLUMBUM_NAME} &&  python setup.py install --user '"
#eval "${REMOTE_CMD} cd ${REMOTE_SRC_FOLDER}/${NUMPY_NAME} && python setup.py install --user '"
#eval "${REMOTE_CMD} cd ${REMOTE_SRC_FOLDER}/${MATPLOTLIB_NAME} &&  python setup.py install --user '"
eval "${REMOTE_CMD} cd ${REMOTE_SRC_FOLDER}/${PSUTIL_NAME} && python setup.py install --user '"

# Download package binaries
echo "[INSTALL PACKAGES] ======== Downloading binary packages ======== "
eval "${REMOTE_CMD} wget ${BLENDER_BIN} -O ${BLENDER_NAME}.tar.bz2 '"
eval "${REMOTE_CMD} apt-get download xvfb'"

echo "[INSTALL PACKAGES] ======== Installing binary packages ======== "
eval "${REMOTE_CMD} mkdir -p ${REMOTE_BIN_FOLDER} && tar -xvf ${BLENDER_NAME}.tar.bz2 -C ${REMOTE_BIN_FOLDER} --strip-components 1 '"
eval "${REMOTE_CMD} rm ${BLENDER_NAME}.tar.bz2 '"
eval "${REMOTE_CMD} dpkg-deb -x ${XVFB_BIN} ${REMOTE_HOME} '"
eval "${REMOTE_CMD} rm ${XVFB_BIN} '"

#clear $REMOTE_PWD