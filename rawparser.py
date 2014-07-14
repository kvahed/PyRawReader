"""
           Measurement file reader for VB13-17
  
  Authors: Kaveh Vahedipour (k.vahedipour@fz-juelich.de)
           Marcus Boland (m.boland@fz-juelich.de)
 
"""



import io
import time
import struct
import numpy as np
import h5py
import VB15MDH

from VB15MDH import *
from numpy import uint32
from subprocess import call
from numpy.core.numeric import dtype

KB =      1024.0
MB = KB * 1024.0 # megabytes
GB = MB * 1024.0

# Helper function
def _map_noise(x):
	if x == 0:
		return 1
	else:
		return x

class RawParser :
	""" Raw data parser for Syngo MR measurement files """
        
	def __init__(self, fname):
		''' Open file and define defaults '''
                
		self.init = False
                
		try:
			self.ios = io.open (fname, 'rb')
		except IOError:
			print ("RawParser._init__\n ERROR: Opening %s failed." % fname)
			raise

		self.fbuf      = io.BufferedReader(self.ios)

		self.init      = True

		self.fname     = fname
		
		self.data      = 0
		self.sync      = 0
		self.noise     = 0
		self.acs       = 0
                
		self.dims      = np.array ([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype='<H')
		self.noisedims = np.array ([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype='<H')
                
		self.last_line = False

		self.syncdims  = np.array ([0, 0])
		self.nch       = 0
		self.ncolb     = 0
		self.noisencolb= 0

		self.dt        = np.dtype('c8')
		self.ds        = 8

		self.sddt      = np.dtype('<f')
		self.sdds      = 4
		
		self.nddt      = np.dtype('c8')
		self.ndds      = 8


	def JumpToDataStart (self):
		''' Jump to start of raw data '''

		size = struct.unpack ('i', self.fbuf.read(4))
		self.fbuf.seek (size[0],0)

		return


	def CalcFileSize (self):
		''' Calculate entire size of raw data '''
		
		start = self.fbuf.tell()
		self.fbuf.seek (   -1,2)
		size  = self.fbuf.tell()
		self.fbuf.seek (start,0)

		return size


	def ParseMDH (self, n = 0, dry = False):
		''' Parse one MDH entry '''

		self.bm = struct.unpack_from ('2I', self.buf, n +  20)
		if (self.bm[0] & SYNCDATA):
			return n + MDHSIZE
		
		if (self.bm[0] & NOISEADJSCAN):
			self.lc  = struct.unpack_from ('%dH' % 16, self.buf, n + 28) # loop counters
			self.ch  = struct.unpack_from ('H', self.buf, n + 124)
	
			if (dry):
				if (self.noisedims[0] == 0):
					self.noisedims[0] = self.lc[0]
					self.noisedims[1] = struct.unpack_from ('H', self.buf, n + 30)[0]
					self.noisencolb = self.noisedims[md.COL] * self.ndds
					self.noisedims[2:16] = np.array(self.lc[2:16])
				else:
					self.noisedims[2:16] = np.maximum (self.noisedims[2:16],self.lc[2:16])
			return n + MDHSIZE
				
		self.lc  = struct.unpack_from ('%dH' % 16, self.buf, n + 28) # loop counters
		self.ch  = struct.unpack_from ('H', self.buf, n + 124)

		if (dry):
			if (self.dims[0] == 0):
				self.dims[0] = self.lc[0]
				self.dims[1] = struct.unpack_from ('H', self.buf, n + 30)[0]
				self.ncolb = self.dims[md.COL] * self.ds
				self.dims[2:16] = np.array(self.lc[2:16])
			else:
				self.dims[2:16] = np.maximum (self.dims[2:16],self.lc[2:16])

		return n + MDHSIZE


	def ParseScan (self, c, i, dryrun = False):

		bend = i+self.ncolb

		if (dryrun):
			return bend
		self.data[
			:, self.ch, self.lc[ 2],self.lc[ 3],self.lc[ 4],self.lc[ 5],self.lc[6],
			self.lc[ 7],self.lc[ 8],self.lc[ 9],self.lc[10],self.lc[11],self.lc[12],
			self.lc[13],self.lc[14],0] = np.reshape(
				np.fromstring (self.buf[i:bend], self.dt), (self.dims[0],1))

		return bend

	def ParseNoiseData (self, c, i, dryrun = False):

		bend = i+self.noisencolb

		if (dryrun):
			return bend

		self.noise[:, self.ch] = np.reshape(np.fromstring(self.buf[i:bend], self.nddt), (self.noisedims[0],1))

		return bend
	
	def ParseSyncData (self, c, i, dryrun = False):

		ndata = struct.unpack_from('i', self.buf, i)[0]
		nhead = 64
		bend  = i + nhead + ndata

		
		if (dryrun):
			self.syncdims[1] = self.syncdims[1] + 1
			if (self.syncdims[0] == 0):
				self.syncdims[0] = ndata/4
		else:
			self.sync[:,c] = np.fromstring (self.buf[i+nhead:bend], self.sddt)

		return bend


	def SaveData (self, fname, verbose = True):

		if (verbose):
			print ("  Saving measurement to %s ... " % fname)

		start = time.clock()

		f = h5py.File(fname, 'w')

		f['data_r'] = np.squeeze(np.real(self.data).transpose())
		f['data_i'] = np.squeeze(np.imag(self.data).transpose())

		if (self.noise != 0):
			f['noise_r'] = np.squeeze(np.real(self.noise).transpose())
			f['noise_i'] = np.squeeze(np.imag(self.noise).transpose())
		
		if (self.acs != 0):
			f['acs_r'] = np.squeeze(np.real(self.acs).transpose())
			f['acs_i'] = np.squeeze(np.imag(self.acs).transpose())
		
		if (self.sync.any() != 0):
                        f['sync']  = self.sync.transpose()

		f.close()

		if (verbose):
			print '    ... saved in %(time).1f s.\n' % {"time": time.clock()-start}

		return


	def ParseProtocol (self, verbose = True):

		if (verbose):
			print ("  Parsing XProtocol ..." )

		if (verbose):
			print '    ... found \n' , self.dims

		return


	def AllocateRAM (self, verbose = True):

		ramsz = np.prod(self.dims) * self.ds / MB

		if (verbose):
			print '  Allocating %.1f MB of RAM' % ramsz

			print '    Data (dims: %(a)d %(b)d %(c)d %(d)d %(e)d %(f)d %(g)d %(h)d %(i)d %(j)d %(k)d %(l)d %(m)d %(n)d %(o)d %(p)d)' % {
				"a": self.dims[ 0], "b": self.dims[ 1], "c": self.dims[ 2], "d": self.dims[ 3], "e": self.dims[ 4], "f": self.dims[ 5],
				"g": self.dims[ 6],	"h": self.dims[ 7], "i": self.dims[ 8], "j": self.dims[ 9], "k": self.dims[10], "l": self.dims[11],
				"m": self.dims[12], "n": self.dims[13],	"o": self.dims[14], "p": self.dims[15]}
			
			print '    Noise (dims: %(a)d %(b)d %(c)d %(d)d %(e)d %(f)d %(g)d %(h)d %(i)d %(j)d %(k)d %(l)d %(m)d %(n)d %(o)d %(p)d)' % {
				"a": self.noisedims[ 0], "b": self.noisedims[ 1], "c": self.noisedims[ 2], "d": self.noisedims[ 3], "e": self.noisedims[ 4], "f": self.noisedims[ 5],
				"g": self.noisedims[ 6],	"h": self.noisedims[ 7], "i": self.noisedims[ 8], "j": self.noisedims[ 9], "k": self.noisedims[10], "l": self.noisedims[11],
				"m": self.noisedims[12], "n": self.noisedims[13],	"o": self.noisedims[14], "p": self.noisedims[15]}
			
			if (self.syncdims[0]):
				print '    SyncData (dims: %(a)d %(b)d )' % {"a": self.syncdims[0], "b": self.syncdims[1]}

		self.data = np.ndarray(shape=self.dims, dtype=self.dt)
		self.sync = np.ndarray(shape=self.syncdims, dtype=self.sddt)
		self.noise = np.ndarray(shape=filter(lambda x:x>0,self.noisedims), dtype=self.nddt)

		if (verbose):
			print ("    ... done.\n" % ramsz)

		return


	def ReadMeas (self, verbose = True):

		self.JumpToDataStart ()

		start = time.clock()
		csize = self.CalcFileSize () / MB
		self.size = csize

		if (verbose):
			print ("  Reading ca. %.1f MB headers and data ..." % csize)

		self.buf = self.fbuf.read()

		tsec  = time.clock() - start
		if (tsec==0):
			tsec = 1.0e-6
		drate = csize / tsec

		if (verbose):
			print '    ... read %(csize).1f MB in %(time).1f s (effective: %(drate).1f MB/s).\n' % {
				"csize": csize, "time": tsec, "drate": drate}
		
		return


	def ParseMeas (self, dry = False, verbose = True):

		if (verbose):
			print '  Parsing headers and data ...'
			if (dry):
				print '    dry run'

		start = time.clock()

		i = 0 # position in buf
		c = 0 # scan counter
		s = 0

		while (True):
				
			i = self.ParseMDH(i, dry)

			if (self.bm[0]&ACQEND):
				print '    hit ACQEND first'
				break

			if (self.bm[0]&SYNCDATA):
				i = self.ParseSyncData(s, i, dry)
				s = s + 1
			elif (self.bm[0]&NOISEADJSCAN):
				i = self.ParseNoiseData(c, i, dry)
			else:
				i = self.ParseScan(c, i, dry)
			
			c = c + 1

		tsec  = time.clock() - start
		rsize = i / MB
		if (tsec == 0):
			tsec = 1.0e-6
		drate = rsize / tsec

		if (dry):
			self.dims[2:16] = self.dims[2:16]+1

		if (verbose):
			print '    ... parsed %(rsize).1f MB in %(time).1f s (effective: %(drate).1f MB/s).\n' % {"rsize": rsize, "time": tsec, "drate": drate}
			
		return
	

	def ParseData (self, fastalloc = False, verbose = True):

		self.ReadMeas()

		if (fastalloc): 
			self.ParseProtocol()       
		else:           
			self.ParseMeas(True, True) 
			
		self.AllocateRAM()
		self.ParseMeas()

		return


	def __del__(self):
		""" Clean up """
		
		if (self.init):
			self.fbuf.detach()
			self.ios.close()
			self.data = []
			self.acs = []
			self.noise = []
			self.sync = []
			
		return
