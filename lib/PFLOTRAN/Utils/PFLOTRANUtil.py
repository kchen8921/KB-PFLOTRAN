import json
import os
import subprocess
from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.DataFileUtilClient import DataFileUtil
from pprint import pprint

class PFLOTRANUtil:
    PREPDE_TOOLKIT_PATH = '/kb/module/lib/PFLOTRAN/Utils'

    def _generate_html_report(self):
        report = "<html> <head> KB-PFLOTRAN report </head> <body> </body> </html>"
        return report 

class PFLOTRANUploadUtil:
    def __init__(self,params):
        self.params = params
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.dfu = DataFileUtil(self.callback_url)

    def run_uploader(self):
        media = self.params['input_Media_model']
        fba = self.params['input_FBA_model']
        # reaction = self.params['input_deck_file']

        media_data = self.dfu.get_objects({'object_refs': [media]})['data'][0]
        media_obj = media_data['data']
        media_meta = media_data['info'][10]

        fba_data = self.dfu.get_objects({'object_refs': [fba]})['data'][0]
        fba_obj = fba_data['data']
        fba_meta = fba_data['info'][10]

        # reaction_data = self.dfu.get_objects({'object_refs': [reaction]})['data'][0]
        # reaction_obj = reaction_data['data']
        # reaction_meta = reaction_data['info'][10]
        pprint(media_meta)
        pprint(media_obj)
        pprint(fba_meta)
        pprint(fba_obj)
        # return PflotranModel (link to pflotran_deck: https://appdev.kbase.us/#spec/module/KBaseReactiveTransport) 
        return {}

    def _generate_html_report(self):
        media = self.params['input_Media_model']
        fba = self.params['input_FBA_model']
        reactioon = self.params['input_deck_file']
        output

    
