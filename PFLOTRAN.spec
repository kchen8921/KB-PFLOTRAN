/*
A KBase module: PFLOTRAN
*/

module PFLOTRAN {
    typedef structure {
        string report_name;
        string report_ref;
    } ReportResults;

    /*
        Thi function enables users to run a pflotran simulation from an input plfotran model and fbamodel chemistry
    */
    funcdef run_PFLOTRAN(mapping<string,UnspecifiedObject> params) returns (ReportResults output) authentication required;
    
    /*
        This function enables users to upload files defining a pflotran model including input_deck and hdf5 parameter file
    */
    funcdef upload_pflotran_model(mapping<string,UnspecifiedObject> params) returns (ReportResults output) authentication required;
};
