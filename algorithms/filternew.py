# -*- coding: cp936 -*-
import os
import  os.path
import time
from common import *
from Similarity import *

RuleList=[]
CntList=[]
SpyList=[]
"""
REG

| 1_0                      |CREATE
| 1_2                      |SET_VALUE_KEY       value
| 1_3                      |RENAME_KEY
| 1_4                      |DELETE_KEY
| 1_5                      |DELETE_VALUE_KEY    value
| 1_8			   |QUERY_VALUE_KEY     value

255/253  all match
252  if 1_0: no
191  if 1_4: no
176  if not 1_2 and 1_0,no
15   if not 1_0,1_3,1_4,no

"""

def match(Line,Rule):       

    LineParam=Line.split('#')
    RuleParam=Rule.split('#')
    #other:2 params at least.
    #NOTE:if not REG,only compare major(param[0]) and minor(param[1])
    if len(RuleParam)<3:
        return False
    if len(LineParam)<2:
        return False
    
    #print 'LP=',LineParam
    #print 'RP=',RuleParam    
    
    if int(LineParam[0])!=1 and int(RuleParam[0])==1:
        return False
    if int(LineParam[0])!=1 and int(RuleParam[0])!=1:
        #convert hips major to mist major
        if int(RuleParam[0])==8:#mem
            RuleParam[0]='6'
        if int(RuleParam[0])==16:#inject
            RuleParam[0]='3'
        if int(RuleParam[0])==32:#section
            RuleParam[0]='8'          
        
        if int(LineParam[0])!=int(RuleParam[0]):
            return False
        else:#in here: major equals.
            major=int(RuleParam[0])
            minor=int(RuleParam[1])
            if major==2:#file##########
                #print 'filelp=',LineParam
                #print 'filerp=',RuleParam   
                if len(LineParam)<3:
                    return False
                if '\n' in RuleParam[2]:
                    RuleParam[2]=RuleParam[2][:-2] #NOTE!!!!  win/linux: -1 or -2
                if minor==127:
                    pass
                if minor==60:
                    if int(LineParam[1])==0 or int(LineParam[1])==1:
                        return False
                    else:
                        pass
                if RuleParam[2] in LineParam[2]:
                    #print '->file match'
                    return True
                else:
                    return False
                #file end#
                
            elif major==6:#mem########
                #print '->mem match'
                return True
                #mem end

            elif major==3:#inject####
                #print '->inject match'
                return True             
                #inject end  
            
            elif majar==8:#section
                if LineParam[1]==3:
                    print '->section match'
                    return True
                else:
                    return False
            else:
                pass  #not going here~
        
    else:
        pass  
    
    #only 'LineParam[0]==1' is left here.
    #START REG MATCH
    if int(RuleParam[0])!=1:
        return False
    if len(LineParam)<3:
        return False
    
    if int(LineParam[0])==1 and int(LineParam[1])==8:  #REG query: omit
        return False
   
    if int(RuleParam[1])==255 or int(RuleParam[1])==253:#255/253: match all.
        pass
    if int(RuleParam[1])==252:
        if int(LineParam[1])==0:
            return False
        else:
            pass
    if int(RuleParam[1])==191:
        if int(LineParam[1])==4:
            return False
        else:
            pass
    if int(RuleParam[1])==176:
        if int(LineParam[1])!=0 and int(LineParam[1])!=2:
            return False
        else:
            pass      
    if int(RuleParam[1])==15:
        if int(LineParam[1])!=0 and int(LineParam[1])!=1 and int(LineParam[1])!=3 and int(LineParam[1])!=4:
            return False
        else:
            pass

    
    if_star = False
    LinePath = LineParam[2]
    RulePath = RuleParam[2][1:]   #del a '|'

    #deal with param2
    if len(RuleParam)==4:
        if '*' not in RuleParam[3]:
            if '\n' in RuleParam[3]:
                RuleParam[3]=RuleParam[3][:-2] #NOTE!!!!  win/linux: -1 or -2
            else:
                pass
            RulePath = RulePath+'|'+RuleParam[3] ##derictly add param2 in Ruleline.  
        else:
            if_star = True
    else:
        pass

    LinePath=LinePath.upper()
    RulePath=RulePath.upper()
    #deal with 'CONTROLSET???'and 'CurrentControlSet'    
    if 'CONTROLSET'in LinePath and 'CURRENTCONTROLSET' not in LinePath:
        pos = LinePath.find('CONTROLSET')
        pos+=len('CONTROLSET')
        posend= LinePath.find('|',pos)
        num=LinePath[pos:posend]
        LinePath = LinePath.replace('CONTROLSET'+num,'CONTROLSET'+'???')
    else:
        pass
    LinePath = LinePath.replace('CURRENTCONTROLSET','CONTROLSET'+'???')
        
    #print 'LP2=',LinePath
    #print 'RP2=',RulePath

    #SPLITTED MATCH:
    #if middle stars exist,split the rule and match each
    if '|*|' in RulePath:
        RuleMatchList=RulePath.split('|*|')
        for item in RuleMatchList:
            if item not in LinePath:
                return False
            else:
                pass
        #print '->split match'
        #print '(%s,  %s)'%(LinePath,RulePath)        
        return True
    else:
        pass #start REGULAR MATCH
        
    #REGULAR MATCH:
    if if_star:
        if RulePath in LinePath:
            #print '->includes'
            #print '(%s,  %s)'%(LinePath,RulePath)
            return True
        else:
            #print '->not includes'
            return False
    else:# directly ==
        if RulePath == LinePath:
            #print '->equals'
            #print '(%s,  %s)'%(LinePath,RulePath)
            return True
        else:
            #print '->not equals'
            return False
            

def hitonerule(Line):
    global RuleList
    #print 'rule num=',len(RuleList)
    #print 'line=',Line
    for Rule in RuleList:
        if match(Line,Rule):
            #print 'match!'
            return True
    return False
    

def hitonespy(Line):
    global SpyList
    for Spy in SpyList:
        if Similar(Line,Spy):
            #print 'match!'
            return True
    return False

def getHitCnt(SrcFile,DstFile):
    global RuleList
    global CntList
    global SpyList
    fetfile = open (SrcFile)
    if len(RuleList)==0:
        print 'No XML found!'
        return
    if len(SpyList)==0:
        print 'No spy found!'
        return
    
    cnt1= 0
    cnt2= 0
    while 1:
        Line = fetfile.readline()
        if not Line:
            break
        hitxml=hitonerule(Line)
        hitspy=hitonespy(Line)
        
        if True==hitxml:
            cnt1+=1
        if True==hitspy and False==hitxml:
            cnt2+=1
            
    cntSum=cnt1+cnt2
    CntList.append('%d(%d,%d) %s\n'%(cntSum,cnt1,cnt2,SrcFile))
    
    threshold=1
    if cntSum>threshold:
        open(DstFile, "wb").write(open(SrcFile,"rb").read())
#end


#srcDir ='./Sample/Fet/Black'
srcDir ='./Sample/Fet/Black'
#srcDir ='./Sample/Fet/White/2013_04_27'
dstDir ='./Sample/Fet_del01/Black'

def ProcessDir(SrcDir,DstDir):
    global CntList
    cnt=0
    for f in os.listdir(SrcDir):
        if cnt%2000==0:
            print 'file num=',cnt
        SrcFile=os.path.join(SrcDir, f)
        DstFile=os.path.join(DstDir, f)
        if os.path.isfile(SrcFile):
            if not os.path.exists(DstDir):
                os.makedirs(DstDir)
            getHitCnt(SrcFile,DstFile)
            cnt+=1
        elif os.path.isdir(SrcFile):
            if not os.path.exists(DstFile):
                os.makedirs(DstFile)
            ProcessDir(SrcFile,DstFile)

    outfile = open ('Cnt_black_del01.log','w')
    for item in CntList:
        #print item
        outfile.write(item)
    

def getFromXML():
    global RuleList
    xmlfile = open ('xmlfet3.log')
    while 1:
        Line = xmlfile.readline()
        if not Line:
            break
        RuleList.append(Line)
    xmlfile.close()

def getFromLog():
    global SpyList   
    spyfile = open ('spyfet.log')
    while 1:
        Line = spyfile.readline()
        if not Line:
            break
        SpyList.append(Line)
    spyfile.close()



st=time.clock()
getFromXML()
getFromLog()
ProcessDir(srcDir,dstDir)
et=time.clock()
print 'time consumed:%d'%(et-st)
