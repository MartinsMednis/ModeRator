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
		vowels = ["[", "]", "-", "(", ")", "_", ",","'","`"];
		result = replace_things(datas,vowels," ")
		#print(datas,len(result))
		if len(result) == 0:
			result = "Empty"
		return result

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

	stringg = strip_unspeakable(stringg)
	#print(find_number(stringg))
	while find_number(stringg):
		number = find_number(stringg)
		wnumber = string.strip(num2eng(number))
		print("wnumber",wnumber)
		stringg = stringg.replace(number, wnumber)
		stringg = string.strip(stringg)
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
		"""Normalize number (remove 0's prefix). Return number and string"""
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


print(num2eng(4213))


print("'" + mrtsound("glucose-6-phosphate'2")+ "'")
print("'" + mrtsound("abc10ssssd11")+ "'")
