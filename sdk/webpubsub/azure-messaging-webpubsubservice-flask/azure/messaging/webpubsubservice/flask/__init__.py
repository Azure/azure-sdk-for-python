from functools import wraps
from flask import request, make_response, session, g, Response, current_app

class EventHandler:
  def __init__(self, app):
    self._app = app

  def abuse_protection_validation(self, endpoints=None):
    if isinstance(endpoints, str):
      endpoints = [endpoints]
    
    def abuse_protection_validation_internal(func):
      app = self._app
      @wraps(func)
      def decorator(*args, **kwargs):
        origin = request.headers.get('WebHook-Request-Origin')
        if request.method != 'OPTIONS' or origin is None:
          return func(*args, **kwargs)
        
        res = make_response()
        if origin in endpoints or '*' in endpoints:
          res.status_code = 200
          res.headers.add_header('WebHook-Allowed-Origin', ', '.join(endpoints))
        else:
          res.status_code = 401
        
        kwargs['res'] = res
        return func(*args, **kwargs)

      return decorator
    return abuse_protection_validation_internal

  