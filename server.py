#!/usr/bin/python3

import asyncio


async def read_headers(reader):
    bytes = await reader.readline()
    line = bytes.decode('UTF-8')
    headers = []
    while line != '\r\n':
        headers.append(line.rsplit('\r\n')[0])
        bytes = await reader.readline()
        line = bytes.decode('UTF-8')
    print(headers)
    return headers


async def connected(reader, writer):
    # m1
    m1_req = b'OPTIONS * RTSP/1.0\r\n\r\n'
    writer.write(m1_req)
    print(m1_req)
    await writer.drain()
    headers = await read_headers(reader)
    if not 'RTSP/1.0 200 OK' in headers:
        return
    # m2
    headers = await read_headers(reader)
    if not 'OPTIONS * RTSP/1.0' in headers:
        return
    m2_resp = b'RTSP/1.0 200 OK\r\n\r\n'
    writer.write(m2_resp)
    print(m2_resp)
    await writer.drain()

    # finished
    writer.close()


async def main():
    server = await asyncio.start_server(connected, '127.0.0.1', 4328)
    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')
    async with server:
        await server.serve_forever()

asyncio.run(main())
