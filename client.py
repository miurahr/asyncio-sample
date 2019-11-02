import asyncio

class AsyncRTSPClient:

    def __init__(self, server, port):
        self.server = server
        self.port = port
        self.reader = None
        self.writer = None

    async def read_headers(self):
        bytes = await self.reader.readline()
        line = bytes.decode('UTF-8')
        # print(":".join("{:02x}".format(ord(c)) for c in line))
        headers = []
        while line != '\r\n':
            headers.append(line.rsplit('\r\n')[0])
            bytes = await self.reader.readline()
            line = bytes.decode('UTF-8')
        print(headers)
        return headers

    async def connect(self):
        print('start connection')
        self.reader, self.writer = await asyncio.open_connection(self.server, self.port)

        # message #1 server -> client
        headers = await self.read_headers()
        if not 'OPTIONS * RTSP/1.0' in headers:
            return False
        m1_resp = b'RTSP/1.0 200 OK\r\nCSeq: 1\r\nPublic: org.wfa.wfd1.0, GET_PARAMETER, SET_PARAMETER\r\n\r\n'
        self.writer.write(m1_resp)
        print(m1_resp)
        await self.writer.drain()

        # message #2 client -> sever
        m2_req = b'OPTIONS * RTSP/1.0\r\nCSeq: 100\r\nRequire: org.wfa.wfd1.0\r\n\r\n'
        self.writer.write(m2_req)
        print(m2_req)
        await self.writer.drain()
        headers = await self.read_headers()
        if not 'RTSP/1.0 200 OK' in headers:
            return False

        # finished
        return True

    async def finish(self):
        if self.writer is not None:
            self.writer.close()
            await self.writer.wait_closed()


async def main():
    client = AsyncRTSPClient('localhost', 4328)
    result = await client.connect()
    if not result:
        print('fails to connect.')
    await client.finish()


asyncio.run(main())
