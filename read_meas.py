import sys
from optparse import OptionParser
from rawparser import RawParser

infile = ""
outfile = ""
verbose = True

def ParseInput ():
	""" @brief Parse command line"""

	global infile
	global outfile
	global verbose
	
	parser = OptionParser()
	parser.add_option("-i", "--infile", dest="infile", help="parse IN_FILE", metavar="IN_FILE")
	parser.add_option("-o", "--outfile", dest="outfile", help="output to HDF5 OUT_FILE", metavar="OUT_FILE")
	parser.add_option("-v", "--verbose", action="store_false", dest="verbose", default=False, help="don't print status messages to stdout")
	(options, args) = parser.parse_args()

	if (options.infile):
		infile = options.infile
		outfile = options.outfile
		verbose = options.verbose
		return True
	else:
		print ("Error:")
		print ("  No file name specified. Exiting!")
		return False


def main (argv=None):

	global infile
	global outfile
	global verbose

	if argv is None:
		argv = sys.argv
		
	if (ParseInput ()):

		rp = 0

		try:
			rp = RawParser (infile)
		except:
			print ("Initialising raw parser failed. Exiting!")
			return 1

		try:
			rp.ParseData ()
		except:
			print ("Parsing data failed. Exiting!")
			return 2

		'''try:'''
		rp.SaveData (outfile)
		'''except:
			print ("Saving output failed. Exiting!")
			return 3'''

		if (rp):
			del rp;

	else:
		return 1
	

if __name__ == '__main__':
	sys.exit(main())

