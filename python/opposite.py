import os,sys,glob
from gribapi import *
import numpy

def opposite(prefix):
    fclist=glob.glob(prefix+'*'+'N000')
    
    for fcn in fclist:
        nprefix=fcn.split('N000')[0]
        f=open(nprefix+'N{:0>3}'.format(0),'rb')
        fcvalues=[]
        while 1:
            try:
                fid=grib_new_from_file(f)
                if fid is not None:
                    fcvalues.append(grib_get_array(fid,'values'))
                    grib_release(fid)
                else:
                    break
            except:
                break
        for i in range(1,26):
            try:
                g=open(nprefix+'N{:0>3}'.format(i),'rb')
                h=open(nprefix+'N{:0>3}'.format(i+25),'wb')
                j=0
                while 1:
                    try:
                        gid=grib_new_from_file(g)
                        if gid is not None:
                            values=grib_get_array(gid,'values')
                            grib_set_array(gid,'values',values-2*(values-fcvalues[j]))
                            grib_set(gid, 'number', i+25)
                            grib_write(gid,h)
                            grib_release(gid)
                            j+=1
                        else:
                            break
                    except:
                        break
                g.close()
                h.close()
                print('wrote '+nprefix+'N{:0>3}'.format(i+25))
            except:
                break
        f.close()
    return
                
if __name__ == "__main__":
    opposite(os.path.expandvars('EN'))

               
        
