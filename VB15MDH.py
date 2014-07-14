ACQEND             = 2**0
RTFEEDBACK         = 2**1
HPFEEDBACK         = 2**2
ONLINE             = 2**3
OFFLINE            = 2**4
SYNCDATA           = 2**5
LASTSCANINCONCAT   = 2**8
RAWDATACORRECTION  = 2**10
LASTSCANINMEAS     = 2**11 # Last scan in measurement
SCANSCALEFACTOR    = 2**12 # Specific additional scale factor
SECONDHADAMARPULSE = 2**13 # 2nd RF excitation of HADAMAR
REFPHASESTABSCAN   = 2**14 # Reference phase stabilisation scan
PHASESTABSCAN      = 2**15 # Phase stabilisation scan
D3FFT              = 2**16 # Subject to 3D FFT
SIGNREV            = 2**17 # Sign reversal
PHASEFFT           = 2**18 # Perform PE FFT
SWAPPED            = 2**19 # Swapped phase/readout direction
POSTSHAREDLINE     = 2**20 # Shared line
PHASCOR            = 2**21 # Phase correction data
PATREFSCAN         = 2**22 # PAT reference data
PATREFANDIMASCAN   = 2**23 # PAT reference and imaging data
REFLECT            = 2**24 # Reflect line
NOISEADJSCAN       = 2**25 # Noise adjust scan
SHARENOW           = 2**26 # All lines are acquired from the actual and previous e.g. phases
LASTMEASUREDLINE   = 2**27 # Last measured line of all succeeding e.g. phases
FIRSTSCANINSLICE   = 2**28 # First scan in slice (needed for time stamps)
LASTSCANINSLICE    = 2**29 # Last scan in slice  (      "       "       )
TREFFECTIVEBEGIN   = 2**30 # Begin time stamp for TReff (triggered measurement)
TREFFECTIVEEND     = 2**31 # End time stamp for TReff (triggered measurement)

MDHSIZE            = 128

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.iteritems())
    enums['reverse_mapping'] = reverse
    return type('Enum', (), enums)

md = enum ('COL', 'LIN', 'SLC', 'PAR', 'ECO', 'PHS', 'REP', 'SET', 'SEG', 'CHA', 'IDA', 'IDB', 'IDC', 'IDD', 'IDE', 'AVE')

def mask_set(v, b):
	return v&b
