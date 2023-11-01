from aiohttp import web
from backend.server import file_storage
from backend.core import exceptions


class FileView(web.View):
    async def get(self) -> web.StreamResponse:
        id = self.request.match_info.get('id')
        if not id:
            raise exceptions.ParameterPathWrong

        response = web.StreamResponse(
            headers={
                "Content-Type": "application/octet-stream",
                "Content-Disposition": f"attachment; filename=text.txt"
            }
        )

        await response.prepare(self.request)

        async for chunk in file_storage.get(id):
            await response.write(chunk)

        await response.write_eof()
        return response


    # async def post(self):
    #     return await post_resp(self.request)