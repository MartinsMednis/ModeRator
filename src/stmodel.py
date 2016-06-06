# -*- coding: utf-8 -*-

##
##   Author: Martins Mednis, 2016. This program compares stoichiometric models
##
##    This program is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation, either version 3 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with this program.  If not, see <http://www.gnu.org/licenses/>
##

import sys
#os.environ['PYTHONPATH'] = '/usr/local/lib64/python2.7/site-packages/libsbml'
#sys.path.append('/usr/local/lib64/python2.7/site-packages/libsbml')

missing_modules = []

try:
	import xlrd
except ImportError:
	missing_modules.append("xlrd")

#try:
#	from libsbml import *
#except ImportError:
#	missing_modules.append("libsml")






libsbml_error=0
try:
	from libsbml import *
except ImportError:
	libsbml_error+=1
# try:
# 	from _libsbml import *
# except ImportError:
# 	libsbml_error+=1
if libsbml_error>1:
	missing_modules.append("libsbml SBML support")







try:
	from chemicalFormulas import split_chemical_formula
	#from modified_cycles import mod_simple_cycles
	import string, re, sys, os, pickle
	import itertools, difflib, subprocess, math
	#import jellyfish
except ImportError:
	print("\tImportant modules are missing.")
	exit()




def is_numeric(s):
	try:
		float(s)
		return True
	except ValueError:
		return False


def remove_html_tags(datas):
	p = re.compile(r'<.*?>')
	return p.sub('', datas)


def replace_things(stringg,listt,replacement):
	for x in listt:
		stringg = stringg.replace(x, replacement)
	return stringg

def prepare_item_id_for_sbml(datas):
	whattoreplace = ["[", "]", "-", "(", ")", " ", ","];
	result = replace_things(datas,whattoreplace,"_")
	#print(datas,len(result))
	if len(result) == 0:
		result = "Empty"
	if is_numeric(result[0]):
		result = "_"+result
	return result



def compare_ec_numbers(ec1,ec2):
	def strip_ec_numbers(string):
		return string.strip()
	if len(ec1) == 0 or len(ec2) == 0:
		return -1
	whattoreplace = ["or", "OR", "and", "AND", ";", ","];
	ec1 = replace_things(ec1,whattoreplace,"|")
	ec2 = replace_things(ec2,whattoreplace,"|")
	ec1 = ec1.split("|")
	ec2 = ec2.split("|")
	ec1 = map(strip_ec_numbers,ec1)
	ec2 = map(strip_ec_numbers,ec2)

	comon_things = 0

	for x in ec1:
		if x in ec2:
			comon_things+=1
	return comon_things

def count_ec_numbers(ec1,ec2):
	def strip_ec_numbers(string):
		return string.strip()
	if len(ec1) == 0 or len(ec2) == 0:
		return -1
	whattoreplace = ["or", "OR", "and", "AND", ";", ","];
	ec1 = replace_things(ec1,whattoreplace,"|")
	ec2 = replace_things(ec2,whattoreplace,"|")
	ec1 = ec1.split("|")
	ec2 = ec2.split("|")
	ec1 = map(strip_ec_numbers,ec1)
	ec2 = map(strip_ec_numbers,ec2)


	return max(len(ec1),len(ec2))


##############################################################################
#                      st_model
##############################################################################

class st_model(object):
	title = ""
	name = ""
	desc = ""
	#reactions = []
	#metabolites = []

	def __init__(self,title,desc):
		self.title = title
		self.name = title
		self.desc = desc
		self.reactions = list()
		self.metabolites = list()
		self.compartments = dict()
		self.unique_ec = dict() # this is a dictionary, not array
		self.duplicate_ractions = list()

	def add_reaction(self,reaction_object):
		self.reactions.append(reaction_object)

	def add_metabolite(self,metabolite_object):
		self.metabolites.append(metabolite_object)


	def metabolites_in_compartment(self,compartment_id):
		result = 0
		for m in self.metabolites:
			if m.compartment_id == compartment_id:
				result+=1
		return result

	def remove_metabolites(self,list_of_removables):
		def remove_from_metabolites_list(longlist,list_of_removables):
			'this function does not return anything. It modifies the outer list'
			for i in xrange(0,len(longlist)):
				if longlist[i].name in list_of_removables:
					#print(longlist[i],i)
					del longlist[i]
					remove_from_metabolites_list(longlist,list_of_removables) ## the list is mutating in this loop, that's why we need to start over each time the criteria is met
					break
				if longlist[i].neutral in list_of_removables:
					del longlist[i]
					remove_from_metabolites_list(longlist,list_of_removables)
					break
				if longlist[i].charged in list_of_removables:
					del longlist[i]
					remove_from_metabolites_list(longlist,list_of_removables)
					break

		affected_elements = 0
		old_a = 0
		for r in self.reactions:
			r.subtract_metabolites(list_of_removables)

		remove_from_metabolites_list(self.metabolites,list_of_removables)
		return affected_elements

	# def get_compartment_name(self,compartment_id):
	# 	return 1

	def get_metabolite(self,metabolite_id):
		for m in self.metabolites:
			if m.id == metabolite_id:
				return m
		return False

	def has_metabolite(self,metabolite_id):
		for m in self.metabolites:
			if m.id == metabolite_id:
				return True
		return False

	def add_metabolite_if_not_exist(self,new_metabolite):
		if not self.has_metabolite(new_metabolite.id):
			self.add_metabolite(new_metabolite)

	def link_metabolites_with_other(self,other):
		"""I don't remember what this function is for."""
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

		combo_l= list(itertools.product(self.metabolites,other.metabolites))
		i = 0
		problems_c = 0
		problems_f = 0
		problems_n = 0
		names_fine = 0
		for m in combo_l:
			ratio = difflib.SequenceMatcher(None, m[0].name, m[1].name).ratio()
			if ratio > 0.97:
				formulas = compare_formulas(m[0].formula,m[1].formula)
				compartments = compare_compartments(m[0].compartment,m[1].compartment)

				#if compartments == 0 or formulas == 0: # filter out clear mismatch
				if formulas == 0: # filter out clear mismatch
					pass
				else:
					if compartments == -1:
						problems_c +=1
					if formulas == -1:
						problems_f +=1
					if ratio < 1:
						problems_n +=1
					if ratio == 1:
						names_fine +=1
					#print(i,formulas,compartments,"\t",ratio,m[0].name, m[1].name,)
					print(str(i)+"\t"+str(formulas)+"\t"+str(compartments)+"\t"+str(ratio)+"\t"+str(m[0].name)+"\t"+m[1].name)
				i+=1

		print("------------------")
		print("Missing compartments:", problems_c)
		print("Missing formulas:", problems_f)
		print("Uncertainty with names:", problems_n)
		print("Certain names:", names_fine)
			#	print(i,ratio,m[0].name, m[1].name)


	def find_duplicates(self,by_what):
		'finds duplicate reactions'
		combo_l= list(itertools.combinations(self.reactions,2))
		# here we just got all possible combinations. It's much simpler than nested FOR loops
		##print(str(len(combo_l))+ " combinations to check")
		results = []
		equal_reactions = 0
		for r in combo_l:
			duplicates = []
			if r[0].is_equal(r[1],by_what):
				ec_result = compare_ec_numbers(r[0].ec_number,r[1].ec_number)
				equal_reactions+=1
				##print(ec_result,r[0].reference, r[1].reference, r[0].to_string(by_what), ' == ', r[1].to_string(by_what))
				results.append({'ec_result': ec_result, 'r0': r[0], 'r1': r[1]})
				r[0].tags['duplicate'].append(r[1].reference) ## just in case. I don't know how this tool will evolve
				r[1].tags['duplicate'].append(r[0].reference)
				# now we will append the duplicate to the class list
				self.duplicate_ractions.append([ec_result,r[0].reference, r[1].reference, r[0].to_string(by_what), r[1].to_string(by_what)])
		##print(equal_reactions)
		return results


	def find_duplicate_metabolites(self,by_what):
		'finds duplicate reactions'
		combo_l= list(itertools.combinations(self.metabolites,2))
		# here we just got all possible combinations. It's much simpler than nested FOR loops
		##print(str(len(combo_l))+ " combinations to check")
		results = []
		equal_metabolites = 0
		for m in combo_l:
			duplicates = []
			if m[0].is_equal(m[1],by_what):
				equal_metabolites+=1
				results.append({'m0': m[0], 'm1': m[1]})
				m[0].tags['duplicate'].append(m[1].row) ## just in case. I don't know how this tool will evolve
				m[1].tags['duplicate'].append(m[0].row)
				# now we will append the duplicate to the class' list
		return results


	def compare_with_other(self, other,check_ec,by_what):
		"""I don't remember what this funtion is for. """
		equal_reactions = 0
		combo_l= list(itertools.product(self.reactions,other.reactions))
		# here we just got all possible combinations. It's so much simpler than nested FOR loops
		##print(str(len(combo_l))+ " combinations to check.")
		results = []
		for r in combo_l:
			is_equal_result = r[0].is_equal(r[1],by_what)
			if is_equal_result > 0:
				ratio_synonyms = r[0].is_equal_by_names(r[1])
				ec_result = compare_ec_numbers(r[0].ec_number,r[1].ec_number)
				total_ec = count_ec_numbers(r[0].ec_number,r[1].ec_number)
				ec_str = str(ec_result)+'/'+str(total_ec)
				if check_ec == 0:
					equal_reactions+=1
					print(str(round(ratio_synonyms,1))+' '+str(r[0].reference)+ ' '+ str(r[1].reference)+ '\t' + r[0].to_string(by_what) + '\t' + r[1].to_string(by_what))
					##print(str(round(ratio_synonyms,1))+' '+str(ec_str)+' '+str(r[0].reference)+ ' '+ str(r[1].reference)+ '\t' + r[0].to_string(by_what) + '\t' + r[1].to_string(by_what))
					r[0].tag = 'common'
					results.append({'ec_result': ec_result, 'ratio_synonyms':ratio_synonyms, 'r0': r[0], 'r1': r[1]})
					r[0].tags['common'] = 1
					r[1].tags['common'] = 1
				else:
					if ec_result != 0:
						equal_reactions+=1
						#print(str(round(ratio_synonyms,1))+' '+str(ec_str)+' '+str(r[0].reference)+ ' '+ str(r[1].reference)+ '\t' + r[0].to_string(by_what) + '\t' + r[1].to_string(by_what))
						print(str(round(ratio_synonyms,1))+' '+str(ec_str)+' '+str(r[0].reference)+ ' '+ str(r[1].reference)+ '\t' + r[0].to_string('name') + '\t' + r[1].to_string('name'))
						##print(str(r[0].name)+ ':\n\t'+ r[0].to_string('name') + '\n\t~\n\t#' + str(r[0].desc))
						r[0].tag = 'common'
						results.append({'ec_result': ec_result, 'ratio_synonyms':ratio_synonyms, 'r0': r[0], 'r1': r[1]})
						r[0].tags['common'] = 1
						r[1].tags['common'] = 1
		print('COLUMNS----------------------------------------------')
		print('Synonyms ratio, EC result, R1#no, R2#no, R1, R2')
		print('-----------------------------------------------------')
		equal_percentage = round((float(equal_reactions)/len(self.reactions)) * 100.,2)
		if check_ec == 1:
			ec_text = 'E.C. numbers checked'
		else:
			ec_text = 'E.C. numbers ignored'
		print('compared by \''+ by_what+'\'')
		print(ec_text)
		print(str(equal_reactions) + ' reactions ('+str(equal_percentage)+'%) from \"' + self.title + '\" found in \"' + other.title +'\"')
		return {'check_ec':check_ec, 'results_list':results}


	def _get_all_unique_ec(self):
		def strip_ec_numbers(string):
			return string.strip()
		for r in self.reactions:
			if len(r.ec_number) != 0:
				whattoreplace = ["or", "OR", "and", "AND", ";", ","];
				ec1 = replace_things(r.ec_number,whattoreplace,"|")
				ec1 = ec1.split("|")
				ec1 = map(strip_ec_numbers,ec1)
				for e in ec1:
					if e not in self.unique_ec:
						self.unique_ec[e]= ''


	def _get_synonyms(self,ec_number):
		if ec_number not in self.unique_ec:
			return -1
		else:
			return self.unique_ec[ec_number]


	def _synonymize_reactions(self):
		def strip_ec_numbers(string):
			return string.strip()
		for r in self.reactions:
			#r.synonyms = [] # just in case...
			if len(r.ec_number) != 0:
				whattoreplace = ["or", "OR", "and", "AND", ";", ","];
				ec1 = replace_things(r.ec_number,whattoreplace,"|")
				ec1 = ec1.split("|")
				ec1 = map(strip_ec_numbers,ec1)
				for e in ec1:
					new_synonyms = self._get_synonyms(e)
					for line in new_synonyms:
						r.synonyms.append(line)
			# and as the last one, I will append the reactions self.desc to its synonyms
			r.synonyms.append(r.desc)

	def download_ec_synonyms(self,client,download):
		self._get_all_unique_ec() # create list of all unique ec_numbers
		filename = str(self.name)+".ec_synonyms.txt"
		if os.path.exists(filename):
			#print("Using previously downloaded synonyms ..."),
			SYNON_FILE = open(filename,"r")
			self.unique_ec = pickle.load(SYNON_FILE)
			#print(len(self.unique_ec)+" E.C. numbers loaded")
			#print(self.unique_ec)
			SYNON_FILE.close()
		if download == 0:
			self._synonymize_reactions() # and the last operation... put the date inside reactions
			return 1
		i = 0
		skipped = 0
		downloaded = 0
		failed = 0
		no_information = 0

		need_to_download = 0
		total_ec_count = 0
		for e in self.unique_ec:
			total_ec_count+=1
			if self.unique_ec[e] == '':
				need_to_download+=1
				#print(e,self.unique_ec[e])
		print("Synonym download needed for: "+str(need_to_download)+" of "+str(total_ec_count)+ " E.C. numbers")
		print("Downloading may take some time.")

		for e in self.unique_ec:
			#print(1)
			i+=1
			#if i > 60:
			#	break
			brenda_synonyms = []
			if self.unique_ec[e] == '':
				ec_to_check = "ecNumber*"+e
				try:
					#print(2)
					print("Downloading "+str(e)),
					resultString = client.getSynonyms(ec_to_check)
				except Exception:
					print("WSDL failed: " + str(e))
					resultString = "WSDL_ERROR"
					failed+=1
				if resultString != "WSDL_ERROR" and len(resultString)>0:
					my_array =  resultString.split("!")
					for entry in my_array:
						fields = entry.split("#")
						name = fields[1].split("*")
						brenda_synonyms.append(name[1])
					self.unique_ec[e] = brenda_synonyms
					print(str(len(brenda_synonyms)) + "synonyms")
					downloaded+=1
				if len(resultString) == 0:
					no_information+=1
					print("Not in database:",e)
			else:
				#print("Skip...",e)
				skipped+=1

		SYNON_FILE = open(filename,"w")
		pickle.dump(self.unique_ec,SYNON_FILE)
		##print(".......PRINT TO FILE")
		print("Downloaded:\t"+str(downloaded))
		print("Not in database:"+str(no_information))
		print("Failed:  \t"+str(failed))
		print("Skipped: \t"+str(skipped))

		print("Total EC:\t"+str(len(self.unique_ec))+"\t sum: "+str(downloaded+skipped+failed+no_information)+"\n")
		SYNON_FILE.close()
		self._synonymize_reactions() # and the last operation... put the date inside reactions

	def compare_reactions_only_by_names(self,other,by_what,treshold_name,treshold_string):
		equal_reactions = 0
		failed_treshold = 0
		not_equal_reactions = 0
		equal_reactions_treshold = 0
		combo_l= list(itertools.product(self.reactions,other.reactions)) # all possible combinations
		print(len(combo_l),' combinations to check')
		for r in combo_l:
			max_ratio_name = r[0].is_equal_by_names(r[1])
			#ratio = difflib.SequenceMatcher(None, r[0].desc, r[1].desc).ratio()
			if max_ratio_name >= treshold_name:
				ratio_string = difflib.SequenceMatcher(None, r[0].to_string(by_what), r[1].to_string(by_what)).ratio()
				if ratio_string >= treshold_string:
					print(round(max_ratio_name,2),round(ratio_string,2),r[0].to_string(by_what), r[1].to_string(by_what))
					equal_reactions_treshold+=1
				else:
					failed_treshold+=1



				equal_reactions+=1
			else:
				#print("        ",max_ratio,r[0].reference, r[1].reference)
				equal_reactions+=1

		print("Treshold pass: ",equal_reactions_treshold)
		print("Treshold fail:   ",failed_treshold)


	def compare_reactions_by_names(self,other,treshold):
		equal_reactions = 0
		not_equal_reactions = 0
		equal_reactions_treshold = 0
		combo_l= list(itertools.product(self.reactions,other.reactions)) # all possible combinations
		for r in combo_l:
			if compare_ec_numbers(r[0].ec_number,r[1].ec_number) >=1:
				max_ratio = r[0].is_equal_by_names(r[1])
				#ratio = difflib.SequenceMatcher(None, r[0].desc, r[1].desc).ratio()
				#print(max_ratio,' ')
				if max_ratio == 0:
					pass
				elif max_ratio >= treshold:
					#print("TRESHOLD",max_ratio,r[0].reference, r[1].reference)
					equal_reactions_treshold+=1
					equal_reactions+=1
				else:
					#print("        ",max_ratio,r[0].reference, r[1].reference)
					equal_reactions+=1
			else:
				not_equal_reactions+=1
		print("Equal t: ",equal_reactions_treshold)
		print("Equal:   ",equal_reactions)
		print("Not e:   ",not_equal_reactions)


	def print_reactions(self,by_what):
		for r in self.reactions:
			print(r.reference, r.to_string(by_what))
			#print(r.reference, r.desc, len(r.synonyms))

	def print_metabolites(self):
		i = 1
		print("Row\tname\tCompartment\tFormula")
		print("------\t------\t------\t------\t------")
		for m in self.metabolites:
			#print(m.row,m.name, m.desc, m.neutral, m.charged)
			print(str(i)+"\t"+str(m.name)+"\t"+str(m.compartment)+"\t"+str(m.formula))
			i+=1
		print("------\t------\t------\t------\t------")
		print("Row\tname\tCompartment\tFormula")

	def get_metabolites(self):
		i = 1
		#print("Row\tname\tCompartment\tFormula")
		#print("------\t------\t------\t------\t------")
		metabolites_out = []

		for m in self.metabolites:
			metabolite_out = {'id':str(m.id),'name':str(m.name),'compartment':str(m.compartment),'formula':str(m.formula)}
			#print(str(i)+"\t"+str(m.name)+"\t"+str(m.compartment)+"\t"+str(m.formula))
			metabolites_out.append(metabolite_out)
		#print("------\t------\t------\t------\t------")
		return metabolites_out

	def max_metabolite_load(self):
		max_c = 0
		max__c_name = ''
		max_p = 0
		max__p_name = ''
		for m in self.metabolites:
			if len(m.reactions_consumed) > max_c:
				max_c = len(m.reactions_consumed)
				max_c_name = m.name
			if len(m.reactions_produced) > max_p:
				max_p = len(m.reactions_produced)
				max_p_name = m.name
		return [max_c_name,max_c,max_p_name,max_p]

	def _count_metabolite_load(self):
		#combo_l= list(itertools.product(self.metabolites,self.reactions))
		for i in xrange(0,len(self.metabolites)):
			self.metabolites[i].reactions_consumed = []
			self.metabolites[i].reactions_produced = []

		for i in xrange(0,len(self.metabolites)):
			for reaction in self.reactions:
				for s in reaction.substrates:
					if self.metabolites[i].name == s.name:
						self.metabolites[i].reactions_consumed.append(reaction.name)
						#print("C",i,self.metabolites[i].name,len(self.metabolites[i].reactions_produced))
				for p in reaction.products:
					if self.metabolites[i].name == p.name:
						self.metabolites[i].reactions_produced.append(reaction.name)
						#print("P",i,self.metabolites[i].name,len(self.metabolites[i].reactions_produced))



	def check_balance(self,by_what):
		if (by_what != "neutral") and (by_what != "charged"):
			print("check_balance() Unknown option",by_what)
			exit()
		#for i in xrange(620,622):
		#	pass
		problematic = 0
		unb_reactions = 0

		for i in xrange(0,len(self.reactions)):
			#print(self.reactions[i].to_string("neutral"))
			#print(i),
			#print(self.reactions[i].to_string("name"))
			#print(self.reactions[i].to_string("neutral"))
			r= self.reactions[i].reference
			unbalanced = self.reactions[i].check_balance(by_what)
			if unbalanced == -3:
				print(r,"NoF",self.reactions[i].to_string(by_what))
				problematic+=1
			elif unbalanced == -2:
				print(r,"Mal",self.reactions[i].to_string(by_what))
				problematic+=1
			elif unbalanced == -1:
				print(r,"Unr",self.reactions[i].to_string(by_what))
				problematic+=1
			elif unbalanced > 0:
				print(r,unbalanced,self.reactions[i].to_string(by_what))
				unb_reactions+=1
			#print("------")
		print("------")
		print(str(unb_reactions)+" unbalanced reactions")
		print(str(problematic)+" problematic reactions (can't check balance)")








##############################################################################
#                      metabolite
##############################################################################

class metabolite:
	'each and every metabolite is an instance of this metabolite object'

	def __init__(self,m_id,name,compartment_id,formula):
		self.id = m_id
		self.name = name
		self.compartment_id = compartment_id
		self.formula = formula
		self.neutral = formula
		self.charged = formula
		self.filtered = False

		try:
			self.splitted_formula = split_chemical_formula(formula)
			# print ("Good formula: {0}".format(self.splitted_formula))
		except:
			print ("Can not split formula: {0}".format(formula))
			self.splitted_formula = False


		self.reactions_consumed = []
		self.reactions_produced = []
		self.tags = {'duplicate': [], 'common': -1}
		self.synonyms = []

	def get_id(self):
		return str(self.id)
	def get_name(self):
		return str(self.name)


	def old__init__(self,id,desc,neutral,charged,charge,keggid,smiles,row):
		self.id = id
		self.name = id
		self.desc = desc
		self.neutral = neutral
		self.charged = charged
		self.charge = charge
		self.keggid = keggid
		self.smiles = smiles
		self.row = row
		tag = ''
		self.reactions_consumed = []
		self.reactions_produced = []
		self.tags = {'duplicate': [], 'common': -1}
		self.synonyms = []

	def __str__(self):
		return str(self.name)
		#return str(str(self.row)+' '+self.name+' '+self.neutral)

	def is_equal(self,other,by_what):
		if by_what == 'name':
			if self.name == other.name:
				return bool(1)
		elif by_what == 'neutral':
			if self.neutral == other.neutral:
				return bool(1)
		elif by_what == 'charged':
			if self.charged == other.charged:
				return bool(1)
		elif by_what == 'id':
			if self.id == other.id:
				return bool(1)
		else:
			return bool(0)








##############################################################################
#                      reactant
##############################################################################




class reactant(object):
	# name = ""
	# st = 0.
	# neutral = ""
	# charged = ""
	#
	# ref = 0 # a reference to an element from "metabolite_in_list"
	def __init__(self,name,stoichiometry,reference):
		self.name = name
		self.st = float(stoichiometry)
		self.ref = reference # a reference to an element from "metabolite_in_list"
		self.reconciled = False
		self.formula = ""
		self.neutral = ""
		self.charged = ""
		self.neutral_elements = []
		self.charged_elements = []

	def get_ref(self):
		return str(self.ref)
	def get_name(self):
		return str(self.name)
	def get_st(self):
		return float(self.st)
	def get_neutral(self):
		return str(self.neutral)
	def get_charged(self):
		return str(self.charged)

	def __str__(self):
		return str(str(self.st) + ' ' + self.name)

	def __eq__(self, other):
		return self.is_equal(other,by_what='name')

	def calculate_formula_difference(f1,f2):
		try:
			splitted_formula1 = split_chemical_formula(f1)
			splitted_formula2 = split_chemical_formula(f2)
		except:
			# print ("Cannot split formula.")
			# return 1 # This number will be used as a multiplier later. So "1" means "nothing".
			return [1,0,0]
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
			return [0.5,0,0]

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

		difference = 0.5*ratioH+diff_atom_count
		difference = (float(1) - ratioH)*0.5 + 0.5 + diff_atom_count
		# print(similarity)
		# return similarity
		return [difference,diff_h_count,diff_atom_count]


	def difference(self,other):
		difference_n = self.calculate_formula_difference(self.neutral, other.neutral)
		difference_c = self.calculate_formula_difference(self.charged, other.charged)
		difference = self.calculate_formula_difference(self.formula, other.formula)
		min_diff = min(difference_n[0],difference_c[0],difference[0])
		if difference[0] == min_diff:
			return difference
		if difference_n[0] == min_diff:
			return difference_n
		if difference_c[0] == min_diff:
			return difference_c
		pass

	def is_equal(self,other,by_what):
		if by_what == 'name':
			if (len(self.get_name()) == 0) or (len(other.get_name()) == 0):
				return 0
			elif (self.get_name() == other.get_name()) and (self.get_st() == other.get_st()):
				return 1

		if by_what == 'id' or by_what == 'ref':
			out = 0
			if (len(self.get_ref()) == 0) or (len(other.get_ref()) == 0):
				return 0
			if self.get_ref() == other.get_ref():
				# element match. Now check if stoichiometry match
				out = 1
				if self.get_st() == other.get_st():
					out+= 1
			return out

		if by_what == 'neutral':
			if (len(self.neutral) == 0) or (len(other.neutral) == 0):
				return 0
			elif (self.neutral == other.neutral) and (self.st == other.st):
				return 1
		if by_what == 'charged':
			if (len(self.charged) == 0) or (len(other.charged) == 0):
				return 0
			elif (self.charged == other.charged) and (self.st == other.st):
				return 1

	def get_formula(self,by_what):
		if by_what == 'neutral':
			return self.neutral
		elif by_what == 'charged':
			return self.charged
		elif by_what == 'name':
			return self.name
		else:
			return ''

	def get_elements(self,by_what):
		if by_what == 'neutral':
			return self.neutral_elements
		elif by_what == 'charged':
			return self.charged_elements
		else:
			return []





##############################################################################
#                      Reaction
##############################################################################






class reaction(object):
	'each reaction is an instance of reaction object'
	def __init__(self,name,desc,ec_number,reversible,reference):
		self.id = str(name)
		self.name = str(name)
		self.desc = str(desc)
		self.ec_number = str(ec_number)
		self.gpr_number = ''
		self.reversible = int(reversible)
		self.original_string = ''
		self.products = []
		self.substrates= []
		self.synonyms = [] # here we store synonyms fetched from databases. Brenda only for now.
		self.reference = reference
		self.tag = '' ## obsolete, please don't use
		## All tags. Duplicates, common r. and other tags go in tags{}
		self.tags = {'duplicate': [], 'common': -1, 'ec_check': -1, 'balance': -1}
		self.compartment = ''
		if(len(name)<2):
			self.id = reference


	def add_to_substrates(self,reactant):
		self.substrates.append(reactant)
		return

	def add_to_products(self,reactant):
		self.products.append(reactant)
		return


	def generate_from_string(self,original_string): # Crunches strings like this "0.195 RNA + 0.027 DNA + 16.45 ATP -> Biomass + 16.45 ADP + 16.45 PI"
		def cleanup_reaction(string):
			string = replace_things(string,['<','--',' -','- ','>','=','=='],'')
			string = string.replace('  ', ' ') # remove double spaces. Excel files may have such anomalies.
			return string
		def process_side(side):
			p_side = cleanup_reaction(side) # removes unwanted strings, like "--" or "<-"
			all_reactants = []
			if len(p_side) < 1: # one side empty is typical for transport reactions
				return all_reactants
			metabolites_raw = p_side.split("+")
			for m in metabolites_raw:
				m = m.strip()
				splited = m.split(' ')
				if m.find(' ') > 0 : # if there is more than zero spaces " "...
					stoichiometry = splited[0]
					name = splited[1]
				else:
					stoichiometry =  1
					name = splited[0]
				#Now, when we have all the components we create the metabolite object
				##name = prepare_item_id_for_sbml(name)
				new_reactant = reactant(name,stoichiometry,-1) # at this point all reactants in the reaction are unreferenced (no refs to metabolite list)
				all_reactants.append(new_reactant)
				#print(str(reactant.st) +' '+ reactant.name)
			return all_reactants
		self.original_string = original_string
		sides = original_string.split(">")
		self.substrates = process_side(sides[0])
		self.products = process_side(sides[1])
		return sides

	def __str__(self):
		return self.to_string('name')

	def to_string(self,by_what):
		def prepare_string(reactants,by_what):
			s = []
			if (by_what == 'id') or (by_what == 'ref'):
				for r in reactants:
					if r.st == 1.:
						s.append(str(r.ref))
					else:
						s.append(str(r.st) + ' ' + str(r.ref))
			if by_what == 'name':
				for r in reactants:
					if r.st == 1.:
						s.append(str(r.name))
					else:
						s.append(str(r.st) + ' ' + str(r.name))
			elif by_what == 'neutral':
				for r in reactants:
					if r.st == 1.:
						s.append(str(r.neutral))
					else:
						s.append(str(r.st) + ' ' + str(r.neutral))
			elif by_what == 'charged':
				for r in reactants:
					if r.st == 1.:
						s.append(str(r.charged))
					else:
						s.append(str(r.st) + ' ' + str(r.charged))
			return " + ".join(s)

		substrates = prepare_string(self.substrates,by_what)
		products = prepare_string(self.products,by_what)
		if self.reversible > 0:
			self.generated_string = " <-> ".join([substrates,products])
		else:
			self.generated_string = " -> ".join([substrates,products])
		return str(self.generated_string)



	def __eq__(self,other):
		return self.is_equal(other,'name')

	def __ne__(self,other):
		return not __eq__(self,other)


	def difference(self,other,by_what,crosscheck,met_filters_a,met_filters_b):
		def build_filtered_list(metabolites,filters):
			list_a = []
			for m in metabolites:
				if m.get_ref() not in filters:
					list_a.append(m)
			# if len(metabolites) > len(list_a):
			# 	print("."),
			# else:
			# 	print("0"),
			return list_a

		def reactants_difference(metabolites,other_metabolites,by_what):
			combo_l= list(itertools.product(metabolites,other_metabolites))
			common = 0
			for pair in combo_l:
				equality = pair[0].is_equal(pair[1],by_what)
				if equality > 0:
					common+=1
			maxis = max(len(metabolites),len(other_metabolites))
			residual = max(len(metabolites),len(other_metabolites)) - min(len(metabolites),len(other_metabolites))
			difference = maxis - common
			#print(difference,len(metabolites),len(other_metabolites))
			return {'diff':difference, 'residual':residual, 'matching':common, 'maxlen':maxis}

		s_substrates = build_filtered_list(self.substrates,met_filters_a)
		s_products = build_filtered_list(self.products,met_filters_a)
		o_substrates = build_filtered_list(other.substrates,met_filters_b)
		o_products = build_filtered_list(other.products,met_filters_b)

		## Direct check
		diff_substrates = reactants_difference(s_substrates,o_substrates,by_what)
		diff_products = reactants_difference(s_products,o_products,by_what)
		## Reverse check
		diff_r_substrates = reactants_difference(s_substrates,o_products,by_what)
		diff_r_products = reactants_difference(s_products,o_substrates,by_what)
		return {'diff_substrates':diff_substrates,
		'diff_products':diff_products,
		'diff_r_substrates':diff_r_substrates,
		'diff_r_products':diff_r_products,
		'len_substrates':len(s_substrates),
		'len_products':len(s_products),
		'len_o_substrates':len(o_substrates),
		'len_o_products': len(o_products)
		}






	def is_equal(self,other,by_what,crosscheck,met_filters_a,met_filters_b):
		## return codes
		## 0 - not equal
		## 1 - equal, one is reversible
		## 2 - equal and in the same direction
		def build_fltered_list(metabolites,filters):
			list_a = []
			for m in metabolites:
				if m.get_ref() not in filters:
					list_a.append(m)
			return list_a

		def reactants_pairwise_comparison(metabolites,other_metabolites,by_what):
			combo_l= list(itertools.product(metabolites,other_metabolites))
			#combo_l= list(itertools.product(list_a,list_b))
			count = 0
			#print(list_a,list_b)
			for pair in combo_l:
				if pair[0].is_equal(pair[1],by_what):
					count+=1
			if count == len(metabolites):
				return 1
			else:
				return 0

		s_substrates = build_fltered_list(self.substrates,met_filters_a)
		s_products = build_fltered_list(self.products,met_filters_a)
		o_substrates = build_fltered_list(other.substrates,met_filters_b)
		o_products = build_fltered_list(other.products,met_filters_b)

		equal_normal = 0
		equal_reverse = 0


		do_it = True
		do_it_right = True
		do_it_reverse = False
		if len(s_substrates) != len(o_substrates):
			do_it_right = False
		if len(s_products) != len(o_products):
			do_it_right = False
		if crosscheck:
			do_it_reverse = True
			if len(s_substrates) != len(o_products):
				do_it_reverse = False
			if len(s_products) != len(o_substrates):
				do_it_reverse = False

		if not (do_it_right or do_it_reverse):
			## all bad, no hope
			return 0


		s_s = ""
		s_p = ""
		o_s = ""
		o_p = ""
		for m in s_substrates:
			#s_s+=m.get_ref()+ ' '
			s_s+=m.get_neutral()+ ' '
		for m in s_products:
			#s_p+=m.get_ref()+ ' '
			s_p+=m.get_neutral()+ ' '
		for m in o_substrates:
			#o_s+=m.get_ref()+ ' '
			o_s+=m.get_neutral()+ ' '
		for m in o_products:
			#o_p+=m.get_ref()+ ' '
			o_p+=m.get_neutral()+ ' '
#		r1 = s_s + ' -> ' + s_p
#		r2 = o_s + ' -> ' + o_p
#		print("r1",r1)
#		print("r2",r2)


		#direct check
		if reactants_pairwise_comparison(s_substrates,o_substrates,by_what):
			equal_normal+=1
		if reactants_pairwise_comparison(s_products,o_products,by_what):
			equal_normal+=1
		# reverse check - compare substrates with products
		if crosscheck:
			if reactants_pairwise_comparison(s_substrates,o_products,by_what):
				equal_reverse+=1
			if reactants_pairwise_comparison(s_products,o_substrates,by_what):
				equal_reverse+=1

		if (equal_normal == 2) or (equal_reverse == 2):
			if(self.reversible == 1) or (other.reversible == 1):
				return 1
			else:
				return 2
			print("somehow equal")
			return 1
		else:
			return 0





	def subtract_metabolites(self,list_of_removables):
		def subtract_from_side(reactants1,list_of_removables):
			reactants = reactants1
			deletables = []
			for i in range(len(reactants)):
				if reactants[i].name in list_of_removables:
					deletables.append(i)
				elif reactants[i].neutral in list_of_removables:
					deletables.append(i)
				elif reactants[i].charged in list_of_removables:
					deletables.append(i)
			for i in reversed(deletables):
				del reactants[i]

			return reactants
		self.substrates = subtract_from_side(self.substrates,list_of_removables)
		self.products = subtract_from_side(self.products,list_of_removables)
		return reaction


	def is_equal_by_names(self,other):
		all_ratios = []
		if len(self.synonyms) == 0 or len(other.synonyms) == 0:
			return 0
		combo_syn= list(itertools.product(self.synonyms,other.synonyms))
		for syn in combo_syn:
			ratio = difflib.SequenceMatcher(None, syn[0], syn[1]).ratio()
			#print(ratio,'reac'),
			all_ratios.append(ratio)
			if len(all_ratios)==0:
				return 0
			else:
				return max(all_ratios)


	def get_brenda_synonyms(self,client):
		def strip_ec_numbers(string):
			return string.strip()
		if len(self.ec_number) == 0:
			return -1
		whattoreplace = ["or", "OR", "and", "AND", ";", ","];
		ec = replace_things(self.ec_number,whattoreplace,"|")
		ec1 = ec.split("|")
		ec1 = map(strip_ec_numbers,ec1)
		# further code in this function needs algorithmic improvement.
		# Now I will check only the first EC number, but somehow one should check all numbers
		ec_to_check = "ecNumber*"+ec1[0]
		try:
			resultString = client.getSynonyms(ec_to_check)
		except Exception:
			print("WSDL failed:",self.to_string('name'),ec1[0])
			return -2
		if len(resultString) > 0:
			my_array =  resultString.split("!")
			for entry in my_array:
				fields = entry.split("#")
				name = fields[1].split("*")
				self.synonyms.append(name[1])
				#print name[1]
		return len(self.synonyms)

	def check_balance(self,by_what):
		def split_reactants(reactants,by_what):
			for m in reactants:
				if len(m.get_formula(by_what)) == 0:
					return -3
				if is_numeric(m.get_formula(by_what)[0]): ## ugly code, but much shorter
					return -2 ## contains malformed formula
				if m.get_formula(by_what).find("NOT_REFERENCED")<0:
					m.neutral_elements = split_chemical_formula(m.neutral)
					m.charged_elements = split_chemical_formula(m.charged)
				else:
					return -1 ## if the metabolite is tagged as NOT_REFERENCED, then quit
			return 0

		is_splited = split_reactants(self.substrates,by_what)
		if is_splited < 0:
			#print("contains malformed formula")
			return is_splited
		is_splited = split_reactants(self.products,by_what)
		if is_splited < 0:
			#print("contains malformed formula")
			return is_splited

		elements = {} # dictionary, not list

		for s in self.substrates:
			for e in s.get_elements(by_what): # e is two dimensional array
				if elements.has_key(e[0]): # if the element is in list, append next atom count
					elements[e[0]] = elements[e[0]] + int(e[1]) * s.st
				else:
					elements[e[0]] = int(e[1]) * s.st
		for p in self.products:
			for e in p.get_elements(by_what):
				if elements.has_key(e[0]): # if the element is in list, subtract next atom count
					elements[e[0]] = elements[e[0]] - int(e[1]) * p.st
				else:
					elements[e[0]] = -int(e[1]) * p.st
		result = []
		for key in elements:
			if elements[key] != 0:
				result.append(key)
				#print(key,elements[key])
		return len(result) ## how many elements are unbalanced















##############################################################################
#                      COBRA importer
##############################################################################





class excel_cobra_model(st_model):
	'this class takes an Excel file and converts it to st_model object'
	bad_metabolites = [] # here goes all metabolites that have something missing: name, neutral,...

	def sanitize_string(self,datas,sanitor):
		## if datas will be empty after sanizite procedure, it will return 'sanitor'
		try:
			out = datas + " " ## convert to string by adding a space
			out = out.encode('ascii', 'replace')
			out=out.strip()
			#print("success",out)
		except TypeError, AttributeError:
			out = datas
			#print("Fail 1",out)
			out = str(datas)
			#print("Fail 2",out)
			out=out.strip()
		if len(out)<1 or out.isdigit():
			out = sanitor
		return str(out)



	def __init__(self,excelfile):
		self.title = str(excelfile)
		self.name = str(excelfile)
		self.desc = "sans description"
		book = xlrd.open_workbook(excelfile)
		self.reactions = []
		self.metabolites = []
		self.unique_ec = {} # this is a dictionary, not array
		self.duplicate_ractions = []
		self.compartments = {}


		m = book.sheet_by_index(0) # metabolites sheet
		r = book.sheet_by_index(1) # reactions sheet


		guess_compartments = False

		# import all compartments.
		# Compartments can be obtainen from metabolites list
		temp_compartments = []
		for i in xrange(1,int(m.nrows)):
			compartment_id = str(m.cell_value(i,5))
			if compartment_id not in temp_compartments:
				temp_compartments.append(compartment_id)
				if len(compartment_id) == 0 or compartment_id == " ":
					compartment_id = "Empty"
				comp_id = compartment_id
				comp_name = compartment_id
				self.compartments[comp_id] = comp_name

		## cheking for empty compartment IDs
		#for c in self.compartments:
		#	if c == ' ' or len(c) == 0:
		#		c = 'Empty'

		if len(self.compartments) < 2:
			guess_compartments = True
			print("There are less than 2 compartments. ModeRator will try to guess them.")

		if guess_compartments:
			self.compartments.clear()
			temp_compartments = []
			for i in xrange(1,int(m.nrows)):
				m_id = str(m.cell_value(i,0))
				l_index = m_id.find('[')
				h_index = m_id.rfind(']')
				#print(l_index,h_index)
				if l_index > 0 and (l_index < h_index):
					compartment_id = m_id[l_index+1:h_index]
					if compartment_id not in temp_compartments:
						temp_compartments.append(compartment_id)
						comp_id = compartment_id
						comp_name = compartment_id
						self.compartments[comp_id] = comp_name
						#print(compartment_id),

		# import all metabolites
		for i in xrange(1,int(m.nrows)):
			row = i
			#m_id = str(m.cell_value(i,0))
			#name = str(m.cell_value(i,1))
			#name = ''.join(s for s in str(m.cell_value(i,1)) if s in string.printable) ## remove non-ascii characters
			## this Try&Catch is workaround for empty cells and cells with unicode characters
			sanitor = str(row)+"_no_id"
			m_id = self.sanitize_string(m.cell_value(i,0),sanitor)
			##m_id = prepare_item_id_for_sbml(m_id)
			sanitor = str(row)+"_no_name"
			name = self.sanitize_string(m.cell_value(i,1),sanitor)
			sanitor = str(row)+"_no_formula"
			neutral = self.sanitize_string(m.cell_value(i,2),sanitor)
			charged = self.sanitize_string(m.cell_value(i,3),sanitor)

			formula = charged

			if guess_compartments:
				l_index = m_id.find('[')
				h_index = m_id.rfind(']')
				if l_index > 0 and (l_index < h_index):
					compartment_id = m_id[l_index+1:h_index]
			else:
				compartment_id = str(m.cell_value(i,5))
			## deal with empty values
			if len(compartment_id) == 0 or compartment_id == " ":
					compartment_id = "Empty"

			if self.is_numeric(m.cell_value(i,4)):
				charge = int(m.cell_value(i,4))
			else:
				charge = 0
			keggid = m.cell_value(i,6)
			smiles = m.cell_value(i,10)

			new_metabolite = metabolite(m_id,name,compartment_id,formula)
			self.add_metabolite(new_metabolite)

		# import all reactions
		for i in xrange(1,int(r.nrows)):
			name = str(r.cell_value(i,0))
			name = ''.join(s for s in name if s in string.printable) ## remove non-ascii characters
			desc = str(r.cell_value(i,1))
			desc = ''.join(s for s in desc if s in string.printable) ## remove non-ascii characters
			reaction_string = r.cell_value(i,2)
			ec_number = r.cell_value(i,12)
			reversible = int(r.cell_value(i,7))

			if len(name) < 2:
				name = "ModeRator_"+str(i)+name
			if len(desc) < 2:
				desc = "ModeRator_"+str(i)+desc

			#print(i)
			new_reaction = reaction(name,desc,ec_number,reversible,int(i+1))
			new_reaction.generate_from_string(reaction_string) # Note that generate_from_string() do not find references for reatctants in metabolite list.
			# now we will find a reference in the metabolite list
			sanitor = str(i)+'_no_ref'
			for s in new_reaction.substrates:
				#print(s.ref),
				s_formulas = self.get_all_formulas(s.name,sanitor)
				s.neutral = s_formulas[1]
				s.charged = s_formulas[2]
			for p in new_reaction.products:
				p_formulas = self.get_all_formulas(p.name,sanitor)
				p.neutral = p_formulas[1]
				p.charged = p_formulas[2]
			#print(i,'name',new_reaction.to_string('name'))
			#print(i,'neutral',new_reaction.to_string('neutral'))
			#print(i,'charged',new_reaction.to_string('charged'))

			self.add_reaction(new_reaction)

		## here we fix reactants references to metabolites
		unreferenced_reactants = []
		for r in self.reactions:
			for s in r.substrates:
				found_it = False
				for m in self.metabolites:
					if s.name == m.id:
						s.ref = str(m.id)
						found_it = True
				if not found_it:
					s.ref = str("REFERENCED_BY_ModeRator-"+s.name)
					unreferenced_reactants.append(s.name)
					self.compartments['missing'] = "missing"
					new_metabolite = metabolite(s.ref,s.name,self.compartments['missing'],'no_formula')
					self.add_metabolite(new_metabolite) # if the metabolite is not referenced, create special reference for it
			for s in r.products:
				found_it = False
				for m in self.metabolites:
					if s.name == m.id:
						s.ref = str(m.id)
						found_it = True
				if not found_it:
					s.ref = str("REFERENCED_BY_ModeRator-"+s.name)
					unreferenced_reactants.append(s.name)
					self.compartments['missing'] = "missing"
					new_metabolite = metabolite(s.ref,s.name,self.compartments['missing'],'no_formula')
					self.add_metabolite(new_metabolite) # if the metabolite is not referenced, create special reference for it

			##print(self.reactions[i-1].generated_string)
		for zz in unreferenced_reactants:
			print("unreferenced reactant: '%s'" %zz)


	def get_formula(self,name,what):
		for m in self.metabolites:
			if m.name == name:
				if what == 'neutral':
					return m.neutral
				if what =='charged':
					return m.charged
		#print("not referenced", name)
		return "NOT_REFERENCED-"+name

	def get_all_formulas(self,ref,sanitor):
		ref = str(ref)
		result = ['','','']
		result[0] = ref
		result[1] = sanitor
		result[2] = sanitor
		for m in self.metabolites:
			if m.id == ref:
				result[0] = m.id
				result[1] = m.neutral
				result[2] = m.charged
		return result

	def is_numeric(self,var):
		try:
			float(var)
			return True
		except ValueError:
			return False






##############################################################################
#                      SBML importer
##############################################################################



class xml_sbml_model(st_model):
	'this class takes SBML xml file and converts it to st_model object'
	def __init__(self,sbmlfile):
		self.title = str(sbmlfile)
		self.name = str(sbmlfile)
		self.desc = 'desc'
		self.reactions = []
		self.metabolites = []
		self.unique_ec = {} # this is a dictionary, not array
		self.duplicate_ractions = []
		self.compartments = {}

		reader = SBMLReader()
		document = reader.readSBML(sbmlfile)
		if document.getNumErrors() > 0:
			print("Model '"+str(sbmlfile)+"' contains "+str(document.getNumErrors())+" errors.")
		sbmlmodel = document.getModel()
		#print(model.getNumSpecies())



		## Compartments
		list_of_comp = sbmlmodel.getListOfCompartments()
		for c in list_of_comp:
			comp_id = c.getId()
			comp_name = c.getName()
			self.compartments[comp_id] = comp_name +"("+comp_id+")"





		## Metabolites (sbml species)
		list_of_species = sbmlmodel.getListOfSpecies()
		i = 0
		for m in list_of_species:
			#print(m.getId(),self.extract_name(m.getId()),m.getName(),self.extract_formula(m.getNotesString()))
			formula = '';
			m_id = str(m.getId())
			compartment_id = str(m.getCompartment())
			# here I process names that may contain chemical formula
			desc_raw = str(m.getName())

			desc_arr = self.discover_formula_in_name(desc_raw)
			name = desc_arr[0]
			formula = desc_arr[1]

			# here I try to figure out if the name contains multiple names - synonyms
			# desc_arr = desc_raw.split(";")
			# if len(desc_arr)>1:
			# 	print("!!! Synonyms in name")

			# If the formula has not already been discovered then look in the description
			#here I try to figure out if Notes contain chemical formula
			if len(formula) == 0:
				notes = self.extract_formula(m.getNotesString())
				try:
					splitted_formula = split_chemical_formula(notes)
					formula = notes
				except:
					print("can't split formula in notes:",notes)
					formula = '';

			#new_metabolite = metabolite(name,desc,neutral,charged,charge,keggid,smiles,row)
			new_metabolite = metabolite(m_id,name,compartment_id,formula)
			self.add_metabolite(new_metabolite)
		#print(len(list_of_species))

		## Reactions loop
		list_of_reactions = sbmlmodel.getListOfReactions()
		i = 0
		for r in list_of_reactions:
			r_name = str(r.getId())
			r_desc = str(r.getName())
			r_ec_number = ''
			reversible = str(r.getReversible())
			if reversible=='True':
				r_reversible = 1
			else:
				r_reversible = 0
			r_reference = str(i)+r_name
			i+=1
			new_reaction = reaction(r_name,r_desc,r_ec_number,r_reversible,r_reference)

			list_of_reactants = r.getListOfReactants()
			for s in list_of_reactants:
				name = str(s.getSpecies())
				stoichiometry = float(s.getStoichiometry())
				reference = name
				new_substrate = reactant(name,stoichiometry,reference)
				new_reaction.add_to_substrates(new_substrate)

			list_of_products = r.getListOfProducts()
			for p in list_of_products:
				name = str(p.getSpecies())
				stoichiometry = float(p.getStoichiometry())
				reference = name
				new_product = reactant(name,stoichiometry,reference)
				new_reaction.add_to_products(new_product)

			# now we will find a reference in the metabolite list
			for s in new_reaction.substrates:
				s_formulas = self.get_all_formulas(s.ref)
				s.neutral = s_formulas[1]
				s.charged = s_formulas[2]
			for p in new_reaction.products:
				p_formulas = self.get_all_formulas(p.ref)
				p.neutral = p_formulas[1]
				p.charged = p_formulas[2]

			## And finaly - add reaction to model
			self.add_reaction(new_reaction)
		#print(len(list_of_reactions))
		pass

	def discover_formula_in_name(self,name):
		# Two separators for formulas are considered: "_" and ":"
		r_name = name.split("_")
		formula_found = False
		if len(r_name) > 1:
			try:
				r_name[-1] = r_name[-1].strip()
				splitted_formula = split_chemical_formula(r_name[-1])
				if splitted_formula[0][0] == '':
					pass
				else:
					out = ' '.join(r_name[0:-1])
					formula_found = True
			except:
				pass
		else:
			pass

		if formula_found:
			return [out,r_name[-1]]
		else:
			return [name,'']

		r_name = name.split(":")
		if len(r_name) > 1:
			try:
				r_name[-1] = r_name[-1].strip()
				splitted_formula = split_chemical_formula(r_name[-1])
				if splitted_formula[0][0] == '':
					pass
				else:
					out = ' '.join(r_name[0:-1])
					formula_found = True
			except:
				pass

		else:
			pass
			# return [name,'']

		if formula_found:
			return [out,r_name[-1]]
		else:
			return [name,'']



	def extract_formula(self,formula):
		#start = formula.find('FORMULA:')
		#end = formula.find('</html')
		charged = remove_html_tags(formula)
		charged = charged.replace('\n',':')
		charged = charged.replace('\r',':')
		charged = charged.strip()

		charged_arr = charged.split(":")
		if len(charged_arr)>1:
			charged_arr = [ string.strip(x) for x in charged_arr ] # apply function to all elements in list
			# print(charged_arr)
			# charged_arr[0] = charged_arr[0].strip()
			# charged_arr[1] = charged_arr[1].strip()
			for x in charged_arr:
				try:
					# print("Trying formula "+str(x))
					splitted_formula = split_chemical_formula(x)
					charged_res = x
					if len(charged_res) > 0:
						# print(str(x)+ " was good")
						break
				except:
					# except KeyError:
					charged_res = '';
					# print(str(x)+ " was bad")

			if len(charged_res) == 0:
				return ''
			else:
				return charged_res
		#return formula[start+9:end]
		return charged

	def extract_name(self,sbml_id):
		return sbml_id[2:]

	def get_all_formulas(self,name):
		result = ['','','']
		result[0] = name
		result[1] = "NO_REF-"+name
		result[2] = "NO_REF-"+name
		for m in self.metabolites:
			if m.id == name:
				result[0] = m.id
				result[1] = m.neutral
				result[2] = m.charged
		#print("not referenced", name)
		#print(result)
		return result
