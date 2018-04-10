from rest_framework.renderers import JSONRenderer


class RespRenderer(JSONRenderer):

    def render(self, data, *args, **kwargs):
        data = {
            '_status': {
                'code': 200,
                'message': 'success'
            },
            '_links': {
                'self': ''
            },
            'results': data
        }
        return super(RespRenderer, self).render(data, *args, **kwargs)

