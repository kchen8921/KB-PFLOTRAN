import json
import os
import subprocess

class PFLOTRANUtil:
    PREPDE_TOOLKIT_PATH = '/kb/module/lib/PFLOTRAN/Utils'

    def _generate_html_report(self):
        report = "<html> <head> KB-PFLOTRAN report </head> <body> </body> </html>"
        return report 