#!/bin/python
# -*- coding: utf-8 -*-


import string
import math






def mrtsound(stringg):
	def replace_things(stringg,listt,replacement):
		for x in listt:
			stringg = stringg.replace(x, replacement)
		return stringg

	def is_numeric(s):
		try:
			float(s)
			return True
		except ValueError:
			return False
		
	def strip_unspeakable(datas):
		
		#print(datas,len(result))
		#if len(result) == 0:
		#	result = "Empty"
		# result = datas

		vowels = ["[", "]", "-", "(", ")", "_", ",", "'", "`", " "];
		result = replace_things(datas,vowels,"")

		result =  string.lower(result)
		result = result.replace("phosphate", "PHSPE")
		result = result.replace("acetoin", "actn")
		result = result.replace("ethanol", "ETOH")
		result = result.replace("thiamine", "THI")
		result = result.replace("hypoxanthine", "HYXN")
		result = result.replace("tetrahydrofolate", "THF")
		result = result.replace("hydrofolate", "HF")
		result = result.replace("guanine", "GNN")
		result = result.replace("folate", "FOL")
		result = result.replace("mannitol", "MNTL")
		result = result.replace("lactose", "LACT")
		result = result.replace("adenosinediphosphate", "ADP")
		result = result.replace("adenosinetriphosphate", "ATP")
		result = result.replace("glucose", "GLC")
		result = result.replace("fructose", "FRC")
		result = result.replace("nitrogen", "N2")
		result = result.replace("natrium", "Na")
		result = result.replace("sodium", "Na")
		result = result.replace("water", "H2O")
		result = result.replace("cellobiose", "CELB")
		result = result.replace("riboflavin", "RIBF")
		result = result.replace("lactate", "LCTT")
		result = result.replace("biotin", "BIOT")
		result = result.replace("biomass", "BMASS")
		
		

		# pyridoxol, pyridoxine are synonyms
		result = result.replace("pyridoxol", "PRDX")
		result = result.replace("pyridoxine", "PRDX")
		
		result = result.replace("adenosine", "ADSIIN")
		result = result.replace("adenonsine", "ADNONSIIN")
		result = result.replace("cysteine", "CYSTIN")
		result = result.replace("malate", "MLT")
		result = result.replace("maleate", "MLEAT")
		result = result.replace("flavin", "FLV")
		result = result.replace("hydro", "HDR")
		result = result.replace("ulose", "ULS")
		result = result.replace("arate", "ART")
		result = result.replace("rate", "RTE")
		result = result.replace("tate", "TT")
		result = result.replace("oate", "OT")
		result = result.replace("tose", "TS")
		result = result.replace("cose", "CE")
		result = result.replace("nnose", "NNS")
		result = result.replace("mnose", "MNS")
		result = result.replace("biose", "BS")
		result = result.replace("rone", "RN")
		result = result.replace("late", "LT")
		result = result.replace("amine", "AMN")
		result = result.replace("nine", "NNE")
		
		result = result.replace("mide", "MD")
		result = result.replace("midine", "DE")

		result = result.replace("itol", "TL")
		result = result.replace("nol", "NL")
		result = result.replace("oxo", "OX")
		result = result.replace("but", "BT")
		result = result.replace("toin", "TN")
		result = result.replace("propan", "PN")
		result = result.replace("isopropyl", "IRO")
		




		result =  string.lower(result)

		


		return result

	# 


	def find_number(stringg):
		start=-1
		end=-1
		for x in range(len(stringg)):
			if is_numeric(stringg[x]):
				if start<0:
					start = x
					end = x
				else:
					end = x
			else:
				if start>-1:
					break

		if start>-1:
			return stringg[start:end+1]
		else:
			return False
		pass

	
	#print(find_number(stringg))
	while find_number(stringg):
		number = find_number(stringg)
		wnumber = string.strip(num2eng(number))
	#	print("wnumber",wnumber)
		stringg = stringg.replace(number, wnumber)
		stringg = string.strip(stringg)
	stringg = strip_unspeakable(stringg)
	return stringg


 

 
#FIXME: Currently num2eng(1012) -> 'one thousand, twelve'
# do we want to add last 'and'?
def num2eng(num):
# Algorithm from http://mini.net/tcl/591 
# Original author: 'Miki Tebeka <tebeka@cs.bgu.ac.il>'

	# Tokens from 1000 and up
	_PRONOUNCE = [ 
		'vigintillion',
		'novemdecillion',
		'octodecillion',
		'septendecillion',
		'sexdecillion',
		'quindecillion',
		'quattuordecillion',
		'tredecillion',
		'duodecillion',
		'undecillion',
		'decillion',
		'nonillion',
		'octillion',
		'septillion',
		'sextillion',
		'quintillion',
		'quadrillion',
		'trillion',
		'billion',
		'million ',
		'thousand ',
		''
	]
	 
	# Tokens up to 90
	_SMALL = {
		'0' : '',
		'1' : 'one',
		'2' : 'two',
		'3' : 'three',
		'4' : 'four',
		'5' : 'five',
		'6' : 'six',
		'7' : 'seven',
		'8' : 'eight',
		'9' : 'nine',
		'10' : 'ten',
		'11' : 'eleven',
		'12' : 'twelve',
		'13' : 'thirteen',
		'14' : 'fourteen',
		'15' : 'fifteen',
		'16' : 'sixteen',
		'17' : 'seventeen',
		'18' : 'eighteen',
		'19' : 'nineteen',
		'20' : 'twenty',
		'30' : 'thirty',
		'40' : 'forty',
		'50' : 'fifty',
		'60' : 'sixty',
		'70' : 'seventy',
		'80' : 'eighty',
		'90' : 'ninety'
	}
	 
	def get_num(num):
		'''Get token <= 90, return '' if not matched'''
		return _SMALL.get(num, '')
	 
	def triplets(l):
		'''Split list to triplets. Pad last one with '' if needed'''
		res = []
		for i in range(int(math.ceil(len(l) / 3.0))):
			sect = l[i * 3 : (i + 1) * 3]
			if len(sect) < 3: # Pad last section
				sect += [''] * (3 - len(sect))
			res.append(sect)
		return res
	 
	def norm_num(num):
		"""Normelize number (remove 0's prefix). Return number and string"""
		n = int(num)
		return n, str(n)
	 
	def small2eng(num):
		'''English representation of a number <= 999'''
		n, num = norm_num(num)
		hundred = ''
		ten = ''
		if len(num) == 3: # Got hundreds
			hundred = get_num(num[0]) + ' hundred'
			num = num[1:]
			n, num = norm_num(num)
		if (n > 20) and (n != (n / 10 * 10)): # Got ones
			tens = get_num(num[0] + '0')
			ones = get_num(num[1])
			ten = tens + ' ' + ones
		else:
			ten = get_num(num)
		if hundred and ten:
			return hundred + ' ' + ten
			#return hundred + ' and ' + ten
		else: # One of the below is empty
			return hundred + ten


	'''English representation of a number'''
	num = str(long(num)) # Convert to string, throw if bad number
	if (len(num) / 3 >= len(_PRONOUNCE)): # Sanity check
		raise ValueError('Number too big')
 
	if num == '0': # Zero is a special case
		return 'zero'
 
	# Create reversed list
	x = list(num)
	x.reverse()
	pron = [] # Result accumolator
	ct = len(_PRONOUNCE) - 1 # Current index
	for a, b, c in triplets(x): # Work on triplets
		p = small2eng(c + b + a)
		if p:
			pron.append(p + ' ' + _PRONOUNCE[ct])
		ct -= 1
	# Create result
	pron.reverse()
	return ', '.join(pron)


