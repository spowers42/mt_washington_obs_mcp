from httpx import AsyncClient, Response, codes

BASE_URL = "https://mountwashington.org"

class WeatherClient:
    def __init__(self) -> None:
        self.client = AsyncClient(base_url=BASE_URL, timeout=30)
    
    async def get_weather(self) -> dict:
        url = '/uploads/json/weather.JSON'
        response = await self._get(url)
        return response.json()
    
    async def get_outlook(self) -> dict:
        url = '/uploads/json/outlook.JSON'
        response = await self._get(url)
        return response.json()
    
    async def get_f6_pdf(self, year: int, month:int) -> bytes:
        url = f'/uploads/pdf/forms/{year}/{month:02d}.pdf'
        response = await self._get(url)
        return response.content
    
    async def close(self) -> None:
        await self.client.aclose()
    
    async def _get(self, url: str) -> Response:
        response = await self.client.get(url)
        if response.status_code != codes.OK:
            response.raise_for_status()
        return response 
    
    async def __aenter__(self) -> WeatherClient:
        return self
    
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> None:
        await self.close()