from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, List

import transmissionrpc as trpc


class TorrentStatus(Enum):
    STOPPED = auto()
    SEEDING = auto()
    CHECKING = auto()
    DOWNLOADING = auto()
    UNKNOWN = auto()

@dataclass
class Torrent:
    name: str
    status: TorrentStatus
    hashStr: str

def str_to_torrent_status(status: str) -> TorrentStatus:
    if status == 'stopped':
        return TorrentStatus.STOPPED
    elif status == 'seeding':
        return TorrentStatus.SEEDING
    elif status == 'checking':
        return TorrentStatus.CHECKING
    elif status == 'downloading':
        return TorrentStatus.DOWNLOADING
    else:
        return TorrentStatus.UNKNOWN

def torrent_status_to_emoji(status: TorrentStatus) -> str:
    if status == TorrentStatus.CHECKING:
        return '🔎'
    elif status == TorrentStatus.SEEDING:
        return '🔋'
    elif status == TorrentStatus.STOPPED:
        return '⛔'
    elif status == TorrentStatus.DOWNLOADING:
        return '⏳'
    elif status == TorrentStatus.UNKNOWN:
        return '❓'

class TransmissionConnection:
    def __init__(self, address='localhost', login=None, password=None, port=9091):
        try:
            if login and password:
                self._conn: trpc.Client = trpc.Client(address=address, user=login, password=password, port=port)
            else:
                self._conn: trpc.Client = trpc.Client(address=address, port=port)
            self._torrents, self._torrents_dict = self.get_torrents()
        except Exception as e:
            raise e 

    def get_torrents(self) -> (List[Torrent], Dict[str, Torrent]):
        l = [Torrent(t.name, str_to_torrent_status(t.status), t.hashString) for t in self._conn.get_torrents()]
        d = {le.hashStr: le for le in l}
        return l, d

    def _refresh_torrents(self):
        self._torrents, self._torrents_dict = self.get_torrents()

    def add_torrent(self, url):
        self._conn.add_torrent(url)
    
    def stop_torrent(self, torrent: Torrent):
        self._conn.stop_torrent(torrent.hashStr)

    def start_torrent(self, torrent: Torrent):
        self._conn.start_torrent(torrent.hashStr)
        
    def del_torrent(self, torrent: Torrent, delete_data=False):
        self.stop_torrent(torrent)
        self._conn.remove_torrent(torrent.hashStr, delete_data=delete_data)
    
    def __getitem__(self, key):
        self._refresh_torrents()
        if isinstance(key, int):
            return self._torrents[key]
        if isinstance(key, str):
            return self._torrents_dict[key]
    
    def __len__(self):
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
