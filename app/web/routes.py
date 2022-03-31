from aiohttp.web_app import Application


def setup_routes(app: Application):
    from app.admin.routes import setup_routes as admin_setup_routes
    from app.pharmacy.routes import setup_routes as pharma_setup_routes

    admin_setup_routes(app)
    pharma_setup_routes(app)
