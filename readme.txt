TCP Socket Programming

1. Environments
python=3.9

2. Preparation
client:
import random
import sys
from socket import *
import struct
from time import sleep

server_nio:
import select
from socket import *
import struct

server_io-multiplexing:
import selectors
from socket import *
import struct

server_aio:
from concurrent.futures import ProcessPoolExecutor
from socket import *
import struct

server修改常量SERVER_IP为guest的ip

3. Running
client在命令行输入SERVER_IP、SERVER_PORT、LMIN、LMAX、FILE_NAME、NEW_FILE_NAME
eg：python client.py 192.168.161.128 20000 10 30 test.txt new_test.txt (host os)

nio —— python server_nio.py (guest os)
io多路复用 —— python server_io-multiplexing.py (guest os)
aio —— python server_aio.py (guest os)