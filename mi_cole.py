import streamlit as st
from gtts import gTTS
import io, PyPDF2, random

# Intentamos importar FPDF para la descarga de deberes
try:
    from fpdf import FPDF
except ImportError:
    st.error("⚠️ Falta la librería fpdf. Recuerda añadir 'fpdf2' en requirements.txt")

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Mi Cole Personalizado", page_icon="🏫", layout="wide")

# --- FUNCIONES DE APOYO ---
def leer_pdf(f):
    try:
        reader = PyPDF2.PdfReader(f)
        texto = "".join([p.extract_text() for p in reader.pages if p.extract_text()])
        return texto if texto.strip() else "⚠️ El PDF parece estar vacío o es una imagen."
    except Exception as e:
        return f"❌ Error al leer el archivo: {e}"

def crear_audio(txt, lang, vel_lenta):
    try:
        tts = gTTS(text=txt, lang=lang, slow=vel_lenta)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        return fp
    except:
        return None

def gen_prob(tipo_sel, nombre):
    objetos = ["canicas", "cromos", "caramelos", "lápices", "manzanas", "estrellas", "pegatinas", "balones"]
    o = random.choice(objetos)
    t = tipo_sel
    if t == "Mixto":
        t = random.choice(["Suma", "Resta", "Multiplicación", "División"])
    
    if t == "Suma":
        a, b = random.randint(10, 99), random.randint(10, 99)
        return f"🌟 {nombre}, tienes {a} {o} y te regalan {b} más. ¿Cuántos tienes ahora?", a + b
    elif t == "Resta":
        a, b = random.randint(50, 99), random.randint(5, 45)
        return f"🍎 {nombre}, tenías {a} {o} pero has perdido {b}. ¿Cuántos te quedan?", a - b
    elif t == "Multiplicación":
        a, b = random.randint(2, 9), random.randint(3, 10)
        return f"📦 {nombre}, tienes {a} bolsas y cada una tiene {b} {o}. ¿Cuántos hay en total?", a * b
    elif t == "División":
        divisor = random.randint(2, 5)
        cociente = random.randint(2, 10)
        dividendo = divisor * cociente
        return f"🍕 {nombre}, quieres repartir {dividendo} {o} entre {divisor} amigos. ¿Cuántos le tocan a cada uno?", cociente
    return "Error al generar", 0

# --- GESTIÓN DE MEMORIA (SESSION STATE) ---
if 'usuarios' not in st.session_state:
    st.session_state.usuarios = {"Jordi": {"puntos": 0, "nivel": 1}} 

if 'usuario_actual' not in st.session_state:
    st.session_state.usuario_actual = None

# --- PANTALLA DE ACCESO ---
if st.session_state.usuario_actual is None:
    st.title("👋 ¡Bienvenidos a Mi Cole!")
    st.subheader("Tu rincón para aprender jugando")
    
    with st.container():
        nom_input = st.text_input("Escribe tu nombre para empezar:").strip().capitalize()
        if st.button("🚀 ¡Entrar a Clase!"):
            if nom_input:
                st.session_state.usuario_actual = nom_input
                if nom_input not in st.session_state.usuarios:
                    st.session_state.usuarios[nom_input] = {"puntos": 0, "nivel": 1}
                st.rerun()
            else:
                st.warning("¡Oye! No olvides decirme cómo te llamas.")
    
    st.markdown("---")
    st.caption("👨‍🏫 Creado por: **Jordi Ramos Gomez**")
    st.caption("📧 Contacto: jordiramos1980@gmail.com")

# --- APLICACIÓN PRINCIPAL ---
else:
    nombre = st.session_state.usuario_actual
    datos = st.session_state.usuarios[nombre]
    
    # Barra lateral con información
    st.sidebar.title(f"🎒 Pupitre de {nombre}")
    st.sidebar.metric("🏆 Mis Puntos", f"{datos['puntos']} pts")
    st.sidebar.write(f"📈 Nivel de Tablas: {datos['nivel']}/10")
    
    menu = st.sidebar.radio("¿Qué quieres hacer hoy?", ["Matemáticas", "Dictados", "Mis Deberes", "Mis Compañeros"])
    
    if st.sidebar.button("🚪 Cerrar Sesión"):
        st.session_state.usuario_actual = None
        st.rerun()

    # 1. SECCIÓN MATEMÁTICAS
    if menu == "Matemáticas":
        st.header(f"🔢 Desafío Matemático")
        tab1, tab2 = st.tabs(["🎯 Examen de Tablas", "🎲 Los 5 Problemas"])
        
        with tab1:
            nv = datos["nivel"]
            if nv <= 10:
                st.subheader(f"Estás en el Nivel {nv} (Tabla del {nv})")
                col_a, col_b = st.columns(2)
                with col_a:
                    for i in range(1, 11): st.write(f"{nv} x {i} = **{nv*i}**")
                with col_b:
                    st.write("📝 **¡Demuestra lo que sabes!**")
                    with st.form("form_examen"):
                        preguntas = [2, 5, 8, 9]
                        respuestas = [st.number_input(f"¿{nv} x {p}?", step=1, key=f"ex_{p}") for p in preguntas]
                        if st.form_submit_button("Corregir Examen"):
                            correctas = 0
                            for i, res in enumerate(respuestas):
                                if res == nv * preguntas[i]:
                                    st.success(f"✅ {nv} x {preguntas[i]} = {res} ¡Bien!")
                                    correctas += 1
                                else:
                                    st.error(f"❌ {nv} x {preguntas[i]} era {nv*preguntas[i]}")
                            
                            st.session_state.usuarios[nombre]["puntos"] += correctas * 10
                            if correctas == len(preguntas):
                                st.balloons()
                                st.session_state.usuarios[nombre]["nivel"] += 1
                                st.info("¡Has subido de nivel! Cambia de pestaña para actualizar.")
            else:
                st.success("🎊 ¡Felicidades! Has completado todas las tablas.")

        with tab2:
            st.subheader("Desafío de los 5 Problemas")
            if 'lista_p' not in st.session_state:
                tipo = st.selectbox("Elige operación:", ["Suma", "Resta", "Multiplicación", "División", "Mixto"])
                if st.button("¡Generar 5 Problemas!"):
                    st.session_state.lista_p = []
                    for _ in range(5):
                        en, sol = gen_prob(tipo, nombre)
                        st.session_state.lista_p.append({"en": en, "sol": sol, "resuelto": False})
                    st.rerun()
            else:
                puntos_ganados = 0
                for idx, p in enumerate(st.session_state.lista_p):
                    with st.expander(f"Problema {idx+1} {'✅' if p['resuelto'] else '❓'}", expanded=not p['resuelto']):
                        st.write(p['en'])
                        if not p['resuelto']:
                            r_niño = st.number_input("Respuesta:", key=f"in_{idx}", step=1)
                            if st.button("Comprobar", key=f"bt_{idx}"):
                                if r_niño == p['sol']:
                                    st.session_state.lista_p[idx]['resuelto'] = True
                                    st.session_state.usuarios[nombre]["puntos"] += 50
                                    st.rerun()
                                else:
                                    st.error("¡Casi! Inténtalo de nuevo.")
                        else:
                            st.success(f"¡Hecho! Resultado: {p['sol']}")
                            puntos_ganados += 1
                
                if puntos_ganados == 5:
                    st.balloons()
                    if st.button("🎉 ¡Reto superado! Pedir otros 5"):
                        del st.session_state.lista_p
                        st.rerun()

    # 2. SECCIÓN DICTADOS
    elif menu == "Dictados":
        st.header("📝 Rincón de Dictados")
        st.write("Sube un PDF y practicaré contigo.")
        archivo = st.file_uploader("Elige tu PDF", type=["pdf"])
        if archivo:
            velocidad = st.radio("Velocidad de voz:", ["Normal", "Tortuga (Lento)"], horizontal=True)
            if st.button("🎤 Empezar Dictado"):
                texto = leer_pdf(archivo)
                audio = crear_audio(texto, "es", (velocidad != "Normal"))
                if audio:
                    st.audio(audio)
                    st.write("**Texto extraído:**")
                    st.info(texto)

    # 3. SECCIÓN DEBERES
    elif menu == "Mis Deberes":
        st.header("📚 Mis Tareas")
        archivo = st.file_uploader("Sube tus deberes para leerlos", type=["pdf"])
        if archivo:
            texto = leer_pdf(archivo)
            st.write("📖 Contenido de tu tarea:")
            st.info(texto)

    # 4. SECCIÓN COMPAÑEROS
    elif menu == "Mis Compañeros":
        st.header("👥 Ranking de la Clase")
        for u, d in st.session_state.usuarios.items():
            icono = "⭐" if u == nombre else "👤"
            st.write(f"{icono} **{u}**: {d['puntos']} puntos | Nivel {d['nivel']}")

    # --- PIE DE PÁGINA COMÚN ---
    st.markdown("---")
    st.caption(f"👨‍💻 Aplicación creada por **Jordi Ramos Gomez** para sus alumnos.")