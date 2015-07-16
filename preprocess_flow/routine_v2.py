import os 
import sys
import subprocess
import time
import shutil

def do_preprocess(WORKING_DIR,SAMPLE_DIR,db_ip,db_name,model_name):
    orig_dir = SAMPLE_DIR+'Sample/orig/'
    log_dir = SAMPLE_DIR+'Sample/Log/'
    fet_dir = SAMPLE_DIR+'Sample/Fet/'
    vec_dir = SAMPLE_DIR+'Vector/'
    pre_script_dir = WORKING_DIR+'md5_get/'
    predict_dir = WORKING_DIR+'md5_get/fet_quality/'
    report_dir = WORKING_DIR+'VDC_report/'    

    print 'orig_dir:',orig_dir

    current_time = time.time()
    vector_file = 'vec_%d'% int(current_time)

    refiner_py = '%srefiner.py'%pre_script_dir
    preprocess_py = '%spreprocess.py'%pre_script_dir
    m2v_py = '%sMist2Vector.py'%pre_script_dir
    mergevec_py = '%sMergeSvmData.py'%pre_script_dir
    predict_py = '%ssvm_predict_output_label.py'%predict_dir
    report_py = '%smd5_report_server_branch.py'%report_dir

    if os.path.isfile(refiner_py)==False:
        print refiner_py,' not exist!'
        sys.exit(1)
    if os.path.isfile(preprocess_py)==False:
        print preprocess_py,' not exist!'
        sys.exit(1)
    if os.path.isfile(m2v_py)==False:
        print m2v_py,' not exist!'
        sys.exit(1)
    if os.path.isfile(mergevec_py)==False:
        print mergevec_py,' not exist!'
        sys.exit(1)
    if os.path.isfile(predict_py)==False:
        print predict_py,' not exist!'
        sys.exit(1)
    if os.path.isfile(report_py)==False:
        print report_py,' not exist!'
        sys.exit(1)

    cmd_refine = 'python %s %s %s 12'%(refiner_py, orig_dir, log_dir)
    cmd_preprocess = 'python %s %s %s 12'%(preprocess_py, log_dir, fet_dir)
    cmd_m2v = 'python %s %s %s %s %s 12'%(m2v_py, fet_dir, vec_dir, db_ip, db_name)
    cmd_mergevec = 'python %s %s %s%s'%(mergevec_py, vec_dir, predict_dir, vector_file)
    cmd_predict = 'python %s  %s%s %s%s'%(predict_py, predict_dir, model_name, predict_dir,vector_file)
    cmd_report = 'python %s %s%s.result'%(report_py, predict_dir,vector_file)    
    
    if os.path.exists(log_dir):
        shutil.rmtree(log_dir)
    os.system(cmd_refine)

    if os.path.exists(fet_dir):
        shutil.rmtree(fet_dir)
    os.system(cmd_preprocess)
    
    if os.path.exists(vec_dir):
        shutil.rmtree(vec_dir)
    os.system(cmd_m2v)
    os.system(cmd_mergevec)
    os.system(cmd_predict)
    #os.system(cmd_report)

    print '****************finish*******************'
    print time.strftime("%Y-%m-%d %X", time.localtime())
    print 'vector_file = ',predict_dir+vector_file
    print '****************finish*******************'    

def import_log_orig(SRC_DIR,SAMPLE_DIR,date_list):
    src_dir = SRC_DIR
    orig_dir = SAMPLE_DIR+'Sample/orig/'
    if os.path.exists(orig_dir):
        shutil.rmtree(orig_dir)
        os.mkdir(orig_dir)

    for date in date_list:
        mv_cmd = 'mv %s %s'%(src_dir+date,orig_dir)
        os.system(mv_cmd)
        print ' %s'%mv_cmd

def export_log_orig(SAMPLE_DIR,DST_DIR,date_list):
    orig_dir = SAMPLE_DIR+'Sample/orig/'
    dst_dir = DST_DIR
    for date in date_list:
        mv_cmd = 'mv %s %s'%(orig_dir+date,dst_dir)
        os.system(mv_cmd)
        print ' %s'%mv_cmd

if __name__ == '__main__':
    if len(sys.argv)!=2:
        print 'Usage:'
        print '%s sample_dir'%sys.argv[0]
        exit(-1)
    
    WORKING_DIR = '/home/karlxu/preprocess/'
    SAMPLE_DIR = '/home/karlxu/%s/'%(sys.argv[1])
    #step1. move all orig log from SRC_DIR to SAMPLE_DIR
    #step2. process and report
    #step3. move all orig log from SAMPLE_DIR to DST_DIR
    SRC_DIR = '/home/hips/FileServer/upload/VDC_report/'
    DST_DIR = '/home/hips/FileServer/upload/VDC_report_done/'    
 
    mv_date_list = ['2015_03_23']

    db_ip = 'nj02-sw-kvmserver01.nj02'
    #db_name = 'iter_g_2gram'
    db_name = 'selected_iter_g_10w_chi2'
    #model_name = 'iter_g_vectors.uniq.final'
    model_name = 'iter_g_10w_chi2.uniq.final.new '
    #import_log_orig(SRC_DIR,SAMPLE_DIR,mv_date_list)
    do_preprocess(WORKING_DIR,SAMPLE_DIR,db_ip,db_name,model_name)
    #export_log_orig(SAMPLE_DIR,DST_DIR,mv_date_list)

