class LeagueStorage(Protocol):
    """
    抽象接口（语义用，不走 import）
    """

    def load_league(self, league: str) -> List[Dict[str, Any]]:
        ...

    def save_league(self, league: str, data: List[Dict[str, Any]]) -> None:
        ...


class OSSLeagueStorage:
    """
    OSS 实现
    依赖：
      - client
      - oss
      - json
    由 handler 注入
    """

    def __init__(self, client, bucket: str):
        self.client = client
        self.bucket = bucket

    def _key(self, league: str) -> str:
        return f"leagues/{league}.json"

    def load_league(self, league: str) -> List[Dict[str, Any]]:
        resp = self.client.get_object(
            oss.GetObjectRequest(
                bucket=self.bucket,
                key=self._key(league)
            )
        )
        return json.loads(resp.body.read().decode("utf-8"))

    def save_league(self, league: str, data: List[Dict[str, Any]]) -> None:
        self.client.put_object(
            oss.PutObjectRequest(
                bucket=self.bucket,
                key=self._key(league),
                body=json.dumps(
                    data,
                    ensure_ascii=False,
                    indent=2
                ).encode("utf-8")
            )
        )
