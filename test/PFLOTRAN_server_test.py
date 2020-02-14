# -*- coding: utf-8 -*-
import os
import time
import unittest
from configparser import ConfigParser

from PFLOTRAN.PFLOTRANImpl import PFLOTRAN
from PFLOTRAN.PFLOTRANServer import MethodContext
from PFLOTRAN.authclient import KBaseAuth as _KBaseAuth

from installed_clients.WorkspaceClient import Workspace
from installed_clients.DataFileUtilClient import DataFileUtil


class PFLOTRANTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = os.environ.get('KB_AUTH_TOKEN', None)
        config_file = os.environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('PFLOTRAN'):
            cls.cfg[nameval[0]] = nameval[1]
        # Getting username from Auth profile for token
        authServiceUrl = cls.cfg['auth-service-url']
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': user_id,
                        'provenance': [
                            {'service': 'PFLOTRAN',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = Workspace(cls.wsURL)
        cls.serviceImpl = PFLOTRAN(cls.cfg)
        cls.scratch = cls.cfg['scratch']
        cls.callback_url = os.environ['SDK_CALLBACK_URL']
        suffix = int(time.time() * 1000)
        cls.wsName = "test_ContigFilter_" + str(suffix)
        ret = cls.wsClient.create_workspace({'workspace': cls.wsName})  # noqa

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    # NOTE: According to Python unittest naming rules test method names should start from 'test'. # noqa

    # def test_upload(self):
    #     # Prepare test objects in workspace if needed using
    #     # self.getWsClient().save_objects({'workspace': self.getWsName(),
    #     #                                  'objects': []})
    #     #
    #     # Run your method by
    #     # ret = self.getImpl().your_method(self.getContext(), parameters...)
    #     #
    #     # Check returned data with
    #     # self.assertEqual(ret[...], ...) or other unittest methods
    #     media = '37663/2/1'
    #     fba = '37663/3/1'
    #     batch = 'batch'
    #     column = 'column'
    #     path = ''
    #     params = {'workspace_name': self.wsName, 'input_FBA_model': fba,
    #               'input_Media_model': media, 'input_deck_file': batch, 'staging_file_subdir_path': path}

    #     ret = self.serviceImpl.upload_pflotran_model(self.ctx, params)
    
    def test_run(self):
        params = {'workspace': self.wsName,
                  'parameter_1': 'Hello World!',
                  'shared_folder': self.scratch}
        ret = self.serviceImpl.run_PFLOTRAN(self.ctx, params)

    def test_run2(self):
        db ={"name": "PFLOTRAN_kb", "description": "test",
             "pflotran_deck": "KBH_102912", "hdf_parameters": "1/1/1"}
        ws_id = 38181

        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.dfu = DataFileUtil(self.callback_url)

        save_object_params = {
            'id': ws_id,
            'objects': [{
                'type': 'KBaseReactiveTransport.PflotranModel',
                'data': db,
                'name': 'test_so'
            }]
        }

        # dfu_oi = self.dfu.save_objects(save_object_params)[0]

        # print(dfu_oi)
        # self.dfu = DataFileUtil(self.callback_url)
        # genome_ref = "your/object_reference"
        # genome_data = dfu.get_objects({'object_refs': [genome_ref]})['data'][0]
        # genome_obj = genome_data['data']
        # genome_meta = genome_data['info'][10]
