import select
from socket import *
import struct


BUFSIZE = 1024
SERVER_IP = "192.168.161.128"  # 127.0.0.1本机测试/192.168.161.128 guest os
SERVER_PORT = 20000  # 20000测试端口
SERVER_ADDR = (SERVER_IP, SERVER_PORT)  # 绑定成元组
timeouts = 30  # 设置select超时时间30s
CLIENT_NUM = 5  # 允许同时连接的client数量


# 封装报文
def pack(packet_type, n_or_length=None, data=None):
    if packet_type == 2:  # agree报文
        return struct.pack('!H', packet_type)
    else:  # answer报文
        return struct.pack(f'!H I {n_or_length}s', packet_type, n_or_length, data)


# 解封装报文
def unpack(message, packet_type, length=None):
    if packet_type == 1:  # Initialization报文
        return struct.unpack('!H I', message)
    else:  # request报文
        if length is None:
            return struct.unpack(f'!H I', message[0:6])
        return struct.unpack(f'!H I {length}s', message)


# tcp通信
def tcp_client(client_socket):
    cnt = 0  # 当前块数
    n = 0  # 总块数
    flag = 0  # 进入数据传输标志
    while True:
        try:
            message = client_socket.recv(BUFSIZE)
            if flag == 0:  # 收到Initialization报文
                n = unpack(message, 1)[1]  # 记录总块数
                client_socket.send(pack(2))  # 发送agree报文
                flag = 1
            else:   # 收到request报文
                length = unpack(message, 3)[1]  # 数据长度
                content = unpack(message, 3, length)[2].decode().strip(b'\x00'.decode())  # 需要反转的数据
                reversed_content = content[::-1]  # 反转
                client_socket.send(pack(4, length, reversed_content.encode()))  # 发送answer报文
                cnt += 1
                if cnt == n:
                    break
        except error as e:
            if e.errno == 10035:
                continue  # 跳过操作阻塞的错误
            else:
                print(f"Error: {e}")
                break


if __name__ == '__main__':
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(SERVER_ADDR)
    server_socket.listen(CLIENT_NUM)
    server_socket.setblocking(False)
    print("wait connect...")

    inputs = [server_socket]  # 初始输入列表包含服务器套接字
    while True:
        try:
            readable, writeable, exceptional = select.select(inputs, [], inputs, timeouts)  # select监控文件描述符的可读、可写和异常状态
            if not(readable or writeable or exceptional):  # 超时则退出阻塞状态，避免长期停留在阻塞状态
                print("长时间未收到信息，关闭连接")
                server_socket.close()
                break
            for read_socket in readable:
                if read_socket is server_socket:
                    client_socket, client_address = server_socket.accept()
                    client_socket.setblocking(False)  # 设置客户端套接字为非阻塞模式
                    inputs.append(client_socket)  # 将客户端套接字加入inputs列表
                    print(f"correct connect from {client_address}")
                else:
                    tcp_client(read_socket)  # 处理客户端连接
                    print(f"correct disconnect from {read_socket.getpeername()}")
                    read_socket.close()

            for exception_socket in exceptional:
                inputs.remove(exception_socket)  # 从inputs列表中移除异常的套接字
                exception_socket.close()
        except ValueError as e:
            for erroe_socket in inputs:
                if erroe_socket.fileno() < 0:  # 如果文件描述符为负数
                    inputs.remove(erroe_socket)  # 从inputs列表中移除该套接字