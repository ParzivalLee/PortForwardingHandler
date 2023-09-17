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
        :param target_port: 目标端口
        :param src_address: 源地址
        """
        self.targetPort: int = target_port
        self.srcAddress: tuple = src_address
        self.server: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('0.0.0.0', self.targetPort))
        self.server.listen()
        self.sockets = []  # 全部的套接字
        self.isAlive: bool = True

    def listenHandler(self):
        while self.isAlive:
            try:
                client, addr = self.server.accept()
                self.sockets.append(client)
                src_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sockets.append(src_socket)
                src_socket.connect(self.srcAddress)
                threading.Thread(target=self.resendHandler, args=(src_socket, client)).start()
                threading.Thread(target=self.resendHandler, args=(client, src_socket)).start()
            except OSError:
                break

    def resendHandler(self, send_socket: socket.socket, recv_socket: socket.socket) -> None:
        """
        数据转发控制器
        :param send_socket: 发送数据的socket
        :param recv_socket: 接收数据的socket
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

    def start(self):
        threading.Thread(target=self.listenHandler).start()

    def stop(self):
        for i in self.sockets:
            i.close()
        self.server.close()
        self.isAlive = False
