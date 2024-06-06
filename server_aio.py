from concurrent.futures import ProcessPoolExecutor
from socket import *
import struct


BUFSIZE = 1024
SERVER_IP = "192.168.161.128"  # 127.0.0.1本机测试/192.168.161.128 guest os
SERVER_PORT = 20000  # 20000测试端口
SERVER_ADDR = (SERVER_IP, SERVER_PORT)  # 绑定成元组
setdefaulttimeout(30)  # 设置全局超时时间30s
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
def tcp_client(client_socket, client_address):
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
                clientAddrList.remove((client_socket, client_address))
                break
    client_socket.close()  # 关闭该client的连接
    print(f"correct disconnect from {client_address}")


if __name__ == '__main__':
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(SERVER_ADDR)
    server_socket.listen(CLIENT_NUM)
    print("wait connect...")
    clientAddrList = []
    pool = ProcessPoolExecutor(CLIENT_NUM)  # CLIENT_NUM个进程一直服务
    while True:
        try:
            client_socket, client_address = server_socket.accept()  # 接收连接
        except:  # 超时退出阻塞状态
            print("长时间未收到信息，关闭连接")
            server_socket.close()
            break
        print(f"correct connect from {client_address}")
        clientAddrList.append((client_socket, client_address))
        pool.submit(tcp_client, client_socket, client_address)  # 异步提交任务