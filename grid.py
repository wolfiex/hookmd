import numpy as np
import re

def get_decomp(data):
    rc = open(data+'/suite.rc','r').read()
    ew = int(re.findall('MAIN_ATM_PROCX=(\d+)',rc)[0])
    ns = int(re.findall('MAIN_ATM_PROCY=(\d+)',rc)[0])

    return calc_decomp(nproc_ew       = ew,
                       nproc_ns       = ns  )


'''
netcdf/ncfile_write_horiz_dim.F90:508



'''

def calc_decomp(#global_row_len = 192,
                global_n_rows  = 144,
                nproc_ew       = 16,
                nproc_ns       = 12):

    global_row_len = nproc_ew * nproc_ns


    """
    calculate the domain decomposition of a UM grid.
    adapted from control/mpp/decomp_db.F90 (vn10.6.1)

    {THIS FN} CODE FROM LUKE ABRAHAM

    suite conf - domain decomposition, atomsphere
    max no
    east west
    north sough

    {% set MAIN_ATM_PROCX=24 %}
    {% set MAIN_ATM_PROCY=21 %}


    """
    size_x = np.zeros(nproc_ew,dtype=np.int32)
    size_y = np.zeros(nproc_ns,dtype=np.int32)
    start_x = np.zeros(nproc_ew,dtype=np.int32)
    start_y = np.zeros(nproc_ns,dtype=np.int32)
    end_x = np.zeros(nproc_ew,dtype=np.int32)
    end_y = np.zeros(nproc_ns,dtype=np.int32)

    mapping = np.zeros([7,nproc_ew*nproc_ns],dtype=np.int32)

    #EW
    start=0
    rsize=np.int(global_row_len/nproc_ew)
    irest=global_row_len-(rsize*nproc_ew)

    for iproc in range(1, nproc_ew+1):
        start_x[iproc-1] = start
        if iproc <= nproc_ew/2:
            if iproc <= irest/2:
                size_x[iproc-1] = rsize+1
            else:
                size_x[iproc-1] = rsize
        else:
            if iproc-(nproc_ew/2) <= irest/2:
                size_x[iproc-1] = rsize+1
            else:
                size_x[iproc-1] = rsize

        start=start+size_x[iproc-1]
        end_x[iproc-1] = start_x[iproc-1] + size_x[iproc-1]

    #NS
    start=0
    rsize=np.int(global_n_rows/nproc_ns)
    irest=global_n_rows-(rsize*nproc_ns)

    for iproc in range(1, nproc_ns+1):
        size_y[iproc-1] = rsize

    if irest  >=  1:
        size_y[0]=rsize+1
        irest=irest-1

    if np.mod(nproc_ns,2)  ==  0:
        prow_s=nproc_ns/2
        prow_n=prow_s+1
    else:
        prow_s=int(nproc_ns/2)+1
        prow_n=prow_s

    while irest  >=  1:
        if prow_n  ==  prow_s:
            size_y[prow_n-1]=rsize+1
            irest=irest-1
        else:
            size_y[prow_s-1]=rsize+1
            irest=irest-1
            if irest  >=  1:
                size_y[prow_n-1]=rsize+1
                irest=irest-1
        prow_s=max([1,prow_s-1])
        prow_n=min([nproc_ns,prow_n+1])

    for iproc in range(1,nproc_ns+1):
        start_y[iproc-1]=start
        start=start+size_y[iproc-1]
        end_y[iproc-1] = start_y[iproc-1] + size_y[iproc-1]


    # assign to procs
    for iproc_y in range(0,nproc_ns):
        for iproc_x in range(0,nproc_ew):
            iproc = iproc_x + (iproc_y*nproc_ew)

            mapping[0,iproc] = iproc+1 # these start at 1
            mapping[1,iproc] = start_x[iproc_x]
            mapping[2,iproc] = end_x[iproc_x]
            mapping[3,iproc] = start_y[iproc_y]
            mapping[4,iproc] = end_y[iproc_y]



    # midpoints for plot (slice stop+1)
    mapping[5] = np.mean(mapping[1:3],axis=0)
    mapping[6] = np.mean(mapping[3:5],axis=0)

    return mapping
