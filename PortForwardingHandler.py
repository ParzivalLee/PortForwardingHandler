"""
@filename PortForwarding.py
@author 葛文星
@date 2023-9-17
@encoding utf-8
@lastModify 2023-9-17
@description 端口映射工具
"""
import socket
import threading
import time


class PortForwardingHandler:
    def __init__(self, target_port: int, src_address: tuple):
        """
        端口转发控制器
        :param target_port: 目标端口（计算机将开放这个端口用于监听）
        :param src_address: 源地址（计算机会将数据转发到这个地址）
        """
        # 基础服务器变量
        self.targetHost: str = '0.0.0.0'  # 目标host
        self.targetPort: int = target_port  # 目标端口
        self.srcAddress: tuple = src_address  # 源地址，数据将转发到这里
        # 缓冲区大小
        self.tcpBufferSize: int = 1024  # TCP接收的数据包的大小
        self.udpBufferSize: int = 1024  # UDP接收的数据包的大小

        # 初始化TCP转发服务器
        self.tcpServer: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 初始化UDP转发服务器
        self.udpServer: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.sockets = []  # 全部的套接字
        self.isAlive: bool = True

    def tcpListeningHandler(self) -> None:
        """
        TCP转发监听控制器
        :return: None
        """
        while self.isAlive:
            try:
                client, addr = self.tcpServer.accept()
                self.sockets.append(client)
                src_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sockets.append(src_socket)
                src_socket.connect(self.srcAddress)
                threading.Thread(target=self.tcpResendHandler, args=(src_socket, client)).start()
                threading.Thread(target=self.tcpResendHandler, args=(client, src_socket)).start()
            except OSError:
                break

    def udpListeningHandler(self) -> None:
        """
        UDP转发监听控制器
        :return: None
        """
        while self.isAlive:
            try:
                data, addr0 = self.udpServer.recvfrom(1024)
                self.udpServer.sendto(data, self.srcAddress)
                data, addr1 = self.udpServer.recvfrom(1024)
                self.udpServer.sendto(data, addr0)
            except Exception as e:
                print(e)

    def tcpResendHandler(self, send_socket: socket.socket, recv_socket: socket.socket) -> None:
        """
        TCP数据转发控制器
        :param send_socket: 发送数据的socket
        :param recv_socket: 接收数据的socket
        :return: None
        """
        try:
            s_buffer = recv_socket.recv(1024)
            while s_buffer:
                send_socket.sendall(s_buffer)
                s_buffer = recv_socket.recv(1024)
        except ConnectionError:
            # 出现主机连接错误则断开连接
            if send_socket in self.sockets:
                self.sockets.remove(send_socket)
            if recv_socket in self.sockets:
                self.sockets.remove(recv_socket)
            send_socket.close()
            recv_socket.close()

    def start(self) -> None:
        """
        开启端口转发
        :return: None
        """
        # 初始化TCP转发服务器
        self.tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcpServer.bind((self.targetHost, self.targetPort))
        self.tcpServer.listen()
        # 初始化UDP转发服务器
        self.udpServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpServer.bind((self.targetHost, self.targetPort))

        # 开启服务器
        threading.Thread(target=self.tcpListeningHandler).start()
        threading.Thread(target=self.udpListeningHandler).start()

    def stop(self) -> None:
        """
        关闭端口转发
        :return: None
        该功能存在一定的延迟
        """
        for i in self.sockets:
            i.close()
        self.tcpServer.close()
        self.udpServer.close()
        self.isAlive = False
