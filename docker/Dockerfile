FROM debian:trixie
RUN apt-get update -y \
&& apt-get -y upgrade \
&& apt-get -y install python3-sympy python3-pip isympy3 curl git ipython3 python3-pyqt5 python3-pyqt5.qsci python3-pyqt5.qtsvg
WORKDIR /root/geophar
# Rebuild last layer only if commits changed.
ADD "https://api.github.com/repos/wxgeo/geophar/commits?per_page=1" latest_commit
RUN git clone https://github.com/wxgeo/geophar.git
