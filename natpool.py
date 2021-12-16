import asyncio, logging, multiprocessing, ssl, os, sys, argparse

from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def __copy_data_thread(reader, writer):
    try:
        while True:
            chunk = await reader.read(102400)
            if not chunk:
                break
            writer.write(chunk)
            await writer.drain()
    except BaseException as e:
        pass


async def on_connection(reader, writer, remote_ip, remote_port, prot, sslau, loop):
    addr = writer.get_extra_info('peername')
    remoteIP = "unknow"
    c_reader, c_writer = (None, None)
    try:
        prot = prot.lower().strip()
        if prot == "ssl":
            _sc = ssl.create_default_context()
            _sc.check_hostname = int(sslau) == 1
        elif prot == "tcp":
            _sc = None
        try:
            c_reader, c_writer = await asyncio.open_connection(host=remote_ip, port=remote_port, ssl=_sc,
                                                               loop=loop)
        except BaseException as ex:
            logger.error(
                "localIP:{},remoteURL:{},remoteIP:{},There was an error connecting to the forwarding server".format(
                    addr, remote_ip, remoteIP))
            return

        remoteIP = c_writer.get_extra_info('peername')
        logger.info("A new client is connecting.localIP:{},remoteURL:{},remoteIP:{}".format(addr, remote_ip, remoteIP))
        dltasks = set()
        dltasks.add(asyncio.ensure_future(__copy_data_thread(c_reader, writer)))
        dltasks.add(asyncio.ensure_future(__copy_data_thread(reader, c_writer)))
        dones, dltasks = await asyncio.wait(dltasks, return_when=asyncio.FIRST_COMPLETED)
    except BaseException as ex:
        logger.error(
            "localIP:{},remoteURL:{},remoteIP:{},An unknown error occurred on the server with details as follows:".format(
                addr, remote_ip, remoteIP, str(ex)))
    finally:
        def cl(_stream):
            for item in _stream:
                try:
                    if item is not None and hasattr(item, "close"):
                        item.close()
                except BaseException as ex:
                    logger.debug(str(ex))

        cl([reader, writer, c_reader, c_writer])

        logger.info("Connection closed.localIP:{},remoteURL:{},remoteIP:{}".format(addr, remote_ip, remoteIP))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        usage="python natpool.py --laddr 0.0.0.0 --lport 6688 --lcrt ssl.crt --lkey ssl.key --caddr jiaoshiyao.xyz --cprot ssl --cport 9000 --lprot ssl --csslau")
    parser.description = ''
    parser.add_argument("--laddr", help="Force specific IP to bind() to when listening", type=str, required=True)
    parser.add_argument("--lprot", help="", type=str, choices=["tcp", "ssl"], required=True)
    parser.add_argument("--lcrt", help="", type=str, default="", required=False)
    parser.add_argument("--lkey", help="", type=str, default="", required=False)
    parser.add_argument("--lport", help="", type=int, default=0, required=True)

    parser.add_argument("--caddr", help="", type=str, default="", required=True)
    parser.add_argument("--csslau", help="", action='store_true', required=False)
    parser.add_argument("--cprot", help="", type=str, choices=["tcp", "ssl"], required=True)
    parser.add_argument("--cport", help="", type=int, default=0, required=True)

    args = parser.parse_args()
    laddr, lprot, lcrt, lkey, lport = (args.laddr, args.lprot.lower(), args.lcrt, args.lkey, args.lport)
    caddr, csslau, cprot, cport = (args.caddr, args.csslau, args.cprot.lower(), args.cport)

    if lprot == "ssl":
        sc = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        lcrt = lcrt if os.path.exists(lcrt) else (
            os.path.basename(lcrt) if os.path.exists(os.path.basename(lcrt)) else None)
        lkey = lkey if os.path.exists(lkey) else (
            os.path.basename(lkey) if os.path.exists(os.path.basename(lkey)) else None)
        if not lcrt:
            logger.error("parameter --lcrt file '{}' not found".format(lcrt))
            sys.exit()
        if not lkey:
            logger.error("parameter --lkey file '{}' not found".format(lkey))
            sys.exit()

        sc.load_cert_chain(lcrt, lkey)
    elif lprot == "tcp":
        sc = None

    loop = asyncio.get_event_loop()
    executor = ThreadPoolExecutor(max_workers=multiprocessing.cpu_count())

    loop.set_default_executor(executor)
    coro = asyncio.start_server(lambda r, w: on_connection(r, w, caddr, cport, cprot, csslau, loop), laddr,
                                lport,
                                ssl=sc, loop=loop)
    server = loop.run_until_complete(coro)
    log_info = server.sockets[0].getsockname()
    logger.info("Serving on {}".format(log_info))
    try:
        loop.run_forever()
    except BaseException as ex:
        pass
    logger.info("Serving stop {}".format(log_info))
