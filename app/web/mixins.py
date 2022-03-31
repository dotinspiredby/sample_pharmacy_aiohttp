from aiohttp.abc import StreamResponse
from aiohttp.web_exceptions import HTTPUnauthorized


class AuthRequiredMixin:
    async def _iter(self) -> StreamResponse:
        if not getattr(self.request, "admin", None):
            raise HTTPUnauthorized
        return await super(AuthRequiredMixin, self)._iter()


class AuthRequiredMixinClient:
    async def _iter(self) -> StreamResponse:
        if not getattr(self.request, "client", None):
            raise HTTPUnauthorized
        return await super(AuthRequiredMixinClient, self)._iter()

