"""
Hospital Management System
Python + Tkinter + MySQL
Modules: Patients, Doctors, Appointments, Billing, Wards/Rooms, Pharmacy
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
from datetime import date, datetime
from db_config import execute_query, initialize_database

# ── Colour Palette ───────────────────────────────────────────
BG_DARK    = "#0D1B2A"
BG_PANEL   = "#1B2A3B"
BG_CARD    = "#243447"
ACCENT     = "#00C9A7"
ACCENT2    = "#3A8EF6"
TEXT_WHITE = "#F0F4F8"
TEXT_MUTED = "#8BA3B8"
DANGER     = "#E74C3C"
SUCCESS    = "#27AE60"
WARNING    = "#F39C12"
ROW_ODD    = "#1E2D3D"
ROW_EVEN   = "#243447"
# ─────────────────────────────────────────────────────────────


def styled_btn(parent, text, command, color=ACCENT, fg=BG_DARK, width=14):
    return tk.Button(parent, text=text, command=command,
                     bg=color, fg=fg, relief="flat", cursor="hand2",
                     font=("Segoe UI", 10, "bold"), width=width,
                     pady=6, padx=8, bd=0,
                     activebackground=color, activeforeground=fg)


def build_tree(parent, columns, heights=400):
    """Create a styled ttk.Treeview with scrollbars."""
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Custom.Treeview",
                    background=BG_CARD, foreground=TEXT_WHITE,
                    fieldbackground=BG_CARD, rowheight=28,
                    font=("Segoe UI", 10))
    style.configure("Custom.Treeview.Heading",
                    background=BG_PANEL, foreground=ACCENT,
                    font=("Segoe UI", 10, "bold"), relief="flat")
    style.map("Custom.Treeview", background=[("selected", ACCENT2)])

    frame = tk.Frame(parent, bg=BG_DARK)
    frame.pack(fill="both", expand=True, pady=(4, 0))

    vsb = ttk.Scrollbar(frame, orient="vertical")
    hsb = ttk.Scrollbar(frame, orient="horizontal")
    tree = ttk.Treeview(frame, columns=columns, show="headings",
                        style="Custom.Treeview",
                        yscrollcommand=vsb.set, xscrollcommand=hsb.set,
                        height=heights)
    vsb.config(command=tree.yview)
    hsb.config(command=tree.xview)

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=130, anchor="center")

    vsb.pack(side="right", fill="y")
    hsb.pack(side="bottom", fill="x")
    tree.pack(side="left", fill="both", expand=True)
    tree.tag_configure("odd",  background=ROW_ODD)
    tree.tag_configure("even", background=ROW_EVEN)
    return tree


def refresh_tree(tree, rows):
    tree.delete(*tree.get_children())
    for i, row in enumerate(rows):
        tag = "odd" if i % 2 == 0 else "even"
        tree.insert("", "end", values=list(row.values()), tags=(tag,))


def label_entry(parent, text, row, col=0, width=22):
    tk.Label(parent, text=text, bg=BG_CARD, fg=TEXT_MUTED,
             font=("Segoe UI", 9)).grid(row=row, column=col, sticky="w",
                                         padx=8, pady=4)
    e = tk.Entry(parent, width=width, bg=BG_PANEL, fg=TEXT_WHITE,
                 insertbackground=TEXT_WHITE, relief="flat",
                 font=("Segoe UI", 10))
    e.grid(row=row, column=col+1, sticky="ew", padx=8, pady=4)
    return e


def label_combo(parent, text, row, values, col=0, width=20):
    tk.Label(parent, text=text, bg=BG_CARD, fg=TEXT_MUTED,
             font=("Segoe UI", 9)).grid(row=row, column=col, sticky="w",
                                         padx=8, pady=4)
    v = tk.StringVar()
    c = ttk.Combobox(parent, textvariable=v, values=values,
                     width=width, state="readonly",
                     font=("Segoe UI", 10))
    c.grid(row=row, column=col+1, sticky="ew", padx=8, pady=4)
    return c


# ════════════════════════════════════════════════════════════════
#  MODULE FRAMES
# ════════════════════════════════════════════════════════════════

class PatientModule(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG_DARK)
        self._build_ui()
        self.load_patients()

    def _build_ui(self):
        # ── Header ──
        hdr = tk.Frame(self, bg=BG_DARK)
        hdr.pack(fill="x", pady=(0, 8))
        tk.Label(hdr, text="👥  Patient Management", bg=BG_DARK,
                 fg=ACCENT, font=("Segoe UI", 16, "bold")).pack(side="left")

        # ── Form Card ──
        card = tk.LabelFrame(self, text=" Add / Edit Patient ",
                             bg=BG_CARD, fg=ACCENT,
                             font=("Segoe UI", 10, "bold"),
                             relief="groove", bd=1)
        card.pack(fill="x", padx=4, pady=4)
        card.columnconfigure(1, weight=1)
        card.columnconfigure(3, weight=1)

        self.e_first  = label_entry(card, "First Name*",   0, 0)
        self.e_last   = label_entry(card, "Last Name*",    0, 2)
        self.e_phone  = label_entry(card, "Phone*",        1, 0)
        self.e_email  = label_entry(card, "Email",         1, 2)
        self.e_dob    = label_entry(card, "DOB (YYYY-MM-DD)", 2, 0)
        self.e_addr   = label_entry(card, "Address",       2, 2)
        self.c_gender = label_combo(card, "Gender*",       3, ["Male","Female","Other"], 0)
        self.c_blood  = label_combo(card, "Blood Group",   3,
                                    ["A+","A-","B+","B-","AB+","AB-","O+","O-","Unknown"], 2)
        self.c_status = label_combo(card, "Status",        4,
                                    ["Outpatient","Inpatient","Discharged"], 0)
        self.e_ec_name  = label_entry(card, "Emergency Contact", 4, 2)

        # Buttons
        btn_row = tk.Frame(card, bg=BG_CARD)
        btn_row.grid(row=5, column=0, columnspan=4, pady=8)
        styled_btn(btn_row, "➕ Add Patient",    self.add_patient).pack(side="left", padx=4)
        styled_btn(btn_row, "✏️ Update",         self.update_patient, ACCENT2, TEXT_WHITE).pack(side="left", padx=4)
        styled_btn(btn_row, "🗑 Delete",          self.delete_patient, DANGER, TEXT_WHITE).pack(side="left", padx=4)
        styled_btn(btn_row, "🔄 Refresh",        self.load_patients, WARNING, BG_DARK).pack(side="left", padx=4)

        # ── Search ──
        sf = tk.Frame(self, bg=BG_DARK)
        sf.pack(fill="x", pady=4)
        tk.Label(sf, text="Search:", bg=BG_DARK, fg=TEXT_MUTED,
                 font=("Segoe UI", 10)).pack(side="left")
        self.search_var = tk.StringVar()
        se = tk.Entry(sf, textvariable=self.search_var, width=30,
                      bg=BG_PANEL, fg=TEXT_WHITE, insertbackground=TEXT_WHITE,
                      relief="flat", font=("Segoe UI", 10))
        se.pack(side="left", padx=6)
        styled_btn(sf, "🔍 Search", self.search_patients, ACCENT2, TEXT_WHITE, 10).pack(side="left")

        # ── Table ──
        cols = ("ID","First Name","Last Name","Gender","Blood","Phone",
                "Email","DOB","Status","Address")
        self.tree = build_tree(self, cols)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        self._selected_id = None

    def load_patients(self):
        ok, rows = execute_query("SELECT patient_id,first_name,last_name,gender,blood_group,phone,email,dob,admission_status,address FROM patients ORDER BY patient_id DESC", fetch=True)
        if ok:
            refresh_tree(self.tree, rows)

    def search_patients(self):
        kw = self.search_var.get()
        q = """SELECT patient_id,first_name,last_name,gender,blood_group,phone,email,dob,admission_status,address
               FROM patients WHERE first_name LIKE %s OR last_name LIKE %s OR phone LIKE %s"""
        ok, rows = execute_query(q, (f"%{kw}%",f"%{kw}%",f"%{kw}%"), fetch=True)
        if ok:
            refresh_tree(self.tree, rows)

    def _on_select(self, _):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0])["values"]
        self._selected_id = vals[0]
        fields = [self.e_first, self.e_last, self.c_gender, self.c_blood,
                  self.e_phone, self.e_email, self.e_dob, self.c_status, self.e_addr]
        data   = [vals[1], vals[2], vals[3], vals[4],
                  vals[5], vals[6], vals[7], vals[8], vals[9]]
        for f, d in zip(fields, data):
            if isinstance(f, ttk.Combobox):
                f.set(d or "")
            else:
                f.delete(0, "end")
                f.insert(0, d or "")

    def _get_form(self):
        return {
            "first_name": self.e_first.get().strip(),
            "last_name":  self.e_last.get().strip(),
            "phone":      self.e_phone.get().strip(),
            "email":      self.e_email.get().strip(),
            "dob":        self.e_dob.get().strip() or None,
            "address":    self.e_addr.get().strip(),
            "gender":     self.c_gender.get(),
            "blood_group":self.c_blood.get() or "Unknown",
            "admission_status": self.c_status.get() or "Outpatient",
            "emergency_contact_name": self.e_ec_name.get().strip(),
        }

    def add_patient(self):
        d = self._get_form()
        if not d["first_name"] or not d["phone"] or not d["gender"]:
            messagebox.showwarning("Validation", "First Name, Phone and Gender are required.")
            return
        q = """INSERT INTO patients (first_name,last_name,phone,email,dob,address,gender,
               blood_group,admission_status,emergency_contact_name)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        ok, result = execute_query(q, tuple(d.values()))
        if ok:
            messagebox.showinfo("Success", f"Patient added! ID: {result}")
            self.load_patients()
        else:
            messagebox.showerror("Error", result)

    def update_patient(self):
        if not self._selected_id:
            messagebox.showwarning("Select", "Select a patient first.")
            return
        d = self._get_form()
        q = """UPDATE patients SET first_name=%s,last_name=%s,phone=%s,email=%s,dob=%s,
               address=%s,gender=%s,blood_group=%s,admission_status=%s,
               emergency_contact_name=%s WHERE patient_id=%s"""
        ok, result = execute_query(q, (*d.values(), self._selected_id))
        if ok:
            messagebox.showinfo("Updated", "Patient updated successfully.")
            self.load_patients()
        else:
            messagebox.showerror("Error", result)

    def delete_patient(self):
        if not self._selected_id:
            messagebox.showwarning("Select", "Select a patient first.")
            return
        if messagebox.askyesno("Confirm", "Delete this patient?"):
            ok, result = execute_query("DELETE FROM patients WHERE patient_id=%s",
                                       (self._selected_id,))
            if ok:
                messagebox.showinfo("Deleted", "Patient deleted.")
                self._selected_id = None
                self.load_patients()
            else:
                messagebox.showerror("Error", result)


# ── Doctor Module ────────────────────────────────────────────

class DoctorModule(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG_DARK)
        self._build_ui()
        self.load_doctors()

    def _build_ui(self):
        tk.Label(self, text="🩺  Doctor Management", bg=BG_DARK,
                 fg=ACCENT, font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 8))

        card = tk.LabelFrame(self, text=" Add / Edit Doctor ",
                             bg=BG_CARD, fg=ACCENT,
                             font=("Segoe UI", 10, "bold"), relief="groove", bd=1)
        card.pack(fill="x", padx=4, pady=4)
        card.columnconfigure(1, weight=1); card.columnconfigure(3, weight=1)

        self.e_first  = label_entry(card, "First Name*",      0, 0)
        self.e_last   = label_entry(card, "Last Name*",       0, 2)
        self.e_spec   = label_entry(card, "Specialization*",  1, 0)
        self.e_phone  = label_entry(card, "Phone*",           1, 2)
        self.e_email  = label_entry(card, "Email",            2, 0)
        self.e_qual   = label_entry(card, "Qualification",    2, 2)
        self.e_exp    = label_entry(card, "Experience (yrs)", 3, 0, 10)
        self.e_fee    = label_entry(card, "Consult Fee (Rs)", 3, 2, 10)
        self.e_sched  = label_entry(card, "Schedule",         4, 0)
        self.c_status = label_combo(card, "Status",           4,
                                    ["Active","Inactive","On Leave"], 2)

        btn_row = tk.Frame(card, bg=BG_CARD)
        btn_row.grid(row=5, column=0, columnspan=4, pady=8)
        styled_btn(btn_row, "➕ Add Doctor",  self.add_doctor).pack(side="left", padx=4)
        styled_btn(btn_row, "✏️ Update",      self.update_doctor, ACCENT2, TEXT_WHITE).pack(side="left", padx=4)
        styled_btn(btn_row, "🗑 Delete",       self.delete_doctor, DANGER, TEXT_WHITE).pack(side="left", padx=4)
        styled_btn(btn_row, "🔄 Refresh",     self.load_doctors, WARNING, BG_DARK).pack(side="left", padx=4)

        cols = ("ID","First","Last","Specialization","Phone","Email","Qualification","Exp","Fee","Schedule","Status")
        self.tree = build_tree(self, cols)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self._selected_id = None

    def load_doctors(self):
        ok, rows = execute_query(
            "SELECT doctor_id,first_name,last_name,specialization,phone,email,qualification,experience_years,consultation_fee,schedule_days,status FROM doctors ORDER BY doctor_id DESC",
            fetch=True)
        if ok:
            refresh_tree(self.tree, rows)

    def _on_select(self, _):
        sel = self.tree.selection()
        if not sel:
            return
        v = self.tree.item(sel[0])["values"]
        self._selected_id = v[0]
        for widget, val in zip(
            [self.e_first,self.e_last,self.e_spec,self.e_phone,
             self.e_email,self.e_qual,self.e_exp,self.e_fee,self.e_sched],
            [v[1],v[2],v[3],v[4],v[5],v[6],v[7],v[8],v[9]]):
            widget.delete(0,"end"); widget.insert(0, val or "")
        self.c_status.set(v[10] or "Active")

    def _get_form(self):
        return (self.e_first.get().strip(), self.e_last.get().strip(),
                self.e_spec.get().strip(),  self.e_phone.get().strip(),
                self.e_email.get().strip(), self.e_qual.get().strip(),
                self.e_exp.get() or 0,      self.e_fee.get() or 0,
                self.e_sched.get().strip(), self.c_status.get() or "Active")

    def add_doctor(self):
        d = self._get_form()
        if not d[0] or not d[2] or not d[3]:
            messagebox.showwarning("Validation","First Name, Specialization & Phone required.")
            return
        q = """INSERT INTO doctors(first_name,last_name,specialization,phone,email,qualification,
               experience_years,consultation_fee,schedule_days,status)
               VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        ok, result = execute_query(q, d)
        if ok:
            messagebox.showinfo("Added",f"Doctor added! ID: {result}")
            self.load_doctors()
        else:
            messagebox.showerror("Error", result)

    def update_doctor(self):
        if not self._selected_id:
            messagebox.showwarning("Select","Select a doctor first.")
            return
        d = self._get_form()
        q = """UPDATE doctors SET first_name=%s,last_name=%s,specialization=%s,phone=%s,
               email=%s,qualification=%s,experience_years=%s,consultation_fee=%s,
               
               schedule_days=%s,status=%s WHERE doctor_id=%s"""
        ok, result = execute_query(q, (*d, self._selected_id))
        if ok:
            messagebox.showinfo("Updated","Doctor updated.")
            self.load_doctors()
        else:
            messagebox.showerror("Error", result)

    def delete_doctor(self):
        if not self._selected_id:
            messagebox.showwarning("Select","Select a doctor first.")
            return
        if messagebox.askyesno("Confirm","Delete this doctor?"):
            ok, r = execute_query("DELETE FROM doctors WHERE doctor_id=%s",(self._selected_id,))
            if ok:
                messagebox.showinfo("Deleted","Doctor deleted.")
                self._selected_id = None
                self.load_doctors()
            else:
                messagebox.showerror("Error", r)


# ── Appointment Module ───────────────────────────────────────

class AppointmentModule(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG_DARK)
        self._build_ui()
        self.load_appointments()

    def _get_patient_options(self):
        ok, rows = execute_query("SELECT patient_id,first_name,last_name FROM patients WHERE admission_status!='Discharged'", fetch=True)
        if ok:
            return {f"{r['patient_id']} - {r['first_name']} {r['last_name']}": r['patient_id'] for r in rows}
        return {}

    def _get_doctor_options(self):
        ok, rows = execute_query("SELECT doctor_id,first_name,last_name,specialization FROM doctors WHERE status='Active'", fetch=True)
        if ok:
            return {f"{r['doctor_id']} - Dr. {r['first_name']} {r['last_name']} ({r['specialization']})": r['doctor_id'] for r in rows}
        return {}

    def _build_ui(self):
        tk.Label(self, text="📅  Appointment Management", bg=BG_DARK,
                 fg=ACCENT, font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 8))

        card = tk.LabelFrame(self, text=" Book Appointment ",
                             bg=BG_CARD, fg=ACCENT,
                             font=("Segoe UI", 10, "bold"), relief="groove", bd=1)
        card.pack(fill="x", padx=4, pady=4)
        card.columnconfigure(1, weight=1); card.columnconfigure(3, weight=1)

        self.patient_map = self._get_patient_options()
        self.doctor_map  = self._get_doctor_options()

        self.c_patient = label_combo(card,"Patient*",       0, list(self.patient_map.keys()), width=30)
        self.c_doctor  = label_combo(card,"Doctor*",        1, list(self.doctor_map.keys()),  width=30)
        self.e_date    = label_entry(card,"Date (YYYY-MM-DD)*", 0, 2)
        self.e_time    = label_entry(card,"Time (HH:MM)*",  1, 2)
        self.e_reason  = label_entry(card,"Reason",         2, 0)
        self.c_status  = label_combo(card,"Status",         2,
                                     ["Scheduled","Completed","Cancelled","No-Show"], 2)

        btn_row = tk.Frame(card, bg=BG_CARD)
        btn_row.grid(row=3, column=0, columnspan=4, pady=8)
        styled_btn(btn_row,"📅 Book",       self.book_appointment).pack(side="left",padx=4)
        styled_btn(btn_row,"✏️ Update Status",self.update_appointment,ACCENT2,TEXT_WHITE).pack(side="left",padx=4)
        styled_btn(btn_row,"🗑 Cancel",      self.cancel_appointment,DANGER,TEXT_WHITE).pack(side="left",padx=4)
        styled_btn(btn_row,"🔄 Refresh",    self.load_appointments,WARNING,BG_DARK).pack(side="left",padx=4)

        cols=("ID","Patient","Doctor","Date","Time","Reason","Status")
        self.tree = build_tree(self, cols)
        self.tree.bind("<<TreeviewSelect>>",self._on_select)
        self._selected_id = None

    def load_appointments(self):
        q="""SELECT a.appointment_id,
                    CONCAT(p.first_name,' ',p.last_name) AS patient,
                    CONCAT('Dr. ',d.first_name,' ',d.last_name) AS doctor,
                    a.appointment_date,a.appointment_time,a.reason,a.status
             FROM appointments a
             JOIN patients p ON a.patient_id=p.patient_id
             JOIN doctors  d ON a.doctor_id =d.doctor_id
             ORDER BY a.appointment_date DESC,a.appointment_time DESC"""
        ok,rows=execute_query(q,fetch=True)
        if ok: refresh_tree(self.tree,rows)

    def _on_select(self,_):
        sel=self.tree.selection()
        if not sel: return
        v=self.tree.item(sel[0])["values"]
        self._selected_id=v[0]
        self.e_date.delete(0,"end"); self.e_date.insert(0,v[3])
        self.e_time.delete(0,"end"); self.e_time.insert(0,v[4])
        self.e_reason.delete(0,"end"); self.e_reason.insert(0,v[5] or "")
        self.c_status.set(v[6])

    def book_appointment(self):
        p_key=self.c_patient.get(); d_key=self.c_doctor.get()
        if not p_key or not d_key:
            messagebox.showwarning("Validation","Select patient and doctor.")
            return
        pid=self.patient_map.get(p_key)
        did=self.doctor_map.get(d_key)
        dt=self.e_date.get().strip(); tm=self.e_time.get().strip()
        if not dt or not tm:
            messagebox.showwarning("Validation","Date and Time are required.")
            return
        q="INSERT INTO appointments(patient_id,doctor_id,appointment_date,appointment_time,reason,status) VALUES(%s,%s,%s,%s,%s,%s)"
        ok,r=execute_query(q,(pid,did,dt,tm,self.e_reason.get().strip(),"Scheduled"))
        if ok:
            messagebox.showinfo("Booked",f"Appointment booked! ID: {r}")
            self.load_appointments()
        else:
            messagebox.showerror("Error",r)

    def update_appointment(self):
        if not self._selected_id:
            messagebox.showwarning("Select","Select an appointment first.")
            return
        q="UPDATE appointments SET status=%s WHERE appointment_id=%s"
        ok,r=execute_query(q,(self.c_status.get(),self._selected_id))
        if ok:
            messagebox.showinfo("Updated","Appointment status updated.")
            self.load_appointments()
        else:
            messagebox.showerror("Error",r)

    def cancel_appointment(self):
        if not self._selected_id:
            messagebox.showwarning("Select","Select an appointment first.")
            return
        if messagebox.askyesno("Confirm","Cancel this appointment?"):
            ok,r=execute_query("UPDATE appointments SET status='Cancelled' WHERE appointment_id=%s",(self._selected_id,))
            if ok:
                messagebox.showinfo("Cancelled","Appointment cancelled.")
                self.load_appointments()
            else:
                messagebox.showerror("Error",r)


# ── Ward / Room Module ───────────────────────────────────────

class WardModule(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG_DARK)
        self._build_ui()
        self.load_data()

    def _build_ui(self):
        tk.Label(self, text="🏥  Wards & Rooms", bg=BG_DARK,
                 fg=ACCENT, font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 8))

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)

        # Tab 1: Wards
        self.tab_ward = tk.Frame(nb, bg=BG_DARK)
        nb.add(self.tab_ward, text="  🏢 Wards  ")

        card = tk.LabelFrame(self.tab_ward, text=" Add Ward ",
                             bg=BG_CARD, fg=ACCENT,
                             font=("Segoe UI", 10, "bold"), relief="groove")
        card.pack(fill="x", padx=4, pady=4)
        card.columnconfigure(1,weight=1); card.columnconfigure(3,weight=1)

        self.ew_name  = label_entry(card,"Ward Name*",   0,0)
        self.cw_type  = label_combo(card,"Type*",        0,
                                    ["General","ICU","Emergency","Pediatric","Maternity","Surgery","Orthopedic","Cardiology"],2)
        self.ew_beds  = label_entry(card,"Total Beds*",  1,0,8)
        self.ew_avail = label_entry(card,"Avail Beds*",  1,2,8)
        self.ew_floor = label_entry(card,"Floor*",       2,0,8)

        br=tk.Frame(card,bg=BG_CARD); br.grid(row=3,column=0,columnspan=4,pady=6)
        styled_btn(br,"➕ Add Ward",self.add_ward).pack(side="left",padx=4)
        styled_btn(br,"🔄 Refresh",self.load_data,WARNING,BG_DARK).pack(side="left",padx=4)

        cols=("ID","Name","Type","Total Beds","Avail Beds","Floor")
        self.tree_ward=build_tree(self.tab_ward,cols,8)

        # Tab 2: Rooms
        self.tab_room=tk.Frame(nb,bg=BG_DARK)
        nb.add(self.tab_room,text="  🚪 Rooms  ")

        card2=tk.LabelFrame(self.tab_room,text=" Add Room ",
                            bg=BG_CARD,fg=ACCENT,
                            font=("Segoe UI",10,"bold"),relief="groove")
        card2.pack(fill="x",padx=4,pady=4)
        card2.columnconfigure(1,weight=1); card2.columnconfigure(3,weight=1)

        self.er_num   = label_entry(card2,"Room Number*",  0,0,10)
        self.er_type  = label_combo(card2,"Room Type*",    0,["Single","Double","Triple","General"],2)
        self.er_charge= label_entry(card2,"Daily Charge*", 1,0,10)
        self.er_status= label_combo(card2,"Status*",       1,["Available","Occupied","Maintenance"],2)

        ok,rows=execute_query("SELECT ward_id,ward_name FROM wards",fetch=True)
        ward_opts=[f"{r['ward_id']} - {r['ward_name']}" for r in rows] if ok else []
        self.ward_map={opt: int(opt.split(" - ")[0]) for opt in ward_opts}
        self.cr_ward  = label_combo(card2,"Ward*",         2,ward_opts,0,28)

        br2=tk.Frame(card2,bg=BG_CARD); br2.grid(row=3,column=0,columnspan=4,pady=6)
        styled_btn(br2,"➕ Add Room",   self.add_room).pack(side="left",padx=4)
        styled_btn(br2,"✏️ Update Status",self.update_room_status,ACCENT2,TEXT_WHITE).pack(side="left",padx=4)
        styled_btn(br2,"🔄 Refresh",   self.load_data,WARNING,BG_DARK).pack(side="left",padx=4)

        cols2=("ID","Ward","Room No","Type","Status","Daily Charge")
        self.tree_room=build_tree(self.tab_room,cols2,8)
        self.tree_room.bind("<<TreeviewSelect>>",self._on_room_select)
        self._sel_room_id=None

    def load_data(self):
        ok,rows=execute_query("SELECT ward_id,ward_name,ward_type,total_beds,available_beds,floor_number FROM wards",fetch=True)
        if ok: refresh_tree(self.tree_ward,rows)
        q="""SELECT r.room_id,w.ward_name,r.room_number,r.room_type,r.status,r.daily_charge
             FROM rooms r JOIN wards w ON r.ward_id=w.ward_id ORDER BY r.room_id"""
        ok,rows=execute_query(q,fetch=True)
        if ok: refresh_tree(self.tree_room,rows)

    def add_ward(self):
        name=self.ew_name.get().strip()
        if not name:
            messagebox.showwarning("Validation","Ward name required."); return
        q="INSERT INTO wards(ward_name,ward_type,total_beds,available_beds,floor_number) VALUES(%s,%s,%s,%s,%s)"
        ok,r=execute_query(q,(name,self.cw_type.get() or "General",
                               self.ew_beds.get() or 10,
                               self.ew_avail.get() or 10,
                               self.ew_floor.get() or 1))
        if ok:
            messagebox.showinfo("Added",f"Ward added! ID: {r}")
            self.load_data()
        else:
            messagebox.showerror("Error",r)

    def _on_room_select(self,_):
        sel=self.tree_room.selection()
        if not sel: return
        v=self.tree_room.item(sel[0])["values"]
        self._sel_room_id=v[0]
        self.er_status.set(v[4])

    def add_room(self):
        w_key=self.cr_ward.get()
        if not w_key:
            messagebox.showwarning("Validation","Select a ward."); return
        wid=self.ward_map.get(w_key)
        q="INSERT INTO rooms(ward_id,room_number,room_type,status,daily_charge) VALUES(%s,%s,%s,%s,%s)"
        ok,r=execute_query(q,(wid,self.er_num.get().strip(),
                               self.er_type.get() or "General",
                               self.er_status.get() or "Available",
                               self.er_charge.get() or 500))
        if ok:
            messagebox.showinfo("Added",f"Room added! ID: {r}")
            self.load_data()
        else:
            messagebox.showerror("Error",r)

    def update_room_status(self):
        if not self._sel_room_id:
            messagebox.showwarning("Select","Select a room first."); return
        ok,r=execute_query("UPDATE rooms SET status=%s WHERE room_id=%s",
                           (self.er_status.get(),self._sel_room_id))
        if ok:
            messagebox.showinfo("Updated","Room status updated.")
            self.load_data()
        else:
            messagebox.showerror("Error",r)


# ── Pharmacy Module ──────────────────────────────────────────

class PharmacyModule(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG_DARK)
        self._build_ui()
        self.load_medicines()

    def _build_ui(self):
        tk.Label(self, text="💊  Pharmacy & Medicines", bg=BG_DARK,
                 fg=ACCENT, font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 8))

        card=tk.LabelFrame(self,text=" Add / Edit Medicine ",
                           bg=BG_CARD,fg=ACCENT,
                           font=("Segoe UI",10,"bold"),relief="groove",bd=1)
        card.pack(fill="x",padx=4,pady=4)
        card.columnconfigure(1,weight=1); card.columnconfigure(3,weight=1)

        self.em_name  = label_entry(card,"Medicine Name*",  0,0)
        self.cm_cat   = label_combo(card,"Category*",       0,
                                    ["Tablet","Syrup","Injection","Capsule","Cream","Drops","Other"],2)
        self.em_mfg   = label_entry(card,"Manufacturer",    1,0)
        self.em_price = label_entry(card,"Unit Price (Rs)*",1,2,10)
        self.em_stock = label_entry(card,"Stock Qty*",      2,0,10)
        self.em_reord = label_entry(card,"Reorder Level",   2,2,10)
        self.em_exp   = label_entry(card,"Expiry (YYYY-MM-DD)",3,0)

        br=tk.Frame(card,bg=BG_CARD); br.grid(row=4,column=0,columnspan=4,pady=8)
        styled_btn(br,"➕ Add Medicine",  self.add_medicine).pack(side="left",padx=4)
        styled_btn(br,"✏️ Update Stock",  self.update_stock,ACCENT2,TEXT_WHITE).pack(side="left",padx=4)
        styled_btn(br,"🗑 Delete",         self.delete_medicine,DANGER,TEXT_WHITE).pack(side="left",padx=4)
        styled_btn(br,"🔄 Refresh",       self.load_medicines,WARNING,BG_DARK).pack(side="left",padx=4)

        # Low-stock warning label
        self.lbl_warn=tk.Label(self,text="",bg=BG_DARK,fg=WARNING,
                               font=("Segoe UI",10,"bold"))
        self.lbl_warn.pack(anchor="w",padx=4)

        cols=("ID","Name","Category","Manufacturer","Price","Stock","Reorder","Expiry")
        self.tree=build_tree(self,cols)
        self.tree.bind("<<TreeviewSelect>>",self._on_select)
        self._selected_id=None

    def load_medicines(self):
        ok,rows=execute_query(
            "SELECT medicine_id,name,category,manufacturer,unit_price,stock_qty,reorder_level,expiry_date FROM medicines ORDER BY name",
            fetch=True)
        if ok:
            refresh_tree(self.tree,rows)
            low=[r['name'] for r in rows if r['stock_qty']<=r['reorder_level']]
            if low:
                self.lbl_warn.config(text=f"⚠️  Low Stock: {', '.join(low)}")
            else:
                self.lbl_warn.config(text="✅  All medicines are adequately stocked.")

    def _on_select(self,_):
        sel=self.tree.selection()
        if not sel: return
        v=self.tree.item(sel[0])["values"]
        self._selected_id=v[0]
        for w,d in zip([self.em_name,self.em_mfg,self.em_price,self.em_stock,self.em_reord,self.em_exp],
                       [v[1],v[3],v[4],v[5],v[6],v[7]]):
            w.delete(0,"end"); w.insert(0,d or "")
        self.cm_cat.set(v[2])

    def add_medicine(self):
        name=self.em_name.get().strip()
        if not name:
            messagebox.showwarning("Validation","Medicine name required."); return
        q="INSERT INTO medicines(name,category,manufacturer,unit_price,stock_qty,reorder_level,expiry_date) VALUES(%s,%s,%s,%s,%s,%s,%s)"
        ok,r=execute_query(q,(name,self.cm_cat.get() or "Tablet",
                               self.em_mfg.get().strip(),
                               self.em_price.get() or 0,
                               self.em_stock.get() or 0,
                               self.em_reord.get() or 10,
                               self.em_exp.get().strip() or None))
        if ok:
            messagebox.showinfo("Added",f"Medicine added! ID: {r}")
            self.load_medicines()
        else:
            messagebox.showerror("Error",r)

    def update_stock(self):
        if not self._selected_id:
            messagebox.showwarning("Select","Select a medicine first."); return
        new_qty=self.em_stock.get()
        ok,r=execute_query("UPDATE medicines SET stock_qty=%s WHERE medicine_id=%s",
                           (new_qty,self._selected_id))
        if ok:
            messagebox.showinfo("Updated","Stock updated.")
            self.load_medicines()
        else:
            messagebox.showerror("Error",r)

    def delete_medicine(self):
        if not self._selected_id:
            messagebox.showwarning("Select","Select a medicine first."); return
        if messagebox.askyesno("Confirm","Delete this medicine?"):
            ok,r=execute_query("DELETE FROM medicines WHERE medicine_id=%s",(self._selected_id,))
            if ok:
                messagebox.showinfo("Deleted","Medicine deleted.")
                self._selected_id=None
                self.load_medicines()
            else:
                messagebox.showerror("Error",r)


# ── Billing Module ───────────────────────────────────────────

class BillingModule(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG_DARK)
        self._build_ui()
        self.load_bills()

    def _get_patient_map(self):
        ok,rows=execute_query("SELECT patient_id,first_name,last_name FROM patients",fetch=True)
        if ok:
            return {f"{r['patient_id']} - {r['first_name']} {r['last_name']}": r['patient_id'] for r in rows}
        return {}

    def _build_ui(self):
        tk.Label(self, text="💰  Billing Management", bg=BG_DARK,
                 fg=ACCENT, font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 8))

        card=tk.LabelFrame(self,text=" Generate Bill ",
                           bg=BG_CARD,fg=ACCENT,
                           font=("Segoe UI",10,"bold"),relief="groove",bd=1)
        card.pack(fill="x",padx=4,pady=4)
        card.columnconfigure(1,weight=1); card.columnconfigure(3,weight=1)

        self.patient_map=self._get_patient_map()
        self.cb_patient=label_combo(card,"Patient*",     0,list(self.patient_map.keys()),width=28)
        self.e_consult = label_entry(card,"Consult Fee", 0,2,12)
        self.e_room    = label_entry(card,"Room Charges",1,0,12)
        self.e_med     = label_entry(card,"Med Charges", 1,2,12)
        self.e_test    = label_entry(card,"Test Charges",2,0,12)
        self.e_other   = label_entry(card,"Other",       2,2,12)
        self.e_paid    = label_entry(card,"Paid Amount", 3,0,12)
        self.cb_method = label_combo(card,"Payment Method",3,
                                     ["Cash","Card","Online","Insurance"],2)
        self.cb_status = label_combo(card,"Status",      4,
                                     ["Pending","Partial","Paid"],0)

        # Total display
        self.lbl_total=tk.Label(card,text="Total: Rs 0.00",bg=BG_CARD,
                                fg=ACCENT,font=("Segoe UI",13,"bold"))
        self.lbl_total.grid(row=4,column=2,columnspan=2,padx=8)

        br=tk.Frame(card,bg=BG_CARD); br.grid(row=5,column=0,columnspan=4,pady=8)
        styled_btn(br,"🧮 Calculate",   self.calculate_total).pack(side="left",padx=4)
        styled_btn(br,"💾 Save Bill",   self.save_bill,SUCCESS,TEXT_WHITE).pack(side="left",padx=4)
        styled_btn(br,"🔄 Refresh",     self.load_bills,WARNING,BG_DARK).pack(side="left",padx=4)

        cols=("ID","Patient","Consult","Room","Medicine","Test","Other","Total","Paid","Status","Method","Date")
        self.tree=build_tree(self,cols)

    def calculate_total(self):
        try:
            total=sum(float(e.get() or 0) for e in
                      [self.e_consult,self.e_room,self.e_med,self.e_test,self.e_other])
            self.lbl_total.config(text=f"Total: Rs {total:,.2f}")
        except ValueError:
            messagebox.showwarning("Input","Enter valid numbers for charges.")

    def save_bill(self):
        p_key=self.cb_patient.get()
        if not p_key:
            messagebox.showwarning("Validation","Select a patient."); return
        pid=self.patient_map.get(p_key)
        try:
            c=float(self.e_consult.get() or 0)
            r=float(self.e_room.get()    or 0)
            m=float(self.e_med.get()     or 0)
            t=float(self.e_test.get()    or 0)
            o=float(self.e_other.get()   or 0)
            paid=float(self.e_paid.get() or 0)
        except ValueError:
            messagebox.showwarning("Input","Enter valid numeric charges."); return
        total=c+r+m+t+o
        q="""INSERT INTO bills(patient_id,consultation_fee,room_charges,medicine_charges,
             test_charges,other_charges,total_amount,paid_amount,payment_status,payment_method)
             VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        ok,result=execute_query(q,(pid,c,r,m,t,o,total,paid,
                                    self.cb_status.get() or "Pending",
                                    self.cb_method.get() or "Cash"))
        if ok:
            messagebox.showinfo("Saved",f"Bill saved! ID: {result}  Total: Rs {total:,.2f}")
            self.load_bills()
        else:
            messagebox.showerror("Error",result)

    def load_bills(self):
        q="""SELECT b.bill_id,CONCAT(p.first_name,' ',p.last_name),
                    b.consultation_fee,b.room_charges,b.medicine_charges,
                    b.test_charges,b.other_charges,b.total_amount,b.paid_amount,
                    b.payment_status,b.payment_method,DATE(b.bill_date)
             FROM bills b JOIN patients p ON b.patient_id=p.patient_id
             ORDER BY b.bill_id DESC"""
        ok,rows=execute_query(q,fetch=True)
        if ok: refresh_tree(self.tree,rows)


# ════════════════════════════════════════════════════════════════
#  DASHBOARD
# ════════════════════════════════════════════════════════════════

class Dashboard(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG_DARK)
        self._build_ui()
        self.refresh_stats()

    def _stat_card(self, parent, label, value_var, color, icon):
        f=tk.Frame(parent, bg=color, padx=20, pady=16)
        f.pack(side="left", fill="both", expand=True, padx=8)
        tk.Label(f, text=icon, bg=color, fg=TEXT_WHITE,
                 font=("Segoe UI",22)).pack()
        tk.Label(f, textvariable=value_var, bg=color, fg=TEXT_WHITE,
                 font=("Segoe UI",26,"bold")).pack()
        tk.Label(f, text=label, bg=color, fg=TEXT_WHITE,
                 font=("Segoe UI",10)).pack()
        return value_var

    def _build_ui(self):
        tk.Label(self, text=f"🏥  Hospital Management System",
                 bg=BG_DARK, fg=ACCENT,
                 font=("Segoe UI", 20, "bold")).pack(pady=(20, 4))
        tk.Label(self, text=f"Dashboard  •  {date.today().strftime('%A, %d %B %Y')}",
                 bg=BG_DARK, fg=TEXT_MUTED,
                 font=("Segoe UI", 11)).pack(pady=(0,20))

        # Stat cards row
        row=tk.Frame(self, bg=BG_DARK)
        row.pack(fill="x", padx=20)

        self.v_patients = tk.StringVar(value="—")
        self.v_doctors  = tk.StringVar(value="—")
        self.v_appts    = tk.StringVar(value="—")
        self.v_rooms    = tk.StringVar(value="—")
        self.v_revenue  = tk.StringVar(value="—")
        self.v_low_stock= tk.StringVar(value="—")

        self._stat_card(row,"Total Patients",  self.v_patients, "#1A5F7A","👥")
        self._stat_card(row,"Active Doctors",  self.v_doctors,  "#16213E","🩺")
        self._stat_card(row,"Today's Appts",   self.v_appts,    "#0F3460","📅")
        self._stat_card(row,"Available Rooms", self.v_rooms,    "#533483","🚪")

        row2=tk.Frame(self, bg=BG_DARK)
        row2.pack(fill="x", padx=20, pady=(12,0))
        self._stat_card(row2,"Total Revenue",  self.v_revenue,  "#1B5E20","💰")
        self._stat_card(row2,"Low-Stock Meds", self.v_low_stock,DANGER,  "💊")

        styled_btn(self, "🔄 Refresh Stats", self.refresh_stats, ACCENT2, TEXT_WHITE, 18).pack(pady=20)

        # Recent appointments
        tk.Label(self, text="📋  Recent Appointments",
                 bg=BG_DARK, fg=ACCENT,
                 font=("Segoe UI",12,"bold")).pack(anchor="w",padx=24,pady=(8,0))
        cols=("ID","Patient","Doctor","Date","Time","Status")
        self.tree=build_tree(self,cols,7)

    def refresh_stats(self):
        checks=[
            ("SELECT COUNT(*) AS c FROM patients",                            self.v_patients),
            ("SELECT COUNT(*) AS c FROM doctors WHERE status='Active'",       self.v_doctors),
            (f"SELECT COUNT(*) AS c FROM appointments WHERE appointment_date='{date.today()}'", self.v_appts),
            ("SELECT COUNT(*) AS c FROM rooms WHERE status='Available'",      self.v_rooms),
            ("SELECT IFNULL(SUM(total_amount),0) AS c FROM bills",            self.v_revenue),
            ("SELECT COUNT(*) AS c FROM medicines WHERE stock_qty<=reorder_level", self.v_low_stock),
        ]
        for q, var in checks:
            ok, rows = execute_query(q, fetch=True)
            if ok and rows:
                val = list(rows[0].values())[0]
                if "revenue" in q.lower():
                    var.set(f"Rs {float(val):,.0f}")
                else:
                    var.set(str(val))

        q="""SELECT a.appointment_id,CONCAT(p.first_name,' ',p.last_name),
                    CONCAT('Dr. ',d.first_name,' ',d.last_name),
                    a.appointment_date,a.appointment_time,a.status
             FROM appointments a
             JOIN patients p ON a.patient_id=p.patient_id
             JOIN doctors  d ON a.doctor_id=d.doctor_id
             ORDER BY a.appointment_date DESC LIMIT 7"""
        ok,rows=execute_query(q,fetch=True)
        if ok: refresh_tree(self.tree,rows)


# ════════════════════════════════════════════════════════════════
#  MAIN APPLICATION
# ════════════════════════════════════════════════════════════════

class HospitalApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hospital Management System")
        self.geometry("1280x760")
        self.configure(bg=BG_DARK)
        self.resizable(True, True)
        self._build_layout()

    def _build_layout(self):
        # ── Sidebar ──
        sidebar = tk.Frame(self, bg=BG_PANEL, width=200)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="🏥", bg=BG_PANEL, fg=ACCENT,
                 font=("Segoe UI",32)).pack(pady=(20,4))
        tk.Label(sidebar, text="HMS", bg=BG_PANEL, fg=TEXT_WHITE,
                 font=("Segoe UI",16,"bold")).pack()
        tk.Label(sidebar, text="Hospital System", bg=BG_PANEL, fg=TEXT_MUTED,
                 font=("Segoe UI",8)).pack(pady=(0,24))

        ttk.Separator(sidebar, orient="horizontal").pack(fill="x", padx=12, pady=4)

        # Nav buttons
        self.content = tk.Frame(self, bg=BG_DARK)
        self.content.pack(side="right", fill="both", expand=True, padx=12, pady=12)

        self.frames = {}
        nav_items = [
            ("🏠  Dashboard",    "dashboard",    Dashboard),
            ("👥  Patients",     "patients",     PatientModule),
            ("🩺  Doctors",      "doctors",      DoctorModule),
            ("📅  Appointments", "appointments", AppointmentModule),
            ("🏥  Wards & Rooms","wards",        WardModule),
            ("💊  Pharmacy",     "pharmacy",     PharmacyModule),
            ("💰  Billing",      "billing",      BillingModule),
        ]

        for label, key, FrameClass in nav_items:
            f = FrameClass(self.content)
            f.place(relwidth=1, relheight=1)
            self.frames[key] = f

            btn = tk.Button(sidebar, text=label, bg=BG_PANEL, fg=TEXT_WHITE,
                            relief="flat", anchor="w", cursor="hand2",
                            font=("Segoe UI", 11), padx=16, pady=10,
                            activebackground=ACCENT, activeforeground=BG_DARK,
                            command=lambda k=key: self.show_frame(k))
            btn.pack(fill="x", pady=1)

        tk.Label(sidebar, text=f"\n© {date.today().year} HMS", bg=BG_PANEL,
                 fg=TEXT_MUTED, font=("Segoe UI",8)).pack(side="bottom", pady=8)

        self.show_frame("dashboard")

    def show_frame(self, key):
        self.frames[key].tkraise()


if __name__ == "__main__":
    ok, err = initialize_database()
    if not ok:
        messagebox.showerror("Database setup failed", err)
        raise SystemExit(err)

    app = HospitalApp()
    app.mainloop()