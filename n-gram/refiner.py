#!/usr/bin/python  

import  os
import  sys
import  os.path
import  time
from multiprocessing import Process,Pool

def refine_one_file(SrcFile,DstFile):
        PathList = SrcFile.split('/')
        if len(PathList[-1])!=36:
                return
        fileIn = open (SrcFile)
        fileOut = open (DstFile,'w')
   
        LastLine = ''
        LastOutLine = ''
        SamplePath= ''
        SampleName= ''
        DsdtSet = set()
        while 1:
                Line = fileIn.readline()
                if not Line:
                        break                    
                if LastLine == Line:
                        continue
                else:
                        LastLine = Line;               
                
                ParamList = Line.split('|#|')
                if(len(ParamList)<3):
                        continue
                if ParamList[0]== 'SECTION':
                        if len(ParamList)<5:
                                continue
                        ParamList[4] = ParamList[4].strip()
                        #2014-10-23 SECTION problem!!!
                        #SECTION|#|2|#|\NLS\NlsSectionSortkey00000804|#|C:\04970105315b3bba96e953a0ad\update\update.exe|#|\Device\HarddiskVolume1\04970105315b3bba96e953a0ad\upda...
                        ParamList[3]=ParamList[3].replace('\Device\HarddiskVolume1','C:')
                        ParamList[4]=ParamList[4].replace('\Device\HarddiskVolume1','C:')
                        if ParamList[4] == '' or ParamList[3]==ParamList[4]:
                                continue
                        #delete param[3],(subject)
                        print ParamList
                        del ParamList[3]
                        print ParamList
                else:
                        ParamList.pop()
                OutLine='' 
                index = 0
                
                #here we all have 4 params.

                #print ParamList
                #print len(ParamList)
                ########################################################################################################################
                #REGISTRY|#|8|#|\REGISTRY\MACHINE\SYSTEM\ControlSet001\Control\Session Manager\CWDIllegalInDLLSearch|#|C:\behavior_tool_v2\samples\00e3279504bd88c8d50f4eb4180c2452.exe
                if SamplePath == '':
                    if len(ParamList) >= 4:
                        sample_name = ParamList[3][ParamList[3].rfind('\\')+1:]
                        if len(sample_name)==36:#confirm this line actually contains md5
                            SamplePath = ParamList[3]
                            #record name to replace lines like this:
                            #REGISTRY|#|8|#|\REGISTRY\MACHINE\SOFTWARE\Microsoft\Internet Explorer\Main\FeatureControl\FEATURE_OBJECT_CACHING\33bcbe7730f851e2b12bd2fc7f9ef0ef.exe|#|C:\behavior_tool_v2\samples\33bcbe7730f851e2b12bd2fc7f9ef0ef.exe|#|
                            SampleName = sample_name
                            #print 'get SamplePath=',sample_name
                        else:
                            continue
                    else:#first line meet 3params,it's rare.
                        pass
                        
                if len(ParamList) == 4:
                    if ParamList[2]== SamplePath:
                        ParamList[2] = '$self'
                    if ParamList[3]== SamplePath:
                        ParamList[3] = '$self'            
                    #PROCESS|#|2|#|C:\behavior_tool_v2\samples\update.exe|#|C:\behavior_tool_v2\samples\update.exe
                    if ParamList[0]== 'PROCESS' and ParamList[2] == ParamList[3]:
                        continue
                    if ParamList[0]== 'PROCESS' and ParamList[1]== '0':
                        DsdtSet.add(ParamList[2])
                    if ParamList[0]== 'FILE' and ParamList[1]== '0':
                        DsdtSet.add(ParamList[2])
                        
                    for item in DsdtSet:
                        if ParamList[2] == item:
                            pos = ParamList[2].rfind('\\')
                            if pos != -1:
                                ParamList[2] = ParamList[2][:pos+1]  
                                ParamList[2] += '$dsdt'
                                        
                    pos1=ParamList[2].find(':\\')
                    pos2=ParamList[2].find('\\Device\\HarddiskVolume')
                    if pos1 != -1 or pos2 != -1:
                        if ParamList[0] != 'REGISTRY':
                            if ParamList[2].find('Program Files')==-1 and ParamList[2].find('WINDOWS')==-1 and ParamList[2].find('Documents and Settings')==-1:
                                ParamList[2] = '$other_path'
                        else: #REGISTRY: only replace the path. 2014-10-23
                            if pos1 != -1:
                                child_path = ParamList[2][pos1-len('C'):]
                                ParamList[2] = ParamList[2][:pos1-len('C')]
                                if child_path == SamplePath:
                                    ParamList[2] += '$self'
                                else:
                                    ParamList[2] += child_path[len('C:\\'):]
                            else:
                                print 'REGISTRY contains: HarddiskVolume '
                                print ParamList
                                print SamplePath           
                                        
                    #end
                    if ParamList[0]!= 'SECTION':
                        del ParamList[3]
                    #end

                else:#len!=4,won't go here
                    pass
                #here, SECTION have 4 params, others have 3 params.

                for index,param in enumerate(ParamList):           
                        if index==0 or index==1:
                               OutLine += param
                               OutLine += '|#|'
                               continue
       
                        pos = param.find('\\S-')
                        if pos != -1:
                                pos2 = param.find('\\',pos+len('\\S-'))
                                if pos2 != -1:                    
                                        paramLeft = param[pos2+1:]
                                        param = param[:pos+len('\\S-')]
                                        param += '*\\'
                                        param += paramLeft
                        #end
                        #replace sample name(md5)in registry path.
                        if param.find(SampleName)!= -1:
                            param = param.replace(SampleName,'$self')
                        #end
                        #MACHINE\SYSTEM\ControlSet001\Control\SafeBoot\Minimal\{71A27CDD-812A-11D0-BEC7-08002BE2092F} ->MACHINE\SYSTEM\ControlSet001\Control\SafeBoot
                        pos = param.find('\Control\SafeBoot')
                        if pos != -1:
                                param = param[:pos+len('\Control\SafeBoot')]          
                        #CurrentVersion\Drivers32\**** -> CurrentVersion\Drivers32
                        #pos = param.find('\CurrentVersion\Drivers32')
                        #if pos != -1:
                        #    param = param[:pos+25] 
                        #end
                        param = param.replace('DOCUME~1','Documents and Settings')
                        param = param.replace('LOCALS~1','Local Settings')
                        #end
        
                        #C:\Documents and Settings\baidu123\backup.exe ->C:\Documents and Settings\backup.exe
                        pos = param.find('Documents and Settings\\')
                        if pos != -1:
                                pos2 = param.find('\\',pos+len('Documents and Settings\\'))
                                if pos2 != -1:                    
                                        paramLeft = param[pos2+1:]
                                        param = param[:pos+len('Documents and Settings\\')]
                                        param += paramLeft
                        #end
                        pos = param.find('C:\\')
                        if pos != -1:               
                                param = param[len('C:\\'):]         
                        #end                   
                        pos = param.find('\\Device\\HarddiskVolume')
                        if pos != -1:               
                                param = param[len('\\Device\\HarddiskVolume')+2:] 
                            
                        #end
                        #############################################################################################################
                        OutLine += param
                        OutLine += '|#|'
        
                if LastOutLine==OutLine:
                        continue
                else:
                        LastOutLine = OutLine;
            
                OutLine = OutLine[:-3]
                OutLine +='\n' 
               # print 'out=',OutLine
                fileOut.write(OutLine)
        #The first while 1 break!
        fileIn.close()
        """
        error = 0
        fileOut.seek(0)
        fileOut2 = open (DstFile+'a','w')
        B1 = fileOut.readline()
        if not B1:
                error = 1                    
        B2 = fileOut.readline()
        if not B2:
                error = 1
        A1 = fileOut.readline()
        if not A1:
                error = 1
        A2 = fileOut.readline()
        if not A2:
                error = 1
        print 'err=',error
        if error == 0:
                fileOut.write(B1)
                fileOut.write(B2)
                while 1:
                        if A1 == B1 and A2 == B2:
                                print 'find'
                                A1 = fileOut.readline()
                                if not A1:                                        
                                        break
                                A2 = fileOut.readline()
                                if not A2:
                                        fileOut.write(A1)
                                        break                                
                        else:
                                fileOut.write(B1)
                                B1 = B2
                                B2 = A1
                                A1 = A2
                                A2 = fileOut.readline()
                                if not A2:
                                        fileOut.write(B1)
                                        fileOut.write(B2)
                                        fileOut.write(A1)
                                        break               
                fileOut2.close
        #end                
        """
        fileOut.close() 

def process_file(rawdata_file):
    tail_path = rawdata_file[len(g_top_rawdata_dir):]
    output_file = g_top_output_dir+tail_path
    if os.path.exists(output_file):
        return
    refine_one_file(rawdata_file,output_file)

def parallel_process_pool(rawdata_dir,num_tasks):
    file_list = []
    for root,dirs,files in os.walk(rawdata_dir):
        for name in files:
            raw_file = os.path.join(root,name)
            file_list.append(raw_file)    
            
            tail_path = raw_file[len(g_top_rawdata_dir):]
            output_file = g_top_output_dir+tail_path
            output_dir = output_file[:output_file.rfind('/')]
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

    print '%d files to refine.'%len(file_list)
    process_pool = Pool(processes=num_tasks)
    process_pool.map(process_file,file_list)

if __name__ == '__main__':

    if len(sys.argv) != 4:
        print 'Usage:'
        print sys.argv[0],' rawdata_dir output_dir num_tasks'
        sys.exit()

    print 'refiner start'
    g_top_rawdata_dir = sys.argv[1]
    g_top_output_dir = sys.argv[2]
    num_tasks = int(sys.argv[3])
    if g_top_rawdata_dir[-1:]!='/':
        g_top_rawdata_dir +='/'
    if g_top_output_dir[-1:]!='/': 
        g_top_output_dir +='/'   

    st=time.clock()
    parallel_process_pool(g_top_rawdata_dir,num_tasks)
    et=time.clock()
    print 'refiner consumes %ds'%(et-st)    






