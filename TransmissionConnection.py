from dataclasses import dataclass
from enum import Enum
from typing import Self

import transmissionrpc as trpc


class TorrentStatus(Enum):
    STOPPED = "stopped"
    SEEDING = "seeding"
    CHECKING = "checking"
    DOWNLOADING = "downloading"
    UNKNOWN = "unknown"

    def to_emoji(self) -> str:
        if self is TorrentStatus.CHECKING:
            return "🔎"
        elif self is TorrentStatus.SEEDING:
            return "🔋"
        elif self is TorrentStatus.STOPPED:
            return "⛔"
        elif self is TorrentStatus.DOWNLOADING:
            return "⏳"
        else:
            return "❓"

    @classmethod
    def from_str(cls, status: str) -> Self:
        try:
            return cls(status)
        except ValueError:
            return cls("unknown")


@dataclass
class Torrent:
    name: str
    status: TorrentStatus
    hashStr: str


class TransmissionConnection:
    def __init__(
        self,
        address: str = "localhost",
        login: str | None = None,
        password: str | None = None,
        port: int = 9091,
    ):
        try:
            if login is not None and password is not None:
                self._conn: trpc.Client = trpc.Client(
                    address=address, user=login, password=password, port=port
                )
            else:
                self._conn: trpc.Client = trpc.Client(address=address, port=port)
            self._torrents, self._torrents_dict = self.get_torrents()
        except Exception as e:
            raise e

    def get_torrents(self) -> tuple[list[Torrent], dict[str, Torrent]]:
        torrents = [
            Torrent(t.name, TorrentStatus.from_str(t.status), t.hashString)
            for t in self._conn.get_torrents()
        ]
        torrents_dict = {le.hashStr: le for le in torrents}
        return torrents, torrents_dict

    def _refresh_torrents(self):
        self._torrents, self._torrents_dict = self.get_torrents()

    def add_torrent(self, url: str) -> Torrent:
        torrent = self._conn.add_torrent(url)
        return Torrent(
            name=torrent.name, status=torrent.status, hashStr=torrent.hashString
        )

    def stop_torrent(self, torrent: Torrent):
        self._conn.stop_torrent(torrent.hashStr)

    def start_torrent(self, torrent: Torrent):
        self._conn.start_torrent(torrent.hashStr)

    def del_torrent(self, torrent: Torrent, delete_data=False):
        self.stop_torrent(torrent)
        self._conn.remove_torrent(torrent.hashStr, delete_data=delete_data)

    def __getitem__(self, key) -> Torrent:
        self._refresh_torrents()
        if isinstance(key, int):
            return self._torrents[key]
        elif isinstance(key, str):
            return self._torrents_dict[key]
        else:
            raise ValueError(f"Unknown type of key: {type(key)}")

    def __len__(self) -> int:
        self._refresh_torrents()
        return len(self._torrents)

    def __delitem__(self, key):
        self._refresh_torrents()
        self.del_torrent(key)

    def __iter__(self):
        self._refresh_torrents()
        return iter(self._torrents)

    def __list__(self):
        self._refresh_torrents()
        return self._torrents
