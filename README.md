# natpool
Wrap a TCP or SSL stream into a new TCP or SSL stream

该项目专门为了中国大陆地区的人无法连接到清退的挖矿矿池而准备的项目，如果你需要使用中转服务器中转你的挖矿数据，那么你可以尝试选择这个项目。
### 安装
1. 可用于中转的服务器(推荐香港节点)
2. 将系统改为debian 9.0以上，或者ubuntu 20版本以上
3. 在系统中安装docker
docker官方的一键安装脚本：
```shell
curl -sSL https://get.docker.com/ | sh
```
阿里云的一键安装脚本：
```shell
curl -sSL http://acs-public-mirror.oss-cn-hangzhou.aliyuncs.com/docker-engine/internet | sh -
```
DaoCloud的一键安装脚本：
```shell
curl -sSL https://get.daocloud.io/docker | sh
```
5. docker安装完成后，可以直接用命令启动
```shell
docker run -ti --restart unless-stopped --name natpool -d -v /root/ssl.crt:/code/ssl.crt -v /root/ssl.key:/code/ssl.key -p 6688:6688 natpool/natpool:latest --laddr 0.0.0.0 --lport 6688 --lprot ssl --lcrt /root/ssl.crt --lkey /root/ssl.key --caddr eth.f2pool.com --cprot tcp --cport 8008 --csslau
```
 * 其中`docker run -ti --restart unless-stopped --name natpool -d`是启用一个后台的docker容器，名字是natpool，这里的natpool可以自行修改
 * `-v /root/ssl.crt:/code/ssl.crt`是将系统中的`/root/ssl.crt`文件，映射为容器中的`/code/ssl.crt`，这里后面的内容必须和下面的`--lcrt /root/ssl.crt`的文件路径一样
 * `-v /root/ssl.key:/code/ssl.key`是将系统中的`/root/ssl.key`文件，映射为容器中的`/code/ssl.key` 这2个文件是启用ssl的时候的证书文件，这里后面的内容必须和下面的`--lcrt /root/ssl.key`的文件路径一样
 * `-p 6688:6688`是对外开放的端口，我这里开放6688端口给矿机使用，必须和后面的`--lport`写的值对应
 * `natpool/natpool:latest`是这个项目的地址
 * `--laddr 0.0.0.0` 是绑定本机的哪个IP对外提供服务，这里绑定了所有的IP，可以固定这么写
 * `--lport 6688` 是对外提供的端口的地址，必须和上面的`-p 6688:6688`一样
 * `--lprot ssl` 是对外提供的协议类型，支持tcp、ssl，tcp是不加密的明文格式，ssl是通过证书加密的格式，如果设置为ssl，那么`--lcrt`和`--lkey`不能为空
 * `--lcrt /root/ssl.crt` 是容器内的证书文件路径
 * `--lkey /root/ssl.key` 是容器内的证书文件路径
 * `--caddr eth.f2pool.com` 你需要中转的矿池的地址
 * `--cprot tcp`是你需要中转的矿池的协议，如果你使用了tcp端口，这里设置为tcp，如果你使用了ssl端口这里设置为ssl，推荐使用ssl的端口
 * `--cport 8008` 这里是你需要中转矿池的端口，需要配合`--cprot`一起使用
 * `--csslau` 这个设置只在`--cprot`为ssl时生效，代表是否检查证书的有效性


### 查看运行日志
```shell
docker logs -f -tail 20 natpool
```
### 转发f2pool.com:8008到本机0.0.0.0:6688上，并且开启ssl的命令(请自行将crt和key证书文件上传到/root目录下)
```shell
docker stop natpool
docker rm natpool
docker run -ti --restart unless-stopped --name natpool -d -v /root/ssl.crt:/code/ssl.crt -v /root/ssl.key:/code/ssl.key -p 6688:6688 natpool/natpool:latest --laddr 0.0.0.0 --lport 6688 --lprot ssl --lcrt /root/ssl.crt --lkey /root/ssl.key --caddr eth.f2pool.com --cprot tcp --cport 8008 --csslau
```

### 转发f2pool.com:6688到本机0.0.0.0:9000上，无ssl加密的创建命令
```shell
docker stop natpool
docker rm natpool
docker run -ti --restart unless-stopped --name natpool -d -p 9000:9000 natpool/natpool:latest --laddr 0.0.0.0 --lport 9000 --lprot tcp --caddr eth.f2pool.com --cprot tcp --cport 6688
```

### 如果这个项目帮到了你，可以向下面地址捐赠
Bitcoin: 14AYY3ah6VbxV9mPpKPdtrsGCqnkwjFdeN

Ethereum: 0xb3f1e1dec11587348590e9a57d5eb191794c1066

WX: ![image](https://github.com/notchampions/natpool/blob/main/pic/vx1.jpg)
