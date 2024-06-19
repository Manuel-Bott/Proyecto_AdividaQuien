import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import mysql.connector

class Personaje:
    def __init__(self, nombre, atributos):
        self.nombre = nombre
        self.atributos = atributos

class JuegoAdivinaQuien(tk.Tk):
    def __init__(self, connection_params):
        super().__init__()
        self.title("Adivina Quién")
        self.geometry("800x600")  # Tamaño de la ventana
        
        self.conn = mysql.connector.connect(**connection_params)
        self.cursor = self.conn.cursor()
        self.personajes = self.obtener_personajes()

        self.background_image = tk.PhotoImage(file="Aragon.png")  # Asegúrate que el archivo 'Aragon.png' está en la misma carpeta
        self.background_label = tk.Label(self, image=self.background_image)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.label_pregunta = tk.Label(self, text="", font=("Arial", 16))
        self.label_pregunta.place(relx=0.5, rely=0.1, anchor="center")

        self.btn_comenzar = tk.Button(self, text="Comenzar", font=("Arial", 14), command=self.comenzar_juego)
        self.btn_comenzar.place(relx=0.5, rely=0.6, anchor="center")

        self.btn_agregar = tk.Button(self, text="Agregar Nuevo", font=("Arial", 14), command=self.agregar_personaje)
        self.btn_agregar.place(relx=0.3, rely=0.8, anchor="center")

        self.btn_salir = tk.Button(self, text="Salir", font=("Arial", 14), command=self.salir)
        self.btn_salir.place(relx=0.7, rely=0.8, anchor="center")

        self.texto_adivinanza = tk.StringVar()
        self.texto_adivinanza.set("Piensa en un personaje mainstream de las siguientes Franquicias:\n"
                                  "El Señor de los Anillos, Dragon Ball Z, Harry Potter, Los Simpson,\n"
                                  "Malcolm in the Middle, Marvel, DC Comics, Super Mario Bros y Pokemon.\n"
                                  "Yo intentaré adivinar quién es, haciendo preguntas sobre sus atributos.")

        self.mostrar_menu()

    def obtener_personajes(self):
        self.cursor.execute("SELECT nombre, atributos FROM Personajes")
        rows = self.cursor.fetchall()
        personajes = []
        for row in rows:
            personajes.append(Personaje(row[0], eval(row[1])))  # Usamos eval para convertir el string JSON a un diccionario Python
        return personajes

    def hacer_pregunta(self, atributo, valor):
        respuesta = messagebox.askyesno("Pregunta", f"¿El personaje es de {atributo} {valor}?")

        if respuesta:
            self.personajes = [p for p in self.personajes if p.atributos.get(atributo) == valor]
            self.personajes = [Personaje(p.nombre, {k: v for k, v in p.atributos.items() if k != atributo}) for p in self.personajes]
        else:
            self.personajes = [p for p in self.personajes if p.atributos.get(atributo) != valor]

        atributos_compartidos = []
        for personaje in self.personajes:
            for a, v in personaje.atributos.items():
                if v == valor and a != atributo:
                    atributos_compartidos.append(a)

        for atributo_compartido in atributos_compartidos:
            self.personajes = [p for p in self.personajes if p.atributos.get(atributo_compartido) == valor]

        return len(self.personajes) > 0

    def mostrar_menu(self):
        self.label_pregunta.config(text="")
        self.btn_comenzar.place(relx=0.5, rely=0.6, anchor="center")
        self.btn_agregar.place(relx=0.3, rely=0.8, anchor="center")
        self.btn_salir.place(relx=0.7, rely=0.8, anchor="center")

    def comenzar_juego(self):
        self.label_pregunta.config(text=self.texto_adivinanza.get())
        self.btn_comenzar.place_forget()
        self.jugar()

    def jugar(self):
        adivinado = False
        while not adivinado:
            try:
                personaje_secreto = random.choice(self.personajes)
            except IndexError:
                messagebox.showinfo("Fin del juego", "No quedan personajes para adivinar. Reiniciando el juego...")
                self.personajes = self.obtener_personajes()
                continue

            for atributo, valor in personaje_secreto.atributos.items():
                if self.hacer_pregunta(atributo, valor):
                    personaje_secreto = random.choice(self.personajes)
                else:
                    break

                if len(self.personajes) == 1:
                    adivinado = True
                    break

            if len(self.personajes) == 0:
                messagebox.showinfo("Fin del juego", "No pude adivinar el personaje. Intentemos con otros atributos.")
                continue

            if len(self.personajes) == 1:
                messagebox.showinfo("¡Adiviné!", f"¡Tu personaje es {self.personajes[0].nombre}!")
                self.personajes = self.obtener_personajes()
                self.mostrar_menu()
                break

    def agregar_personaje(self):
        nueva_ventana = tk.Toplevel(self)
        nueva_ventana.title("Agregar Nuevo Personaje")

        label_nombre = tk.Label(nueva_ventana, text="Nombre del personaje:")
        label_nombre.pack(pady=10)

        entry_nombre = tk.Entry(nueva_ventana, width=30)
        entry_nombre.pack()

        btn_guardar = tk.Button(nueva_ventana, text="Guardar", command=lambda: self.guardar_personaje(entry_nombre.get(), nueva_ventana))
        btn_guardar.pack(pady=20)

    def guardar_personaje(self, nombre, ventana_padre):
        atributos = {}
        atributos_orden = ["Estatura", "Color de Piel", "Habilidad", "Tipo de Especie", "Característica Distintiva"]

        for atributo in atributos_orden:
            valor = simpledialog.askstring("Nuevo Atributo", f"Ingrese el valor para el atributo '{atributo}':")
            if valor:
                atributos[atributo] = valor
            else:
                messagebox.showerror("Error", f"Debe ingresar un valor para el atributo '{atributo}'")
                return
        
        sql = "INSERT INTO Personajes (nombre, atributos) VALUES (%s, %s)"
        try:
            self.cursor.execute(sql, (nombre, str(atributos)))
            self.conn.commit()
            messagebox.showinfo("Éxito", "Personaje agregado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo agregar el personaje: {str(e)}")

        # Actualizar la lista de personajes
        self.personajes = self.obtener_personajes()

        # Cerrar la ventana de agregar personaje
        ventana_padre.destroy()

    def salir(self):
        self.conn.close()
        self.destroy()

# Parámetros de conexión a la base de datos MySQL
connection_params = {
    'host': 'localhost',
    'user': 'ManuelPena00',
    'password': 'Khtb453749.Dt',
    'database': 'adivinaquiendb',
    'port': '3306'
}

# Iniciar el juego
juego = JuegoAdivinaQuien(connection_params)
print("Bienvenido al juego Adivina Quién.")
juego.mainloop()



#Khtb453749.Dt

