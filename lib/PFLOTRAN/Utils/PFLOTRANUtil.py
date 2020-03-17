import json
import os
import subprocess
import h5py
import uuid
from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.DataFileUtilClient import DataFileUtil
from pprint import pprint
from shutil import copy
import subprocess
import matplotlib.pyplot as plt
import numpy as np

class PFLOTRANUtil:
    PREPDE_TOOLKIT_PATH = '/kb/module/lib/PFLOTRAN/Utils'

    def _generate_html_report(self):
        report = "<html> <head> KB-PFLOTRAN report </head> <body> </body> </html>"
        return report 

class PFLOTRANRunUtil:
    def __init__(self,params):
        self.params = params
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.dfu = DataFileUtil(self.callback_url)
        self.output_files = []
        self.html_files = []
        self.data_folder = os.path.abspath('./data/')
        self.shared_folder = params['shared_folder']
        self.scratch_folder = os.path.join(params['shared_folder'],"scratch")

    def run_pflotran(self):
        print('params:',self.params)
        try:
            os.mkdir(self.scratch_folder)
        except OSError:
            print ("Creation of the directory %s failed" % self.scratch_folder)
        else:
            print ("Successfully created the directory %s " % self.scratch_folder)

        # copy pflotran input deck for test
        input_deck_src = os.path.join(self.data_folder,'batch.in')
        database_src = os.path.join(self.data_folder,'database.dat')
        input_deck_des = os.path.join(self.scratch_folder,'batch.in')
        database_des = os.path.join(self.scratch_folder,'database.dat')
        print('input_deck_des:',input_deck_des)
        copy(input_deck_src,self.scratch_folder)  
        copy(database_src,self.scratch_folder)      
        if os.path.isfile(input_deck_des):
            print ("Input deck exist")
        else:
            print ("Input deck not exist")
        if os.path.isfile(database_des):
            print ("Database exist")
        else:
            print ("Database exist")

        # running pflotran
        exepath = '/bin/pflotran/src/pflotran/pflotran'
        run_pflotran_cmd = exepath + ' -n 1 -pflotranin ' + input_deck_des
        process = subprocess.Popen(run_pflotran_cmd.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        print("process output:",output[-300:])
        print("process err:",error)
        pprint(os.listdir(self.scratch_folder))


        output_file = os.path.join(self.scratch_folder,'batch.h5')
        if os.path.isfile(output_file):
            print ("Successfully run PFLOTRAN")
        else:
            print ("Fail to run PFLOTRAN")

        # generate plots in /kb/module/work/tmp/scratch/
        self.plot_time_series(output_file)
        
        # Check PFLOTRAN input deck
# <<<<<<< HEAD
        pprint(self.params)
        pflotran_model = self.params['PflotranModel_id']
        pflotran_model_data = self.dfu.get_objects({'object_refs': [pflotran_model]})['data'][0]
        pflotran_model_data_obj = pflotran_model_data['data']
        pflotran_model_data_meta = pflotran_model_data['info'][10]

        pprint(pflotran_model_data_obj)
        pprint(pflotran_model_data_meta)
# =======
#         # pflotran_model = self.params['input_model']
#         # hdf5_file = pflotran_model['hdf5_parameters']
#         # input_deck = pflotran_model['input_deck']

# >>>>>>> parent of 3374f33... run pflotran
        # Run PFLOTRAN


        # Get the output file
        self.hdf_output_file = os.path.join(self.shared_folder,'test.h5')
        with h5py.File(self.hdf_output_file, 'w') as f:
            dset = f.create_dataset("mydataset", (100,), dtype='i')
        self.output_files.append(
            {'path': self.hdf_output_file,
             'name': os.path.basename(self.hdf_output_file),
             'label': os.path.basename(self.hdf_output_file),
             'description': 'File(s) generated by run_pflotran App'}
        )

        # Return the report
        return self._generate_html_report()
        
    def plot_time_series(self,h5_file):
        var_name = ['Total_O2(aq) [M]','Total_CH2O(aq) [M]','Total_NO3- [M]']
        obs_coord = [0.5,0.5,0.5]

        file = h5py.File(h5_file,'r+')
        time_str = [list(file.keys())[i] for i in range(len(list(file.keys()))) if list(file.keys())[i][0:4] == "Time"]
        time_unit = time_str[0][-1]
        time = sorted([float(time_str[i].split()[1]) for i in range(len(time_str))])
        bound = []
        bound.append(file['Coordinates']['X [m]'][0])
        bound.append(file['Coordinates']['X [m]'][-1])
        bound.append(file['Coordinates']['Y [m]'][0])
        bound.append(file['Coordinates']['Y [m]'][-1])
        bound.append(file['Coordinates']['Z [m]'][0])
        bound.append(file['Coordinates']['Z [m]'][-1])
        nxyz = []
        nxyz.append(len(file['Coordinates']['X [m]'])-1)
        nxyz.append(len(file['Coordinates']['Y [m]'])-1)
        nxyz.append(len(file['Coordinates']['Z [m]'])-1)

        x_coord = (np.linspace(bound[0],bound[1],nxyz[0]+1)[:-1]+np.linspace(bound[0],bound[1],nxyz[0]+1)[1:])/2
        y_coord = (np.linspace(bound[2],bound[3],nxyz[1]+1)[:-1]+np.linspace(bound[2],bound[3],nxyz[1]+1)[1:])/2
        z_coord = (np.linspace(bound[4],bound[5],nxyz[2]+1)[:-1]+np.linspace(bound[4],bound[5],nxyz[2]+1)[1:])/2
        x_idx = np.argmin(np.absolute(x_coord-obs_coord[0]))
        y_idx = np.argmin(np.absolute(y_coord-obs_coord[1]))
        z_idx = np.argmin(np.absolute(z_coord-obs_coord[2]))
        var_value = np.zeros((len(var_name),len(time)))
        for i, itime in enumerate(time):
            time_slice = "Time:"+str(" %12.5E" % itime)+str(" %s" % time_unit)
        #     print(file[time_slice][var_name].keys())
            for j in range(len(var_name)):
                var_value[j,i] = file[time_slice][var_name[j]][x_idx][y_idx][z_idx]

        fig = plt.figure(num=1,dpi=150)
        legend = []
        lines = []
        for i in range(len(var_name)):
            line = plt.plot(time,var_value[i,:])[0]
            plt.ioff()
            lines.append(line)
            legend.append(var_name[i])
            plt.ioff()

        plt.xlabel("Time (%s)" %time_unit)
        ylabel = 'Concentration [M]'
        #     if 'Total' in var_name[0]:
        #         ylabel = 'Concentration [M]'
        #     else:
        #         ylabel = var_name[0][var_name[0].index('_')+1:]
        plt.ylabel(ylabel)
        plt.legend(lines,legend,frameon=False)
        figpath = os.path.join(self.scratch_folder,'time_series_plot.png')    
        plt.savefig(figpath,dpi=150) 

        if os.path.isfile(figpath):
            print ("Successfully generated time series plot")
        else:
            print ("Fail to generate time series plot")

        return

    def visualize_hdf_in_html(self):
        # Open the HDF5 file
        # f = h5py.File(self.hdf_output_file, 'r')
        shared_folder = self.params['shared_folder']
        output_directory = os.path.join(shared_folder, str(uuid.uuid4()))
        os.makedirs(output_directory)
        html_file = os.path.join(output_directory,'test.html')
        figpath = os.path.join(self.scratch_folder,'time_series_plot.png')
        with open(html_file, 'w') as f:
            f.write("""
                <!DOCTYPE html>
                <html>
                <body>

                <h1>PFLOTRAN-KB</h1>

                <p>Visulize PFLOTRAN output</p>
                <h2>Time series plot for batch reaction</h2>
                <img src="%s" alt="Time series plot of batch reaction">
                </body>
                </html>
            """ % (figpath))
            print(f)
        report_shock_id = self.dfu.file_to_shock({'file_path': output_directory,
                                                  'pack': 'zip'})['shock_id']

        return {'shock_id': report_shock_id,
                'name': os.path.basename(html_file),
                'label': os.path.basename(html_file),
                'description': 'HTML summary report for run_pflotran App'}

 
    def _generate_html_report(self):
        # Get the workspace name from the parameters
        ws_name = self.params["workspace"]

        # Visualize the result in html
        html_report_viz_file = self.visualize_hdf_in_html()

        self.html_files.append(html_report_viz_file)

        # Save the html to the report dictionary
        report_params = {
            # message is an optional field.
            # A string that appears in the summary section of the result page
            'message': "Say something...",

            # A list of typed objects created during the execution
            #   of the App. This can only be used to refer to typed
            #   objects in the workspace and is separate from any files
            #   generated by the app.
            # See a working example here:
            #   https://github.com/kbaseapps/kb_deseq/blob/586714d/lib/kb_deseq/Utils/DESeqUtil.py#L262-L264
            # 'objects_created': objects_created_in_app,

            # A list of strings that can be used to alert the user
            # 'warnings': warnings_in_app,

            # The workspace name or ID is included in every report
            'workspace_name': ws_name,

            # A list of paths or Shock IDs pointing to
            #   a single flat file. They appear in Files section
            'file_links': self.output_files,

            # HTML files that appear in “Links”
            'html_links': self.html_files,
            'direct_html_link_index': 0,
            'html_window_height': 333,
        } # end of report_params

        # Make the client, generate the report

        kbase_report_client = KBaseReport(self.callback_url)
        output = kbase_report_client.create_extended_report(report_params)

        # Return references which will allow inline display of
        # the report in the Narrative
        report_output = {'report_name': output['name'],
                        'report_ref': output['ref']}
        
        return report_output
    
    # def _mkdir_p(self, path):
    #     """
    #     _mkdir_p: make directory for given path
    #     """
    #     if not path:
    #         return
    #     try:
    #         os.makedirs(path)
    #     except OSError as exc:
    #         if exc.errno == errno.EEXIST and os.path.isdir(path):
    #             pass
    #         else:
    #             raise



class PFLOTRANUploadUtil:
    def __init__(self,params):
        self.params = params
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.dfu = DataFileUtil(self.callback_url)
        self.data_folder = os.path.abspath('./data/')

    def run_uploader(self):
        print('params:',self.params)
        print('PFLOTRAN_obj:',self.params['PFLOTRAN_obj'])
        shared_folder = self.params['shared_folder']
        print('shared_folder:',shared_folder)
        scratch_folder = os.path.join(shared_folder,"scratch")
        print('scratch_folder:',scratch_folder)
        data_folder = self.data_folder
        print('data_folder:',data_folder)
        staging_folder = "/staging/"
        print('staging_folder:',staging_folder)
        simu_type = self.params['input_deck_type']
        print('simulation_type:',simu_type)

        if simu_type == 'batch':
            data_file = os.path.join(data_folder, "batch.in")
            print('data_file:',data_file)
            copyfile(data_file,scratch_folder)
        else:
            data_file = os.path.join(staging_folder,self.params['staging_custom_input_deck'])
            print('data_file:',data_file)
            copyfile(data_file,scratch_folder)

        pprint(os.listdir(data_folder))
        # print("Contents in scratch folder:",os.listdir(scratch_folder+'/'))


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
        # pprint(media_meta)
        # pprint(media_obj)
        # pprint(fba_meta)
        # pprint(fba_obj)
        # return PflotranModel (link to pflotran_deck: https://appdev.kbase.us/#spec/module/KBaseReactiveTransport) 
        
        # pf_fp = f"{shared_folder}/pflotran_deck"
        # with open(pf_fp, 'w') as f:
        #     f.write("{}\n".format(data_folder))
        # hdf_fp = f"{shared_folder}/hdf_parameters"
        # with open(hdf_fp, 'w') as f:
        #     f.write("{}\n".format(data_folder))

        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.dfu = DataFileUtil(self.callback_url)

        deck_handle = self.dfu.file_to_shock({'file_path': scratch_folder, 'make_handle': True})['handle']['hid']
        hdf_handle = self.dfu.file_to_shock({'file_path': scratch_folder, 'make_handle': True})['handle']['hid']
        print("deck_handle:",deck_handle)
        print("hdf_handle:",hdf_handle)
        db = {"name": "PFLOTRAN_kb", "description": "test","pflotran_deck": deck_handle, "hdf_parameters": hdf_handle}
        #CHANGE THIS!
        ws_id = 38181   
        name = self.params.get("PFLOTRAN_obj", "unamed_plfotran")
        save_object_params = {
            'id': ws_id,
            'objects': [{
                'type': 'KBaseReactiveTransport.PflotranModel',
                'data': db,
                'name': name
            }]
        }
        # save_objects return a list of objects,[0] indicates the first one
        dfu_oi = self.dfu.save_objects(save_object_params)[0]

        pprint(self.dfu.get_objects({'object_refs': ['38181/test_so']}))
        pflo_data = self.dfu.get_objects({'object_refs': ['38181/test_so']})['data'][0]
        
        pflo_obj = pflo_data['data']
        # pflo_deck = pflo_obj['pflotran_deck']
        # pprint(pflo_deck)

        return {'Name':dfu_oi[1],'PFLOTRAN model':dfu_oi[2]}

    def _generate_html_report(self):
        media = self.params['input_Media_model']
        fba = self.params['input_FBA_model']
        reactioon = self.params['input_deck_file']
        output

    
