#cd D:/tools/eerat/python_apps/online_analysis
#run test_gui
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from Tkinter import *
from EeratAPI.API import *
from EeratAPI.OnlineAPIExtension import *
from sqlalchemy.orm import *
from sqlalchemy import *
import random

def reset_frame(frame):
    for ww in frame.pack_slaves():
        ww.pack_forget()
    #frame.grid_forget()
    return frame

def my_button_dict():
    return {"Subject Type": Subject_type\
            , "Subject": Subject\
            , "Datum Type": Datum_type\
            , "Detail Type": Detail_type\
            , "Feature Type": Feature_type}
    
class App:
    
    def __init__(self, master):
        
        #master is the root
        button_frame = Frame(master)#Simple container
        button_frame.pack(side = LEFT, fill = Y)
        
        dat_frame = Frame(master)
        dat_frame.pack(side = RIGHT, fill = Y)
        
        self.btn_dict = {}
                
        #Make a list of buttons
        for bb in my_button_dict().iterkeys():
            #action = lambda x = bb: DatFrame(frame=reset_frame(dat_frame), button_text=x)
            action = lambda bb = bb: ListFrame(frame=reset_frame(dat_frame)\
                           , title_text=bb\
                           , item_class=my_button_dict()[bb])
            self.btn_dict[bb] = Button(button_frame, text=bb, command=action)
            self.btn_dict[bb].pack(side = TOP, fill = X)

def def_render_func(item):
    return item.Name

class ListFrame:
    def __init__(self, frame=None, title_text=None, list_data=None, list_render_func=def_render_func, item_class=None, edit_frame='embed', new_item_func=None, open_item_func=None):
        #Sanitize the input
        if not frame: frame = Toplevel()
        self.frame = frame
        self.title_text=title_text
        if not list_data:
            session = Session()
            list_data = session.query(item_class).all()
        self.list_data=list_data
        self.list_render_func=list_render_func
        self.item_class = item_class
        #Need to define the other frames before the edit frame.
        list_frame = Frame(frame)
        list_frame.pack(side=LEFT, fill=Y)
        button_frame=Frame(list_frame)
        button_frame.pack(side=BOTTOM)
        if edit_frame=='embed':
            edit_frame=Frame(frame)
            edit_frame.pack(side=RIGHT, fill=Y)
        self.edit_frame=edit_frame
        #Parent has the option of passing in new_func (useful for setting associations)
        self.new_item_func = new_item_func
        #Parent has the option of passing in show_func (useful if new or double-click should spawn non-standard edit window)
        if not open_item_func: open_item_func=self.show_item
        self.open_item_func = open_item_func
        
        ##
        ## Prepare the elements
        ##
        ll = Label(list_frame, text=title_text)
        ll.pack(side=TOP, fill=X)
        ls = Scrollbar(list_frame)
        ls.pack(side=RIGHT, fill=Y)
        lb = Listbox(list_frame, yscrollcommand=ls.set)
        ls.config(command=lb.yview)
        i=0
        for item in self.list_data:
            lb.insert(i, self.list_render_func(item))
            i=i+1
        lb.bind("<Double-Button-1>", self.dbl_click)
        lb.pack(side=LEFT, fill=BOTH)
        self.lb=lb
                
        #New Button
        new_button = Button (button_frame, text="NEW", command = self.new_press)
        new_button.pack(side = LEFT, fill = X)
        
        #Delete Button
        del_button = Button (button_frame, text="DELETE", command = self.del_press)
        del_button.pack(side = RIGHT, fill = X)
 
    def new_press(self):
        #Instantiate the item
        #TODO: If we want to use default values, then this should be persisted to db immediately.
        if not self.new_item_func: item=self.item_class()
        else: item=self.new_item_func(self)
        item.Name='test'
        #Insert it into list_data and listbox.
        self.list_data.append(item)
        self.lb.insert(END, self.list_render_func(item))
        self.lb.see(self.lb.size())
        self.lb.selection_clear(0,END)
        self.lb.selection_set(END)
        #Show the item in the edit frame
        self.open_item_func(item)
    
    def del_press(self):
        curs = self.lb.curselection()
        for dd in curs:
            instance = self.list_data[int(dd)]
            session = Session.object_session(instance)
            #session.delete(instance)
            print "Disabled db delete of"
            print instance
            self.list_data.pop(int(dd))
            self.lb.delete(int(dd))#Remove the index from the listbox
    
    def dbl_click(self,ev):
        item = self.list_data[int(self.lb.curselection()[0])]
        #Show the item in the edit frame
        self.open_item_func(item)
    
    def show_item(self,item):
        if self.edit_frame: self.edit_frame=reset_frame(self.edit_frame)
        EditFrame(frame=self.edit_frame, item=item)
        
class EditFrame:
    def __init__(self, frame=None, item=None):
        self.item = item
        if not frame: frame=Toplevel()
        self.frame = frame
        
        #Everything has Name
        name_frame = Frame(frame)
        name_frame = name_frame
        name_frame.pack(side = TOP, fill = X)
        name_label = Label(name_frame, text="Name")
        name_label.pack(side = LEFT)
        name_var = StringVar(name_frame)
        name_var.set(item.Name)
        name_var.trace("w", lambda name, index, mode, name_var=name_var: self.update_name(name_var))
        name_entry = Entry(name_frame, textvariable=name_var)
        name_entry.pack(side = RIGHT, fill = X)
        
        #Many things have Description
        if hasattr(item,'Description'):
            desc_frame = Frame(frame)
            desc_frame.pack(side = TOP, fill = X)
            desc_label = Label(desc_frame, text="Description")
            desc_label.pack(side = LEFT)
            desc_var = StringVar(desc_frame)
            desc_var.set(item.Description)
            desc_var.trace("w", lambda name, index, mode, desc_var=desc_var: self.update_description(desc_var))
            desc_entry = Entry(desc_frame, textvariable=desc_var)
            desc_entry.pack(side = RIGHT, fill = X)
            
        #Almost as many things have DefaultValue
        if hasattr(item,'DefaultValue'):
            dv_frame = Frame(frame)
            dv_frame.pack(side = TOP, fill = X)
            dv_label = Label(dv_frame, text="Default Value")
            dv_label.pack(side = LEFT)
            dv_var = StringVar(dv_frame)
            if isinstance(item.DefaultValue,str):
                dv_var.set(item.DefaultValue)
            else: dv_var.set(str(item.DefaultValue))
            dv_var.trace("w", lambda name, index, mode, dv_var=dv_var: self.update_defaultvalue(dv_var))
            dv_entry = Entry(dv_frame, textvariable=dv_var)
            dv_entry.pack(side = RIGHT, fill = X)
            
        #TODO: Associations (datum_type_has_feature_type)
            
        #Further attributes require separate frames.
        if hasattr(item, 'DateOfBirth'):
            ss_frame = Frame(frame)
            ss_frame.pack(side = TOP)
            SubjectFrame(frame=ss_frame, subject=item)
    
    def update_name(self, name_var):
        self.item.Name = name_var.get()
        #Should flush right away?
                
    def update_description(self, desc_var):
        self.item.Description = desc_var.get()
        #Should flush right away?
        
    def update_defaultvalue(self, dv_var):
        if isinstance(item.DefaultValue,str):
            self.item.DefaultValue = dv_var.get()
        else:
            self.item.DefaultValue = float(dv_var.get())
              
class SubjectFrame:
    def __init__(self, frame=None, subject=None):
        self.subject = subject
        if not frame: frame=Toplevel()
        self.frame = frame
        
        det_frame = Frame(frame)
        det_frame.pack(side=LEFT, fill=Y)
        pd_frame = Frame(frame)
        pd_frame.pack(side=RIGHT, fill=Y)
        
        #We already have Name, this is for everything else related to the subject
        #DateOfBirth
        dob_frame = Frame(det_frame)
        dob_frame.pack(side=TOP, fill=X)
        dob_label = Label(dob_frame, text="DOB (YYYY-MM-DD)")
        dob_label.pack(side = LEFT)
        dob_var = StringVar(dob_frame)
        dob_var.set(self.subject.DateOfBirth)
        dob_var.trace("w", lambda name, index, mode, dob_var=dob_var: self.update_dob(dob_var))
        dob_entry = Entry(dob_frame, textvariable=dob_var)
        dob_entry.pack(side=RIGHT, fill=X)

        #IsMale
        gender_frame = Frame(det_frame)
        gender_frame.pack(side=TOP, fill=X)
        gender_label = Label(gender_frame, text="Gender")
        gender_label.pack(side = LEFT)
        self.gender_var = IntVar(gender_frame)
        self.gender_var.set(self.subject.IsMale)
        gender_rb_frame = Frame(gender_frame)
        gender_rb_frame.pack(side=RIGHT, fill=X)
        gender_m_radio = Radiobutton(gender_rb_frame, text="M", variable=self.gender_var, value=1, command=self.update_gender)
        gender_m_radio.pack(side=LEFT)
        gender_f_radio = Radiobutton(gender_rb_frame, text="F", variable=self.gender_var, value=0, command=self.update_gender)
        gender_f_radio.pack(side=LEFT)
        
        #Weight
        wt_frame = Frame(det_frame)
        wt_frame.pack(side=TOP, fill=X)
        wt_label = Label(wt_frame, text="Weight (g)")
        wt_label.pack(side=LEFT)
        wt_var = StringVar(wt_frame)
        wt_var.set(self.subject.Weight)
        wt_var.trace("w", lambda name, index, mode, wt_var=wt_var: self.update_weight(wt_var))
        wt_entry = Entry(wt_frame, textvariable=wt_var)
        wt_entry.pack(side=RIGHT, fill=X)
        
        #TODO: Notes
        
        #species_type (spinbox)
        sp_frame = Frame(det_frame)
        sp_frame.pack(side=TOP, fill=X)
        sp_label = Label(sp_frame, text="Species Type")
        sp_label.pack(side=LEFT)
        self.sp_var = StringVar(sp_frame)
        self.sp_var.set(self.subject.species_type)
        sp_sb = Spinbox(sp_frame, values=('rat','human'), command=self.update_species)
        sp_sb.configure(textvariable=self.sp_var)
        sp_sb.pack(side=RIGHT, fill=X)
        
        #TODO: subject_type spinbox
        
        #TODO: Each detail for this subject_type - do as a function that can change if subject_type changes
        #self.subject.details is a kv struct.
        
        #TODO: MVIC preview
        
        #TODO: SIC preview
        
        #button to load periods
        self.showing_periods = False
        pb_frame = Frame(det_frame)
        pb_frame.pack(side=BOTTOM, fill=X)
        self.pb_button = Button(pb_frame, text="Periods >>", command=self.toggle_periods)
        self.pb_button.pack(side=RIGHT)
        self.per_list_frame = pd_frame
        
    def update_dob(self, dob_var):
        #TODO: Check that it matches 'YYYY-MM-DD'
        self.subject.DateOfBirth = dob_var.get()
    def update_gender(self):
        self.subject.IsMale = self.gender_var.get()
    def update_weight(self, wt_var):
        self.subject.Weight=float(wt_var.get())
    def update_species(self):
        self.subject.species_type=self.sp_var.get()
    def toggle_periods(self):
        frame=reset_frame(self.per_list_frame)
        self.showing_periods = not self.showing_periods
        self.pb_button.configure(text="Periods <<" if self.showing_periods else "Periods >>")
        if self.showing_periods:
            PerListFrame(frame=frame, subject=self.subject)
        
class PerListFrame:
    def __init__(self, frame=None, subject=None):
        self.subject = subject
        if not frame: frame=Toplevel()
        self.frame = frame
        
        lf = ListFrame(frame, title_text="Periods", list_data=subject.periods\
                  , list_render_func=lambda x: x.datum_type.Name + " " + str(x.Number) + " " + str(x.StartTime) + " to " + str(x.EndTime)
                  , item_class=Datum\
                  , edit_frame=None\
                  , new_item_func=self.new_per\
                  , open_item_func=self.open_per)
        
    #period instantiation requires keys, 
    #thus we need a custom new_per function that creates the persists immediately.
    def new_per(self,lf):
        #self is PerListFrame, lf is ListFrame
        period = get_or_create(Datum\
            , subject=self.subject\
            , datum_type=my_dat_type\
            , span_type='period'\
            , IsGood=1\
            , Number=0)
        return period
    
    #Use a separate frame for periods
    def open_per(self,period):
        PeriodFrame(period=period)
        
class PeriodFrame:
    def __init__(self, frame=None, period=None):
        self.period = period
        if not frame: frame=Toplevel()
        self.frame = frame
        
        id_frame = Frame(frame)
        id_frame.pack(side=TOP, fill=X)
        dates_frame = Frame(frame)
        dates_frame.pack(side=TOP, fill=X)
        plot_frame = Frame(frame)
        plot_frame.pack(side=TOP, fill=X)
        bframe = Frame(frame)
        bframe.pack(side=TOP, fill=X)
        self.detail_frame = Frame(bframe)
        self.detail_frame.pack(side=LEFT)
        pbutton_frame = Frame(bframe)
        pbutton_frame.pack(side=LEFT)
        
        #Period ID
        subj_name_label = Label(id_frame, text="Subject: " + self.period.subject.Name)
        subj_name_label.pack(side=LEFT)
        self.num_label = Label(id_frame, text="Number: " + str(self.period.Number))
        self.num_label.pack(side=LEFT)
        type_label = Label(id_frame, text="Datum type:")
        type_label.pack(side=LEFT)
        type_var = StringVar()
        type_var.set(self.period.datum_type.Name)
        type_var.trace("w", lambda name, index, mode, type_var=type_var: self.update_type(type_var))
        session = Session.object_session(self.period)
        datum_types = session.query(Datum_type).all()
        dt_names = [dt.Name for dt in datum_types]
        dt_menu = OptionMenu(id_frame, type_var, self.period.datum_type.Name, *dt_names)
        dt_menu.pack(side=LEFT)
        
        #Dates
        start_label = Label(dates_frame, text="StartTime (YYYY-MM-DD hh:mm:ss)")
        start_label.pack(side = LEFT)
        start_var = StringVar(dates_frame)
        start_var.set(self.period.StartTime)#str()?
        start_var.trace("w", lambda name, index, mode, start_var=start_var: self.update_start(start_var))
        start_entry = Entry(dates_frame, textvariable=start_var)
        start_entry.pack(side=LEFT, fill=X)
        end_label = Label(dates_frame, text="EndTime")
        end_label.pack(side = LEFT)
        end_var = StringVar(dates_frame)
        end_var.set(self.period.EndTime)#str()?
        end_var.trace("w", lambda name, index, mode, end_var=end_var: self.update_end(end_var))
        end_entry = Entry(dates_frame, textvariable=end_var)
        end_entry.pack(side=LEFT, fill=X)
        
        #Plot
        self.erp_fig = Figure()
        erp_canvas = FigureCanvasTkAgg(self.erp_fig, master=plot_frame)
        erp_canvas.show()
        erp_canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        toolbar = NavigationToolbar2TkAgg( erp_canvas, plot_frame )
        toolbar.update()
        erp_canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)
        self.plot_erps()
        
        self.render_details()
        
        #Plot buttons
        refr_button = Button(pbutton_frame, text="Refresh", command=self.plot_erps)
        refr_button.pack(side=TOP, fill=X)
        reavg_button = Button(pbutton_frame, text="ReAvg ERP", command=self.period.update_store)
        reavg_button.pack(side=TOP, fill=X)
        model_button = Button(pbutton_frame, text="Model IO", command=self.show_model)
        model_button.pack(side=TOP, fill=X)
        mapping_button = Button(pbutton_frame, text="MEP Mapping", command=self.mep_map)
        mapping_button.pack(side=TOP, fill=X)
        recalc_button = Button(pbutton_frame, text="Recalculate", command=self.recalc_features)
        recalc_button.pack(side=LEFT)  
        
    def update_type(self, type_var):
        session = Session.object_session(self.period)
        self.period.datum_type = session.query(Datum_type).filter(Name==type_var.get()).first()
        #TODO: flush
        self.render_details()
        self.num_label.configure(text="Number: " + str(self.period.Number))
    def update_start(self, start_var):
        #TODO: Check that it matches 'YYYY-MM-DD hh:mm:ss'
        self.period.StartTime = start_var.get()
    def update_end(self, end_var):
        #TODO: Check that it matches 'YYYY-MM-DD hh:mm:ss'
        self.period.EndTime = end_var.get()
    def plot_erps(self):
        per_store=self.period.store
        
        #Find any channel that appears in period.detail_values
        chans_list = [pdv for pdv in self.period.detail_values.itervalues() if pdv in per_store['channel_labels']]
        chans_list = list(set(chans_list))#make unique
        #Boolean array to index the data.
        chan_bool = np.array([cl in chans_list for cl in per_store['channel_labels']])
        n_chans = sum(chan_bool)
        
        x_vec = per_store['x_vec']
        y_avg = per_store['data'].T[:,chan_bool]
        
        #get y data from up to 100 trials.
        trials = self.period.trials
        if len(trials)>100:
            trials=random.sample(trials,100)
        y_trials = np.zeros((x_vec.shape[0],n_chans * len(trials)))
        tt=0
        for tr in trials:
            store=tr.store
            dat=store['data'].T[:,chan_bool]
            y_trials[:,2*tt:2*tt+1]=dat
            tt=tt+1
            
        #Find values for axvline
        window_lims = [pdv for pdk,pdv in self.period.detail_values.iteritems() if '_ms' in pdk]
        
        erp_ax = self.erp_fig.gca()
        #self.erp_fig.delaxes(erp_ax)
        erp_ax.clear()
        erp_ax = self.erp_fig.add_subplot(111)
        
        erp_ax.plot(x_vec, y_trials)
        erp_ax.plot(x_vec, y_avg, linewidth=3.0, label='avg')
        for ll  in window_lims:
            erp_ax.axvline(x=float(ll))
        erp_ax.set_xlim([-10,100])
        erp_ax.set_xlabel('TIME AFTER STIM (ms)')
        erp_ax.set_ylabel('AMPLITUDE (uV)')
        self.erp_fig.canvas.draw()
        
    def show_model(self):
        ModelFrame(period=self.period)
    def mep_map(self):
        pass
        
    def render_details(self):
        self.detail_frame=reset_frame(self.detail_frame)
        parent = Frame(self.detail_frame)
        parent.pack(side=TOP, fill=X)
        lab = Label(parent, text="Detail")
        lab.pack(side=LEFT)
        lab = Label(parent, text="Value")
        lab.pack(side=RIGHT)
        for ddv in self.period.datum_detail_value.itervalues():
            self.render_ddv(ddv,self.detail_frame)
    def render_ddv(self,ddv,frame):
        parent = Frame(frame)
        parent.pack(side=TOP, fill=X)
        lab = Label(parent, text=ddv.detail_name)
        lab.pack(side=LEFT)
        str_var = StringVar(parent)
        str_var.set(ddv.Value)
        str_var.trace("w", lambda name, index, mode, str_var=str_var: self.update_ddv(ddv,str_var))
        entry = Entry(parent, textvariable=str_var)
        entry.pack(side=RIGHT)
    def update_ddv(self,ddv,str_var):
        ddv.Value=str_var.get()
        #TODO: flush
    def recalc_features(self):
        self.period._get_detection_limit()#Reget detection limit
        print "calculate_all_features does not seem to recalulate values using newly set details"
        self.period.calculate_all_features#Recalculate features. This flushes the transaction.

class ModelFrame:
    def __init__(self, frame=None, period=None, doing_threshold=True):
        self.period = period
        if not frame: frame=Toplevel()
        self.frame = frame
        
        io_plot_frame=Frame(frame)
        io_plot_frame.pack(side=TOP, fill=X)
        self.io_label_frame=Frame(frame)
        self.io_label_frame.pack(side=TOP, fill=X)
        thresh_plot_frame=Frame(frame)
        thresh_plot_frame.pack(side=TOP, fill=X)
        self.thresh_label_frame=Frame(frame)
        self.thresh_label_frame.pack(side=TOP, fill=X)
        button_frame=Frame(frame)
        button_frame.pack(side=TOP, fill=X)
        
        #Plot IO
        self.io_fig = Figure()
        io_canvas = FigureCanvasTkAgg(self.io_fig, master=io_plot_frame)
        io_canvas.show()
        io_canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        toolbar = NavigationToolbar2TkAgg( io_canvas, io_plot_frame )
        toolbar.update()
        io_canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)
        self.plot_io()
        
        #Plot Threshold
        self.thresh_fig = Figure()
        thresh_canvas = FigureCanvasTkAgg(self.thresh_fig, master=thresh_plot_frame)
        thresh_canvas.show()
        thresh_canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        toolbar = NavigationToolbar2TkAgg( thresh_canvas, thresh_plot_frame )
        toolbar.update()
        thresh_canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)
        self.plot_thresh()
        
        #Buttons
        io_button = Button(button_frame, text="Model IO", command=self.plot_io)
        io_button.pack(side=LEFT)
        thresh_button = Button(button_frame, text="Model Threshold", command=self.plot_thresh)
        thresh_button.pack(side=LEFT)
        
    def plot_io(self):
        self.plot_either()
    def plot_thresh(self):
        self.plot_either(mode='threshold')
    def plot_either(self,mode=None):
        parms,parms_err = self.period.model_erp(model_type=mode)
        
        if 'hr' in self.period.type_name:
            stim_det_name='dat_Nerve_stim_output'
            erp_name='HR_aaa'
        elif 'mep' in self.period.type_name:
            stim_det_name='dat_TMS_powerA'
            erp_name='MEP_aaa'
            
        x = self.period._get_child_details(stim_det_name)
        x = x.astype(np.float)
        y = self.period._get_child_features(erp_name)
        
        if not mode:#Default to io
            fig = self.io_fig
            ylabel = "AMPLITUDE"
            l_frame = reset_frame(self.io_label_frame)
            l_names = ['x0','k','a','c']
            sig_func = my_sigmoid
        elif mode=='threshold':
            y=y>self.period.erp_detection_limit
            y=y.astype(int)
            fig = self.thresh_fig
            ylabel = "EP DETECTED"
            l_frame = reset_frame(self.thresh_label_frame)
            l_names = ['x0','k']
            sig_func = my_simp_sigmoid
            
        x_est = np.arange(min(x),max(x),(max(x)-min(x))/100)
        y_est = sig_func(x_est,*list(parms))
            
        #Plot model estimate and actual values
        model_ax = fig.gca()
        model_ax.clear()
        model_ax = fig.add_subplot(111)
        model_ax.plot(x, y, 'o', label='data')
        model_ax.plot(x_est,y_est, label='fit')
        model_ax.legend(loc='upper left')
        model_ax.set_xlabel('STIMULUS INTENSITY')
        model_ax.set_ylabel(ylabel)
        fig.canvas.draw()
        
        #Display the model parameters x0, k, a, c
        
        i=0
        for ln in l_names:
            lab = Label(l_frame, text=ln + ": " + str(parms[i]) + "+/- " + str(parms_err[i]) + "(" + str(100*parms_err[i]/parms[i]) + "%)")
            lab.pack(side=TOP)
            i=i+1
    
engine = create_engine("mysql://root@localhost/eerat", echo=False)#echo="debug" gives a ton.
Session = scoped_session(sessionmaker(bind=engine, autocommit=True))
root = Tk() #Creating the root widget. There must be and can be only one.
app = App(root)
root.mainloop() #Event loops