import json
from tornado import web
from jupyterhub.apihandlers import APIHandler, default_handlers


class BatchSpawnerAPIHandler(APIHandler):
    @web.authenticated
    def post(self):
        """POST set user spawner data"""
        if hasattr(self, "current_user"):
            # Jupyterhub compatability, (september 2018, d79a99323ef1d)
            user = self.current_user
            spawner = user.spawner
            data = self.get_json_body()
            port = int(data.get('port', 0))
            try:
                from wrapspawner import WrapSpawner
                if isinstance(spawner, WrapSpawner):
                    spawner = spawner.child_spawner
            except:
                self.log.info('Exception finding wrapped spawner')
                import traceback
                traceback.print_exc()
            spawner.port = port
        else:
            # Previous jupyterhub, 0.9.4 and before.
            user = self.get_current_user()
        token = self.get_auth_token()
        spawner = None
        for s in user.spawners.values():
            if s.api_token == token:
                spawner = s
                break
        data = self.get_json_body()
        for key, value in data.items():
            if hasattr(spawner, key):
                setattr(spawner, key, value)
        self.finish(json.dumps({"message": "BatchSpawner data configured"}))
        self.set_status(201)


default_handlers.append((r"/api/batchspawner", BatchSpawnerAPIHandler))
