#!/usr/bin/python
# -*- coding: utf-8 -*-

import difflib
# import Levenshtein
from mymodlevenshtein import mymodlevenshtein
import itertools, string
from chemicalFormulasC import split_chemical_formula
from mrtsound import *


def Dscore(mA_name, mB_name, **kwargs):
	'''Calculate Difference score'''
	A = (kwargs['A'] if 'A' in kwargs else 1.)
	B = (kwargs['B'] if 'B' in kwargs else 1.)
	L = min(len(str(mA_name)), len(str(mB_name)))

	R = difflib.SequenceMatcher(None, mA_name, mB_name).ratio()
	# E = Levenshtein.distance(mA_name, mB_name)
	E = mymodlevenshtein(mA_name, mB_name,1,1)

	# previously used equation
	# cscore = (1+(float(1) - ratio)*d_distance)*float(formula_similarity[0])
	return A*(1.-R) + B*(E/L), R, E

def rate_metabolite_pair(A, B, Alpha, Beta, ignore_compartments,check_id,phonetic,tolerate_h):
	if not ignore_compartments:
		compartments_match = compare_compartments(A.compartment_id, B.compartment_id)
		if compartments_match == 0:
			# print("c"),
			return {'ok': False, 'reason':'c', 'idA':A.id, 'idB': B.id}
	if check_id:
		print("check_id True")
		if p[0].id == p[1].id:
			# print("i"),
			return {'ok': True, 'reason':'id', 'idA':A.id, 'idB': B.id, 'dscore':0}
			# final_list.append([ p[0].id, p[1].id ,0])
	# fsim = 0.5
	# diff_h_count = 0
	# diff_other_count = 0
	fsim, diff_h_count, diff_other_count = calculate_formula_similarity(A.splitted_formula,B.splitted_formula)
	if diff_other_count > 0:
		# print("O"),
		return {'ok': False, 'reason':'o', 'idA':A.id, 'idB': B.id}
	if diff_h_count > tolerate_h:
		# print("H"),
		return {'ok': False, 'reason':'h', 'idA':A.id, 'idB': B.id}
	# print("At this point everything should be fine.")
	if phonetic:
		mA_name = mrtsound(A.name)
		mB_name = mrtsound(B.name)
	else:
		mA_name = A.name
		mB_name = B.name
	# dscore = Dscore(p[0].name,p[1].name,A=Alpha, B=Beta)
	score,ratio,distance = Dscore(mA_name, mB_name, A=Alpha, B=Beta)
	# S = (D + C) · F
	realscore = (score + 0.5)*fsim
	return {'ok': True, 'reason':'none', 'idA':A.id, 'idB': B.id, 'nameA':A.name, 'nameB':B.name, 'formulaA':A.formula, 'formulaB':B.formula, 'dscore':realscore, 'ratio': ratio, 'distance': distance, 'fsim':fsim, 'diff_h_count':diff_h_count, 'compartments_match':compartments_match}




def filtered_metabolite_lists(metabolitesA, metabolitesB):
	## Create metabolites filters
	met_filters_a = []
	met_filters_b = []
	for m in metabolitesA:
		if m.filtered == True:
			met_filters_a.append(m.get_id())
	for m in metabolitesB:
		if m.filtered == True:
			met_filters_b.append(m.get_id())

	list_a = []
	list_b = []
	for m in metabolitesA:
		if m.get_id() not in met_filters_a:
			list_a.append(m)
	for m in metabolitesB:
		if m.get_id() not in met_filters_b:
			list_b.append(m)
	return list_a, list_b

def compare_formulas(f1,f2):
	if len(f1) == 0 or len(f2) == 0:
		return -1
	elif f1 == f2:
		return 1
	else:
		return 0

def compare_compartments(c1,c2):
	if len(c1) == 0 or len(c2) == 0:
		return -1
	elif c1 == c2:
		return 1
	else:
		return 0

# this is to format output for list
def format_output_for_liststore(fsim,diff_h_count,compartments_match):
	if compartments_match == 1:
		out_comp = ""
	elif compartments_match == -1:
		out_comp = "?"
	else:
		out_comp = "!"

	out_form = ""
	if diff_h_count > 0:
		out_form = "H"+str(diff_h_count)
	if fsim == 1:
		out_form = "?"

	return {'out_comp':out_comp, 'out_form':out_form}


def calculate_formula_similarity(f1,f2):
	"""Processes already splitted formulas."""
	# try:
	# 	splitted_formula1 = split_chemical_formula(f1)
	# 	splitted_formula2 = split_chemical_formula(f2)
	# except:
	# 	# print ("Cannot split formula.")
	# 	# return 1 # This number will be used as a multiplier later. So "1" means "nothing".
	# 	return 1,0,0
	if f1==False or f2 == False:
		return 1,0,0
	else:
		splitted_formula1 = f1
		splitted_formula2 = f2
	# print(splitted_formula1)
	# print(splitted_formula2)
	# print("\n-------------New pair------------")

	# we have to find the longest formula to efficiently compare pairwise
	if len(splitted_formula1) > len(splitted_formula2):
		longest_formula = splitted_formula1
		shortest_formula = splitted_formula2
	else:
		if len(splitted_formula1) == len(splitted_formula2):
			longest_formula = splitted_formula1
			shortest_formula = splitted_formula2
		else:
			longest_formula = splitted_formula2
			shortest_formula = splitted_formula1

	# print(f1,f2)
	# print("long",longest_formula)
	# print("short",shortest_formula)
	differences = {}
	found = False
	for x1 in longest_formula:
		found = False
		# print("New x1")
		# print(x1)
		for x2 in shortest_formula:
			# print("New x2")
			# print(x2)
			if x1[0] == x2[0]: # if chemical elements match, then compare also atom count
				found = True
				# print("Elements match: " + str(x1[0]) +" and "+ str(x2[0]))
				if x1[1] == x2[1]: # here we compare atom count
					pass
				else: # if the atom count do not match then we start to count different atoms
					differences[x1[0]] = max(x1[1],x2[1]) - min(x1[1],x2[1])
			else: # in case where an element is not even found it is even worse.
				pass

		if not found:
			# print("+ Surplus element: "+str(x1[0])+str(x1[1]))
			differences[x1[0]] = x1[1]
	# print(f1,f2)
	# print("Differences: "),
	# print(differences)

	if len(differences) == 0:
		# return 0.5 # The value of 0.5 is the best possible. It means that formulas are identical.
		return 0.5,0,0

	# The formula is this: = (1 - (minH/maxH))*0.5 + 0.5
	# Count all differences
	diff_atom_count = 0
	diff_h_count = 0
	h_involved=False
	for x in differences:
		if x == 'H':
			pass # We have to count H atoms separately
			diff_h_count+=differences[x]
			h_involved=True
		else:
			diff_atom_count+=differences[x]
	# find H ratio
	if h_involved:
		H1 = 0
		H2 = 0
		for x in longest_formula:
			if x[0] == 'H':
				H1 = x[1]
		for x in shortest_formula:
			if x[0] == 'H':
				H2 = x[1]
		H1+=1
		H2+=1
		maxH = max(H1,H2)
		minH = min(H1,H2)

		ratioH = float(minH)/(maxH)
	else:
		ratioH = 1

	# similarity = 0.5*ratioH+diff_atom_count
	similarity = (float(1) - ratioH)*0.5 + 0.5 + diff_atom_count
	return similarity, diff_h_count, diff_atom_count
