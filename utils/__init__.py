from django.conf import settings
from django.apps import apps
from django.core.urlresolvers import reverse
from TileStache import parseConfig
from TileStache.Config import _parseConfigLayer
from caching.models import G3WCachingLayer

tilestache_cfg = None


class TilestacheConfig(object):

    config_dict = dict()

    def __init__(self, tilestache_config_file):

        self.cache_dict = self.init_cache_dict()
        self.config_dict.update({'cache': self.cache_dict})
        self.config = parseConfig(self.config_dict)
        self.init_layers()

    def init_cache_dict(self):

        if settings.TILESTACHE_CACHE_TYPE == 'Disk':
            return {
                'name': 'Disk',
                'path': getattr(settings, 'TILESTACHE_CACHE_DISK_PATH', 'tmp/tilestache_g3wsuite'),
                'umask': getattr(settings, 'TILESTACHE_CACHE_DISK_UMASK', '0000')
            }
        else:
            return {
                'name': 'Test'
            }

    def init_layers(self):
        """
        Add layers to tilestache config obj on startup
        :return:
        """

        # get caching layers activated
        caching_layers = G3WCachingLayer.objects.all()
        for caching_layer in caching_layers:
            self.add_layer(str(caching_layer.app_name + str(caching_layer.layer_id)), caching_layer)

    def build_layer_dict(self, caching_layer):

        #get layer object
        Layer = apps.get_app_config(caching_layer.app_name).get_model('layer')
        layer = Layer.objects.get(pk=caching_layer.layer_id)

        # build template
        base_tamplate = reverse('ows', kwargs={
            'group_slug': '0',
            'project_type': str(caching_layer.app_name),
            'project_id': str(layer.project.pk)
        })

        # build dict
        layer_dict = {
            'provider': {
                'name': 'url template',
                'template': ''
            },
            # 'projection': ''
        }

        return layer_dict

    def add_layer(self, layer_key_name, caching_layer):
        """
        Add layer to tilestache config
        :param layer_key_name:
        :param layer_dict:
        :return:
        """
        self.config.layers[layer_key_name] = _parseConfigLayer(self.build_layer_dict(caching_layer), self.config,
                                                               dirpath='.')

    def remove_layer(self, layer_key_name):
        """
        Remove layer from tilestache config obj
        :param layer_key_name:
        :return: None
        """
        del(self.config.layers[layer_key_name])

        # todo: delete cache direcotory

