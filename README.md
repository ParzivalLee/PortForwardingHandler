# 端口转发控制器 PortForwardingHandler
## 使用说明 Introduction for use
### example
```python
from PortForwardingHandler import PortForwardingHandler
pfh = PortForwardingHandler(8080, ('192.168.1.110', 80))
pfh.start()  # 该方法将开启端口转发 This method will open the port-forwarding
# 现在你再访问本地的8080端口将转到192.168.1.110:80
# now you can reach 192.168.1.110:80 by 127.0.0.1:8080
pfh.stop()  # 这个方法将关闭端口转发 This method is for close
```