Cloud Detours
=============

Cloud Detours is an architecture \ framework that aims on providing support to migrate web application into Cloud Environments.

Building Cloud Detours
----------------------

### **  Environment Setup **

The following components are mandatory to build up Detours:

* [Java][1];
* [Apache Python][2];
* [Apache Libcloud][3];
* [ZeroMQ][4] and its bidings to Java \ Python;
* [Gradle][5].

#### Installing Java
You can use any method you want to install java. I've installed java8 as described in [Webupd8][6].

#### Apache Python
I'm currently using Python3 installed from Ubuntu 14.04 canonical sources.

#### Apache Libcloud
You can have this through PIP3 or you can also install it through Ubuntu sources. I just installed python3-libcloud .

#### ZeroMQ and Java Bindings
You can install it from Ubuntu sources (libzmq3 and libzmq3-dev) or download the tarball from [ZMQ download site][7].

If you're using the tarball just follow the instructions from INSTALL file and you're going to get it good.

In order to have Java bindings installed, just download the sources and follow the usual way to compile it: autogen, configure, make and make install.


#### Gradle
Download and extract gradle bundle. After that, create an environment variable GRADLE_HOME and make Gradle available in path:

> GRADLE_HOME=$HOME/apps/gradle

> PATH=$PATH:$GRADLE_HOME/bin

You can load _.profile_ and check gradle version:

> $ . .profile

> $ gradle -v


[1]: http://www.oracle.com/br/technologies/java/overview/index.html 	"Java"
[2]: https://www.python.org/ 											"Python"
[3]: https://libcloud.apache.org/										"Apache Libcloud"
[4]: http://zeromq.org/												"ZeroMQ"
[5]: http://gradle.org "Gradle"
[6]: http://www.webupd8.org/2012/09/install-oracle-java-8-in-ubuntu-via-ppa.html "Webupd8"
[7]: http://download.zeromq.org/zeromq-4.0.4.tar.gz "ZMQ 4.0.4 download"
