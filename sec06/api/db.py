from fastapi import Request


def get_system(request: Request):
    return request.app.state.system
