import streamlit as st
from datetime import date
import pandas as pd
import re
import time
from reportlab.lib.pagesizes import letter, LEGAL
from reportlab.pdfgen import canvas
import io
from PIL import Image
from reportlab.lib.utils import ImageReader
import base64
import textwrap

# Configuración inicial de session_state
if 'sic_counter' not in st.session_state:
    st.session_state.sic_counter = 1
if 'solicitudes' not in st.session_state:
    st.session_state.solicitudes = {}
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "Dashboard"
if 'usuarios' not in st.session_state:
    st.session_state.usuarios = {
        "admin@ccm.cl": {
            "password": "admin123",
            "rol": "Administrador",
            "nombre_completo": "Administrador del Sistema",
            "cargo": "Administrador",
            "departamento": "Informática",
            "activo": True
        },
        "creador@ccm.cl": {
            "password": "123",
            "rol": "Creador SIC",
            "nombre_completo": "Juan Pérez",
            "cargo": "Asistente Administrativo",
            "departamento": "Área Médica",
            "activo": True
        },
        "jefe.area@ccm.cl": {
            "password": "123",
            "rol": "Jefe de Área",
            "nombre_completo": "María González",
            "cargo": "Jefe Área Médica",
            "departamento": "Área Médica",
            "activo": True
        },
        "finanzas@ccm.cl": {
            "password": "123",
            "rol": "Jefe de Finanzas",
            "nombre_completo": "Carlos Rodríguez",
            "cargo": "Jefe de Finanzas",
            "departamento": "Finanzas",
            "activo": True
        },
        "supervisor@ccm.cl": {
            "password": "123",
            "rol": "Supervisor Mercado Público",
            "nombre_completo": "Ana Martínez",
            "cargo": "Supervisor de Adquisiciones",
            "departamento": "Adquisiciones",
            "activo": True
        },
        "jefe.adm@ccm.cl": {
            "password": "123",
            "rol": "Jefe Administrativo",
            "nombre_completo": "Pedro Soto",
            "cargo": "Jefe Administrativo",
            "departamento": "Administración",
            "activo": True
        },
        "director@ccm.cl": {
            "password": "123",
            "rol": "Director",
            "nombre_completo": "Luis Morales",
            "cargo": "Director CCM",
            "departamento": "Dirección",
            "activo": True
        },
        "visualizador@ccm.cl": {
            "password": "123",
            "rol": "Visualizador",
            "nombre_completo": "Visualizador Sistema",
            "cargo": "Visualizador",
            "departamento": "Administración",
            "activo": True
        }
    }
if 'registro_cambios' not in st.session_state:
    st.session_state.registro_cambios = []

# Mover la creación de ejemplos a una función separada
def crear_solicitudes_ejemplo():
    if 'solicitudes_ejemplo_creadas' not in st.session_state:
        st.session_state.solicitudes_ejemplo_creadas = False

    if not st.session_state.solicitudes_ejemplo_creadas and not st.session_state.solicitudes:
        # Agregar las 3 solicitudes de ejemplo solo si no hay solicitudes existentes
        st.session_state.solicitudes["SIC-2024-0001"] = {
            "num_sic": "SIC-2024-0001",
            "fecha": date.today(),
            "area_origen": "Área Médica",
            "destinatario": "Director del CCM 'Coyhaique'",
            "tipo_compra": "Convenio Marco",
            "nombre_proveedor": "Proveedor 1",
            "rut_proveedor": "11.111.111-1",
            "descripcion": "Insumos médicos",
            "motivo": "Reposición de stock",
            "valor_estimado": 1500000,
            "estado": "Pendiente",
            "creador": {
                "nombre": "Juan Pérez",
                "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}
            },
            "aprobaciones": {
                "jefe_area": {"estado": "Pendiente", "comentario": "", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}},
                "finanzas": {"estado": "Pendiente", "comentario": "", "cdp": "", "catalogo": "", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}},
                "supervisor": {"estado": "Pendiente", "comentario": "", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}},
                "jefe_adm": {"estado": "Pendiente", "comentario": "", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}},
                "director": {"estado": "Pendiente", "comentario": "", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}}
            }
        }

        # Solicitud pendiente de Finanzas (Jefe de Área ya aprobó)
        st.session_state.solicitudes["SIC-2024-0002"] = {
            "num_sic": "SIC-2024-0002",
            "fecha": date.today(),
            "area_origen": "Área Médica",
            "destinatario": "Director del CCM 'Coyhaique'",
            "tipo_compra": "Licitación Pública",
            "licitacion_num": "2024-01",
            "saldo": 5000000,
            "nombre_proveedor": "Proveedor 2",
            "rut_proveedor": "22.222.222-2",
            "descripcion": "Equipamiento médico",
            "motivo": "Actualización de equipos",
            "valor_estimado": 3000000,
            "estado": "Pendiente",
            "creador": {
                "nombre": "Juan Pérez",
                "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}
            },
            "aprobaciones": {
                "jefe_area": {"estado": "Aprobado", "comentario": "Aprobado según especificaciones", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}},
                "finanzas": {"estado": "Pendiente", "comentario": "", "cdp": "", "catalogo": "", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}},
                "supervisor": {"estado": "Pendiente", "comentario": "", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}},
                "jefe_adm": {"estado": "Pendiente", "comentario": "", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}},
                "director": {"estado": "Pendiente", "comentario": "", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}}
            }
        }

        # Solicitud pendiente de Supervisor (Finanzas ya aprobó)
        st.session_state.solicitudes["SIC-2024-0003"] = {
            "num_sic": "SIC-2024-0003",
            "fecha": date.today(),
            "area_origen": "Área Médica",
            "destinatario": "Director del CCM 'Coyhaique'",
            "tipo_compra": "Compra Ágil",
            "nombre_proveedor": "Proveedor 3",
            "rut_proveedor": "33.333.333-3",
            "descripcion": "Material de oficina",
            "motivo": "Reposición mensual",
            "valor_estimado": 500000,
            "estado": "Pendiente",
            "creador": {
                "nombre": "Juan Pérez",
                "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}
            },
            "aprobaciones": {
                "jefe_area": {"estado": "Aprobado", "comentario": "Aprobado", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}},
                "finanzas": {"estado": "Aprobado", "comentario": "Presupuesto disponible", "cdp": "CDP-2024-001", "catalogo": "CAT-001", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}},
                "supervisor": {"estado": "Pendiente", "comentario": "", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}},
                "jefe_adm": {"estado": "Pendiente", "comentario": "", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}},
                "director": {"estado": "Pendiente", "comentario": "", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}}
            }
        }

        # Solicitud pendiente de Jefe Administrativo
        st.session_state.solicitudes["SIC-2024-0004"] = {
            "num_sic": "SIC-2024-0004",
            "fecha": date.today(),
            "area_origen": "Área Médica",
            "destinatario": "Director del CCM 'Coyhaique'",
            "tipo_compra": "Convenio Marco",
            "nombre_proveedor": "Proveedor 4",
            "rut_proveedor": "44.444.444-4",
            "descripcion": "Equipos de computación",
            "motivo": "Renovación de equipos",
            "valor_estimado": 2500000,
            "estado": "Pendiente",
            "creador": {
                "nombre": "Juan Pérez",
                "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}
            },
            "aprobaciones": {
                "jefe_area": {"estado": "Aprobado", "comentario": "Aprobado", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}},
                "finanzas": {"estado": "Aprobado", "comentario": "Presupuesto disponible", "cdp": "CDP-2024-002", "catalogo": "CAT-002", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}},
                "supervisor": {"estado": "Aprobado", "comentario": "Aprobado según normativa", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}},
                "jefe_adm": {"estado": "Pendiente", "comentario": "", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}},
                "director": {"estado": "Pendiente", "comentario": "", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}}
            }
        }

        # Solicitud pendiente de Director
        st.session_state.solicitudes["SIC-2024-0005"] = {
            "num_sic": "SIC-2024-0005",
            "fecha": date.today(),
            "area_origen": "Área Médica",
            "destinatario": "Director del CCM 'Coyhaique'",
            "tipo_compra": "Licitación Pública",
            "licitacion_num": "2024-02",
            "saldo": 8000000,
            "nombre_proveedor": "Proveedor 5",
            "rut_proveedor": "55.555.555-5",
            "descripcion": "Equipamiento médico especializado",
            "motivo": "Implementación nueva área",
            "valor_estimado": 7500000,
            "estado": "Pendiente",
            "creador": {
                "nombre": "Juan Pérez",
                "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}
            },
            "aprobaciones": {
                "jefe_area": {"estado": "Aprobado", "comentario": "Aprobado", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}},
                "finanzas": {"estado": "Aprobado", "comentario": "Presupuesto aprobado", "cdp": "CDP-2024-003", "catalogo": "CAT-003", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}},
                "supervisor": {"estado": "Aprobado", "comentario": "Proceso licitatorio correcto", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}},
                "jefe_adm": {"estado": "Aprobado", "comentario": "Aprobado según procedimientos", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}},
                "director": {"estado": "Pendiente", "comentario": "", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}}
            }
        }

        # Agregar esta SIC en la función crear_solicitudes_ejemplo()
        # Solicitud completamente aprobada
        st.session_state.solicitudes["SIC-2024-0006"] = {
            "num_sic": "SIC-2024-0006",
            "fecha": date.today(),
            "area_origen": "Área Médica",
            "destinatario": "Director del CCM 'Coyhaique'",
            "tipo_compra": "Convenio Marco",
            "nombre_proveedor": "Proveedor 6",
            "rut_proveedor": "66.666.666-6",
            "descripcion": "Equipamiento de laboratorio",
            "motivo": "Actualización de equipos de laboratorio clínico",
            "valor_estimado": 4500000,
            "estado": "Aprobado",
            "creador": {
                "nombre": "Juan Pérez",
                "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}
            },
            "aprobaciones": {
                "finanzas": {
                    "estado": "Aprobado", 
                    "comentario": "Presupuesto disponible", 
                    "cdp": "CDP-2024-004",
                    "catalogos": [  # Cambiar de "catalogo" a "catalogos" como lista
                        {
                            "numero": "22-01-001",
                            "monto": 2500000
                        },
                        {
                            "numero": "22-02-001",
                            "monto": 2000000
                        }
                    ],
                    "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}
                },
                "jefe_area": {
                    "estado": "Aprobado", 
                    "comentario": "Equipamiento necesario para el servicio", 
                    "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}
                },
                "supervisor": {
                    "estado": "Aprobado", 
                    "comentario": "Proceso de compra validado", 
                    "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}
                },
                "jefe_adm": {
                    "estado": "Aprobado", 
                    "comentario": "Documentación completa", 
                    "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}
                },
                "director": {
                    "estado": "Aprobado", 
                    "comentario": "Se autoriza la compra", 
                    "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}
                }
            }
        }

        st.session_state.solicitudes_ejemplo_creadas = True
        st.session_state.sic_counter = 7  # Actualizado para empezar después de los ejemplos

def login():
    st.sidebar.header("Inicio de Sesión")
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Contraseña", type="password")
    
    if st.sidebar.button("Iniciar Sesión"):
        if email in st.session_state.usuarios:
            user_data = st.session_state.usuarios[email]
            if user_data["password"] == password:
                if user_data["activo"]:
                    st.session_state.user = email
                    st.session_state.rol = user_data["rol"]
                    return True
                else:
                    st.sidebar.error("Usuario desactivado")
            else:
                st.sidebar.error("Contraseña incorrecta")
        else:
            st.sidebar.error("Email no encontrado")
    return False

def crear_sic():
    st.title("Crear Nueva Solicitud Interna de Compra (SIC)")
    
    # Control de pasos en session_state
    if 'paso_creacion' not in st.session_state:
        st.session_state.paso_creacion = 1
    
    # Generar número SIC
    año_actual = date.today().year
    num_sic = f"SIC-{año_actual}-{st.session_state.sic_counter:04d}"
    
    # PASO 1: Información básica y tipo de compra
    if st.session_state.paso_creacion == 1:
        with st.form("paso1_form"):
            st.write(f"N° SIC: {num_sic}")
            fecha = st.date_input("Fecha", value=date.today())
            
            area_origen = st.selectbox(
                "Área",
                [
                    "Área Médica",
                    "Área Administrativa",
                    "Enfermerías"
                ]
            )
            
            destinatario = st.text_input("Destinatario", value="Director del CCM 'Coyhaique'")
            
            tipo_compra = st.radio(
                "Tipo de Compra",
                ["Convenio Marco", "Licitación Pública", "Compra Ágil", "Trato Directo", "OPI"],
                horizontal=True,
                key="tipo_compra",
                index=None
            )
            
            st.markdown("### Su Declaración de Conflicto de Interés")
            st.markdown("""
                <div style="
                    background-color: #E7F1FF;
                    border: 1px solid #CCE5FF;
                    border-radius: 5px;
                    padding: 15px;
                    margin: 10px 0;
                    font-size: 14px;
                    color: #004085;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                ">
                    <p style='margin-bottom: 10px; font-size: 15px;'>
                        <strong>⚠️ ¡IMPORTANTE! Existe conflicto de interés cuando hay:</strong>
                    </p>
                    <ul style='list-style-type: none; padding-left: 10px; margin: 0;'>
                        <li style='margin-bottom: 8px;'>
                            👥 <strong>Vínculos Familiares:</strong> 
                            cónyuge, parientes hasta 3er grado consanguíneo, 2do grado afín
                        </li>
                        <li style='margin-bottom: 8px;'>
                            💼 <strong>Vínculos Comerciales:</strong> 
                            socio >10%, director, gerente, empleado (últimos 24 meses)
                        </li>
                        <li style='margin-bottom: 8px;'>
                            🔍 <strong>Otros Vínculos:</strong> 
                            participación en bases o afectación a la imparcialidad
                        </li>
                    </ul>
                    <p style='margin-top: 12px; font-size: 13px; color: #DC3545;'>
                        ⚖️ <strong>Nota:</strong> La no declaración puede resultar en sanciones administrativas, 
                        disciplinarias y/o penales según Ley N° 19.886 y N° 18.575
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            st.write("¿Tiene algún conflicto de interés con esta compra?")
            conflicto_creador = st.radio(
                "",  # Label vacío porque ya pusimos la pregunta arriba
                ["No", "Sí"],
                horizontal=True,
                key="conflicto_creador",
                index=None
            )
            
            if conflicto_creador == "Sí":
                detalle_conflicto = st.text_area(
                    "Por favor, detalle el conflicto de interés:",
                    key="detalle_conflicto_creador"
                )
            else:
                detalle_conflicto = ""
            
            submitted = st.form_submit_button("Siguiente")
            
            if submitted:
                if not tipo_compra:
                    st.error("Debe seleccionar un tipo de compra")
                    return
                if not conflicto_creador:
                    st.error("Debe declarar si existe o no conflicto de interés")
                    return
                if conflicto_creador == "Sí" and not detalle_conflicto:
                    st.error("Debe detallar el conflicto de interés")
                    return
                
                # Guardar datos del paso 1 en session_state
                st.session_state.paso1_datos = {
                    "num_sic": num_sic,
                    "fecha": fecha,
                    "area_origen": area_origen,
                    "destinatario": destinatario,
                    "conflicto_creador": conflicto_creador,
                    "detalle_conflicto": detalle_conflicto,
                    "tipo_compra": tipo_compra
                }
                
                # Avanzar al siguiente paso
                st.session_state.paso_creacion = 2
                st.rerun()

    # PASO 2: Campos específicos según tipo de compra
    elif st.session_state.paso_creacion == 2:
        st.subheader("Detalles de la Compra")
        datos_paso1 = st.session_state.paso1_datos
        
        # Mostrar resumen del paso 1
        with st.expander("Resumen del Paso 1", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.write("### Información Básica")
                st.write(f"N° SIC: {datos_paso1['num_sic']}")
                st.write(f"Fecha: {datos_paso1['fecha']}")
                st.write(f"Área: {datos_paso1['area_origen']}")
                st.write(f"Destinatario: {datos_paso1['destinatario']}")
            with col2:
                st.write("### Tipo de Compra")
                st.write(f"Tipo seleccionado: {datos_paso1['tipo_compra']}")
                st.write("### Conflicto de Interés")
                st.write(f"Declaración: {datos_paso1['conflicto_creador']}")
                if datos_paso1['conflicto_creador'] == "Sí":
                    st.write(f"Detalle: {datos_paso1['detalle_conflicto']}")
        
        st.markdown("---")
        
        # Formulario del paso 2
        with st.form("paso2_form"):
            # Campos específicos para Licitación Pública
            if datos_paso1["tipo_compra"] == "Licitación Pública":
                col1, col2 = st.columns(2)
                with col1:
                    licitacion_num = st.text_input("ID Licitación")
                    nombre_proveedor = st.text_input("Nombre del Proveedor")
                with col2:
                    saldo = st.number_input(
                        "Saldo Disponible ($)",
                        min_value=0,
                        step=1000,
                        help="Saldo disponible para la licitación"
                    )
                    rut_proveedor = st.text_input(
                        "RUT del Proveedor",
                        placeholder="XX.XXX.XXX-X"
                    )
            elif datos_paso1["tipo_compra"] == "Trato Directo":
                col1, col2 = st.columns(2)
                with col1:
                    nombre_proveedor = st.text_input("Nombre del Proveedor")
                with col2:
                    rut_proveedor = st.text_input(
                        "RUT del Proveedor",
                        placeholder="XX.XXX.XXX-X"
                    )
                causal = st.selectbox(
                    "Causal de Trato Directo",
                    [
                        "Proveedor Único",
                        "Emergencia, Urgencia o Imprevisto",
                        "Servicios Especializados",
                        "Prórroga de Contrato",
                        "Confianza y Seguridad",
                        "Otros"
                    ]
                )
                if causal == "Otros":
                    detalle_causal = st.text_area("Especifique la causal")
            elif datos_paso1["tipo_compra"] == "OPI":
                col1, col2 = st.columns(2)
                with col1:
                    nombre_proveedor = st.text_input("Nombre del Proveedor")
                    num_opi = st.text_input(
                        "N° OPI",
                        placeholder="OPI-XXXX-XXXX"
                    )
                with col2:
                    rut_proveedor = st.text_input(
                        "RUT del Proveedor",
                        placeholder="XX.XXX.XXX-X"
                    )
            else:
                licitacion_num = None
                saldo = None
                nombre_proveedor = None
                rut_proveedor = None
                causal = None
                detalle_causal = None
                num_opi = None
            
            # Campos comunes para todos los tipos
            descripcion_compra = st.text_area("Se solicita la compra de")
            motivo_solicitud = st.text_area("Motivo y fundamento de la solicitud")
            valor_estimado = st.number_input(
                "Valor Estimado de la Compra ($)",
                min_value=0,
                value=None,
                step=1000,
                placeholder="Ingrese el valor estimado"
            )
            
            # Subida de archivos
            st.subheader("Documentos de Respaldo")
            archivos_subidos = st.file_uploader(
                "Subir documentos de respaldo",
                accept_multiple_files=True,
                type=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png'],
                help="Formatos permitidos: PDF, DOC, DOCX, XLS, XLSX, JPG, PNG"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("Crear Solicitud")
            with col2:
                if st.form_submit_button("Volver"):
                    st.session_state.paso_creacion = 1
                    st.rerun()

            if submitted:
                # Validaciones según tipo de compra
                if datos_paso1["tipo_compra"] == "Licitación Pública":
                    if not all([licitacion_num, saldo, nombre_proveedor, rut_proveedor]):
                        st.error("Para Licitación Pública, todos los campos son obligatorios")
                        return
                elif datos_paso1["tipo_compra"] == "Trato Directo":
                    if not all([nombre_proveedor, rut_proveedor, saldo, causal]):
                        st.error("Para Trato Directo, todos los campos son obligatorios")
                        return
                    if causal == "Otros" and not detalle_causal:
                        st.error("Debe especificar la causal del Trato Directo")
                        return
                elif datos_paso1["tipo_compra"] == "OPI":
                    if not all([nombre_proveedor, rut_proveedor, saldo, num_opi]):
                        st.error("Para OPI, todos los campos son obligatorios")
                        return

                # Procesar archivos subidos
                archivos_guardados = []
                if archivos_subidos:
                    for archivo in archivos_subidos:
                        archivo_info = {
                            "nombre": archivo.name,
                            "tipo": archivo.type,
                            "contenido": archivo.getvalue()
                        }
                        archivos_guardados.append(archivo_info)
                
                # Crear nueva solicitud
                nueva_solicitud = {
                    **datos_paso1,  # Incluir datos del paso 1
                    "descripcion": descripcion_compra,
                    "motivo": motivo_solicitud,
                    "valor_estimado": valor_estimado,
                    "licitacion_num": licitacion_num if datos_paso1["tipo_compra"] == "Licitación Pública" else None,
                    "saldo": saldo if datos_paso1["tipo_compra"] == "Licitación Pública" else None,
                    "nombre_proveedor": nombre_proveedor if datos_paso1["tipo_compra"] == "Licitación Pública" else None,
                    "rut_proveedor": rut_proveedor if datos_paso1["tipo_compra"] == "Licitación Pública" else None,
                    "causal_trato_directo": causal if datos_paso1["tipo_compra"] == "Trato Directo" else None,
                    "detalle_causal": detalle_causal if datos_paso1["tipo_compra"] == "Trato Directo" and causal == "Otros" else None,
                    "num_opi": num_opi if datos_paso1["tipo_compra"] == "OPI" else None,
                    "archivos": archivos_guardados,
                    "estado": "Pendiente",
                    "creador": {
                        "nombre": st.session_state.usuarios[st.session_state.user]['nombre_completo'],
                        "conflicto_interes": {
                            "tiene_conflicto": datos_paso1["conflicto_creador"],
                            "detalle": datos_paso1.get("detalle_conflicto", "")
                        }
                    },
                    "aprobaciones": {
                        "jefe_area": {"estado": "Pendiente", "comentario": "", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}},
                        "finanzas": {"estado": "Pendiente", "comentario": "", "cdp": "", "catalogo": "", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}},
                        "supervisor": {"estado": "Pendiente", "comentario": "", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}},
                        "jefe_adm": {"estado": "Pendiente", "comentario": "", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}},
                        "director": {"estado": "Pendiente", "comentario": "", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}}
                    }  # Cierre del diccionario nueva_solicitud
                }
                # Guardar solicitud y limpiar estado
                st.session_state.solicitudes[datos_paso1["num_sic"]] = nueva_solicitud
                st.session_state.sic_counter += 1
                del st.session_state.paso_creacion
                del st.session_state.paso1_datos
                
                st.success(f"Solicitud {datos_paso1['num_sic']} creada exitosamente")
                st.session_state.current_tab = "Dashboard"
                time.sleep(1)
                st.rerun()

def mostrar_cuadro_conflicto_interes():
    st.markdown("### Su Declaración de Conflicto de Interés")
    
    st.markdown("""
        <div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
            <p style='font-weight: bold; color: #0d47a1;'>
                ⚠️ ¡IMPORTANTE! Existe conflicto de interés cuando hay:
            </p>
            
            <p style='margin-left: 20px; color: #1565c0;'>
                👥 <strong>Vínculos Familiares:</strong> cónyuge, parientes hasta 3er grado consanguíneo, 2do grado afín
            </p>
            
            <p style='margin-left: 20px; color: #1565c0;'>
                💼 <strong>Vínculos Comerciales:</strong> socio >10%, director, gerente, empleado (últimos 24 meses)
            </p>
            
            <p style='margin-left: 20px; color: #1565c0;'>
                🔍 <strong>Otros Vínculos:</strong> participación en bases o afectación a la imparcialidad
            </p>
            
            <p style='color: #dc3545; margin-top: 15px;'>
                ⚖️ <strong>Nota:</strong> La no declaración puede resultar en sanciones administrativas, disciplinarias y/o penales según Ley N° 19.886 y N° 18.575
            </p>
        </div>
    """, unsafe_allow_html=True)

    conflicto_creador = st.radio(
        "¿Tiene algún conflicto de interés con esta compra?",
        ["No", "Sí"],
        horizontal=True,
        key="conflicto_creador",
        index=None
    )
    
    return conflicto_creador

def revisar_solicitudes():
    st.title("Revisar Solicitudes")
    
    if not st.session_state.solicitudes:
        st.warning("No hay solicitudes pendientes")
        return

    # Mapeo de roles a sus campos correspondientes en las aprobaciones
    rol_mapping = {
        "Jefe de Área": "jefe_area",
        "Jefe de Finanzas": "finanzas",
        "Supervisor Mercado Público": "supervisor",
        "Jefe Administrativo": "jefe_adm",
        "Director": "director"
    }
    
    rol_actual = rol_mapping.get(st.session_state.rol)
    
    # Filtrar solicitudes según el rol
    solicitudes_pendientes = {}
    for num_sic, solicitud in st.session_state.solicitudes.items():
        # Lógica de filtrado específica para cada rol
        if st.session_state.rol == "Jefe de Área":
            if (solicitud['area_origen'] == "Área Médica" and 
                solicitud['aprobaciones']['jefe_area']['estado'] == "Pendiente"):
                solicitudes_pendientes[num_sic] = solicitud
        
        elif st.session_state.rol == "Jefe de Finanzas":
            if ((solicitud['area_origen'] != "Área Médica" or 
                 solicitud['aprobaciones']['jefe_area']['estado'] == "Aprobado") and 
                solicitud['aprobaciones']['finanzas']['estado'] == "Pendiente"):
                solicitudes_pendientes[num_sic] = solicitud
        
        elif st.session_state.rol == "Supervisor Mercado Público":
            if (solicitud['aprobaciones']['finanzas']['estado'] == "Aprobado" and 
                solicitud['aprobaciones']['supervisor']['estado'] == "Pendiente"):
                solicitudes_pendientes[num_sic] = solicitud
        
        elif st.session_state.rol == "Jefe Administrativo":
            if (solicitud['aprobaciones']['supervisor']['estado'] == "Aprobado" and 
                solicitud['aprobaciones']['jefe_adm']['estado'] == "Pendiente"):
                solicitudes_pendientes[num_sic] = solicitud
        
        elif st.session_state.rol == "Director":
            if (solicitud['aprobaciones']['jefe_adm']['estado'] == "Aprobado" and 
                solicitud['aprobaciones']['director']['estado'] == "Pendiente"):
                solicitudes_pendientes[num_sic] = solicitud

    if not solicitudes_pendientes:
        st.info(f"No hay solicitudes pendientes para {st.session_state.rol}")
        return

    # Mostrar solicitudes pendientes
    for num_sic, solicitud in solicitudes_pendientes.items():
        with st.expander(f"Solicitud {num_sic} - Pendiente de aprobación"):
            # Información básica siempre visible
            st.write(f"Fecha: {solicitud['fecha']}")
            st.write(f"Área: {solicitud['area_origen']}")
            st.write(f"Proveedor: {solicitud['nombre_proveedor']}")
            st.write(f"Valor Estimado: ${solicitud['valor_estimado']:,}")
            st.write(f"Descripción: {solicitud['descripcion']}")
            st.write(f"Tipo de Compra: {solicitud['tipo_compra']}")

            # Mostrar información específica según el rol y la cadena de aprobación
            if st.session_state.rol == "Jefe de Finanzas":
                # Puede ver la aprobación del Jefe de Área si existe
                if solicitud['area_origen'] == "Área Médica":
                    st.write("### Aprobación Jefe de Área")
                    st.write(f"Estado: {solicitud['aprobaciones']['jefe_area']['estado']}")
                    st.write(f"Comentario: {solicitud['aprobaciones']['jefe_area']['comentario']}")
                    if 'conflicto_interes' in solicitud['aprobaciones']['jefe_area']:
                        st.write(f"Conflicto de Interés: {solicitud['aprobaciones']['jefe_area']['conflicto_interes']['tiene_conflicto']}")
                        if solicitud['aprobaciones']['jefe_area']['conflicto_interes']['tiene_conflicto'] == "Sí":
                            st.write(f"Detalle: {solicitud['aprobaciones']['jefe_area']['conflicto_interes']['detalle']}")

            elif st.session_state.rol == "Supervisor Mercado Público":
                # Puede ver aprobaciones anteriores
                st.write("### Aprobaciones Anteriores")
                if solicitud['area_origen'] == "Área Médica":
                    mostrar_aprobacion("Jefe de Área", solicitud['aprobaciones']['jefe_area'])
                mostrar_aprobacion("Jefe de Finanzas", solicitud['aprobaciones']['finanzas'])
                # Mostrar información de CDP
                if solicitud['aprobaciones']['finanzas']['cdp']:
                    st.write(f"N° CDP: {solicitud['aprobaciones']['finanzas']['cdp']}")
                    if 'catalogos' in solicitud['aprobaciones']['finanzas']:
                        st.write("### Distribución Presupuestaria")
                        for catalogo in solicitud['aprobaciones']['finanzas']['catalogos']:
                            st.write(f"- {catalogo['numero']}: ${catalogo['monto']:,}")

            elif st.session_state.rol == "Jefe Administrativo":
                # Puede ver todas las aprobaciones anteriores
                st.write("### Aprobaciones Anteriores")
                if solicitud['area_origen'] == "Área Médica":
                    mostrar_aprobacion("Jefe de Área", solicitud['aprobaciones']['jefe_area'])
                mostrar_aprobacion("Jefe de Finanzas", solicitud['aprobaciones']['finanzas'])
                mostrar_aprobacion("Supervisor Mercado Público", solicitud['aprobaciones']['supervisor'])
                # Mostrar información de CDP
                if solicitud['aprobaciones']['finanzas']['cdp']:
                    st.write(f"N° CDP: {solicitud['aprobaciones']['finanzas']['cdp']}")
                    if 'catalogos' in solicitud['aprobaciones']['finanzas']:
                        st.write("### Distribución Presupuestaria")
                        for catalogo in solicitud['aprobaciones']['finanzas']['catalogos']:
                            st.write(f"- {catalogo['numero']}: ${catalogo['monto']:,}")

            elif st.session_state.rol == "Director":
                # Puede ver todas las aprobaciones anteriores
                st.write("### Aprobaciones Anteriores")
                if solicitud['area_origen'] == "Área Médica":
                    mostrar_aprobacion("Jefe de Área", solicitud['aprobaciones']['jefe_area'])
                mostrar_aprobacion("Jefe de Finanzas", solicitud['aprobaciones']['finanzas'])
                mostrar_aprobacion("Supervisor Mercado Público", solicitud['aprobaciones']['supervisor'])
                mostrar_aprobacion("Jefe Administrativo", solicitud['aprobaciones']['jefe_adm'])
                # Mostrar información de CDP
                if solicitud['aprobaciones']['finanzas']['cdp']:
                    st.write(f"N° CDP: {solicitud['aprobaciones']['finanzas']['cdp']}")
                    if 'catalogos' in solicitud['aprobaciones']['finanzas']:
                        st.write("### Distribución Presupuestaria")
                        for catalogo in solicitud['aprobaciones']['finanzas']['catalogos']:
                            st.write(f"- {catalogo['numero']}: ${catalogo['monto']:,}")

            # Campos específicos para Jefe de Finanzas (sin línea divisoria aquí)
            if st.session_state.rol == "Jefe de Finanzas":
                st.markdown("---")  # Una sola línea divisoria
                st.subheader("Información Presupuestaria")
                
                # CDP
                cdp = st.text_input(
                    "Número de CDP",
                    key=f"cdp_{num_sic}",
                    help="Ingrese el número del Certificado de Disponibilidad Presupuestaria"
                )
                
                # Sección de Catálogos
                st.write("### Distribución Presupuestaria")
                st.info("Ingrese los catálogos presupuestarios y sus montos correspondientes")
                
                # Inicializar variables de session_state
                if 'catalogos_count' not in st.session_state:
                    st.session_state.catalogos_count = {}
                
                if num_sic not in st.session_state.catalogos_count:
                    st.session_state.catalogos_count[num_sic] = 1
                
                catalogos = []
                total_catalogos = 0
                
                # Mostrar campos de catálogos
                for i in range(st.session_state.catalogos_count[num_sic]):
                    col1, col2 = st.columns(2)
                    with col1:
                        numero_catalogo = st.text_input(
                            "Número de Catálogo",
                            key=f"catalogo_num_{num_sic}_{i}",
                            placeholder="Ej: 22-01-001"
                        )
                    with col2:
                        monto_catalogo = st.number_input(
                            "Monto ($)",
                            key=f"catalogo_monto_{num_sic}_{i}",
                            min_value=0,
                            step=1000
                        )
                    
                    if numero_catalogo or monto_catalogo > 0:
                        catalogos.append({
                            "numero": numero_catalogo,
                            "monto": monto_catalogo
                        })
                        total_catalogos += monto_catalogo
                
                # Botón para agregar más catálogos
                col1, col2 = st.columns([1, 3])
                with col1:
                    if st.button("➕ Agregar Catálogo", key=f"add_catalogo_{num_sic}"):
                        st.session_state.catalogos_count[num_sic] += 1
                        st.rerun()
                
                # Mostrar diferencia de montos
                if total_catalogos > 0:
                    diferencia = solicitud['valor_estimado'] - total_catalogos
                    
                    if diferencia != 0:
                        if diferencia > 0:
                            st.warning(f"⚠️ Falta asignar ${diferencia:,} para igualar el valor solicitado")
                        else:
                            st.warning(f"⚠️ El monto asignado excede en ${abs(diferencia):,} al valor solicitado")
                    else:
                        st.success("✅ Los montos coinciden correctamente")
                
                st.markdown("---")  # Una sola línea divisoria al final
                
                # Botón único para descargar CDP
                if cdp and catalogos and total_catalogos == solicitud['valor_estimado']:
                    # Crear una copia temporal de la solicitud con los datos actuales
                    solicitud_temp = solicitud.copy()
                    solicitud_temp['aprobaciones']['finanzas'].update({
                        'cdp': cdp,
                        'catalogos': catalogos
                    })
                    
                    try:
                        # Generar CDP temporal y convertir a bytes
                        cdp_buffer = generar_cdp(solicitud_temp)
                        cdp_bytes = cdp_buffer.getvalue()  # Convertir BytesIO a bytes
                        
                        # Botón de descarga
                        st.download_button(
                            label="📥 Descargar CDP",
                            data=cdp_bytes,
                            file_name=f"CDP_{solicitud['num_sic']}.pdf",
                            mime="application/pdf",
                            key=f"download_cdp_{num_sic}"
                        )
                    except Exception as e:
                        st.error(f"Error al generar el CDP: {str(e)}")
                else:
                    st.info("Complete el N° CDP y la distribución presupuestaria para generar el CDP")
            
            # Mostrar cuadro de conflicto de interés
            st.markdown("### Su Declaración de Conflicto de Interés")
            st.markdown("""
                <div style="
                    background-color: #E7F1FF;
                    border: 1px solid #CCE5FF;
                    border-radius: 5px;
                    padding: 15px;
                    margin: 10px 0;
                    font-size: 14px;
                    color: #004085;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                ">
                    <p style='margin-bottom: 10px; font-size: 15px;'>
                        <strong>⚠️ ¡IMPORTANTE! Existe conflicto de interés cuando hay:</strong>
                    </p>
                    <ul style='list-style-type: none; padding-left: 10px; margin: 0;'>
                        <li style='margin-bottom: 8px;'>
                            👥 <strong>Vínculos Familiares:</strong> 
                            cónyuge, parientes hasta 3er grado consanguíneo, 2do grado afín
                        </li>
                        <li style='margin-bottom: 8px;'>
                            💼 <strong>Vínculos Comerciales:</strong> 
                            socio >10%, director, gerente, empleado (últimos 24 meses)
                        </li>
                        <li style='margin-bottom: 8px;'>
                            🔍 <strong>Otros Vínculos:</strong> 
                            participación en bases o afectación a la imparcialidad
                        </li>
                    </ul>
                    <p style='margin-top: 12px; font-size: 13px; color: #DC3545;'>
                        ⚖️ <strong>Nota:</strong> La no declaración puede resultar en sanciones administrativas, 
                        disciplinarias y/o penales según Ley N° 19.886 y N° 18.575
                    </p>
                </div>
            """, unsafe_allow_html=True)

            # Radio button para la selección de conflicto
            conflicto = st.radio(
                "¿Tiene algún conflicto de interés con esta compra?",
                ["No", "Sí"],
                key=f"conflicto_{rol_actual}_{num_sic}",
                horizontal=True,
                index=None
            )
            
            if conflicto == "Sí":
                detalle_conflicto = st.text_area(
                    "Detalle del conflicto de interés",
                    key=f"detalle_conflicto_{rol_actual}_{num_sic}"
                )
            else:
                detalle_conflicto = ""
            
            # Radio button para el estado de aprobación
            estado = st.radio(
                "Estado de aprobación",
                ["Aprobado", "Rechazado"],
                key=f"radio_{rol_actual}_{num_sic}",
                index=None
            )
            
            # Campo de comentario
            comentario = st.text_area(
                "Comentario",
                key=f"comentario_{rol_actual}_{num_sic}",
                help="El comentario es obligatorio en caso de rechazo"
            )
            
            # Botón de guardar con validaciones específicas
            if st.button("Guardar decisión", key=f"btn_{rol_actual}_{num_sic}"):
                if conflicto is None:
                    st.error("⚠️ Debe indicar si tiene o no conflicto de interés")
                elif conflicto == "Sí" and not detalle_conflicto.strip():
                    st.error("⚠️ Debe detallar el conflicto de interés declarado")
                elif estado is None:
                    st.error("⚠️ Debe seleccionar si aprueba o rechaza la solicitud")
                elif estado == "Rechazado" and not comentario.strip():
                    st.error("⚠️ Debe ingresar un comentario explicando el motivo del rechazo")
                elif st.session_state.rol == "Jefe de Finanzas" and estado == "Aprobado":
                    if not cdp:
                        st.error("⚠️ Debe ingresar el número de CDP")
                    elif not catalogos:
                        st.error("⚠️ Debe ingresar al menos un catálogo presupuestario")
                    elif total_catalogos != solicitud['valor_estimado']:
                        st.error("⚠️ El total de los catálogos debe ser igual al valor de la solicitud")
                    else:
                        # Guardar con información presupuestaria
                        solicitud['aprobaciones'][rol_actual].update({
                            'estado': estado,
                            'comentario': comentario,
                            'cdp': cdp,
                            'catalogos': catalogos,
                            'conflicto_interes': {
                                "tiene_conflicto": conflicto,
                                "detalle": detalle_conflicto if conflicto == "Sí" else ""
                            }
                        })
                        st.success("✅ Decisión guardada exitosamente")
                        time.sleep(1)
                        st.rerun()
                else:
                    # Guardar decisión normal
                    solicitud['aprobaciones'][rol_actual].update({
                        'estado': estado,
                        'comentario': comentario,
                        'conflicto_interes': {
                            "tiene_conflicto": conflicto,
                            "detalle": detalle_conflicto if conflicto == "Sí" else ""
                        }
                    })
                    st.success("✅ Decisión guardada exitosamente")
                    time.sleep(1)
                    st.rerun()

            # Mostrar archivos adjuntos si existen
            if 'archivos' in solicitud and solicitud['archivos']:
                st.subheader("Documentos Adjuntos")
                for i, archivo in enumerate(solicitud['archivos']):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"📎 {archivo['nombre']} ({archivo['tipo']})")
                    with col2:
                        st.download_button(
                            label="Descargar",
                            data=archivo['contenido'],
                            file_name=archivo['nombre'],
                            mime=archivo['tipo'],
                            key=f"download_{num_sic}_{i}"
                        )
                
                st.markdown("---")  # Separador después de los documentos
            
            # Mostrar CDP solo si está aprobado por Finanzas
            if solicitud['aprobaciones']['finanzas']['estado'] == "Aprobado":
                st.write("### Certificado de Disponibilidad Presupuestaria")
                cdp_buffer = generar_cdp(solicitud)
                st.download_button(
                    label="Descargar CDP",
                    data=cdp_buffer,
                    file_name=f"CDP_{solicitud['num_sic']}.pdf",
                    mime="application/pdf",
                    key=f"cdp_download_{num_sic}"
                )
            
            # Mostrar Resumen SIC solo si está aprobado por el Director
            if solicitud['aprobaciones']['director']['estado'] == "Aprobado":
                st.write("### Resumen SIC")
                st.download_button(
                    label="Descargar Resumen SIC",
                    data=generar_resumen_sic(solicitud),
                    file_name=f"SIC_{solicitud['num_sic']}_Resumen.pdf",
                    mime="application/pdf",
                    key=f"download_resumen_{num_sic}"
                )

# Función auxiliar para mostrar aprobaciones
def mostrar_aprobacion(titulo, aprobacion):
    st.write(f"#### {titulo}")
    st.write(f"Estado: {aprobacion['estado']}")
    if aprobacion['comentario']:
        st.write(f"Comentario: {aprobacion['comentario']}")
    if 'conflicto_interes' in aprobacion:
        st.write(f"Conflicto de Interés: {aprobacion['conflicto_interes']['tiene_conflicto']}")
        if aprobacion['conflicto_interes']['tiene_conflicto'] == "Sí":
            st.write(f"Detalle: {aprobacion['conflicto_interes']['detalle']}")

def mostrar_resumen_solicitudes():
    st.header("Resumen de Solicitudes")
    
    if not st.session_state.solicitudes:
        st.info("No hay solicitudes registradas")
        return

    # Crear DataFrame para mejor visualización
    import pandas as pd
    
    datos_resumen = []
    for num_sic, solicitud in st.session_state.solicitudes.items():
        # Determinar estado general
        estado_actual = "Pendiente"
        if solicitud['aprobaciones']['director']['estado'] == "Aprobado":
            estado_actual = "Aprobado"
        elif any(apr['estado'] == "Rechazado" for apr in solicitud['aprobaciones'].values()):
            estado_actual = "Rechazado"
        
        # Formatear el valor estimado
        valor_estimado = solicitud['valor_estimado']
        valor_formateado = f"${valor_estimado:,}" if valor_estimado is not None else "No especificado"
        
        # Crear fila de datos
        fila = {
            'N° SIC': num_sic,
            'Fecha': solicitud['fecha'],
            'Área': solicitud['area_origen'],
            'Proveedor': solicitud['nombre_proveedor'],
            'Valor ($)': valor_formateado,
            'Estado': estado_actual,
            'Jefe Área': "N/A" if solicitud['area_origen'] in ["Área Administrativa", "Enfermerías"] else solicitud['aprobaciones']['jefe_area']['estado'],
            'N° CDP': solicitud['aprobaciones']['finanzas']['cdp'] or 'Pendiente',
            'Finanzas': solicitud['aprobaciones']['finanzas']['estado'],
            'Supervisor': solicitud['aprobaciones']['supervisor']['estado'],
            'Jefe Adm': solicitud['aprobaciones']['jefe_adm']['estado'],
            'Director': solicitud['aprobaciones']['director']['estado']
        }
        datos_resumen.append(fila)
    
    df = pd.DataFrame(datos_resumen)
    
    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        estado_filtro = st.multiselect(
            "Filtrar por Estado",
            options=["Pendiente", "Aprobado", "Rechazado"],
            default=["Pendiente", "Aprobado", "Rechazado"]
        )
    with col2:
        fecha_filtro = st.date_input(
            "Filtrar desde fecha",
            value=None
        )
    
    # Aplicar filtros
    if fecha_filtro:
        df = df[df['Fecha'] >= fecha_filtro]
    if estado_filtro:
        df = df[df['Estado'].isin(estado_filtro)]

    # Estilo del DataFrame
    def highlight_estado(val):
        if val == "Aprobado":
            return 'background-color: #90EE90'
        elif val == "Rechazado":
            return 'background-color: #FFB6C1'
        return ''

    # Mostrar DataFrame con estilo
    st.dataframe(
        df.style.applymap(highlight_estado, subset=['Estado', 'Jefe Área', 'Finanzas', 'Supervisor', 'Jefe Adm', 'Director']),
        use_container_width=True
    )

    # Selector para ver detalles
    num_sic_seleccionado = st.selectbox(
        "Seleccionar SIC para ver detalles",
        options=df['N° SIC'].tolist(),
        format_func=lambda x: f"Ver detalles de {x}"
    )

    if num_sic_seleccionado:
        mostrar_detalles_solicitud(num_sic_seleccionado)

def mostrar_dashboard_aprobaciones():
    st.header("Panel de Control de Aprobaciones")
    
    # Estadísticas al inicio del dashboard
    st.subheader("Estadísticas Generales")
    
    # Crear DataFrame para las estadsticas
    df = pd.DataFrame(st.session_state.solicitudes).T
    
    col1, col2, col3 = st.columns(3)
    with col1:
        total_solicitudes = len(df)
        st.metric("Total Solicitudes", total_solicitudes)
    with col2:
        aprobadas = len([s for s in st.session_state.solicitudes.values() 
                        if s['aprobaciones']['director']['estado'] == "Aprobado"])
        st.metric("Aprobadas", aprobadas)
    with col3:
        pendientes = len([s for s in st.session_state.solicitudes.values() 
                        if s['aprobaciones']['director']['estado'] == "Pendiente"])
        st.metric("Pendientes", pendientes)
    
    st.markdown("---")  # Separador
    
    # Definir colores base para cada rol
    colores_roles = {
        "Jefe de\nÁrea": "#FF9800",  # Naranja
        "Jefe de\nFinanzas": "#4CAF50",  # Verde
        "Supervisor\nMercado\nPúblico": "#FF9800",  # Naranja
        "Jefe\nAdministrativo": "#4CAF50",  # Verde
        "Director": "#4CAF50"  # Verde
    }
    
    # Contar solicitudes pendientes por nivel
    pendientes_por_nivel = {
        "Jefe de\nÁrea": 0,
        "Jefe de\nFinanzas": 0,
        "Supervisor\nMercado\nPúblico": 0,
        "Jefe\nAdministrativo": 0,
        "Director": 0
    }
    
    # Listas para almacenar detalles de SIC pendientes por nivel
    detalles_pendientes = {
        "Jefe de\nÁrea": [],
        "Jefe de\nFinanzas": [],
        "Supervisor\nMercado\nPúblico": [],
        "Jefe\nAdministrativo": [],
        "Director": []
    }
    
    for num_sic, solicitud in st.session_state.solicitudes.items():
        # Solo contar para Jefe de Área si es del área médica y está pendiente
        if solicitud['area_origen'] == "Área Médica" and solicitud['aprobaciones']['jefe_area']['estado'] == "Pendiente":
            pendientes_por_nivel["Jefe de\nÁrea"] += 1
            detalles_pendientes["Jefe de\nÁrea"].append(num_sic)
        
        # Para Finanzas, contar si:
        # 1. Es del área administrativa o enfermerías y está pendiente
        # 2. Es del área médica, está aprobada por jefe de área y está pendiente
        if ((solicitud['area_origen'] in ["Área Administrativa", "Enfermerías"] and 
             solicitud['aprobaciones']['finanzas']['estado'] == "Pendiente") or
            (solicitud['area_origen'] == "Área Médica" and 
             solicitud['aprobaciones']['jefe_area']['estado'] == "Aprobado" and 
             solicitud['aprobaciones']['finanzas']['estado'] == "Pendiente")):
            pendientes_por_nivel["Jefe de\nFinanzas"] += 1
            detalles_pendientes["Jefe de\nFinanzas"].append(num_sic)
        
        # Para el resto de los niveles, contar solo si el nivel anterior aprobó
        elif solicitud['aprobaciones']['finanzas']['estado'] == "Aprobado":
            if solicitud['aprobaciones']['supervisor']['estado'] == "Pendiente":
                pendientes_por_nivel["Supervisor\nMercado\nPúblico"] += 1
                detalles_pendientes["Supervisor\nMercado\nPúblico"].append(num_sic)
            elif solicitud['aprobaciones']['supervisor']['estado'] == "Aprobado":
                if solicitud['aprobaciones']['jefe_adm']['estado'] == "Pendiente":
                    pendientes_por_nivel["Jefe\nAdministrativo"] += 1
                    detalles_pendientes["Jefe\nAdministrativo"].append(num_sic)
                elif solicitud['aprobaciones']['jefe_adm']['estado'] == "Aprobado":
                    if solicitud['aprobaciones']['director']['estado'] == "Pendiente":
                        pendientes_por_nivel["Director"] += 1
                        detalles_pendientes["Director"].append(num_sic)

    # Mostrar mtricas en cards
    col1, col2, col3, col4, col5 = st.columns(5)
    cols = [col1, col2, col3, col4, col5]
    
    for i, (rol, cantidad) in enumerate(pendientes_por_nivel.items()):
        with cols[i]:
            # Determinar color según cantidad
            if cantidad == 0:
                estado_color = "#4CAF50"  # Verde
                emoji = "✅"
                border_color = "#4CAF50"  # Verde
            elif 1 <= cantidad <= 3:
                estado_color = "#FF9800"  # Naranja
                emoji = "⚠️"
                border_color = "#FF9800"  # Naranja
            else:
                estado_color = "#F44336"  # Rojo
                emoji = "🚨"
                border_color = "#F44336"  # Rojo
            
            # Crear contenedor con color
            with st.container():
                st.markdown(
                    f"""
                    <div style="
                        padding: 15px;
                        border-radius: 5px;
                        border: 2px solid {border_color};
                        background-color: rgba({','.join(map(str, hex_to_rgb(estado_color)))}, 0.1);
                        min-height: 200px;
                        display: flex;
                        flex-direction: column;
                        justify-content: space-between;
                    ">
                        <div>
                            <h4 style="
                                color: {estado_color};
                                margin: 0;
                                white-space: pre-line;
                                line-height: 1.3;
                                font-size: 1.2em;
                            ">{rol} {emoji}</h4>
                        </div>
                        <div style="
                            text-align: center;
                            margin-top: auto;
                            padding-bottom: 10px;
                        ">
                            <div style="
                                font-size: 36px;
                                color: {estado_color};
                                font-weight: bold;
                            ">{cantidad}</div>
                            <div style="
                                font-size: 18px;
                                color: {estado_color};
                            ">pendientes</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

# Agregar función auxiliar para convertir colores hex a RGB
def hex_to_rgb(color):
    # Remover el # si existe
    color = color.lstrip('#')
    
    # Convertir el color hexadecimal a RGB
    if len(color) == 6:
        r = int(color[:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:], 16)
        return (r, g, b)
    
    # Colores predefinidos
    color_map = {
        "#4CAF50": (76, 175, 80),    # Verde
        "#FF9800": (255, 152, 0),    # Naranja
        "#F44336": (244, 67, 54)     # Rojo
    }
    
    return color_map.get(color, (0, 0, 0))

def validar_email(email):
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'  # Acepta cualquier email vlido
    return bool(re.match(patron, email))

def administrar_usuarios():
    st.title("Administración de Usuarios")
    
    # Tabla de usuarios existentes
    st.subheader("Usuarios Existentes")
    usuarios_data = []
    for email, data in st.session_state.usuarios.items():
        if email != "admin@ccm.cl":
            usuarios_data.append({
                "Email": email,
                "Rol": data["rol"],
                "Nombre": data["nombre_completo"],
                "Cargo": data["cargo"],
                "Departamento": data["departamento"],
                "Estado": "Activo" if data["activo"] else "Inactivo",
                "Firma": "✅ Registrada" if data.get("firma") else "❌ No registrada"
            })
    
    if usuarios_data:
        df = pd.DataFrame(usuarios_data)
        st.dataframe(df, use_container_width=True)

    # Selector de modo al principio
    modo_edicion = st.radio("Seleccione una acción:", ["Crear Nuevo Usuario", "Editar Usuario Existente"])
    
    if modo_edicion == "Editar Usuario Existente":
        usuario_a_editar = st.selectbox(
            "Seleccionar Usuario para Editar",
            [e for e in st.session_state.usuarios.keys() if e != "admin@ccm.cl"]
        )
        
        if usuario_a_editar:
            datos_usuario = st.session_state.usuarios[usuario_a_editar]
            with st.form("usuario_form"):
                st.subheader(f"Editando usuario: {usuario_a_editar}")
                
                col1, col2 = st.columns(2)
                with col1:
                    nuevo_password = st.text_input("Nueva Contraseña (opcional)", type="password")
                    if nuevo_password:
                        confirmar_password = st.text_input("Confirmar Nueva Contraseña", type="password")
                    
                    nuevo_rol = st.selectbox(
                        "Rol",
                        [
                            "Creador SIC",
                            "Jefe de Área",
                            "Jefe de Finanzas",
                            "Supervisor Mercado Público",
                            "Jefe Administrativo",
                            "Director",
                            "Visualizador"
                        ],
                        index=[
                            "Creador SIC",
                            "Jefe de Área",
                            "Jefe de Finanzas",
                            "Supervisor Mercado Público",
                            "Jefe Administrativo",
                            "Director",
                            "Visualizador"
                        ].index(datos_usuario["rol"])
                    )
                    nuevo_nombre = st.text_input("Nombre Completo", value=datos_usuario["nombre_completo"])
                    nuevo_cargo = st.text_input("Cargo", value=datos_usuario["cargo"])
                    nuevo_departamento = st.text_input("Departamento", value=datos_usuario["departamento"])
                    
                with col2:
                    st.subheader("Firma del Usuario")
                    if datos_usuario.get("firma"):
                        st.write("Firma actual:")
                        if datos_usuario["firma"]["tipo"].startswith("image"):
                            st.image(datos_usuario["firma"]["contenido"], width=200)
                    
                    nueva_firma = st.file_uploader(
                        "Subir nueva firma (opcional)",
                        type=['jpg', 'jpeg', 'png'],
                        help="Formatos permitidos: JPG, PNG"
                    )
                
                submitted = st.form_submit_button("Guardar Cambios")
                
                if submitted:
                    if nuevo_password and nuevo_password != confirmar_password:
                        st.error("Las contraseñas no coinciden")
                    else:
                        # Actualizar datos
                        if nuevo_password:
                            datos_usuario["password"] = nuevo_password
                        datos_usuario["rol"] = nuevo_rol
                        datos_usuario["nombre_completo"] = nuevo_nombre
                        datos_usuario["cargo"] = nuevo_cargo
                        datos_usuario["departamento"] = nuevo_departamento
                        
                        if nueva_firma:
                            datos_usuario["firma"] = {
                                "nombre_archivo": nueva_firma.name,
                                "tipo": nueva_firma.type,
                                "contenido": nueva_firma.getvalue()
                            }
                            datos_usuario["activo"] = True
                        
                        st.success("Usuario actualizado exitosamente")
                        st.rerun()
    
    else:  # Crear nuevo usuario
        with st.form("nuevo_usuario_form"):
            st.subheader("Crear Nuevo Usuario")
            
            col1, col2 = st.columns(2)
            with col1:
                email = st.text_input("Email")
                password = st.text_input("Contraseña", type="password")
                confirmar_password = st.text_input("Confirmar Contraseña", type="password")
                rol = st.selectbox("Rol", [
                    "Creador SIC",
                    "Jefe de Área",
                    "Jefe de Finanzas",
                    "Supervisor Mercado Público",
                    "Jefe Administrativo",
                    "Director",
                    "Visualizador"
                ])
                nombre_completo = st.text_input("Nombre Completo")
                cargo = st.text_input("Cargo")
                departamento = st.text_input("Departamento")
            
            with col2:
                st.subheader("Firma del Usuario")
                if rol == "Visualizador":
                    st.info("El rol Visualizador no requiere firma digital")
                    firma_archivo = None
                else:
                    st.write("La firma es obligatoria para activar el usuario")
                    firma_archivo = st.file_uploader(
                        "Subir firma digitalizada",
                        type=['jpg', 'jpeg', 'png'],
                        help="Formatos permitidos: JPG, PNG"
                    )
            
            submitted = st.form_submit_button("Crear Usuario")
            
            if submitted:
                if not all([email, password, confirmar_password, rol, nombre_completo, cargo, departamento]):
                    st.error("Por favor complete todos los campos")
                elif password != confirmar_password:
                    st.error("Las contraseñas no coinciden")
                elif not validar_email(email):
                    st.error("Por favor ingrese un email válido")
                elif email in st.session_state.usuarios:
                    st.error("Este email ya está registrado")
                elif not firma_archivo and rol != "Visualizador":
                    st.error("La firma es obligatoria para roles distintos a Visualizador")
                else:
                    nuevo_usuario = {
                        "password": password,
                        "rol": rol,
                        "nombre_completo": nombre_completo,
                        "cargo": cargo,
                        "departamento": departamento,
                        "activo": True
                    }
                    
                    if firma_archivo and rol != "Visualizador":
                        nuevo_usuario["firma"] = {
                            "nombre_archivo": firma_archivo.name,
                            "tipo": firma_archivo.type,
                            "contenido": firma_archivo.getvalue()
                        }
                    
                    st.session_state.usuarios[email] = nuevo_usuario
                    st.success("Usuario creado exitosamente")
                    st.rerun()

def mostrar_formulario():
    st.sidebar.write(f"Usuario actual: {st.session_state.usuarios[st.session_state.user]['nombre_completo']}")
    if st.sidebar.button("Cerrar Sesión"):
        del st.session_state.user
        del st.session_state.rol
        st.rerun()

    # Mostrar pestañas según el rol
    if st.session_state.rol == "Visualizador":
        tab1, tab2 = st.tabs(["Dashboard", "SIC Aprobadas"])
        
        with tab1:
            mostrar_dashboard_aprobaciones()
        with tab2:
            mostrar_sic_aprobadas()
    elif st.session_state.rol == "Administrador":
        tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Resumen", "Gestión de Solicitudes", "Administración"])
        
        with tab1:
            mostrar_dashboard_aprobaciones()
        with tab2:
            mostrar_resumen_solicitudes()
        with tab3:
            revisar_solicitudes()
        with tab4:
            administrar_usuarios()
    else:
        tab1, tab2, tab3 = st.tabs(["Dashboard", "Resumen", "Gestión de Solicitudes"])
        
        with tab1:
            mostrar_dashboard_aprobaciones()
        with tab2:
            mostrar_resumen_solicitudes()
        with tab3:
            if st.session_state.rol == "Creador SIC":
                crear_sic()
            else:
                revisar_solicitudes()

    # Actualizar la pestaña actual
    if tab1:
        st.session_state.current_tab = "Dashboard"
    elif tab2:
        st.session_state.current_tab = "Resumen"
    elif tab3:
        st.session_state.current_tab = "Gestión de Solicitudes"

def main():
    if 'user' not in st.session_state:
        if login():
            crear_solicitudes_ejemplo()  # Crear ejemplos solo al primer inicio
            st.rerun()
    else:
        mostrar_formulario()

def registrar_cambio(accion, usuario, detalles):
    st.session_state.registro_cambios.append({
        "fecha": date.today(),
        "accion": accion,
        "usuario": usuario,
        "detalles": detalles
    })

def generar_cdp(solicitud):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # Configuración de márgenes y posiciones
    # Márgenes estándar: 1 pulgada (72 puntos) en todos los lados
    left_margin = 72
    right_margin = 540  # 612 - 72 = 540 (ancho total - margen izquierdo)
    top_margin = 720   # 792 - 72 = 720 (alto total - margen superior)
    
    # Título y encabezado
    c.setFont("Helvetica-Bold", 12)
    c.drawString(left_margin, top_margin, "EJÉRCITO DE CHILE")
    c.drawString(left_margin, top_margin - 20, "DIVISIÓN DE SALUD")
    c.drawString(left_margin, top_margin - 40, "CENTRO CLÍNICO MILITAR COYHAIQUE")
    
    # Nmero de documento y fecha (alineado a la derecha)
    c.setFont("Helvetica", 10)
    c.drawString(right_margin - 200, top_margin, f"CDP N° {solicitud['aprobaciones']['finanzas']['cdp']}")
    c.drawString(right_margin - 200, top_margin - 20, f"COYHAIQUE, {solicitud['fecha'].strftime('%d-%m-%Y')}")
    
    # Título del documento (centrado)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString((right_margin + left_margin)/2, top_margin - 80, "CERTIFICADO DE DISPONIBILIDAD PRESUPUESTARIA")
    
    # Cuerpo del documento
    c.setFont("Helvetica", 10)
    y = top_margin - 120
    line_height = 15  # Altura de línea estándar
    
    texto = f"""
    El Jefe de Finanzas del Centro Clínico Militar "Coyhaique" que suscribe, certifica que:

    De conformidad al presupuesto disponible, conforme a lo que indica la Ley N° 21.640 "Presupuesto 
    para el Sector Público año 2024", se cuenta con los recursos necesarios para financiar la siguiente 
    adquisición:

    N° SIC: {solicitud['num_sic']}
    Descripción: {solicitud['descripcion']}
    Monto Total: ${f"{solicitud['valor_estimado']:,.0f}".replace(",", ".")}
    Tipo de Compra: {solicitud['tipo_compra']}
    """
    
    # Agregar catálogos si existen
    if 'catalogos' in solicitud['aprobaciones']['finanzas']:
        texto += "\n\nDistribución presupuestaria:"
        for catalogo in solicitud['aprobaciones']['finanzas']['catalogos']:
            if catalogo['numero'] and catalogo['monto'] > 0:
                texto += f"\n{catalogo['numero']}: ${catalogo['monto']:,.0f}".replace(",", ".")
    
    # Escribir el texto línea por línea respetando los saltos
    lineas = texto.strip().split('\n')
    for linea in lineas:
        if linea.strip():  # Si la línea tiene contenido
            c.drawString(left_margin, y, linea.strip())
            y -= line_height
        else:  # Si la línea está vacía (salto de línea)
            y -= line_height  # Agregar espacio adicional
    
    # Sección de firma (centrada en la parte inferior)
    y = 200  # Posición fija para la sección de firma
    c.drawString(left_margin, y, "Se extiende el presente certificado para los fines que correspondan.")
    
    # Línea y datos de firma centrados
    firma_x = (right_margin + left_margin)/2
    y -= 60
    
    # Si hay firma digitalizada, agregarla (centrada)
    if 'firma' in st.session_state.usuarios['finanzas@ccm.cl']:
        firma = st.session_state.usuarios['finanzas@ccm.cl']['firma']
        if firma and firma['tipo'].startswith('image'):
            img = ImageReader(io.BytesIO(firma['contenido']))
            firma_width = 120
            firma_height = 60
            img_x = firma_x - (firma_width/2)
            img_y = y - 20
            c.drawImage(img, img_x, img_y, width=firma_width, height=firma_height)
    
    # Ajustar espaciado de la firma
    c.drawCentredString(firma_x, y - 20, "_____________________________")
    c.drawCentredString(firma_x, y - 40, f"{st.session_state.usuarios['finanzas@ccm.cl']['nombre_completo']}")
    c.drawCentredString(firma_x, y - 55, "Jefe de Finanzas CCM 'Coyhaique'")
    
    c.save()
    buffer.seek(0)
    return buffer

def mostrar_cdp(solicitud):
    buffer = generar_cdp(solicitud)
    st.download_button(
        label="Descargar CDP",
        data=buffer,
        file_name=f"CDP_{solicitud['num_sic']}.pdf",
        mime="application/pdf"
    )

def agregar_linea_divisoria(c, y, left_margin, right_margin):
    """Función auxiliar para dibujar línea divisoria"""
    c.setLineWidth(0.5)  # Línea delgada
    c.line(left_margin, y, right_margin, y)  # Línea horizontal
    return y - 10  # Retorna nueva posición Y con espacio adicional

def generar_resumen_sic(solicitud):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # Configuración de márgenes y posiciones
    left_margin = 72
    right_margin = 540
    top_margin = 720
    
    # Título y encabezado
    c.setFont("Helvetica-Bold", 12)
    c.drawString(left_margin, top_margin, "EJÉRCITO DE CHILE")
    c.drawString(left_margin, top_margin - 20, "DIVISIÓN DE SALUD")
    c.drawString(left_margin, top_margin - 40, "CENTRO CLÍNICO MILITAR COYHAIQUE")
    
    # Número de documento y fecha
    c.setFont("Helvetica", 10)
    c.drawString(right_margin - 200, top_margin, f"SIC N° {solicitud['num_sic']}")
    c.drawString(right_margin - 200, top_margin - 20, f"FECHA: {solicitud['fecha'].strftime('%d-%m-%Y')}")
    
    # Título del documento
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString((right_margin + left_margin)/2, top_margin - 80, "RESUMEN SOLICITUD INTERNA DE COMPRA")
    
    # Contenido del documento
    c.setFont("Helvetica", 10)
    y = top_margin - 120
    line_height = 15
    
    # Información básica
    c.drawString(left_margin, y, f"Área Origen: {solicitud['area_origen']}")
    y -= line_height * 2
    
    c.drawString(left_margin, y, f"Tipo de Compra: {solicitud['tipo_compra']}")
    y -= line_height * 2
    
    # Información específica según tipo de compra
    if solicitud['tipo_compra'] == "Licitación Pública":
        c.drawString(left_margin, y, f"ID Licitación: {solicitud.get('licitacion_num', 'No especificado')}")
        y -= line_height
        c.drawString(left_margin, y, f"Saldo Disponible: ${solicitud.get('saldo', 0):,.0f}")
        y -= line_height
    elif solicitud['tipo_compra'] == "Trato Directo":
        c.drawString(left_margin, y, f"Causal: {solicitud.get('causal_trato_directo', 'No especificado')}")
        y -= line_height
        if solicitud.get('detalle_causal'):
            c.drawString(left_margin, y, f"Detalle Causal: {solicitud['detalle_causal']}")
            y -= line_height
    elif solicitud['tipo_compra'] == "OPI":
        c.drawString(left_margin, y, f"N° OPI: {solicitud.get('num_opi', 'No especificado')}")
        y -= line_height
    
    # Información del proveedor
    y -= line_height
    c.drawString(left_margin, y, f"Proveedor: {solicitud['nombre_proveedor']}")
    y -= line_height
    c.drawString(left_margin, y, f"RUT: {solicitud['rut_proveedor']}")
    y -= line_height * 2
    
    # Descripción y motivo
    c.drawString(left_margin, y, "Descripción:")
    y -= line_height
    # Dividir descripción en líneas si es muy larga
    descripcion_lines = textwrap.wrap(solicitud['descripcion'], width=80)
    for line in descripcion_lines:
        c.drawString(left_margin + 20, y, line)
        y -= line_height
    
    y -= line_height
    c.drawString(left_margin, y, "Motivo:")
    y -= line_height
    # Dividir motivo en líneas si es muy largo
    motivo_lines = textwrap.wrap(solicitud['motivo'], width=80)
    for line in motivo_lines:
        c.drawString(left_margin + 20, y, line)
        y -= line_height
    
    # Valor estimado
    y -= line_height
    c.drawString(left_margin, y, f"Valor Estimado: ${solicitud['valor_estimado']:,.0f}")
    
    # Información de CDP si existe
    if solicitud['aprobaciones']['finanzas']['cdp']:
        y -= line_height * 2
        c.drawString(left_margin, y, f"N° CDP: {solicitud['aprobaciones']['finanzas']['cdp']}")
        
        # Mostrar catálogos si existen
        if 'catalogos' in solicitud['aprobaciones']['finanzas']:
            y -= line_height
            c.drawString(left_margin, y, "Distribución Presupuestaria:")
            y -= line_height
            for catalogo in solicitud['aprobaciones']['finanzas']['catalogos']:
                c.drawString(left_margin + 20, y, f"{catalogo['numero']}: ${catalogo['monto']:,.0f}")
                y -= line_height
    
    # Cadena de aprobaciones
    y -= line_height * 2
    c.drawString(left_margin, y, "Estado de Aprobaciones:")
    y -= line_height
    
    for rol, aprobacion in solicitud['aprobaciones'].items():
        rol_formato = rol.replace('_', ' ').title()
        c.drawString(left_margin + 20, y, f"{rol_formato}: {aprobacion['estado']}")
        y -= line_height
        if aprobacion['comentario']:
            c.drawString(left_margin + 40, y, f"Comentario: {aprobacion['comentario']}")
            y -= line_height
    
    c.save()
    buffer.seek(0)
    return buffer

def mostrar_info_conflicto_interes(key_suffix=""):
    """
    Muestra información sobre conflicto de interés como tooltip
    Parámetro key_suffix para generar keys únicas
    """
    st.markdown("### Declaración de Conflicto de Interés ❔", help="""
        **Declaración de Conflicto de Interés**

        Según la Ley de Compras Públicas N° 19.886 y la Ley de Bases N° 18.575, existe conflicto de interés cuando:

        **1. Vínculos Familiares:**
        • Cónyuge o conviviente civil
        • Parientes hasta tercer grado de consanguinidad (padres, hijos, hermanos, abuelos, nietos, tíos, sobrinos)
        • Parientes hasta segundo grado de afinidad (suegros, cuñados)

        **2. Vínculos Comerciales o Laborales:**
        • Ser socio o accionista con más del 10% del capital
        • Ser director, administrador, representante o gerente
        • Tener vínculo laboral actual o dentro de los últimos 24 meses

        **3. Otros Vínculos:**
        • Participación en la elaboración de bases o términos de referencia
        • Cualquier circunstancia que afecte la imparcialidad en la toma de decisiones

        La no declaración de conflictos de interés puede resultar en sanciones administrativas, medidas disciplinarias y responsabilidad civil y/o penal según corresponda.
        """)

def mostrar_detalles_solicitud(num_sic):
    """
    Muestra los detalles completos de una solicitud específica
    """
    solicitud = st.session_state.solicitudes[num_sic]
    
    with st.expander("Detalles de la Solicitud", expanded=True):
        # Información básica
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write("### Información General")
            st.write(f"**N° SIC:** {num_sic}")
            st.write(f"**Fecha:** {solicitud['fecha']}")
            st.write(f"**Área:** {solicitud['area_origen']}")
            st.write(f"**Tipo de Compra:** {solicitud['tipo_compra']}")
        
        with col2:
            st.write("### Datos de la Compra")
            st.write(f"**Valor Estimado:** ${solicitud['valor_estimado']:,}")
            if solicitud['tipo_compra'] == "Licitación Pública":
                st.write(f"**N° Licitación:** {solicitud['licitacion_num']}")
            elif solicitud['tipo_compra'] == "Trato Directo":
                st.write(f"**Causal:** {solicitud['causal_trato_directo']}")
                if solicitud.get('detalle_causal'):
                    st.write(f"**Detalle Causal:** {solicitud['detalle_causal']}")
            elif solicitud['tipo_compra'] == "OPI":
                st.write(f"**N° OPI:** {solicitud['num_opi']}")
            
            if solicitud.get('saldo'):
                st.write(f"**Saldo:** ${solicitud['saldo']:,}")
            st.write(f"**Proveedor:** {solicitud['nombre_proveedor']}")
            if solicitud.get('rut_proveedor'):
                st.write(f"**RUT:** {solicitud['rut_proveedor']}")
        
        with col3:
            st.write("### Estado")
            estado_actual = "Pendiente"
            if solicitud['aprobaciones']['director']['estado'] == "Aprobado":
                estado_actual = "Aprobado"
            elif any(apr['estado'] == "Rechazado" for apr in solicitud['aprobaciones'].values()):
                estado_actual = "Rechazado"
            
            if estado_actual == "Aprobado":
                st.success(f"Estado: {estado_actual}")
            elif estado_actual == "Rechazado":
                st.error(f"Estado: {estado_actual}")
            else:
                st.warning(f"Estado: {estado_actual}")
        
        # Descripción y motivo
        st.write("### Descripción y Motivo")
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Descripción:**")
            st.write(solicitud['descripcion'])
        with col2:
            st.write("**Motivo:**")
            st.write(solicitud['motivo'])
        
        # Información del creador
        st.write("### Información del Solicitante")
        st.write(f"**Nombre:** {solicitud['creador']['nombre']}")
        st.write(f"**Conflicto de Interés:** {solicitud['creador']['conflicto_interes']['tiene_conflicto']}")
        if solicitud['creador']['conflicto_interes']['tiene_conflicto'] == "Sí":
            st.write(f"**Detalle del Conflicto:** {solicitud['creador']['conflicto_interes']['detalle']}")
        
        # Estado de aprobaciones
        st.write("### Estado de Aprobaciones")
        for rol, aprobacion in solicitud['aprobaciones'].items():
            if rol == "jefe_area" and solicitud['area_origen'] not in ["Área Mdica"]:
                continue
                
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**{rol.replace('_', ' ').title()}:**")
                if aprobacion['estado'] == "Aprobado":
                    st.success(aprobacion['estado'])
                elif aprobacion['estado'] == "Rechazado":
                    st.error(aprobacion['estado'])
                else:
                    st.warning(aprobacion['estado'])
            
            with col2:
                if aprobacion['comentario']:
                    st.write(f"**Comentario:** {aprobacion['comentario']}")
                if rol == "finanzas" and aprobacion['cdp']:
                    st.write(f"**N° CDP:** {aprobacion['cdp']}")
                    if 'catalogos' in aprobacion:
                        st.write("**Distribución Presupuestaria:**")
                        for catalogo in aprobacion['catalogos']:
                            st.write(f"- {catalogo['numero']}: ${catalogo['monto']:,}")
            
            with col3:
                st.write(f"**Conflicto:** {aprobacion['conflicto_interes']['tiene_conflicto']}")
                if aprobacion['conflicto_interes']['tiene_conflicto'] == "Sí":
                    st.write(f"**Detalle:** {aprobacion['conflicto_interes']['detalle']}")
        
        # Documentos
        st.write("### Documentos")
        col1, col2 = st.columns(2)
        
        # Columna 1: Archivos adjuntos
        with col1:
            st.write("**Archivos Adjuntos:**")
            if 'archivos' in solicitud and solicitud['archivos']:
                for i, archivo in enumerate(solicitud['archivos']):
                    st.download_button(
                        label=f"📎 {archivo['nombre']}",
                        data=archivo['contenido'],
                        file_name=archivo['nombre'],
                        mime=archivo['tipo'],
                        key=f"download_detail_{num_sic}_{i}"
                    )
            else:
                st.write("No hay archivos adjuntos")
        
        # Columna 2: CDP y Resumen SIC
        with col2:
            st.write("**Documentos Generados:**")
            if solicitud['aprobaciones']['finanzas']['estado'] == "Aprobado":
                cdp_buffer = generar_cdp(solicitud)
                st.download_button(
                    label="📄 Descargar CDP",
                    data=cdp_buffer,
                    file_name=f"CDP_{num_sic}.pdf",
                    mime="application/pdf",
                    key=f"cdp_download_detail_{num_sic}"
                )
            
            if solicitud['aprobaciones']['director']['estado'] == "Aprobado":
                st.download_button(
                    label="📄 Descargar Resumen SIC",
                    data=generar_resumen_sic(solicitud),
                    file_name=f"SIC_{num_sic}_Resumen.pdf",
                    mime="application/pdf",
                    key=f"resumen_download_detail_{num_sic}"
                )
            
            if solicitud['aprobaciones']['finanzas']['estado'] != "Aprobado" and \
               solicitud['aprobaciones']['director']['estado'] != "Aprobado":
                st.write("No hay documentos generados disponibles")

# Agregar nueva función para mostrar solo SIC aprobadas
def mostrar_sic_aprobadas():
    st.header("Solicitudes Internas de Compra Aprobadas")
    
    # Filtrar solo las SIC completamente aprobadas
    sic_aprobadas = {
        num_sic: solicitud 
        for num_sic, solicitud in st.session_state.solicitudes.items()
        if all(apr['estado'] == "Aprobado" for apr in solicitud['aprobaciones'].values())
    }
    
    if not sic_aprobadas:
        st.info("No hay solicitudes completamente aprobadas")
        return

    # Crear DataFrame para mejor visualización
    datos_resumen = []
    for num_sic, solicitud in sic_aprobadas.items():
        # Formatear el valor estimado
        valor_estimado = solicitud['valor_estimado']
        valor_formateado = f"${valor_estimado:,}" if valor_estimado is not None else "No especificado"
        
        # Crear fila de datos
        fila = {
            'N° SIC': num_sic,
            'Fecha': solicitud['fecha'],
            'Área': solicitud['area_origen'],
            'Proveedor': solicitud['nombre_proveedor'],
            'Valor ($)': valor_formateado,
            'Tipo Compra': solicitud['tipo_compra'],
            'N° CDP': solicitud['aprobaciones']['finanzas']['cdp']
        }
        datos_resumen.append(fila)
    
    df = pd.DataFrame(datos_resumen)
    
    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        area_filtro = st.multiselect(
            "Filtrar por Área",
            options=df['Área'].unique(),
            default=df['Área'].unique()
        )
    with col2:
        fecha_filtro = st.date_input(
            "Filtrar desde fecha",
            value=None
        )
    
    # Aplicar filtros
    if fecha_filtro:
        df = df[df['Fecha'] >= fecha_filtro]
    if area_filtro:
        df = df[df['Área'].isin(area_filtro)]

    # Mostrar DataFrame
    st.dataframe(df, use_container_width=True)

    # Selector para ver detalles
    sic_seleccionada = st.selectbox(
        "Seleccionar SIC para ver detalles",
        options=df['N° SIC'].tolist(),
        format_func=lambda x: f"Ver detalles de {x}"
    )

    if sic_seleccionada:
        mostrar_detalles_sic_aprobada(sic_seleccionada)

def mostrar_detalles_sic_aprobada(num_sic):
    solicitud = st.session_state.solicitudes[num_sic]
    
    with st.expander(f"Detalles de {num_sic}", expanded=True):
        # Información básica
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write("### Información General")
            st.write(f"Fecha: {solicitud['fecha']}")
            st.write(f"Área: {solicitud['area_origen']}")
            st.write(f"Tipo de Compra: {solicitud['tipo_compra']}")
        
        with col2:
            st.write("### Proveedor")
            st.write(f"Nombre: {solicitud['nombre_proveedor']}")
            st.write(f"RUT: {solicitud['rut_proveedor']}")
        
        with col3:
            st.write("### Valores")
            st.write(f"Valor Estimado: ${solicitud['valor_estimado']:,}")
            st.write(f"N° CDP: {solicitud['aprobaciones']['finanzas']['cdp']}")
        
        # Descripción y motivo
        st.write("### Descripción")
        st.write(solicitud['descripcion'])
        st.write("### Motivo")
        st.write(solicitud['motivo'])
        
        # Información de aprobaciones
        st.write("### Cadena de Aprobación")
        for rol, aprobacion in solicitud['aprobaciones'].items():
            st.write(f"**{rol.replace('_', ' ').title()}**")
            st.write(f"Estado: {aprobacion['estado']}")
            if aprobacion['comentario']:
                st.write(f"Comentario: {aprobacion['comentario']}")
        
        # Botones para descargar documentos
        col1, col2 = st.columns(2)
        with col1:
            # Botón para descargar CDP
            cdp_buffer = generar_cdp(solicitud)
            st.download_button(
                label="📄 Descargar CDP",
                data=cdp_buffer,
                file_name=f"CDP_{num_sic}.pdf",
                mime="application/pdf"
            )
        
        with col2:
            # Botón para descargar Resumen SIC
            resumen_buffer = generar_resumen_sic(solicitud)
            st.download_button(
                label="📄 Descargar Resumen SIC",
                data=resumen_buffer,
                file_name=f"SIC_{num_sic}_Resumen.pdf",
                mime="application/pdf"
            )

if __name__ == "__main__":
    main()
