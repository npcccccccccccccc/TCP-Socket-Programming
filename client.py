import random
import sys
from socket import *
import struct
from time import sleep

BUFSIZE = 1024
SERVER_IP = "127.0.0.1"  # 127.0.0.1本机测试
SERVER_PORT = 20000  # 20000测试端口
SERVER_ADDR = (SERVER_IP, SERVER_PORT)  # 绑定成元组
FILE_NAME = 'test.txt'  # 默认原文件
NEW_FILE_NAME = 'new_test.txt'  # 默认新文件
LMIN = 10
LMAX = 30


# 封装报文
def pack(packet_type, n_or_length, data=None):
    if packet_type == 1:  # Initialization报文
        return struct.pack('!H I', packet_type, n_or_length)
    else :  # request报文
        return struct.pack(f'!H I {n_or_length}s', packet_type, n_or_length, data)


# 解封装报文
def unpack(message, packet_type, length=None):
    if packet_type == 2:  # agree报文
        return struct.unpack('!H', message)
    else:  # answer报文
        return struct.unpack(f'!H I {length}s', message)


# tcp通信
def tcp_client():
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((SERVER_IP, SERVER_PORT))
    with open(FILE_NAME, 'r') as file:  # 读文件
        file_content = file.read()

    n = 0  # 块数
    reverse_content = []  # 每一块数据
    position = 0  # 记录划分位置
    while position < len(file_content):  # 随机划分块
        length = 0
        while length == 0:
            length = random.randint(LMIN, LMAX)  # 随机生成位于[LMIN,LMAX]范围内的长度
        if position + length > len(file_content):
            end_position = len(file_content)
        else:
            end_position = position + length
        content = file_content[position: end_position]
        reverse_content.append(content)
        position += length
        n += 1

    print(f"总块数为：{n}")
    client_socket.send(pack(1, n))  # 发送initialization报文
    message = client_socket.recv(BUFSIZE)
    write_method = 0
    if unpack(message, 2)[0] == 2:  # 收到agree报文
        for i, data in enumerate(reverse_content):
            print(f"第{i + 1}块反转前的文本：{data}")
            client_socket.send(pack(3, len(data), data.encode()))  # 发送request报文
            message = client_socket.recv(BUFSIZE)  # 收到answer报文
            if unpack(message, 4, len(data))[0] == 4:
                reversed_content = unpack(message, 4, len(data))[2].decode().strip(b'\x00'.decode())
                sleep(0.5)
                print(f"第{i + 1}块反转后的文本：{reversed_content}")
                if write_method == 0:  # 第一次覆盖写文件
                    with open(NEW_FILE_NAME, 'w') as new_file:  # 写文件
                        new_file.write(reversed_content)
                    write_method += 1
                else:
                    with open(NEW_FILE_NAME, "r+") as new_file:  # 在开头追加写文件
                        old = new_file.read()
                        new_file.seek(0)
                        new_file.write(reversed_content)
                        new_file.write(old)
    else:
        print("未收到agree报文")
    client_socket.close()


if __name__ == '__main__':
    SERVER_IP = sys.argv[1]
    SERVER_PORT = int(sys.argv[2])
    LMIN = int(sys.argv[3])
    LMAX = int(sys.argv[4])
    FILE_NAME = sys.argv[5]
    NEW_FILE_NAME = sys.argv[6]
    if LMIN == LMAX and LMIN == 0:
        print("LMIN和LMAX不能同时为0")
        exit(0)
    SERVER_ADDR = (SERVER_IP, SERVER_PORT)
    tcp_client()
