"""
Async UDP Gateway Server for Receiving 16-Byte Telemetry Packets from Pit Gateway.
"""
from __future__ import annotations

import asyncio
from typing import Callable, Optional

from app.core.logging_config import get_logger
from app.telemetry.packet_decoder import PacketDecoder, DecodedTelemetryPacket

logger = get_logger("udp_gateway")


class TelemetryUDPServerProtocol(asyncio.DatagramProtocol):
    def __init__(self, on_packet_received: Callable[[DecodedTelemetryPacket], None]):
        self.on_packet_received = on_packet_received
        self.transport: Optional[asyncio.DatagramTransport] = None
        self.packet_count = 0
        self.error_count = 0

    def connection_made(self, transport: asyncio.DatagramTransport):
        self.transport = transport
        logger.info("Telemetry UDP listener bound and ready.")

    def datagram_received(self, data: bytes, addr: tuple[str, int]):
        if len(data) != PacketDecoder.PACKET_SIZE:
            self.error_count += 1
            return

        try:
            packet = PacketDecoder.decode(data)
            if packet.is_valid_checksum:
                self.packet_count += 1
                self.on_packet_received(packet)
            else:
                self.error_count += 1
        except Exception as e:
            self.error_count += 1
            logger.debug(f"Failed to decode packet from {addr}: {e}")

    def error_received(self, exc: Exception):
        logger.error(f"UDP listener socket error: {exc}")


async def start_udp_gateway(host: str, port: int, callback: Callable[[DecodedTelemetryPacket], None]):
    """Launch background UDP listener."""
    loop = asyncio.get_running_loop()
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: TelemetryUDPServerProtocol(callback),
        local_addr=(host, port),
    )
    logger.info(f"UDP Telemetry Gateway listening on {host}:{port}")
    return transport, protocol

