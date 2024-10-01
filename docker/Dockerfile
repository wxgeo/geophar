FROM debian:trixie
RUN apt-get update -y \
&& apt-get -y upgrade \
&& apt-get -y install python3-sympy python3-pip isympy3 curl git ipython3 python3-pyqt5 python3-pyqt5.qsci python3-pyqt5.qtsvg
WORKDIR /root/geophar
RUN git clone https://github.com/wxgeo/geophar.git
