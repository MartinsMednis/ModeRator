#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# main.py
# Copyleft (CC) 2013 martins <martins.mednis@llu.lv>
#
# ModeRator-gtk is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ModeRator-gtk is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.


from __future__ import generators

from gi.repository import GObject, Gtk #, GdkPixbuf, Gdk

import os, sys, copy

##os.environ['PYTHONPATH'] = '/usr/local/lib64/python2.7/site-packages/libsbml'
#sys.path.append('/usr/local/lib64/python2.7/site-packages/libsbml')

#from threading import Thread






## first we try to import all required modules
missing_modules2 = []
try:
	import xlrd
except ImportError:
	missing_modules2.append("xlrd")


try:
	from libsbml import *
except ImportError:
	missing_modules2.append("libSBML")


try:
	## for string distance calculation
	import Levenshtein
except ImportError:
	missing_modules2.append("Levenshtein")



from comparison_utilities import Dscore
from comparison_utilities import calculate_formula_similarity
from comparison_utilities import filtered_metabolite_lists
from comparison_utilities import compare_formulas
from comparison_utilities import compare_compartments
from comparison_utilities import format_output_for_liststore
# from comparison_utilities import rate_metabolite_pairs
from comparison_utilities import rate_metabolite_pair

import itertools, difflib, string

from stmodel import *
from mrtsound import *




#Comment the first line and uncomment the second before installing
#or making the tarball (alternatively, use project variables)
UI_FILE = "moderator_gtk.ui"
#UI_FILE = "src/moderator_gtk.ui"
#UI_FILE = "/usr/local/share/moderator_gtk/ui/moderator_gtk.ui"


#class TestClass(gobject.GObject):
#	def __init__(self, name):
#		gobject.GObject.__init__(self)
#		self.name = name

class GUI:
	def __init__(self):

#		global missing_modules

		self.builder = Gtk.Builder()
		self.builder.add_from_file(UI_FILE)
		self.builder.connect_signals(self)

		window = self.builder.get_object('window')

		#self.treestore = self.builder.get_object('treestore1')

		## Here we get liststores where metabolites and reactions are stored for display purposes
		self.liststore_met1 = self.builder.get_object('liststore_met1')
		self.liststore_r1 = self.builder.get_object('liststore_r1')
		self.liststore_met2 = self.builder.get_object('liststore_met2')
		self.liststore_r2 = self.builder.get_object('liststore_r2')
		self.liststore_comp1 = self.builder.get_object('liststore_comp1')
		self.liststore_comp2 = self.builder.get_object('liststore_comp2')

		self.liststore_met_results = self.builder.get_object('liststore_met_results')
		self.liststore_met_results_temp = self.builder.get_object('liststore_met_results_temp')


		#init treeview
		self.treestore = self.builder.get_object('treestore1')
		self.treeview2 = self.builder.get_object('treeview2')
		self.treecounter = float(1)

		self.met_comp_counter = float(1)

		self.reconciled_reactions_a = []
		self.reconciled_reactions_b = []

		#switch_check_id = self.builder.get_object('switch_check_id')
		#switch_check_id.connect('notify::active', self.on_switch_check_id_activate)



		## if some modules are missing, tell it
		print(missing_modules)
		if len(missing_modules) > 0:
			dialog = Gtk.MessageDialog(window, 0, Gtk.MessageType.INFO,
			Gtk.ButtonsType.OK, "Some of the modules are missing")
			print(missing_modules)
			missing_modules_text  = '\n'.join(missing_modules)
			missing_modules_text  = '\n'.join(missing_modules2)
			missing_modules_text+="\n\nModeRator will not work properly without all the required modules.\nPlease see the documentation on how to fix this."
			dialog.format_secondary_text(missing_modules_text)
			dialog.run()
			dialog.destroy()

		window.show_all()

		self.models = [] # here we store all models that we load

		self.reaction_results = []




	def destroy(window, self):
		Gtk.main_quit()

	def file_greeter(self,user_file):
		if user_file[-3:len(user_file)] == 'xls':
			print("---------------Ekselis")
			user_model = excel_cobra_model(user_file)
			return user_model
		elif user_file[-3:len(user_file)] == 'xml':
			print("---------------SBML (xml)")
			user_model = xml_sbml_model(user_file)
			return user_model
		elif user_file[-4:len(user_file)] == 'sbml':
			print("---------------SBML (sbml)")
			user_model = xml_sbml_model(user_file)
			return user_model
		else:
			return 0

	def file_open_dialog(self, window):
		filechooserdialog = Gtk.FileChooserDialog("Select a File", None, Gtk.FileChooserAction.OPEN, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
		filechooserdialog.set_current_folder("/home/martins/workspace/python/models")

		filefilter = Gtk.FileFilter()
		filefilter.set_name("Supported")
		filefilter.add_pattern("*.xml")
		filefilter.add_pattern("*.sbml")
		filefilter.add_pattern("*.xls")
		filechooserdialog.add_filter(filefilter)

		filefilter = Gtk.FileFilter()
		filefilter.set_name("SBML")
		filefilter.add_pattern("*.xml")
		filefilter.add_pattern("*.sbml")
		filechooserdialog.add_filter(filefilter)

		filefilter = Gtk.FileFilter()
		filefilter.set_name("Spreadsheets")
		filefilter.add_pattern("*.xls")
		#filefilter.add_pattern("*.ods")
		filechooserdialog.add_filter(filefilter)

		filefilter = Gtk.FileFilter()
		filefilter.set_name("All Files")
		filefilter.add_pattern("*")
		filechooserdialog.add_filter(filefilter)

		response = filechooserdialog.run()
		#response = dialog.run()
		new_path = ''
		if response == Gtk.ResponseType.OK:
			#print "Open clicked"
			#print "File: " + filechooserdialog.get_filename()
			new_path = filechooserdialog.get_filename()
		elif response == Gtk.ResponseType.CANCEL:
			#print "Cancel clicked"
			pass
		filechooserdialog.destroy()
		return new_path

	def file_save_dialog(self, window):
		filechooserdialog = Gtk.FileChooserDialog("Select a File", None, Gtk.FileChooserAction.SAVE, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
		filechooserdialog.set_current_folder("/home/martins/workspace/python/moderator3/")

		filefilter = Gtk.FileFilter()
		filefilter.set_name("SBML")
		filefilter.add_pattern("*.xml")
		filefilter.add_pattern("*.sbml")
		filechooserdialog.add_filter(filefilter)

		filefilter = Gtk.FileFilter()
		filefilter.set_name("CSV")
		filefilter.add_pattern("*.csv")
		filechooserdialog.add_filter(filefilter)

		filefilter = Gtk.FileFilter()
		filefilter.set_name("All Files")
		filefilter.add_pattern("*")
		filechooserdialog.add_filter(filefilter)

		#filefilter = Gtk.FileFilter()
		#filefilter.set_name("Spreadsheets")
		#filefilter.add_pattern("*.xsl")
		#filefilter.add_pattern("*.ods")
		#filechooserdialog.add_filter(filefilter)

		response = filechooserdialog.run()
		#response = dialog.run()
		new_path = ''
		if response == Gtk.ResponseType.OK:
			print "Open clicked"
			print "File: " + filechooserdialog.get_filename()
			new_path = filechooserdialog.get_filename()
		elif response == Gtk.ResponseType.CANCEL:
			print "Cancel clicked"
		filechooserdialog.destroy()
		return new_path
	###################################################################
	# Here we load model A
	###################################################################


	def on_load_model_a(self, window):
		dialog_value = ''
		dialog_value = self.file_open_dialog(window)
		if len(dialog_value) > 0:
			self.model_a_path = dialog_value
			self.model_a = self.file_greeter(self.model_a_path)
			self.liststore_met1.clear()
			self.liststore_r1.clear()
			i = 1
			checbox = True
			for r in self.model_a.reactions:
				#print(r.name)
				self.liststore_r1.append([i,r.name,r.desc,r.ec_number,r.to_string('name')])
				i+=1
			i = 1
			for m in self.model_a.metabolites:
				self.liststore_met1.append([i,m.id,m.name,m.formula,self.model_a.compartments[m.compartment_id],False])
				i+=1
			# tab_label = self.builder.get_object('label1')
			# tab_label.set_text(os.path.basename(self.model_a_path))
			button1_load_model = self.builder.get_object('button1')
			button1_load_model.props.label = os.path.basename(self.model_a_path)
			## now add compartments to the compartment sorting tab
			for c in self.model_a.compartments:
				self.liststore_comp1.append([ str(c), str(self.model_a.compartments[c]), self.model_a.metabolites_in_compartment(c) ])
			## put values in summary screen
			label_comp = self.builder.get_object('model_a_total_comp')
			label_mets = self.builder.get_object('model_a_total_mets')
			label_react = self.builder.get_object('model_a_total_react')
			label_comp.set_text(str(len(self.model_a.compartments)))
			label_mets.set_text(str(len(self.model_a.metabolites)))
			label_react.set_text(str(len(self.model_a.reactions)))

	def on_cell_toggled1(self, widget, path):
		# first we switch the toggle
		self.liststore_met1[path][5] = not self.liststore_met1[path][5]
		#print(path)
		#print("toggle")
		# then we rebuild the list of filtered elements
		filtered = self.builder.get_object('liststore_filtered1')
		filtered.clear()
		m_i = 0
		for m in self.liststore_met1:
			if m[5] == True:
				path = m[0] - 1
				filtered.append([ m[1], m[2], path ])
				self.model_a.metabolites[m_i].filtered = True
				#print(m[1], m[2], path)
				#filtered.append([ self.liststore_met1[path][1],self.liststore_met1[path][2],int(path) ])
			else:
				self.model_a.metabolites[m_i].filtered = False
			m_i+=1



	def jump_to_metabolite1(self, not_used1):
		combobox = self.builder.get_object('combobox_filtered1')
		tree_iter = combobox.get_active_iter()
		if tree_iter != None:
			liststore = self.builder.get_object('liststore_filtered1')
			set_to = liststore.get_value(tree_iter, 2) # 2 is for path in the big liststore
			treeview = self.builder.get_object('treeview_met1')
			treeview.scroll_to_cell(set_to)
			treeview.set_cursor(set_to)


	###################################################################
	# Here we load model B
	###################################################################


	def on_load_model_b(self, window):
		dialog_value = ''
		dialog_value = self.file_open_dialog(window)
		if len(dialog_value) > 0:
			self.model_b_path = dialog_value
			self.model_b = self.file_greeter(self.model_b_path)
			self.liststore_met2.clear()
			self.liststore_r2.clear()
			i = 1
			for r in self.model_b.reactions:
				#print(r.name)
				self.liststore_r2.append([i,r.name,r.desc,r.ec_number,r.to_string('name')])
				i+=1
			i = 1
			for m in self.model_b.metabolites:
				#print(r.name)
				self.liststore_met2.append([i,m.id,m.name,m.formula,self.model_b.compartments[m.compartment_id],False])
				#self.liststore_met1.append([i,m.id,m.name,m.formula,self.model_a.compartments[m.compartment_id],False])
				i+=1
			# tab_label = self.builder.get_object('label2')
			# tab_label.set_text(os.path.basename(self.model_b_path))
			button1_load_model = self.builder.get_object('button2')
			button1_load_model.props.label = os.path.basename(self.model_b_path)
			## now add compartments to the compartment sorting tab
			for c in self.model_b.compartments:
				self.liststore_comp2.append([ str(c), str(self.model_b.compartments[c]), self.model_b.metabolites_in_compartment(c) ])
			## put values in summary screen
			label_comp = self.builder.get_object('model_b_total_comp')
			label_mets = self.builder.get_object('model_b_total_mets')
			label_react = self.builder.get_object('model_b_total_react')
			label_comp.set_text(str(len(self.model_b.compartments)))
			label_mets.set_text(str(len(self.model_b.metabolites)))
			label_react.set_text(str(len(self.model_b.reactions)))

	def on_cell_toggled2(self, widget, path):
		# first we switch the toggle
		self.liststore_met2[path][5] = not self.liststore_met2[path][5]
		#print(path)
		#print("toggle")
		# then we rebuild the list of filtered elements
		filtered = self.builder.get_object('liststore_filtered2')
		filtered.clear()
		m_i = 0
		for m in self.liststore_met2:
			if m[5] == True:
				path = m[0] - 1
				filtered.append([ m[1], m[2], path ])
				self.model_b.metabolites[m_i].filtered = True
				#print(m[1], m[2], path)
				#filtered.append([ self.liststore_met1[path][1],self.liststore_met1[path][2],int(path) ])
			else:
				self.model_b.metabolites[m_i].filtered = False
			m_i+=1


	def jump_to_metabolite2(self, not_used1):
		combobox = self.builder.get_object('combobox_filtered2')
		tree_iter = combobox.get_active_iter()
		if tree_iter != None:
			liststore = self.builder.get_object('liststore_filtered2')
			set_to = liststore.get_value(tree_iter, 2) # 2 is for path in the big liststore
			treeview = self.builder.get_object('treeview_met2')
			treeview.scroll_to_cell(set_to)
			treeview.set_cursor(set_to)







	def update_progressbar(self,fraction,bar):
		pbar = self.builder.get_object(bar)
		pbar.set_fraction(fraction)
		return False
	def update_progressbartext(self,text,bar):
		pbar = self.builder.get_object(bar)
		pbar.set_text(text)
		return False



	###################################################################
	# Here we map compartments
	###################################################################


	def on_apply_compartment_mapping(self, unused1):
		comp_a = self.builder.get_object('liststore_comp1')
		comp_b = self.builder.get_object('liststore_comp2')
		label = self.builder.get_object('label_comp_mapping')

		affected_compartments = []
		#for c in self.model_a.compartments:
		#	print(self.model_a.compartments[c])
		len_a = len(comp_a)
		len_b = len(comp_b)
		smallest = min(len_a,len_b)
		for i in xrange(smallest):
			affected_compartments.append([comp_b[i][0],comp_b[i][1],comp_a[i][0],comp_a[i][1]])
			del self.model_b.compartments[comp_b[i][0]]
			self.model_b.compartments[comp_a[i][0]] = comp_a[i][1]


		## here we update compartment_id for all metabolites in model_b
		for a in affected_compartments:
			for m in self.model_b.metabolites:
				if m.compartment_id == a[0]: ## if the ID match the old one, then update to new one
					m.compartment_id = a[2]

		## print in GUI
		comp_a.clear()
		comp_b.clear()
		for c in self.model_a.compartments:
				comp_a.append([ str(c), str(self.model_a.compartments[c]), self.model_a.metabolites_in_compartment(c) ])
		for c in self.model_b.compartments:
				comp_b.append([ str(c), str(self.model_b.compartments[c]), self.model_b.metabolites_in_compartment(c) ])


		#for c in self.model_b.compartments:
		#	print(c)
		print("-------------")
		big_result = 0
		for aff in affected_compartments:
			a = self.model_a.metabolites_in_compartment(aff[2])
			b = self.model_b.metabolites_in_compartment(aff[2])
			res = min(a,b)
			big_result+=res
			print(res)

		label.set_text(str(len(affected_compartments))+" compartments mapped.\nWith this mapping it is possible to map no more than "+ str(big_result) +" metabolites.")
		# do some calculations




	###################################################################
	# Here we compare metabolites
	###################################################################

	def compare_metabolites(self,model_a,model_b,Alpha,Beta,ignore_compartments,check_id,phonetic,tolerate_h):


		button = self.builder.get_object('button5_compare_mets')
		button.set_sensitive(False)
		## Create metabolites filters
		list_a, list_b = filtered_metabolite_lists(model_a.metabolites, model_b.metabolites)

		result_label = self.builder.get_object('label_met_result')
		i = 1
		total_steps = len(list_a)*len(list_b)
		self.met_comp_counter = float(0)
		gui_update = 0
		gui_update_limit = total_steps/100
		print("Pairs to compare: {0}\t GUI update limit:{1}". format(total_steps,gui_update_limit))
		self.liststore_met_results.clear()
		current_id = -1
		best_pair = []
		self.update_progressbartext('Comparing metabolites...','metabolite_progressbar')


		counter = 0

		counter_of_rejected_c =0
		counter_of_rejected_id =0
		counter_of_rejected_o =0
		counter_of_rejected_h =0
		counter_of_passed =0

		first_list = []
		for A in list_a:
			for B in list_b:
				counter+=1
				comparison = rate_metabolite_pair(A, B, Alpha, Beta, ignore_compartments,check_id,phonetic,tolerate_h)
				if comparison['ok']:
					comparison['row'] = counter
					first_list.append(comparison)

				if comparison['reason'] =='c':
					counter_of_rejected_c+=1
				if comparison['reason'] =='id':
					counter_of_rejected_id+=1
				if comparison['reason'] =='o':
					counter_of_rejected_o+=1
				if comparison['reason'] =='h':
					counter_of_rejected_h+=1
				if comparison['reason'] =='none':
					counter_of_passed+=1

				# The rest in this loop is for progressbar
				fraction = float(counter)/total_steps
				self.update_progressbar(fraction,'metabolite_progressbar')
				## here we limit GUI update
				gui_update+=1
				if gui_update > gui_update_limit:
					gui_update = 0
					yield True
			yield True

		print("Rejected C: {0}".format(counter_of_rejected_c))
		print("Rejected id: {0}".format(counter_of_rejected_id))
		print("Rejected o: {0}".format(counter_of_rejected_o))
		print("Rejected H: {0}".format(counter_of_rejected_h))
		print("Passed L1: {0}".format(counter_of_passed))



		# At this point the Level 1 filtering is done. The next task is to filter out weakest links in one direction.

		# print("Passed L1 (by len()): {0}".format(len(first_list)))


		print("Hello profiler")
		import cProfile, pstats
		pr = cProfile.Profile()
		pr.enable()


		total_steps = len(first_list)
		self.met_comp_counter = float(0)
		gui_update = 0
		gui_update_limit = total_steps/1000
		self.update_progressbartext('Filtering...','metabolite_progressbar')

		second_list = []
		i = 0
		for x in first_list:
			best_score_row = False
			minDscore = x['dscore']
			for y in first_list:
				if x['idA'] == y['idA'] and y['dscore'] < minDscore: # smaller is better!
					best_score_row = y
					minDscore = y['dscore']
			if best_score_row == False:
				best_score_row = x
			else:
				best_score_row = y
			if best_score_row not in second_list:
				second_list.append(best_score_row)
			print("F {0}/{1}".format(i,len(first_list)))
			i+=1



			# The rest in this loop is for progressbar
			self.met_comp_counter+=1
			fraction = float(self.met_comp_counter)/total_steps
			## here we limit GUI update
			gui_update+=1
			if gui_update > gui_update_limit:
				self.update_progressbar(fraction,'metabolite_progressbar')
				gui_update = 0
				yield True

		pr.disable()
		f = open('x.prof', 'w')
		sortby = 'cumulative'
		pstats.Stats(pr, stream=f).strip_dirs().sort_stats(sortby).print_stats()
		f.close()
		print("Thank you profiler")


		# At this point the Level 2 filtering is done. The next tast is to filter out weakest links in the other direction.

		third_list = []
		i = 0
		for x in second_list:
			best_score_row = False
			minDscore = x['dscore']
			for y in second_list:
				if x['idB'] == y['idB'] and y['dscore'] < minDscore: # smaller is better!
					best_score_row = y
					minDscore = y['dscore']
			if best_score_row == False:
				best_score_row = x
			else:
				best_score_row = y
			if best_score_row not in third_list:
				third_list.append(best_score_row)
			print("S {0}/{1}".format(i,len(second_list)))
			i+=1


		print("Levels passed (L1->L2->L3): {0}->{1}->{2}".format(len(first_list),len(second_list),len(third_list)))
		# print("Passed L3 (by len()): {0}".format(len(third_list)))


		# now put the content of third_list in the liststore
		# best_pair = [ i, O['out_form'],O['out_comp'],mA.name,mB.name,O['out_ratio'], True, mA.formula, mB.formula, mA.id, mB.id, O['out_distance'], O['bgcolor'], O['bgcolor'], False, score]

		# Structure of first_list[] elements
		# {'ok': True, 'reason':'none', 'idA':A.id, 'idB': B.id, 'dscore':realscore, 'ratio': ratio, 'distance': distance, 'diff_h_count':diff_h_count}

		i=0
		for x in third_list:
			O = format_output_for_liststore(x['fsim'],x['diff_h_count'],x['compartments_match'])
			element = [ i, O['out_form'], O['out_comp'], x['nameA'],x['nameB'], True, x['formulaA'], x['formulaB'], x['idA'], x['idB'], 'white', 'white', False, x['dscore']]
			self.liststore_met_results.append(element)
			i+=1

		result_label.set_text(str(len(self.liststore_met_results)))


						# te es paliku



		self.update_progressbar(0,'metabolite_progressbar')
		self.update_progressbartext('Comparison completed','metabolite_progressbar')

		## here we update number selected elements
		col_appr = 5 # column for 'approve'
		selected_items = 0
		for m in self.liststore_met_results:
			if m[col_appr] == True: # 5 is for 'approve' in liststore_met_results
				selected_items+=1
		label_selected = self.builder.get_object('label_met_selected')
		label_selected.set_text(str(selected_items))

		button.set_sensitive(True)


		# set upper and lower bounds for the Dscore slider to reflect the actual highest and lowest Dscore
		adjustment_D_threshold = self.builder.get_object('adjustment_D_threshold')
		allDscores =[]
		sumofDscores = 0
		for x in third_list:
			allDscores.append(x['dscore'])
			sumofDscores+=x['dscore']
		adjustment_D_threshold.set_upper(max(allDscores))
		adjustment_D_threshold.set_lower(min(allDscores))
		adjustment_D_threshold.set_value(sumofDscores/len(allDscores)) # the average Dscore

		yield False



	def on_compare_metabolites(self, window):
		adjustmentA = self.builder.get_object('adjustmentA')
		adjustmentB = self.builder.get_object('adjustmentB')
		switch_ignore_compartments = self.builder.get_object('switch_ignore_compartments')
		switch_check_id = self.builder.get_object('switch_check_id')
		switch_ignore_case = self.builder.get_object('switch_ignore_case')
		switch_phonetic = self.builder.get_object('switch_phonetic')
		adjustment_tolerate_atoms_h = self.builder.get_object('adjustment_tolerate_atoms_h')

		Alpha = adjustmentA.get_value()
		Beta = adjustmentB.get_value()
		ignore_compartments = switch_ignore_compartments.get_active()
		check_id = switch_check_id.get_active()
		phonetic = switch_phonetic.get_active()
		tolerate_h = adjustment_tolerate_atoms_h.get_value()

		task2 = self.compare_metabolites(self.model_a,self.model_b,Alpha,Beta,ignore_compartments,check_id,phonetic,tolerate_h)
		GObject.idle_add(task2.next)




	def on_cell_toggled_met_results(self, widget, path):
		# first we switch the toggle
		col_appr = 5 # column for 'approve'
		liststore = self.builder.get_object('liststore_met_results')
		label = self.builder.get_object('label_met_selected')
		liststore[path][col_appr] = not liststore[path][col_appr] # Column 5. is for Approve
		selected_items = 0
		for m in liststore:
			if m[col_appr] == True:
				selected_items+=1
		label.set_text(str(selected_items))

	def on_cursor_changed_met_results(self,treeview):
		#label_formula_a
		#label_name_a
		if treeview:
			liststore = self.builder.get_object('liststore_met_results')
			formula_a = self.builder.get_object('label_formula_a')
			formula_b = self.builder.get_object('label_formula_b')
			name_a = self.builder.get_object('label_name_a')
			name_b = self.builder.get_object('label_name_b')

			c = treeview.get_cursor()
			path = c[0]
			if path != None:
				name_a.set_text(liststore[path][3])
				name_b.set_text(liststore[path][4])
				formula_a.set_text(liststore[path][6])
				formula_b.set_text(liststore[path][7])
		pass

	def on_d_threshold_changed(self,adjustment):
		col_dscore = 13
		col_color1 = 10
		col_appr = 5 # column for 'approve'
		# print('A'),
		value = adjustment.get_value()
		for x in self.liststore_met_results:
			if x[col_dscore] < value:
				x[col_appr] = True
				x[col_color1] = 'white'
			else:
				x[col_appr] = False
				x[col_color1] = 'pink'
		## here we update number selected elements
		selected_items = 0
		for m in self.liststore_met_results:
			if m[col_appr] == True: # 5 is for 'approve' in liststore_met_results
				selected_items+=1
		label_selected = self.builder.get_object('label_met_selected')
		label_selected.set_text(str(selected_items))


	def apply_met_mapping(self):
		col_appr = 5 # column for 'approve'
		col_idA = 8
		col_idB = 9
		liststore = self.builder.get_object('liststore_met_results')
		#total_steps = float(len(self.liststore_met_results))
		total_steps = float(len(self.model_b.reactions))
		self.reconciled_reactions_a = []
		self.reconciled_reactions_b = []

		## now we will rewrite all metabolite IDs in all reactions in all reactants in model B
		self.update_progressbartext('Applying to model B...','metabolite_progressbar')
		self.met_comp_counter = 0

		r_i = 0
		gui_update = 0
		for r in self.model_b.reactions:
			something_changed = False
			for pair in liststore:
				if pair[col_appr]: ## the 5. is for approve
					s_i = 0
					for s in r.substrates:
						if s.ref == pair[col_idB]: ## 9 is for id_b
							self.model_b.reactions[r_i].substrates[s_i].ref = pair[col_idA]+'_reconciled' # 8 is for id_a
							self.model_b.reactions[r_i].substrates[s_i].reconciled = True
							something_changed = True
						s_i+=1
						pass
					s_i = 0
					for s in r.products:
						if s.ref == pair[col_idB]: ## 9 is for id_b
							self.model_b.reactions[r_i].products[s_i].ref = pair[col_idA]+'_reconciled'
							self.model_b.reactions[r_i].products[s_i].reconciled = True
							something_changed = True
						s_i+=1
						pass
			if something_changed:
				self.reconciled_reactions_b.append(self.model_b.reactions[r_i])

			r_i+=1

			fraction = self.met_comp_counter/total_steps
			self.met_comp_counter+=1
			self.update_progressbar(fraction,'metabolite_progressbar')
			## here we limit GUI update
			gui_update+=1
			if gui_update > 50: # gui_update_mapping
				gui_update = 0
				yield True
		self.update_progressbar(0,'metabolite_progressbar')



		## now we will rewrite metabolite IDs in all reactions in all reconciled reactants model A
		self.update_progressbartext('Applying to model A...','metabolite_progressbar')
		self.met_comp_counter = 0
		total_steps = float(len(self.model_a.reactions))

		r_i = 0
		gui_update = 0
		for r in self.model_a.reactions:
			something_changed = False
			for pair in liststore:
				if pair[col_appr]: ## the 5. is for approve
					s_i = 0
					for s in r.substrates:
						if s.ref == pair[col_idB]: ## 9 is for id_b
							self.model_a.reactions[r_i].substrates[s_i].ref = pair[col_idB]+'_reconciled'
							self.model_a.reactions[r_i].substrates[s_i].reconciled = True
							something_changed = True
						s_i+=1
						pass
					s_i = 0
					for s in r.products:
						if s.ref == pair[col_idA]: ## 8 is for id_a
							self.model_a.reactions[r_i].products[s_i].ref = pair[col_idA]+'_reconciled'
							self.model_a.reactions[r_i].products[s_i].reconciled = True
							something_changed = True
						s_i+=1
						pass
			if something_changed:
				self.reconciled_reactions_a.append(self.model_a.reactions[r_i])
				#print("Original",r_temp.to_string('name'))
				#print("Affected",self.model_b.reactions[r_i].to_string('id'))
			r_i+=1

			fraction = self.met_comp_counter/total_steps
			self.met_comp_counter+=1
			self.update_progressbar(fraction,'metabolite_progressbar')
			gui_update+=1
			if gui_update > 50:
				gui_update = 0
				yield True
		self.update_progressbar(0,'metabolite_progressbar')
		self.update_progressbartext('Mapping applied','metabolite_progressbar')


		print(len(self.reconciled_reactions_a),"reactions with reconciled metabolites in A")
		print(len(self.reconciled_reactions_b),"reactions with reconciled metabolites in B")

		## Write reconciled reactions in a file
		f = open("reconciled_a.csv", 'w')
		for r in self.reconciled_reactions_a:
			f.write(r.to_string("id")+"\n")
		f.close()

		f = open("reconciled_b.csv", 'w')
		for r in self.reconciled_reactions_b:
			f.write(r.to_string("id")+"\n")
		f.close()

		yield False







	def on_apply_met_mapping(self,not_used):
		task3 = self.apply_met_mapping()
		GObject.idle_add(task3.next)
















	###################################################################
	# Compare reactions
	###################################################################

	def compare_reactions(self, reactions_a, reactions_b,check_ec,crosscheck,by_what,filter_gpr,only_missing,cumulative,similarity_threshold):
		# only_missing : when we evaluate only reactions with reconciled reactions, we have to relax "missing metabolites" tolerance.
		# only_missing : by default True. If we evaluate reactants similarity then False
		similarity_threshold = float(similarity_threshold) / 100

		def chech_thresholds(diff_result,crosscheck,threshold_left,threshold_right,cumulative):
			go_on = False
			summed_d = diff_result['diff_substrates']['diff'] + diff_result['diff_products']['diff']
			summed = summed_d

			if diff_result['diff_substrates']['diff'] <= threshold_left and diff_result['diff_products']['diff'] <= threshold_right: ## if differences are smaller then thresholds
				go_on = True
				# print("..Direct")
			if crosscheck:
				if diff_result['diff_r_substrates']['diff'] <= threshold_left and diff_result['diff_r_products']['diff'] <= threshold_right: ## if differences are smaller then thresholds
					summed_r = diff_result['diff_r_substrates']['diff'] + diff_result['diff_r_products']['diff']
					summed = min(summed_d,summed_r)
					# print("..Found as reversible")
					go_on = True

			if cumulative:
				if summed > max(threshold_left,threshold_right):
					go_on = False
				else:
					go_on = True

				pass
			return go_on

		def chech_overall_thresholds(diff_result,overall_threshold):
			if diff_result['len_substrates'] >= overall_threshold and diff_result['len_products'] >= overall_threshold:
				return True
			else:
				return False




		def tolerate_only_missing(diff_result,only_missing,crosscheck):
			go_on = False
			if only_missing:
				if diff_result['diff_substrates']['residual'] == diff_result['diff_substrates']['diff'] and diff_result['diff_products']['residual'] == diff_result['diff_products']['diff']: # len must be different
					go_on = True
				if crosscheck:
					if diff_result['diff_r_substrates']['residual'] == diff_result['diff_r_substrates']['diff'] and diff_result['diff_r_products']['residual'] == diff_result['diff_r_products']['diff']: # len must be different
						go_on = True
				# print("tolerate_only_missing result",go_on)
				return go_on
			else:
				print("")
				return True

		def calculate_reactants_similarity(diff_result,crosscheck):
			sim_subst = float(diff_result['diff_substrates']['matching']) / diff_result['diff_substrates']['maxlen']
			sim_produ = float(diff_result['diff_products']['matching']) / diff_result['diff_products']['maxlen']
			sim_d = float(sim_subst + sim_produ)/2
			sim = sim_d

			if crosscheck:
				sim_subst = float(diff_result['diff_r_substrates']['matching']) / diff_result['diff_r_substrates']['maxlen']
				sim_produ = float(diff_result['diff_r_products']['matching']) / diff_result['diff_r_products']['maxlen']
				sim_r = float(sim_subst + sim_produ)/2

				sim = max(sim_d,sim_r)

			return sim


		adjustment_left = self.builder.get_object('adjustment_come_off_left')
		adjustment_right = self.builder.get_object('adjustment_come_off_right')
		threshold_left = adjustment_left.get_value()
		threshold_right = adjustment_right.get_value()
		adjustment_not_tolerate = self.builder.get_object('adjustment_not_tolerate')
		overall_threshold = adjustment_not_tolerate.get_value()

		switch_greedy_reaction_matching = self.builder.get_object('switch_greedy_reaction_matching')
		greedy_reaction_matching = switch_greedy_reaction_matching.get_active()
		# greedy_reaction_matching = False

		#button = self.builder.get_object('button5_compare_mets')
		result_label = self.builder.get_object('label_react_result')
		liststore = self.builder.get_object('liststore_react_results')
		liststore2 = self.builder.get_object('liststore_reaction_evaluation')
		# liststore = self.builder.get_object('treestore_react_results') # previously was liststore, now is treestore

		liststore.clear()
		liststore2.clear()

		equal_reactions = 0

		## First, clear we have to set 'common' tag for all reactions to 0
		for r in self.model_a.reactions:
			r.tags['common'] = 0
		for r in self.model_b.reactions:
			r.tags['common'] = 0

		combo_l= list(itertools.product(reactions_a,reactions_b))
		# here we just got all possible combinations. It's so much simpler than nested FOR loops
		print(str(len(combo_l))+ " combinations to check.")

		## Create metabolites filters
		met_filters_a = []
		met_filters_b = []
		for m in self.model_a.metabolites:
			if m.filtered == True:
				met_filters_a.append(m.get_id())
		for m in self.model_b.metabolites:
			if m.filtered == True:
				met_filters_b.append(m.get_id())


		print("-----------------------------------------------------")
		print("Filters")
		print(len(met_filters_a))
		print(met_filters_a)
		print(len(met_filters_b))
		print(met_filters_b)
		print("-----------------------------------------------------")

		total_steps = len(combo_l)
		react_counter = float(0)
		print("Pairs to compare: "),
		print(total_steps)
		gui_update = 0
		gui_update_limit = (total_steps/1000)
		print("GUI update limit: "),
		print(gui_update_limit)

		results = []
		self.reaction_results = []
		i = 0
		p_i = 0
		bgcolor = 'white'
		identical_reactions = 0

		# since we are storing found results in a Treeview, it is important to keep track on current reaction
		has_changed = False
		old_reaction_id = ''
		best_similarity = 0
		self.update_progressbartext('Comparing reactions...','reaction_progressbar')

		L2_current_id = ''
		for r in combo_l:
			fraction = react_counter/total_steps
			self.update_progressbar(fraction,'reaction_progressbar')
			react_counter+=1
			reactants_similarity = 0

			diff_result = r[0].difference(r[1],by_what,crosscheck,met_filters_a,met_filters_b)

			go_on = False
			## Now check if the thresholds are not met.
			## first chack if reactions are identical

			bgcolor = 'white'

			if chech_thresholds(diff_result,crosscheck,threshold_left,threshold_right,cumulative):
				if tolerate_only_missing(diff_result,only_missing,crosscheck):
					if chech_overall_thresholds(diff_result,overall_threshold):
						go_on = True
						reactants_similarity = calculate_reactants_similarity(diff_result,crosscheck)
						if reactants_similarity == 1:
							bgcolor = 'LightGreen'



			if go_on:
				ec_result = compare_ec_numbers(r[0].ec_number,r[1].ec_number)
				total_ec = count_ec_numbers(r[0].ec_number,r[1].ec_number)
				ec_str = str(ec_result)+'/'+str(total_ec)
				if check_ec:
					if ec_result < 1:
						go_on = False

				if reactants_similarity < similarity_threshold:
						# if reactants similarity is below the threshold, then just skip this reaction
					go_on = False

				if go_on:
					i+=1
					equal_reactions+=1

					## prepare printable difference
					if diff_result['diff_substrates']['diff'] > 0:
						display_diff_substrates = str(diff_result['diff_substrates']['diff'])
					else:
						display_diff_substrates = ''
					if diff_result['diff_products']['diff'] > 0:
						display_diff_products = str(diff_result['diff_products']['diff'])
					else:
						display_diff_products = ''




					liststore.append([ i, r[0].name, r[1].name, str(ec_result), r[0].desc, r[0].to_string('id'), r[1].desc, r[1].to_string('id'), display_diff_substrates, display_diff_products,True,r[0].to_string('neutral'),r[1].to_string('neutral'),bgcolor,reactants_similarity])

					##print(str(round(ratio_synonyms,1))+' '+str(ec_str)+' '+str(r[0].reference)+ ' '+ str(r[1].reference)+ '\t' + r[0].to_string(by_what) + '\t' + r[1].to_string(by_what))

					self.reaction_results.append(r[0])

					## this block populates liststore2
					if L2_current_id == '': #pirmais elements
						L2_current_id = r[0].name
						L2_current_name = r[0].desc
						L2_current_matching_other = 0
						L2_current_best_sim = reactants_similarity
						L2_i = 1

					if L2_current_id == r[0].name:
						# L2_current_id = r[0].name
						# L2_current_name = r[0].desc
						L2_current_matching_other+=1
						if L2_current_best_sim > reactants_similarity:
							L2_current_best_sim = reactants_similarity
					if L2_current_id != r[0].name: # id has changed. Now add current record
						liststore2.append([ L2_i, L2_current_id, L2_current_name, L2_current_matching_other, L2_current_best_sim])
						L2_i+=1
						L2_current_id = r[0].name
						L2_current_name = r[0].desc
						L2_current_matching_other = 1
						L2_current_best_sim = reactants_similarity
						if L2_current_best_sim > reactants_similarity:
							L2_current_best_sim = reactants_similarity
					## this block populates liststore2: END

					## this peace of code makes no sense. We have to find the real reactions
					r[0].tag = 'common'
					r[0].tags['common'] = 1
					r[1].tags['common'] = 1
					## This is how it should have been implemented!
					for rr in self.model_a.reactions:
						if r[0].reference == rr.reference:
							rr.tags['common'] = 1
					for rr in self.model_b.reactions:
						if r[1].reference == rr.reference:
							rr.tags['common'] = 1



			p_i+=1

			result_label.set_text(str(i))

			gui_update+=1
			# if gui_update > gui_update_limit:
			if gui_update > gui_update_limit:
				gui_update = 0
				yield True
		# have to add the last "current record"
		if L2_current_id != '': #pirmais elements
			liststore2.append([ L2_i, L2_current_id, L2_current_name, L2_current_matching_other, L2_current_best_sim])
		else:
			self.update_progressbartext('Nothing to do! Please apply metabolite mapping','reaction_progressbar')



		ii=0
		for ra in self.model_a.reactions:
			if ra.tags['common'] > 0: ## we need only reactions that are common
				ii+=1
		print("True number of common reactions",ii,"list lenght",len(self.reaction_results))

		if greedy_reaction_matching:
			# Greedy matching for reactions
			print("Running greedy matching on reactions")
			old_reaction_id = ''
			best_similarity = 0
			self.update_progressbartext('Greedy matching...','reaction_progressbar')
			gr_i = 0
			i = 0

			gui_update_limit = (len(liststore)/500)

			for r in liststore:
				gr_i+=1
				i+=1
				fraction = float(gr_i) / len(liststore)
				self.update_progressbar(fraction,'reaction_progressbar')
				gui_update+=1
				if gui_update > gui_update_limit:
					gui_update = 0
					yield True
				# yield True



				best_similarity = 0
				best_counter = 0
				for r1 in liststore: # find the best in this loop
					if r[1] == r1[1]:
						if best_similarity < r1[14]:
							best_similarity = r1[14]
							best_counter = 0
						if best_similarity == r1[14]:
							best_counter+=1
							# r[13] = "yellow" ## 13. is for bgcolor
				# print("best_similarity",best_similarity)
				for r1 in liststore:
					if r[1] == r1[1]: # in this loop disapprove all that are below the best
						if r[14] < best_similarity:
							r[10] = False
							r[13] = "pink" ## 13. is for bgcolor
						elif r[14] == best_similarity:
							r[13] = "LightGreen" ## 13. is for bgcolor
						if best_counter > 1 :
							r[13] = "yellow" ## 13. is for bgcolor
							r[10] = False
			print("Matching finished")

		self.update_progressbar(0,'reaction_progressbar')
		self.update_progressbartext('Comparison completed','reaction_progressbar')


		for zzz in results:
			print(zzz)
		print('-----------------------------------------------------')




		if check_ec == 1:
			ec_text = 'E.C. numbers checked'
		else:
			ec_text = 'E.C. numbers ignored'
		print('compared by \''+ by_what+'\'')
		print(ec_text)
		#print(str(equal_reactions) + ' reactions ('+str(equal_percentage)+'%) from \"' + self.title + '\" found in \"' + other.title +'\"')
		#return {'check_ec':check_ec, 'results_list':results}
		yield False

	def on_compare_by_formulas(self, window):
		switch_filter_ec = self.builder.get_object('switch_filter_ec')
		switch_cumulative = self.builder.get_object('switch_cumulative')
		cumulative = switch_cumulative.get_active()
		switch_only_missing = self.builder.get_object('switch_only_missing')
		only_missing = switch_only_missing.get_active()
		adjustment_reaction_similarity = self.builder.get_object('adjustment_reaction_similarity')
		reaction_similarity = adjustment_reaction_similarity.get_value()
		# switch_filter_gpr = self.builder.get_object('switch_filter_gpr')
		switch_allow_crosscheck = self.builder.get_object('switch_allow_crosscheck')
		filter_ec = switch_filter_ec.get_active()
		#filter_gpr = switch_filter_gpr.get_active()
		filter_gpr = False
		crosscheck = switch_allow_crosscheck.get_active()

		by_what = 'charged'
		task3 = self.compare_reactions(self.model_a.reactions, self.model_b.reactions,filter_ec,crosscheck,by_what,filter_gpr,only_missing,cumulative,reaction_similarity)
		GObject.idle_add(task3.next)

	def on_compare_by_ids(self, window):
		switch_filter_ec = self.builder.get_object('switch_filter_ec')
		switch_cumulative = self.builder.get_object('switch_cumulative')
		cumulative = switch_cumulative.get_active()
		switch_only_missing = self.builder.get_object('switch_only_missing')
		only_missing = switch_only_missing.get_active()
		adjustment_reaction_similarity = self.builder.get_object('adjustment_reaction_similarity')
		reaction_similarity = adjustment_reaction_similarity.get_value()
		#switch_filter_gpr = self.builder.get_object('switch_filter_gpr')
		switch_allow_crosscheck = self.builder.get_object('switch_allow_crosscheck')
		filter_ec = switch_filter_ec.get_active()
		#filter_gpr = switch_filter_gpr.get_active()
		filter_gpr = False
		crosscheck = switch_allow_crosscheck.get_active()

		by_what = 'id'

		#self.reconciled_reactions_a
		task3 = self.compare_reactions(self.model_a.reactions, self.model_b.reactions,filter_ec,crosscheck,by_what,filter_gpr,only_missing,cumulative,reaction_similarity)
		#task3 = self.compare_reactions(self.reconciled_reactions_a, self.reconciled_reactions_b,filter_ec,crosscheck,by_what,filter_gpr)
		GObject.idle_add(task3.next)

	def on_evaluate_reaction_similarity(self, window):
		switch_filter_ec = self.builder.get_object('switch_filter_ec')
		switch_cumulative = self.builder.get_object('switch_cumulative')
		cumulative = switch_cumulative.get_active()
		switch_only_missing = self.builder.get_object('switch_only_missing')
		only_missing = switch_only_missing.get_active()
		adjustment_reaction_similarity = self.builder.get_object('adjustment_reaction_similarity')
		reaction_similarity = adjustment_reaction_similarity.get_value()

		# switch_filter_gpr = self.builder.get_object('switch_filter_gpr')
		switch_allow_crosscheck = self.builder.get_object('switch_allow_crosscheck')
		filter_ec = switch_filter_ec.get_active()
		#filter_gpr = switch_filter_gpr.get_active()
		filter_gpr = False
		crosscheck = switch_allow_crosscheck.get_active()

		by_what = 'id'
		task3 = self.compare_reactions(self.reconciled_reactions_a, self.reconciled_reactions_b,filter_ec,crosscheck,by_what,filter_gpr,only_missing,cumulative,reaction_similarity)
		GObject.idle_add(task3.next)

	def on_cursor_changed_react_results(self,treeview):
		#label_formula_a
		#label_name_a
		if treeview:
			liststore = self.builder.get_object('liststore_react_results')
			# liststore = self.builder.get_object('treestore_react_results')

			string_a = self.builder.get_object('label_rstring_a')
			string_b = self.builder.get_object('label_rstring_b')
			string_f_a = self.builder.get_object('label_rstring_f_a')
			string_f_b = self.builder.get_object('label_rstring_f_b')
			name_a = self.builder.get_object('label_rname_a')
			name_b = self.builder.get_object('label_rname_b')

			c = treeview.get_cursor()
			path = c[0]
			if path != None:
				name_a.set_text(liststore[path][4])
				name_b.set_text(liststore[path][6])
				string_a.set_text(liststore[path][5])
				string_b.set_text(liststore[path][7])
				string_f_a.set_text(liststore[path][11])
				string_f_b.set_text(liststore[path][12])
		pass

	def on_cell_toggled_react_results(self, widget, path):
		# first we switch the toggle
		liststore = self.builder.get_object('liststore_react_results')
		# liststore = self.builder.get_object('treestore_react_results')

		label = self.builder.get_object('label_react_selected')
		liststore[path][10] = not liststore[path][10] # Column 10. is for Approve
		selected_items = 0
		for m in liststore:
			if m[10] == True:
				selected_items+=1
		label.set_text(str(selected_items))
		## now find the real reactions
		for r in self.model_a.reactions:
			if r.id == liststore[path][1]:
				if liststore[path][10] == True:
					r.tags['common'] = 1
				else:
					r.tags['common'] = 0
		## now find the real reactions
		for r in self.model_b.reactions:
			if r.id == liststore[path][2]:
				if liststore[path][10] == True:
					r.tags['common'] = 1
				else:
					r.tags['common'] = 0


	###################################################################
	# Exporting
	###################################################################

	def on_export_to_csv(self, window): #export metabolites mapping to CSV
		print("export to CSV")
		dialog_value = ''
		dialog_value = self.file_save_dialog(window)
		if len(dialog_value) > 0:
			print(dialog_value)
			f = open(dialog_value, 'w')

			# [ i, 			0
			# O['out_form'],	1
			# O['out_comp'],	2
			# x['nameA'],		3
			# x['nameB'], 	4
			# True, 			5
			# x['formulaA'],	6
			# x['formulaB'],	7
			# x['idA'],		8
			# x['idB'],		9
			# 'white',		10
			# 'white',		11
			# False,			12
			# x['dscore']]	13
			f.write('Approved\tRow\tFormulas\tCompartments\tDscore\tFormula A\tFormula B\tName A\tName B\n\r')

			for m in self.liststore_met_results:
				if m[5] == True:
					approved = "Yes"
				else:
					approved = "No"
				# f.write(str(approved)+'\t'+str(m[0])+'\t'+str(m[1])+'\t'+str(m[2])+'\t'+str(m[13]) +'\t'+m[6]+'\t'+m[7]+'\t'+m[2]+'\t'+m[3]+'\n\r')
				f.write("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\n\r".format(approved,m[0],m[1],m[2],m[13],m[6],m[7],m[3],m[4]))
			f.close()

	def on_export_to_csv_reactions(self, window): #export metabolites mapping to CSV
		print("export to CSV")
		dialog_value = ''
		dialog_value = self.file_save_dialog(window)
		liststore = self.builder.get_object('liststore_react_results')
		if len(dialog_value) > 0:
			print(dialog_value)
			f = open(dialog_value, 'w')
			f.write('ModeRator approved\tRow\tMatching reactants\tName A\tName B\tReaction A\tReaction B\tReaction A (formulas)\tReaction B (formulas)\n\r')
			for m in liststore:
				if m[10] == True: # 10. is for Approve
					approved = "Yes"
				else:
					approved = "No"
				f.write(str(approved)+'\t'+str(m[0])+'\t'+str(m[14])+'\t'+str(m[4])+'\t'+str(m[6])+'\t'+str(m[5])+'\t'+str(m[7])+'\t'+str(m[11])+'\t'+str(m[12])+'\n\r')
			f.close()
			self.update_progressbartext('Comparison of reactions exported to CSV','reaction_progressbar')

	def on_export_to_csv_reactions_evaluation(self, window): #export metabolites mapping to CSV
		print("export to CSV")
		dialog_value = ''
		dialog_value = self.file_save_dialog(window)
		liststore = self.builder.get_object('liststore_reaction_evaluation')
		if len(dialog_value) > 0:
			print(dialog_value)
			f = open(dialog_value, 'w')
			f.write('Row\tReaction ID\tReaction name\tSimilar reactions\tBest similarity\n\r')
			for m in liststore:
				f.write(str(m[0])+'\t'+str(m[1])+'\t'+str(m[2])+'\t'+str(m[3])+'\t'+str(m[4])+'\n\r')
			f.close()
			self.update_progressbartext('Evaluation of similar reactions exported to CSV','reaction_progressbar')




	def on_export_to_sbml(self, window): # exports the intersection of modelA and modelB
		def process_one_side(reactants,metabolites,suffix):
			for re in reactants:
				## get reactants reference to the particular metabolite and get that metabolite
				for m in metabolites:
					if m.id == re.ref:
						if not self.model_d.has_metabolite(string.join([suffix,m.id],"")):
							new_metabolite = copy.deepcopy(m)
							new_metabolite.id = string.join([suffix,new_metabolite.id],"")
							self.model_d.add_metabolite(new_metabolite)
							#print("ADD", m.id),
		def process_reaction(r,suffix):
			new_reaction = copy.deepcopy(r)
			for re in new_reaction.substrates:
				re.ref = string.join([suffix,re.ref],"")
			for re in new_reaction.products:
				re.ref = string.join([suffix,re.ref],"")

			new_reaction.id = string.join([suffix,new_reaction.id],"")
			self.model_d.add_reaction(new_reaction)

		dialog_value = ''
		dialog_value = self.file_save_dialog(window)
		if len(dialog_value) > 0:
			self.model_d = st_model("Intersection model","Intersection of "+self.model_a.title+" and "+self.model_b.title)

			suffix2 = ''
			print("===== Metabolites from A =====")
			## Add metabolites from model A

			for r in self.model_a.reactions:
				if r.tags['common'] > 0: ## we need only reactions that are common
					process_one_side(r.substrates,self.model_a.metabolites,suffix2)
					process_one_side(r.products,self.model_a.metabolites,suffix2)
			## Add reactions from model A
			i=0
			for r in self.model_a.reactions:
				if r.tags['common'] > 0: ## we need only reactions that are common
					i+=1
					process_reaction(r,suffix2)
			print("Reactions added",i)
			## Add compartments
			for m in self.model_a.metabolites:
				if m.compartment_id not in self.model_d.compartments:
					self.model_d.compartments[m.compartment_id] = self.model_a.compartments[m.compartment_id]

			print("====== Model D: compartments", len(self.model_d.compartments))
			print("=====Model D: metabolites", len(self.model_d.metabolites))
			print("=====Model D: reactions", len(self.model_d.reactions))




			self.save_as_sbml(self.model_d,dialog_value)
			self.update_progressbartext('Exported to SBML','reaction_progressbar')






	def on_save_as_sbml_c(self, window): # export model C
		dialog_value = ''
		dialog_value = self.file_save_dialog(window)
		if len(dialog_value) > 0:
			#print(dialog_value)
			self.save_as_sbml(self.model_c,dialog_value)
		print("Probably saved into SBML")


	def save_as_sbml(self,model_a,dialog_value): ## exports any given model to SBML
		compartments = []
		species_names = []
		species = []

		#for c in model_a.compartments:
		#	print(model_a.compartments[c])


		for r in model_a.reactions:
			for reactant in r.substrates:
				if reactant.ref not in species_names:
					species_names.append(reactant.ref)
					species.append([reactant.ref,reactant.name, ''])
			for reactant in r.products:
				if reactant.ref not in species_names:
					species_names.append(reactant.ref)
					species.append([reactant.ref,reactant.name, ''])

		## Now find compartments for all species
		for m in model_a.metabolites:
				c_id = prepare_item_id_for_sbml(m.compartment_id)
#				print(m.compartment_id,c_id)
				if c_id not in compartments:
					compartments.append(c_id)
		for s in species:
				for m in model_a.metabolites:
					if s[0] == prepare_item_id_for_sbml(m.id):
						s[1] = m.name
						s[2] = prepare_item_id_for_sbml(m.compartment_id)


		## Now do the libSBML work
		document = SBMLDocument(2, 4)
		model = document.createModel()
		for c in compartments:
			c1 = model.createCompartment()
			c1.setName(c)
			c1.setId(c)
			c1.setVolume(10)
		for s in species:
			s1 = model.createSpecies()
			s1.setName(str(s[1]))
			s1.setId(prepare_item_id_for_sbml(s[0]))
			s1.setCompartment(prepare_item_id_for_sbml(s[2]))
			s1.setInitialAmount(100)
		for r in model_a.reactions:
			r1 = model.createReaction()
			r1.setName(r.desc)
			r1.setId(prepare_item_id_for_sbml(r.name))
			for re in r.substrates:
				re1 = r1.createReactant()
				re1.setSpecies(prepare_item_id_for_sbml(re.ref))
				re1.setStoichiometry(re.st)
			for re in r.products:
				re1 = r1.createProduct()
				re1.setSpecies(prepare_item_id_for_sbml(re.ref))
				re1.setStoichiometry(re.st)

		model_name = 'ModeRator_exported-'+model_a.title
		model.setName(model_name)
		model.setId('ModelID')
		#document.setLevelAndVersion(3,1)
		writeSBMLToFile(document,dialog_value)
		pass


	###################################################################
	# Merging
	###################################################################

	def merge_networks(self,suffix1, suffix2):
		def process_one_side(reactants,metabolites,suffix):
			for re in reactants:
				## get reactants reference to the particular metabolite and get that metabolite
				for m in metabolites:
					if m.id == re.ref:
						if not self.model_c.has_metabolite(string.join([suffix,m.id],"")):
							new_metabolite = copy.deepcopy(m)
							new_metabolite.id = string.join([suffix,new_metabolite.id],"")
							self.model_c.add_metabolite(new_metabolite)
							#print("ADD", m.id),
		def process_reaction(r,suffix):
			new_reaction = copy.deepcopy(r)
			for re in new_reaction.substrates:
				re.ref = string.join([suffix,re.ref],"")
			for re in new_reaction.products:
				re.ref = string.join([suffix,re.ref],"")

			new_reaction.id = string.join([suffix,new_reaction.id],"")
			#print(suffix)
			#print(new_reaction.id)
			self.model_c.add_reaction(new_reaction)

		liststore_comp3 = self.builder.get_object('liststore_comp3')
		liststore_rect3 = self.builder.get_object('liststore_r3')
		liststore_mets3 = self.builder.get_object('liststore_met3')

		label_comp = self.builder.get_object('model_c_total_comp')
		label_mets = self.builder.get_object('model_c_total_mets')
		label_react = self.builder.get_object('model_c_total_react')

		#self.model_c1 = st_model("Temporary model","Description of the model C1")
		self.model_c = st_model("Merged model","Description of the Merged model")

		## Add metabolites from model A
		print("===== Metabolites from A =====")
		for r in self.model_a.reactions:
			process_one_side(r.substrates,self.model_a.metabolites,suffix1)
			process_one_side(r.products,self.model_a.metabolites,suffix1)
		## Add reactions from model A
		for r in self.model_a.reactions:
			process_reaction(r,suffix1)

		print("===== Metabolites from B =====")
		## Add metabolites from model B
		for r in self.model_b.reactions:
			if r.tags['common'] < 1: ## from model B we need only reactions that are not common
				process_one_side(r.substrates,self.model_b.metabolites,suffix2)
				process_one_side(r.products,self.model_b.metabolites,suffix2)
		## Add reactions from model B
		for r in self.model_b.reactions:
			if r.tags['common'] < 1: ## from model B we need only reactions that are not common
				process_reaction(r,suffix2)

		## Add compartments from bth models
		for m in self.model_a.metabolites:
			if m.compartment_id not in self.model_c.compartments:
				self.model_c.compartments[m.compartment_id] = self.model_a.compartments[m.compartment_id]
		for m in self.model_b.metabolites:
			if m.compartment_id not in self.model_c.compartments:
				self.model_c.compartments[m.compartment_id] = self.model_b.compartments[m.compartment_id]


		print("======= Summary =============")
		#for m in self.model_c1.metabolites:
		#	print(m.id,m.name)


		print("CompA: "+ str(len(self.model_a.compartments))+"\t MetaA: "+ str(len(self.model_a.metabolites))+"\t ReacA: "+ str(len(self.model_a.reactions)))
		print("CompB: "+ str(len(self.model_b.compartments))+"\t MetaB: "+ str(len(self.model_b.metabolites))+"\t ReacB: "+ str(len(self.model_b.reactions)))
		print("CompC: "+ str(len(self.model_c.compartments))+"\t MetaC: "+ str(len(self.model_c.metabolites))+"\t ReacC: "+ str(len(self.model_c.reactions)))


		## fill liststores with data
		i = 0
		for c in self.model_c.compartments:
			i+=1
			liststore_comp3.append([ i, c, self.model_c.compartments[c],0])
		label_comp.set_text(str(i))

		i = 0
		for m in self.model_c.metabolites:
			i+=1
			liststore_mets3.append([ i, m.id, m.name, m.formula, m.compartment_id, False])
		label_mets.set_text(str(i))

		i = 0
		for r in self.model_c.reactions:
			i+=1
			liststore_rect3.append([ i, r.id, r.name, r.ec_number, r.to_string('ref')])
		label_react.set_text(str(i))



	def on_merge_networks_simple(self, window):
		self.merge_networks("M1_", "M2_")

	def on_merge_networks(self, window):
		self.merge_networks('', '')



	def Exit(self, not_used1):
		Gtk.main_quit()





def main():
	app = GUI()
	Gtk.main()

if __name__ == "__main__":
    sys.exit(main())
