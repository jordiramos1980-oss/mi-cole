import streamlit as st
from gtts import gTTS
import io, PyPDF2, random
try:
    from fpdf import FPDF
except ImportError:
    st.error("⚠️ Te falta instalar: Escribe 'pip install fpdf' en la terminal")

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Mi Cole Personalizado", page_icon="🏫", layout="wide")

# --- FUNCIONES ---
def leer_pdf(f):
    try:
        reader = PyPDF2.PdfReader(f)
        texto = "".join([p.extract_text() for p in reader.pages if p.extract_text()])
        return texto if texto.strip() else "⚠️ PDF sin texto."
    except: return "❌ Error al leer PDF."

def crear_audio(txt, lang, vel_lenta):
    tts = gTTS(text=txt, lang=lang, slow=vel_lenta)
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    return fp

def gen_prob(tipo_sel, nombre):
    objetos = ["canicas", "cromos", "caramelos", "lápices", "manzanas", "estrellas", "cromos de fútbol", "pegatinas"]
    o = random.choice(objetos)
    
    t = tipo_sel
    if t == "Mixto":
        t = random.choice(["Suma", "Resta", "Multiplicación", "División"])
    
    if t == "Suma":
        a, b = random.randint(10, 99), random.randint(10, 99)
        return f"🌟 {nombre}, tienes {a} {o} y te regalan {b} más. ¿Cuántos tienes en total?", a + b
    elif t == "Resta":
        a, b = random.randint(50, 99), random.randint(5, 45)
        return f"🍎 {nombre}, tenías {a} {o} pero has perdido {b}. ¿Cuántos te quedan ahora?", a - b
    elif t == "Multiplicación":
        a, b = random.randint(2, 9), random.randint(3, 10)
        return f"📦 {nombre}, hay {a} cajas y cada una tiene {b} {o}. ¿Cuántos {o} hay por todos?", a * b
    elif t == "División":
        b = random.randint(2, 5)
        res = random.randint(2, 10)
        a = b * res
        return f"🍕 {nombre}, quieres repartir {a} {o} entre {b} amigos a partes iguales. ¿Cuántos le tocan a cada uno?", res
    return "Error", 0

# --- MEMORIA ---
if 'usuarios' not in st.session_state:
    st.session_state.usuarios = {"Jordi": {"puntos": 0, "nivel": 1}} 

if 'usuario_actual' not in st.session_state:
    st.session_state.usuario_actual = None

# --- PANTALLA INICIO ---
if st.session_state.usuario_actual is None:
    st.title("👋 ¡Bienvenidos al Cole!")
    nom = st.text_input("¿Cómo te llamas?").capitalize()
    if st.button("¡Entrar a Clase!"):
        if nom:
            st.session_state.usuario_actual = nom
            if nom not in st.session_state.usuarios:
                st.session_state.usuarios[nom] = {"puntos": 0, "nivel": 1}
            st.rerun()
    st.markdown("---")
    st.caption("👨‍🏫 Creado por: **Jordi Ramos Gomez**")
    st.caption("📧 Contacto: jordiramos1980@gmail.com")

else:
    nombre = st.session_state.usuario_actual
    datos = st.session_state.usuarios[nombre]
    
    st.sidebar.title(f"🎒 Pupitre de {nombre}")
    st.sidebar.metric("🏆 Mis Puntos", datos["puntos"])
    op = st.sidebar.radio("Menú", ["Matemáticas", "Dictados", "Mis Deberes", "Mis Compañeros"])
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.usuario_actual = None
        st.rerun()

    if op == "Matemáticas":
        st.header(f"🔢 ¡A por todas, {nombre}!")
        t1, t2 = st.tabs(["Tablas y Exámenes", "Desafío de 5 Problemas"])
        
        with t1:
            nv = datos["nivel"]
            if nv <= 10:
                st.subheader(f"Nivel {nv}: Tabla del {nv}")
                c1, c2 = st.columns(2)
                with c1:
                    for i in range(1, 11): st.write(f"{nv} x {i} = **{nv*i}**")
                with c2:
                    with st.form("ex"):
                        p = [2, 5, 8]
                        r = [st.number_input(f"¿{nv} x {i}?", step=1, key=f"ex{i}") for i in p]
                        if st.form_submit_button("Corregir"):
                            ac = sum(1 for idx, val in enumerate(r) if val == nv*p[idx])
                            st.session_state.usuarios[nombre]["puntos"] += ac * 10
                            if ac == 3:
                                st.balloons(); st.session_state.usuarios[nombre]["nivel"] += 1
                            st.rerun()
            else: st.success("🎊 ¡TABLAS COMPLETADAS!")

        with t2:
            st.subheader("🎲 Los 5 Desafíos")
            
            # Si no hay problemas o ya se terminaron, dejamos elegir tipo
            if 'lista_problemas' not in st.session_state:
                tipo_p = st.selectbox("Elige operación:", ["Suma", "Resta", "Multiplicación", "División", "Mixto"])
                if st.button("¡Generar 5 Problemas Nuevos!"):
                    st.session_state.lista_problemas = []
                    for _ in range(5):
                        en, sol = gen_prob(tipo_p, nombre)
                        st.session_state.lista_problemas.append({"enunciado": en, "solucion": sol, "resuelto": False})
                    st.rerun()
            else:
                st.warning("🎯 Tienes 5 problemas pendientes. ¡Resuélvelos todos para pedir más!")
                
                completados = 0
                for idx, p in enumerate(st.session_state.lista_problemas):
                    with st.expander(f"Problema {idx+1} {'✅' if p['resuelto'] else '❓'}", expanded=not p['resuelto']):
                        st.write(p['enunciado'])
                        if not p['resuelto']:
                            res_niño = st.number_input("Tu respuesta:", key=f"prob_{idx}", step=1)
                            if st.button("Comprobar", key=f"btn_{idx}"):
                                if res_niño == p['solucion']:
                                    st.session_state.lista_problemas[idx]['resuelto'] = True
                                    st.session_state.usuarios[nombre]["puntos"] += 50
                                    st.success("¡Bien hecho! +50 puntos")
                                    st.rerun()
                                else:
                                    st.error("¡Casi! Revisa la cuenta.")
                        else:
                            st.write(f"**Completado.** La respuesta era {p['solucion']}.")
                            completados += 1
                
                if completados == 5:
                    st.balloons()
                    st.success("🏆 ¡Increíble! Has terminado los 5 problemas.")
                    if st.button("Limpiar y pedir nuevos"):
                        del st.session_state.lista_problemas
                        st.rerun()

    elif op == "Dictados":
        st.header("📝 Rincón de los Dictados")
        f = st.file_uploader("Sube el PDF", type=["pdf"])
        if f:
            vel = st.radio("Velocidad:", ["Normal", "Lento"], horizontal=True)
            if st.button("¡Escuchar! 🎤"):
                t = leer_pdf(f)
                st.audio(crear_audio(t, "es", (vel == "Lento")))
                st.write(t)

    elif op == "Mis Deberes":
        st.header("📚 Mis Tareas")
        f = st.file_uploader("Archivo PDF", type=["pdf"])
        if f: st.info(leer_pdf(f))

    elif op == "Mis Compañeros":
        st.header("👥 Lista de Clase")
        for u, d in st.session_state.usuarios.items():
            st.write(f"👤 **{u}**: {d['puntos']} puntos (Nivel {d['nivel']})")

    st.markdown("---")
    st.caption("👨‍💻 Creado por: **Jordi Ramos Gomez**")