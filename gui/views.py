import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from database.database import Database

class MainApplication:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Sistema de Gestión Parroquial")
        self.root.geometry("1200x700")
        
        self.db = Database()
        if not self.db.connect():
            messagebox.showerror("Error", "No se pudo conectar a la base de datos")
            self.root.destroy()
            return
        
        self.create_main_menu()
        self.show_main_panel()
    
    def create_main_menu(self) -> None:
        """Crea el menú principal de la aplicación"""
        self.menu_bar = tk.Menu(self.root)
        
        # Menú Archivo
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="Salir", command=self.root.quit)
        self.menu_bar.add_cascade(label="Archivo", menu=file_menu)
        
        # Menú Gestión
        management_menu = tk.Menu(self.menu_bar, tearoff=0)
        management_menu.add_command(label="Feligreses", command=self.show_fieles)
        management_menu.add_command(label="Sacramentos", command=self.show_sacramentos)
        management_menu.add_command(label="Eventos", command=self.show_eventos)
        management_menu.add_command(label="Donaciones", command=self.show_donaciones)
        management_menu.add_command(label="Intenciones", command=self.show_intenciones)
        
        self.menu_bar.add_cascade(label="Gestión", menu=management_menu)
        self.root.config(menu=self.menu_bar)
    
    def clear_frame(self) -> None:
        """Limpia el frame principal"""
        for widget in self.root.winfo_children():
            if not isinstance(widget, tk.Menu):
                widget.destroy()
    
    def show_main_panel(self) -> None:
        """Muestra el panel principal"""
        self.clear_frame()
        
        frame = ttk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(frame, text="Sistema de Gestión Parroquial", 
                 font=('Helvetica', 16)).pack(pady=20)
        
        ttk.Label(frame, text="Seleccione una opción del menú para comenzar", 
                 font=('Helvetica', 12)).pack(pady=10)
    
    def show_fieles(self) -> None:
        """Muestra la gestión de feligreses con estructura adaptada a la BD"""
        self.clear_frame()
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Barra superior con botones
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(toolbar, text="Agregar Feligrés", command=self.show_add_fiel).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Regresar", command=self.show_main_panel).pack(side=tk.RIGHT, padx=5)
        
        # Treeview para mostrar los fieles
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("ID", "Nombre", "Dirección", "Teléfono", "Email")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        # Configuración explícita de columnas
        column_config = {
            "ID": {"width": 50, "anchor": tk.CENTER},
            "Nombre": {"width": 150, "anchor": tk.W},
            "Dirección": {"width": 200, "anchor": tk.W},
            "Teléfono": {"width": 100, "anchor": tk.W},
            "Email": {"width": 150, "anchor": tk.W}
        }
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, **column_config[col])
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True)
        
        # Cargar datos con manejo robusto
        try:
            fieles = self.db.get_fieles()
            
            if not fieles:
                messagebox.showinfo("Información", "No hay feligreses registrados")
                return
                
            for fiel in fieles:
                # Asegurar el orden: id_fiel, nombre, direccion, telefono, email
                tree.insert("", tk.END, values=(
                    fiel[0],  # id_fiel
                    fiel[1],  # nombre
                    fiel[2] if fiel[2] else "",  # direccion (manejo de NULL)
                    fiel[3] if fiel[3] else "",  # telefono (manejo de NULL)
                    fiel[4] if fiel[4] else ""   # email (manejo de NULL)
                ))
                
        except Exception as e:
            print("Error al cargar feligreses:", str(e))
            messagebox.showerror("Error", 
                f"No se pudieron cargar los feligreses.\nError: {str(e)}")
        
    def show_add_fiel(self) -> None:
        """Muestra el formulario para agregar un feligrés"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Agregar Feligrés")
        dialog.geometry("400x300")
        
        ttk.Label(dialog, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        nombre_entry = ttk.Entry(dialog)
        nombre_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(dialog, text="Dirección:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        direccion_entry = ttk.Entry(dialog)
        direccion_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(dialog, text="Teléfono:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.E)
        telefono_entry = ttk.Entry(dialog)
        telefono_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(dialog, text="Email:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.E)
        email_entry = ttk.Entry(dialog)
        email_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        
        def save():
            nombre = nombre_entry.get()
            direccion = direccion_entry.get() or None
            telefono = telefono_entry.get() or None
            email = email_entry.get() or None
            
            if not nombre:
                messagebox.showerror("Error", "El nombre es obligatorio")
                return
            
            if self.db.add_fiel(nombre, direccion, telefono, email):
                messagebox.showinfo("Éxito", "Feligrés agregado correctamente")
                dialog.destroy()
                self.show_fieles()
            else:
                messagebox.showerror("Error", "No se pudo agregar el feligrés")
        
        ttk.Button(dialog, text="Guardar", command=save).grid(row=4, column=0, columnspan=2, pady=10)
    
    def show_sacramentos(self):
        """Muestra sacramentos y registros según estructura de la BD"""
        self.clear_frame()
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña de Sacramentos
        sacramentos_tab = ttk.Frame(notebook)
        notebook.add(sacramentos_tab, text="Sacramentos")
        
        # Treeview para sacramentos
        sac_columns = ("ID", "Nombre", "Descripción")
        sac_tree = ttk.Treeview(sacramentos_tab, columns=sac_columns, show="headings")
        
        sac_tree.heading("ID", text="ID")
        sac_tree.column("ID", width=50, anchor=tk.CENTER)
        
        sac_tree.heading("Nombre", text="Nombre")
        sac_tree.column("Nombre", width=150, anchor=tk.W)
        
        sac_tree.heading("Descripción", text="Descripción")
        sac_tree.column("Descripción", width=250, anchor=tk.W)
        
        sac_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Cargar sacramentos
        sacramentos = self.db.get_sacramentos()
        if sacramentos:
            for sac in sacramentos:
                sac_tree.insert("", tk.END, values=(
                    sac[0],  # id_sacramento
                    sac[1],  # nombre
                    sac[2] if sac[2] else ""  # descripcion
                ))
        
        # Pestaña de Registros
        registros_tab = ttk.Frame(notebook)
        notebook.add(registros_tab, text="Registros")
        
        # Botones
        btn_frame = ttk.Frame(registros_tab)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="Agregar Registro", command=self.show_add_registro).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Regresar", command=self.show_main_panel).pack(side=tk.RIGHT, padx=5)
        
        # Treeview para registros
        reg_columns = ("ID", "Feligrés", "Sacramento", "Fecha", "Sacerdote")
        reg_tree = ttk.Treeview(registros_tab, columns=reg_columns, show="headings")
        
        reg_tree.heading("ID", text="ID")
        reg_tree.column("ID", width=50, anchor=tk.CENTER)
        
        reg_tree.heading("Feligrés", text="Feligrés")
        reg_tree.column("Feligrés", width=150, anchor=tk.W)
        
        reg_tree.heading("Sacramento", text="Sacramento")
        reg_tree.column("Sacramento", width=150, anchor=tk.W)
        
        reg_tree.heading("Fecha", text="Fecha")
        reg_tree.column("Fecha", width=100, anchor=tk.CENTER)
        
        reg_tree.heading("Sacerdote", text="Sacerdote")
        reg_tree.column("Sacerdote", width=150, anchor=tk.W)
        
        reg_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Cargar registros
        registros = self.db.get_registros_sacramentales()
        if registros:
            for reg in registros:
                fecha = reg[3].strftime("%d/%m/%Y") if hasattr(reg[3], 'strftime') else reg[3]
                reg_tree.insert("", tk.END, values=(
                    reg[0],  # id_registro
                    reg[1],  # nombre_feligres
                    reg[2],  # nombre_sacramento
                    reg[3],   # fecha formateada
                    reg[4]   # sacerdote
                ))

    def show_add_registro(self):
        """Muestra el formulario para agregar un registro sacramental"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Agregar Registro Sacramental")
        dialog.geometry("500x400")
        
        # Obtener datos necesarios
        fieles = self.db.get_fieles()
        sacramentos = self.db.get_sacramentos()
        
        ttk.Label(dialog, text="Feligrés:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        fiel_combobox = ttk.Combobox(dialog, values=[f[1] for f in fieles], state="readonly")
        fiel_combobox.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        if fieles:
            fiel_combobox.current(0)
        
        ttk.Label(dialog, text="Sacramento:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        sacramento_combobox = ttk.Combobox(dialog, values=[s[1] for s in sacramentos], state="readonly")
        sacramento_combobox.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        if sacramentos:
            sacramento_combobox.current(0)
        
        ttk.Label(dialog, text="Fecha:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.E)
        fecha_entry = DateEntry(dialog, date_pattern='yyyy-mm-dd')
        fecha_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(dialog, text="Sacerdote:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.E)
        sacerdote_entry = ttk.Entry(dialog)
        sacerdote_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        
        def save():
            fiel_nombre = fiel_combobox.get()
            sacramento_nombre = sacramento_combobox.get()
            fecha = fecha_entry.get_date()
            sacerdote = sacerdote_entry.get()
            
            if not all([fiel_nombre, sacramento_nombre, fecha, sacerdote]):
                messagebox.showerror("Error", "Por favor complete todos los campos")
                return
            
            # Obtener IDs
            fiel_id = next(f[0] for f in fieles if f[1] == fiel_nombre)
            sacramento_id = next(s[0] for s in sacramentos if s[1] == sacramento_nombre)
            
            if self.db.add_registro_sacramental(fiel_id, sacramento_id, fecha, sacerdote):
                messagebox.showinfo("Éxito", "Registro agregado correctamente")
                dialog.destroy()
                self.show_sacramentos()
            else:
                messagebox.showerror("Error", "No se pudo agregar el registro")
        
        ttk.Button(dialog, text="Guardar", command=save).grid(row=4, column=0, columnspan=2, pady=10)
    
    def show_eventos(self):
        """Muestra la gestión de eventos con datos correctamente alineados"""
        self.clear_frame()
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="Agregar Evento", command=self.show_add_evento).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Regresar", command=self.show_main_panel).pack(side=tk.RIGHT, padx=5)
        
        # Treeview para eventos
        columns = ("ID", "Título", "Descripción", "Fecha", "Lugar")
        tree = ttk.Treeview(main_frame, columns=columns, show="headings")
        
        # Configuración de columnas
        tree.heading("ID", text="ID")
        tree.column("ID", width=50, anchor=tk.CENTER)
        
        tree.heading("Título", text="Título")
        tree.column("Título", width=150, anchor=tk.W)
        
        tree.heading("Descripción", text="Descripción")
        tree.column("Descripción", width=200, anchor=tk.W)
        
        tree.heading("Fecha", text="Fecha")
        tree.column("Fecha", width=120, anchor=tk.CENTER)
        
        tree.heading("Lugar", text="Lugar")
        tree.column("Lugar", width=150, anchor=tk.W)
        
        tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Cargar datos con manejo seguro
        try:
            eventos = self.db.get_eventos()
            if eventos:
                for evento in eventos:
                    # Asegurar que tenemos todos los campos necesarios
                    if len(evento) >= 5:
                        tree.insert("", tk.END, values=(
                            evento[0],  # id_evento
                            evento[1],  # título
                            evento[2] if evento[2] else "",  # descripción
                            evento[3],  # fecha ya formateada
                            evento[4]   # lugar
                        ))
        except Exception as e:
            print(f"Error al cargar eventos: {e}")
            messagebox.showerror("Error", "No se pudieron cargar los eventos")

    def show_add_evento(self):
        """Muestra el formulario para agregar un evento"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Agregar Evento")
        dialog.geometry("500x400")
        
        ttk.Label(dialog, text="Título:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        titulo_entry = ttk.Entry(dialog)
        titulo_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(dialog, text="Descripción:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        descripcion_entry = tk.Text(dialog, height=5, width=30)
        descripcion_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(dialog, text="Fecha y Hora:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.E)
        fecha_frame = ttk.Frame(dialog)
        fecha_frame.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        fecha_entry = DateEntry(fecha_frame, date_pattern='yyyy-mm-dd')
        fecha_entry.pack(side=tk.LEFT)
        
        hora_spinbox = ttk.Spinbox(fecha_frame, from_=0, to=23, width=2)
        hora_spinbox.pack(side=tk.LEFT)
        ttk.Label(fecha_frame, text=":").pack(side=tk.LEFT)
        minuto_spinbox = ttk.Spinbox(fecha_frame, from_=0, to=59, width=2)
        minuto_spinbox.pack(side=tk.LEFT)
        
        ttk.Label(dialog, text="Lugar:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.E)
        lugar_entry = ttk.Entry(dialog)
        lugar_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        
        def save():
            titulo = titulo_entry.get()
            descripcion = descripcion_entry.get("1.0", tk.END).strip()
            fecha = f"{fecha_entry.get_date()} {hora_spinbox.get()}:{minuto_spinbox.get()}:00"
            lugar = lugar_entry.get()
            
            if not all([titulo, descripcion, fecha, lugar]):
                messagebox.showerror("Error", "Por favor complete todos los campos")
                return
            
            if self.db.add_evento(titulo, descripcion, fecha, lugar):
                messagebox.showinfo("Éxito", "Evento agregado correctamente")
                dialog.destroy()
                self.show_eventos()
            else:
                messagebox.showerror("Error", "No se pudo agregar el evento")
        
        ttk.Button(dialog, text="Guardar", command=save).grid(row=4, column=0, columnspan=2, pady=10)
    
    def show_donaciones(self):
        """Muestra la gestión de donaciones"""
        self.clear_frame()
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="Agregar Donación", command=self.show_add_donacion).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Regresar", command=self.show_main_panel).pack(side=tk.RIGHT, padx=5)
        
        # Treeview para donaciones
        columns = ("ID", "Feligrés", "Monto", "Fecha", "Método de Pago")
        tree = ttk.Treeview(main_frame, columns=columns, show="headings")
        
        # Configurar encabezados y columnas con anchos específicos
        tree.heading("ID", text="ID")
        tree.column("ID", width=50, anchor=tk.CENTER)
        
        tree.heading("Feligrés", text="Feligrés")
        tree.column("Feligrés", width=200, anchor=tk.W)
        
        tree.heading("Monto", text="Monto")
        tree.column("Monto", width=100, anchor=tk.E)
        
        tree.heading("Fecha", text="Fecha")
        tree.column("Fecha", width=100, anchor=tk.CENTER)
        
        tree.heading("Método de Pago", text="Método de Pago")
        tree.column("Método de Pago", width=150, anchor=tk.W)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True)
        
        # Cargar datos con formato adecuado
        donaciones = self.db.get_donaciones()
        if donaciones:
            for donacion in donaciones:
                # Asegurar el orden correcto: ID, Feligrés, Monto, Fecha, Método
                id_donacion, nombre_feligres, monto, fecha, metodo = donacion
                
                # Formatear monto como moneda
                try:
                    monto_formateado = f"${float(monto):,.2f}"
                except (ValueError, TypeError):
                    monto_formateado = monto
                
                # Formatear fecha si es necesario
                if hasattr(fecha, 'strftime'):
                    fecha_formateada = fecha.strftime("%d/%m/%Y")
                else:
                    fecha_formateada = fecha
                
                tree.insert("", tk.END, values=(id_donacion, nombre_feligres, monto_formateado, fecha_formateada, metodo))
    
    def show_add_donacion(self):
        """Muestra el formulario para agregar una donación"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Agregar Donación")
        dialog.geometry("400x300")
        
        # Obtener fieles
        fieles = self.db.get_fieles()
        
        ttk.Label(dialog, text="Feligrés:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        fiel_combobox = ttk.Combobox(dialog, values=[f[1] for f in fieles], state="readonly")
        fiel_combobox.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        if fieles:
            fiel_combobox.current(0)
        
        ttk.Label(dialog, text="Monto:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        monto_entry = ttk.Entry(dialog)
        monto_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(dialog, text="Fecha:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.E)
        fecha_entry = DateEntry(dialog, date_pattern='yyyy-mm-dd')
        fecha_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(dialog, text="Método de Pago:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.E)
        metodo_combobox = ttk.Combobox(dialog, values=["Efectivo", "Transferencia", "Tarjeta"], state="readonly")
        metodo_combobox.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        metodo_combobox.current(0)
        
        def save():
            fiel_nombre = fiel_combobox.get()
            monto = monto_entry.get()
            fecha = fecha_entry.get_date()
            metodo = metodo_combobox.get()
            
            if not all([fiel_nombre, monto, fecha, metodo]):
                messagebox.showerror("Error", "Por favor complete todos los campos")
                return
            
            try:
                monto = float(monto)
            except ValueError:
                messagebox.showerror("Error", "El monto debe ser un número válido")
                return
            
            fiel_id = next(f[0] for f in fieles if f[1] == fiel_nombre)
            
            if self.db.add_donacion(fiel_id, monto, fecha, metodo):
                messagebox.showinfo("Éxito", "Donación registrada correctamente")
                dialog.destroy()
                self.show_donaciones()
            else:
                messagebox.showerror("Error", "No se pudo registrar la donación")
        
        ttk.Button(dialog, text="Guardar", command=save).grid(row=4, column=0, columnspan=2, pady=10)
    
    def show_intenciones(self):
        """Muestra la gestión de intenciones con datos correctamente alineados"""
        self.clear_frame()
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="Agregar Intención", command=self.show_add_intencion).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Regresar", command=self.show_main_panel).pack(side=tk.RIGHT, padx=5)
        
        # Treeview para intenciones
        columns = ("ID", "Feligrés", "Descripción", "Fecha")
        tree = ttk.Treeview(main_frame, columns=columns, show="headings")
        
        # Configuración explícita de columnas
        tree.heading("ID", text="ID")
        tree.column("ID", width=50, anchor=tk.CENTER)
        
        tree.heading("Feligrés", text="Feligrés")
        tree.column("Feligrés", width=150, anchor=tk.W)
        
        tree.heading("Descripción", text="Descripción")
        tree.column("Descripción", width=250, anchor=tk.W)
        
        tree.heading("Fecha", text="Fecha")
        tree.column("Fecha", width=100, anchor=tk.CENTER)
        
        tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Cargar datos con manejo seguro
        try:
            intenciones = self.db.get_intenciones_misa()
            if intenciones:
                for intencion in intenciones:
                    # Asegurar que tenemos todos los campos necesarios
                    if len(intencion) >= 4:
                        tree.insert("", tk.END, values=(
                            intencion[0],  # id_intencion
                            intencion[1],  # nombre_feligres
                            intencion[2],  # descripcion
                            intencion[3]   # fecha ya formateada
                        ))
        except Exception as e:
            print(f"Error al cargar intenciones: {e}")
            messagebox.showerror("Error", "No se pudieron cargar las intenciones")
    
    def show_add_intencion(self):
        """Muestra el formulario para agregar una intención de misa"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Agregar Intención de Misa")
        dialog.geometry("500x400")
        
        # Obtener fieles
        fieles = self.db.get_fieles()
        
        ttk.Label(dialog, text="Feligrés:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        fiel_combobox = ttk.Combobox(dialog, values=[f[1] for f in fieles], state="readonly")
        fiel_combobox.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        if fieles:
            fiel_combobox.current(0)
        
        ttk.Label(dialog, text="Descripción:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        descripcion_entry = tk.Text(dialog, height=5, width=30)
        descripcion_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(dialog, text="Fecha:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.E)
        fecha_entry = DateEntry(dialog, date_pattern='yyyy-mm-dd')
        fecha_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        def save():
            fiel_nombre = fiel_combobox.get()
            descripcion = descripcion_entry.get("1.0", tk.END).strip()
            fecha = fecha_entry.get_date()
            
            if not all([fiel_nombre, descripcion, fecha]):
                messagebox.showerror("Error", "Por favor complete todos los campos")
                return
            
            fiel_id = next(f[0] for f in fieles if f[1] == fiel_nombre)
            
            if self.db.add_intencion_misa(fiel_id, descripcion, fecha):
                messagebox.showinfo("Éxito", "Intención agregada correctamente")
                dialog.destroy()
                self.show_intenciones()
            else:
                messagebox.showerror("Error", "No se pudo agregar la intención")
        
        ttk.Button(dialog, text="Guardar", command=save).grid(row=3, column=0, columnspan=2, pady=10)

def main():
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()

if __name__ == "__main__":
    main()