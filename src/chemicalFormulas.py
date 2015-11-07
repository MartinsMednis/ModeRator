# chemicalFormulas.py
#
# Original code by Paul McGuire
# Code obtained from Python forum http://www.daniweb.com/software-development/python/threads/102740
# Code shared in forum in Dec 29th, 2007
#
# wrapped and adapted by Martins Mednis
#

from pyparsing import Word, Optional, OneOrMore, Group, ParseException

# define a simple Python dict of atomic weights, with chemical symbols
# for keys



atomicWeight = {
	'Ac': 227.000000,
	'Ag': 107.868000,
	'Al': 26.981540,
	'Am': 243.000000,
	'Ar': 39.948000,
	'As': 74.921600,
	'At': 210.000000,
	'Au': 196.966500,
	'B': 10.811000,
	'Ba': 137.330000,
	'Be': 9.012180,
	'Bi': 208.980400,
	'Br': 79.904000,
	'C': 12.011000,
	'Ca': 40.078000,
	'Cd': 112.410000,
	'Ce': 140.120000,
	'Cl': 35.452700,
	'Co': 58.933200,
	'Cr': 51.996000,
	'Cs': 132.905400,
	'Cu': 63.546000,
	'Dy': 162.500000,
	'Er': 167.260000,
	'Eu': 151.965000,
	'F': 18.998400,
	'Fe': 55.847000,
	'Fr': 223.000000,
	'Ga': 69.723000,
	'Gd': 157.250000,
	'Ge': 72.610000,
	'H': 1.007940,
	'He': 4.002600,
	'Hf': 178.490000,
	'Hg': 200.590000,
	'Ho': 164.930300,
	'I': 126.904500,
	'In': 114.820000,
	'Ir': 192.220000,
	'K': 39.098300,
	'Kr': 83.800000,
	'La': 138.905500,
	'Li': 6.941000,
	'Lu': 174.967000,
	'Mg': 24.305000,
	'Mn': 54.938000,
	'Mo': 95.940000,
	'N': 14.006700,
	'Na': 22.989770,
	'Nb': 92.906400,
	'Nd': 144.240000,
	'Ne': 20.179700,
	'Ni': 58.693400,
	'Np': 237.048200,
	'O': 15.999400,
	'Os': 190.200000,
	'P': 30.973760,
	'Pa': 231.035900,
	'Pb': 207.200000,
	'Pd': 106.420000,
	'Pm': 145.000000,
	'Po': 209.000000,
	'Pr': 140.907700,
	'Pt': 195.080000,
	'Pu': 244.000000,
	'Ra': 226.025400,
	'Rb': 85.467800,
	'Re': 186.207000,
	'Rh': 102.905500,
	'Rn': 222.000000,
	'Ru': 101.070000,
	'S': 32.066000,
	'Sb': 121.757000,
	'Sc': 44.955900,
	'Se': 78.960000,
	'Si': 28.085500,
	'Sm': 150.360000,
	'Sn': 118.710000,
	'Sr': 87.620000,
	'Ta': 180.947900,
	'Tb': 158.925300,
	'Tc': 98.000000,
	'Te': 127.600000,
	'Th': 232.038100,
	'Ti': 47.880000,
	'Tl': 204.383000,
	'Tm': 168.934200,
	'U': 238.029000,
	'V': 50.941500,
	'W': 183.850000,
	'Xe': 131.290000,
	'Y': 88.905900,
	'Yb': 173.040000,
	'Zn': 65.390000,
	'Zr': 91.224000,
	'R': 0.0, ## nonexistent element for residuals
	'X': 0.0, ## nonexistent element for unknown compounds
	'L': 0.0, ## nonexistent element for whatever
	'T': 0.0 ## nonexistent element for whatever
}


def split_chemical_formula(formula):
	def is_number(s):
		try:
			float(s)
			return True
		except ValueError:
			return False

	def replace_things(stringg,listt,replacement):
		for x in listt:
			stringg = stringg.replace(x, replacement)
		return stringg

	bad_chars = ["(", ")", "-","."]
	formula = replace_things(formula,bad_chars,"|")

	if is_number(formula):
		return [['',0]]

	if len(formula) == 0:
		return [['',0]]







	# define some strings to use later, when describing valid lists
	# of characters for chemical symbols and numbers
	caps = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
	lowers = caps.lower()
	digits = "0123456789"

	# Version 1




	# Version 2 - Auto-convert integers, and add results names
	def convertIntegers(tokens):
		return int(tokens[0])

	element = Word( caps, lowers )
	integer = Word( digits ).setParseAction( convertIntegers )
	elementRef = Group( element("symbol") + Optional( integer, default=1 )("qty") )
	# pre-1.4.7, use this:
	# elementRef = Group( element.setResultsName("symbol") + Optional( integer, default=1 ).setResultsName("qty") )
	chemicalFormula = OneOrMore( elementRef )



	# Version 3 - Compute partial molecular weight per element, simplifying
	# summing
	# No need to redefine grammar, just define parse action function, and
	# attach to elementRef
	def computeElementWeight(tokens):
		element = tokens[0]
		element["weight"] = atomicWeight[element.symbol] * element.qty

	elementRef.setParseAction(computeElementWeight)


	formulaData = chemicalFormula.parseString(formula)
	mw = sum( [ element.weight for element in formulaData ] )
	return formulaData
